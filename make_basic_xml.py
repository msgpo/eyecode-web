#!/usr/bin/env python

import argparse, os, pandas, string
import lxml.builder as lb
from io import StringIO
from lxml import etree
from glob import glob
from datetime import datetime
from db import DB, Experiment

# Utility methods {{{

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Text answers for questions
questions = {
    "gender":       ["female", "male", "unreported"],
    "education":    ["none", "bachelors", "masters", "phd", "other"],
    "major":        ["current", "past", "no"],
    "difficulty":   ["easy", "medium", "hard"],
    "correct":      ["most", "half", "few"]
}

def lookup_answer(q, a):
    """Looks up a numeric answer in the questions table, otherwise
    returns the string answer"""
    if q in questions:
        return questions[q][int(a)]
    else:
        return a

def expand_backspace(s):
    """Interprets a backspace control character in a string
    to mean 'delete previous character' and then excludes
    other non-printable characters."""
    new_s = []
    for c in s:
        if c == '\b' or ord(c) == 24:
            new_s = new_s[:-1]  # Backspace
        elif c in string.printable:
            new_s.append(c)
    return "".join(new_s)

# }}}

# Auto Grading {{{

MATCH_EXACT = 3
MATCH_LINES = 2
MATCH_VALUES = 1
MATCH_NONE = 0

CORRECT_EXACT = 10
CORRECT_LINES = 9
CORRECT_VALUES = 7
COMMON_EXACT = 4
COMMON_LINES = 3
COMMON_VALUES = 2

def common_errors(base, version):
    """Returns a list of common error responses for the given
    program base and version"""
    if base == "between":
        return ["[8, 7, 9]\n[1, 0, 8, 1]\n[8]"]
    elif base == "scope":
        return ["22"]
    elif base == "counting":
        return ["The count is 1\nThe count is 2\nThe count is 3\nThe count is 4\nDone counting"]
    elif base == "partition":
        if version == "balanced":
            return ["low\nlow\nhigh\nhigh"]
        elif (version == "unbalanced") or (version == "unbalanced_pivot"):
            return ["low\nlow\nhigh"]
    elif base == "overload":
        if version == "plusmixed":
            return ["7\n9\n\"53\"", "7\n9\n8"]
        elif version == "multmixed":
            return ["12\n14\n8"]
        elif version == "strings":
            return ["hibye\nstreetpenny\n8"]
    elif base == "funcall":
        return ["-60", "0", "-80"]
    elif base == "order":
        return ["5 2 10"]
    elif base == "whitespace":
        return ["0 5\n1 10\n2 15"]
    elif base == "initvar":
        if version == "bothbad":
            return ["0\n10"]
        elif version == "good":
            return ["1\n2\n3\n4\n1\n2\n3\n4"]
        elif version == "onebad":
            return ["24\n10"]
    return []

def grade_string(expected, actual):
    """Grades a single response against the true (actual) output.
    Possible return values are:
        * MATCH_EXACT (perfect match)
        * MATCH_LINES (correct number of lines, non-formatting characters match)
        * MATCH_VALUES (non-formatting characters match)
        * MATCH_NONE (no match)"""
    # Convert to universal newlines, strip extraneous whitespace
    expected_io = StringIO(unicode(expected.strip()), newline=None)
    actual_io = StringIO(unicode(actual.strip()), newline=None)

    expected_str = expected_io.read()
    actual_str = actual_io.read()

    # Pefect match
    if expected_str == actual_str:
        return MATCH_EXACT

    format_chars = ['[', ']', ',', ' ', '\n', '"', '\'']
    table = dict.fromkeys(map(ord, format_chars), None)

    expected_io.seek(0)
    expected_lines = [line.strip() for line in expected_io.readlines()]
    actual_io.seek(0)
    actual_lines = [line.strip() for line in actual_io.readlines()]

    # Remove blank lines
    removed_blanks = False

    if len(expected_lines) != len(actual_lines):
        actual_lines = [line for line in actual_lines if len(line.strip()) > 0]
        removed_blanks = True

    # Check for line by line exact/partial match
    if len(expected_lines) == len(actual_lines):
        exact_match = True
        partial_match = False

        for (e_line, a_line) in zip(expected_lines, actual_lines):
            if e_line != a_line:
                exact_match = False
                if (e_line.translate(table).lower() == a_line.translate(table).lower()):
                    partial_match = True
                else:
                    partial_match = False
                    break

        if exact_match:
            return MATCH_EXACT if not removed_blanks else MATCH_LINES
        elif partial_match:
            return MATCH_LINES

    # Check for partial match of values only
    if expected_str.translate(table).lower() == actual_str.translate(table).lower():
        return MATCH_VALUES

    return MATCH_NONE

def auto_grade(trial, true_output):
    """Auto-grades a trial response against the true output. Response
    must either be correct or a common error (otherwise, a manual grade
    should have existed)"""
    category = ""
    value = -1
    match = grade_string(true_output, trial.response)

    # Try common errors
    if match == MATCH_NONE:
        for error_output in common_errors(trial.program_base, trial.program_version):
            match = grade_string(error_output, trial.response)
            if match != MATCH_NONE:
                break

        # Common error
        category = "common "
        if match == MATCH_EXACT:
            category += "exact"
            value = COMMON_EXACT
        elif match == MATCH_LINES:
            category += "lines"
            value = COMMON_LINES
        elif match == MATCH_VALUES:
            category += "values"
            value = COMMON_VALUES
    else:
        # Correct answer
        category = "correct "
        if match == MATCH_EXACT:
            category += "exact"
            value = CORRECT_EXACT
        elif match == MATCH_LINES:
            category += "lines"
            value = CORRECT_LINES
        elif match == MATCH_VALUES:
            category += "values"
            value = CORRECT_VALUES

    if value < 0:
        category = "unknown"

    return category, value

# }}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=str, default="sqlite:///local.db")
    parser.add_argument("--xml_path", type=str, default="response_data.xml")
    args = parser.parse_args()

    xml_path = args.xml_path

    # Gather Python program files
    prog_dir = os.path.abspath("programs")
    prog_paths = glob(os.path.join(prog_dir, "*.py"))
    prog_names = sorted([os.path.splitext(os.path.split(p)[1])[0]
        for p in prog_paths])

    # Create map from program name to program output
    prog_output = dict([(p, open(os.path.join(prog_dir, "output", "{0}.py.txt".format(p)), "r").read())
                        for p in prog_names])

    # Load program metrics
    metrics_df = pandas.read_csv("program_metrics.csv")

    # Create <experiments> element
    xml_experiments = lb.E.experiments(created=datetime.strftime(datetime.now(), TIME_FORMAT))

    # ================
    # Import SQL Files
    # ================

    db_path = args.database
    exp_id = 0
    num_imported = 0

    # Connect using SQLAlchemy to import objects
    db = DB()
    db.connect_to_db(db_path, echo=False)

    for db_exp in db.session.query(Experiment).all():

        # Skip experiments that aren't finished or approved
        if db_exp.ended is None:
            print "Skipping experiment {0} (no end time)".format(db_exp)
            continue

        print "Importing experiment {0}".format(db_exp)

        # Create <experiment> element
        xml_exp = lb.E.experiment(id = str(exp_id),
            started=str(db_exp.started), ended=str(db_exp.ended))

        # Pre/post test answers
        xml_qs = lb.E.questions()
        for test_answer in db_exp.test_answers:
            if test_answer.question == "thoughts":
                continue  # Skip for privacy
            answer = lookup_answer(test_answer.question, test_answer.answer)
            xml_qs.append(lb.E.question(answer, name=test_answer.question))

        xml_exp.append(xml_qs)

        # ======
        # Trials
        # ======

        xml_trials = lb.E.trials()
        ordered_trials = sorted(db_exp.trials, key=lambda t: t.started)

        for i, t in enumerate(db_exp.trials):
            # Skip restarted or unfinished trials
            if t.restarted > 0:
                print "Skipping trial {0} (restarted)".format(t)
                continue

            if not t.ended:
                print "Skipping trial {0} (no end time)".format(t)
                continue

            print "Importing trial: {0}".format(t)

            # What the program actually outputs
            true_output = prog_output["{0}_{1}".format(t.program_base, t.program_version)]

            grade_category = ""
            grade_value = -1
            auto_graded = False

            grade_category, grade_value = auto_grade(t, true_output)
            auto_graded = True

            # Build <trial> element
            xml_trial = lb.E.trial(id=str(t.id), order=str(i), base=t.program_base,
                version=t.program_version, started=str(t.started), ended=str(t.ended),
                language=t.language, **{ "auto-graded": str(auto_graded),
                "grade-category": str(grade_category),
                "grade-value": str(grade_value)})

            # Add code/output metrics
            trial_metrics = metrics_df[(metrics_df["base"] == t.program_base) &
                (metrics_df["version"] == t.program_version)].irow(0)

            xml_metrics = lb.E.metrics()
            metric_cols = [c for c in metrics_df.columns
                if not c in ["base", "version"]]

            for col in metric_cols:
                xml_metrics.append(lb.E.metric(
                    name = col,
                    value = str(trial_metrics[col])
                ))

            # Add metrics to <trial>
            xml_trial.append(xml_metrics)

            # True output
            true_elem = lb.ET.Element("true-output")
            true_elem.text = lb.ET.CDATA(true_output)
            xml_trial.append(true_elem)

            # Predicted output
            predicted_output = t.response
            pred_elem = lb.ET.Element("predicted-output")
            pred_elem.text = lb.ET.CDATA(predicted_output)
            xml_trial.append(pred_elem)

            # Responses (intermediary keystrokes)
            xml_responses = lb.E.responses()
            for resp in t.responses:
                timestamp = resp.timestamp / 1000  # Milliseconds
                xml_resp = lb.E.response(timestamp=str(timestamp))
                xml_resp.text = lb.ET.CDATA(expand_backspace(resp.response))
                xml_responses.append(xml_resp)
                    
            xml_trial.append(xml_responses)

            # Add trial to <trials>
            xml_trials.append(xml_trial)

        # Add trials to <experiment>
        xml_exp.append(xml_trials)

        # Add experiment to <experiments>
        xml_experiments.append(xml_exp)

        num_imported += 1
        exp_id += 1

    # Close database session
    db.session.close()

    # Done
    print "Imported {0} experiments".format(num_imported)

    with open(xml_path, "w") as xml_file:
        etree.ElementTree(xml_experiments).write(xml_file, xml_declaration=True,
            pretty_print=True, encoding="UTF-8")

    print "Wrote {0}".format(xml_path)
