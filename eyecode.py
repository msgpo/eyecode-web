import csv, logging, svgwrite, os, random
from svgwrite import animate
from db import DB, Participant, Trial, GazeEvent
from datetime import datetime, timedelta
from PIL import Image
from copy import copy
from glob import glob

logger = logging.getLogger("eyecode.analyze")

def copy_participant(from_session, participant_id, to_session):
    part_old = from_session.query(Participant).get(participant_id)

    part_new = copy(part_old)
    to_session.add(part_new)

    for exp_old in part_old.experiments:
        exp_new = copy(exp_old)
        exp_new.participant_id = part_new.id
        to_session.add(exp_new)

        for tri_old in exp_old.trials:
            tri_new = copy(tri_old)
            tri_new.experiment_id = exp_new.id
            to_session.add(tri_new)

    to_session.commit()


def write_fixations(csv_path, session, experiment_id):
    last_fixation_idx = -1
    trials = list(session.query(Trial).filter(Trial.experiment_id == experiment_id))

    with open(csv_path, "r") as csv_file:
        dialect = "excel-tab" if os.path.splitext(csv_path)[1] == ".tsv" else "excel"

        for row in csv.DictReader(csv_file, dialect=dialect):

            try:
                fixation_idx = int(row["FixationIndex"])

                if fixation_idx != last_fixation_idx:
                    try:
                        x = int(row["FixationPointX (MCSpx)"])
                        y = int(row["FixationPointY (MCSpx)"])

                        #res_str = str(row["RecordingResolution"]).split(" x ")
                        #res = (int(res_str[0]), int(res_str[1]))

                        # Build timestamp from recording date and local time fields
                        date_str = str(row["RecordingDate"])
                        time_str, milli_str = str(row["LocalTimeStamp"]).split(".")

                        time_str = "{0} {1}".format(date_str, time_str)
                        timestamp = datetime.strptime(time_str, "%m/%d/%Y %H:%M:%S") + \
                                timedelta(milliseconds=int(milli_str))

                        duration_ms = int(row["GazeEventDuration"])

                        trial = None
                        for t in trials:
                            if (t.started <= timestamp) and (timestamp <= t.ended):
                                trial = t
                                break

                        last_fixation_idx = fixation_idx

                        if trial is None:
                            logger.warn("Skipping fixation {0} (no trial)".format(fixation_idx))
                            continue

                        fix = Fixation(trial.id, x, y, timestamp, duration_ms)
                        session.add(fix)
                    except ValueError:
                        pass

            except ValueError:
                pass

    session.commit()


def write_gaze_events(csv_path, session, experiment_id):
    last_fix_idx = -1
    last_sac_idx = -1

    trials = list(session.query(Trial).filter(Trial.experiment_id == experiment_id))

    with open(csv_path, "r") as csv_file:
        dialect = "excel-tab" if os.path.splitext(csv_path)[1] == ".tsv" else "excel"

        for row in csv.DictReader(csv_file, dialect=dialect):

            try:
                event_type_str = str(row["GazeEventType"])
                event_type = GazeEvent.UNCLASSIFIED
                x = 0
                y = 0

                gx = int(row["GazePointX (ADCSpx)"])
                gy = int(row["GazePointY (ADCSpx)"])

                # Build timestamp from recording date and local time fields
                date_str = str(row["RecordingDate"])
                time_str, milli_str = str(row["LocalTimeStamp"]).split(".")

                time_str = "{0} {1}".format(date_str, time_str)
                timestamp = datetime.strptime(time_str, "%m/%d/%Y %H:%M:%S") + \
                        timedelta(milliseconds=int(milli_str))

                trial = None
                for t in trials:
                    if (t.started <= timestamp) and (timestamp <= t.ended):
                        trial = t
                        break

                if trial is None:
                    gaze_idx = int(row["GazePointIndex"])
                    logger.warn("Skipping gaze point {0} (no trial)".format(gaze_idx))
                    continue

                duration_ms = int(row["GazeEventDuration"])

                # Add raw gaze event
                ge = GazeEvent(trial.id, GazeEvent.GAZE, gx, gy, timestamp, duration_ms)
                session.add(ge)

                # Add fixation/saccade event
                if (event_type_str == "Fixation"):
                    event_type = GazeEvent.FIXATION

                    fix_idx = int(row["FixationIndex"])

                    if fix_idx == last_fix_idx:
                        continue

                    x = int(row["FixationPointX (MCSpx)"])
                    y = int(row["FixationPointY (MCSpx)"])

                    last_fix_idx = fix_idx

                elif (event_type_str == "Saccade"):
                    event_type = GazeEvent.SACCADE

                    sac_idx = int(row["SaccadeIndex"])
                    
                    if sac_idx == last_sac_idx:
                        continue

                    x = gx
                    y = gy

                    last_sac_idx = sac_idx

                else:
                    continue

                ge = GazeEvent(trial.id, event_type, x, y, timestamp, duration_ms)
                session.add(ge)
            except ValueError:
                pass

    session.commit()

def write_gaze_svg(trial, svgpath, images_path, time_mult = 1):
    time_mult = float(time_mult)
    image_name = "base_{0}.png".format(trial.program_name)
    prog_img = Image.open(os.path.join(images_path, image_name))

    draw = svgwrite.Drawing(filename=svgpath, size=prog_img.size)

    # Program image
    draw.add( draw.image(href="images/{0}".format(image_name),
        width="{0}px".format(prog_img.size[0]), height="{0}px".format(prog_img.size[1])) )

    gaze_id = "gaze"
    fix_id = "fix"

    # Add gaze circle
    circle_gaze = draw.circle(id=gaze_id, center=(0, 0), r=25,
            fill="blue", opacity=0.5, display="none")

    draw.add(circle_gaze)

    for gp in trial.gaze_points():
        rel_start = time_mult * (gp.timestamp - trial.started).total_seconds()

        # Create gaze animations.
        # NOTE: Validation is broken, so we have to set debug=False

        # Show gaze circle
        circle_gaze.add( animate.Set(begin=rel_start, attributeType="CSS",
            attributeName="display", to="block", debug=False) )

        circle_gaze.add( animate.Set(begin=rel_start, attributeType="XML",
            attributeName="cx", to=gp.x, debug=False) )

        circle_gaze.add( animate.Set(begin=rel_start, attributeType="XML",
            attributeName="cy", to=gp.y, debug=False) )


    # Add fixations
    for fix in trial.fixations():
        rel_start = time_mult * (fix.timestamp - trial.started).total_seconds()
        grow_dur = fix.duration_ms * 7 / 1000.0
        fade_dur = fix.duration_ms * 5 / 1000.0

        circle_fix = draw.circle(id=fix_id, center=(fix.x, fix.y), r=25,
                fill="red", opacity=0.5, display="none")
        #        **{ "stroke-width": 2, "stroke": "#330000" })

        grow_id = "fixgrow{0}".format(fix.id)
        fade_id = "fixfade{0}".format(fix.id)

        # Create animations.
        # NOTE: Validation is broken, so we have to set debug=False

        # Show fixation circle at the start time
        circle_fix.add( animate.Set(begin=rel_start, attributeType="CSS",
            attributeName="display", to="block", debug=False) )

        # Grow during display
        radius = int(fix.duration_ms / 5.0)
        circle_fix.add( animate.Animate(id=grow_id, begin=rel_start, attributeType="XML",
            attributeName="r", to=radius, dur=grow_dur, fill="freeze", debug=False) )

        # Fade out
        circle_fix.add( animate.Animate(id=fade_id, begin=rel_start, attributeType="CSS",
            attributeName="opacity", to=0, dur=fade_dur, fill="freeze", debug=False) )

        # Hide after fade out
        circle_fix.add( animate.Set(begin="{0}.end".format(fade_id), attributeType="CSS",
            attributeName="display", to="none", debug=False) )

        draw.add(circle_fix)


    # Add saccades
    #gaze_events = sorted(trial.gaze_events, key=lambda f: f.timestamp)
    #last_pt = None

    #for ge in gaze_events:
        #if last_pt is None:
            #last_pt = (ge.x, ge.y)
        #else:

            #if ge.event_type == GazeEvent.SACCADE:
                #rel_start = time_mult * (ge.timestamp - trial.started).total_seconds()
                #line = draw.line(x1=last_pt[0], y1=last_pt[1], x2=ge.x, y2=ge.y,
                        #style="stroke='red'; stroke-width: 2;")

                ##line.add( animate.Set(begin=rel_start, attributeType="CSS",
                    ##attributeName="display", to="block", debug=False) )

                #draw.add(line)

            #last_pt = (ge.x, ge.y)

    rel_end = time_mult * (trial.ended - trial.started).total_seconds()

    # Add overlay on "Continue" button when trial is complete
    cont_overlay = draw.rect(insert=(1431, 844), size=(249, 87), opacity=0.5,
            fill="green", display="none")

    cont_overlay.add( animate.Set(begin=rel_end, attributeType="CSS",
        attributeName="display", to="block", debug=False) )

    draw.add(cont_overlay)

    # Add response
    ty = 244

    for line in trial.response.splitlines():
        resp_text = draw.text(line, insert=(1245, ty),
                display="none", **{ "font-size": 25 })

        resp_text.add( animate.Set(begin=rel_end, attributeType="CSS",
            attributeName="display", to="block", debug=False) )

        draw.add(resp_text)
        ty += 35

    # Save to SVG file
    draw.save()

#def gen_trial_responses(csv_path, experiment_id):
    #trials = list(session.query(Trial).filter(Trial.experiment_id == experiment_id))
    #lines = [""]
    #cur_pos = (0, 0)

    #with open(csv_path, "r") as csv_file:
        #dialect = "excel-tab" if os.path.splitext(csv_path)[1] == ".tsv" else "excel"

        #for row in csv.DictReader(csv_file, dialect=dialect):
            #try:
                #key_idx = int(row["KeyPressEventIndex"])
                #key_event = str(row["KeyPressEvent"])

                #if re.match("^[a-z]$", key_event, flags=re.IGNORECASE):
                    #lines[cur_pos[1]].insert(cur_pos[0], key_event)

                ## Build timestamp from recording date and local time fields
                #date_str = str(row["RecordingDate"])
                #time_str, milli_str = str(row["LocalTimeStamp"]).split(".")

                #time_str = "{0} {1}".format(date_str, time_str)
                #timestamp = datetime.strptime(time_str, "%m/%d/%Y %H:%M:%S") + \
                        #timedelta(milliseconds=int(milli_str))

                #trial = None
                #for t in trials:
                    #if (t.started <= timestamp) and (timestamp <= t.ended):
                        #trial = t
                        #break

                #if trial is None:
                    #logger.warn("Skipping key event {0} (no trial)".format(key_idx))
                    #continue

            #except ValueError:
                #pass


def get_program_order(programs_dir):
    programs = {}

    for prog_path in glob(os.path.join(programs_dir, "*.py")):
        prog_name = os.path.splitext(os.path.split(prog_path)[1])[0]
        base, version = prog_name.split("_", 1)

        if base in programs:
            programs[base].append(version)
        else:
            programs[base] = [version]

    program_bases = programs.keys()
    random.shuffle(program_bases)
    program_order = []

    for base in program_bases:
        #version_hist = dict([(version, 0) for version in programs[base]])

        #for version in session.query(Trial.program_version).filter(Trial.program_base == base):
            #version_hist[version[0]] += 1

        #min_ver = min(version_hist, key=version_hist.get)
        #program_order.append((base, min_ver))
        program_order.append((base, random.choice(programs[base])))

    return program_order

def mysql_db():
    db = DB()
    db.connect_to_db("mysql://eyecode_user:bARutH7ph3QAdrU@127.0.0.1/eyecode", echo=False)
    return db
