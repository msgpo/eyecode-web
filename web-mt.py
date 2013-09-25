import sys, os
sys.stdout = sys.stderr
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

import cherrypy, random, string, MySQLdb, json
from time import mktime
from sqlalchemy import create_engine, Column, Integer, BigInteger, Text, DateTime, ForeignKey, TypeDecorator, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref

from mako.lookup import TemplateLookup
from eyecode import get_program_order
from urllib import urlencode
from datetime import datetime
from dateutil import parser

mysql_mod = MySQLdb

words = ["hotshot", "fiendish", "shadow", "radish", "pugnacious",
         "haywire", "chummy", "sloth", "unworldly", "boggle",
         "scuttle", "firefighter", "apple", "wallpaper", "vindictive",
         "liquid", "appalling", "weirdo", "brawny", "elder",
         "couch", "rooster", "prophetic", "cuddle", "hermit"]

def random_string(length):
    return "".join(random.sample(string.ascii_letters + string.digits, length))

# ==================================================

Base = declarative_base()
Session = scoped_session(sessionmaker(autoflush = True, autocommit = False))

class FractionalDateTime(TypeDecorator):
    """
    Stores datetimes as a big integer with microsecond precision.
    """
    impl = BigInteger
                  
    def process_bind_param(self, value, _):
        """Assumes a datetime.datetime"""
        if value is None:
            return None # support nullability
        elif isinstance(value, datetime):
            return (long(mktime(value.timetuple())) * 1000000) + value.microsecond

        raise ValueError("Can operate only on datetime values. "
                         "Offending value type: {0}".format(type(value).__name__))

    def process_result_value(self, value, _):
        if value is not None: # support nullability
            return datetime.fromtimestamp(value / 1000000.0)

# ==================================================

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Participant({0}, {1})>".format(self.id, self.name)

    def __copy__(self):
        return Participant(self.name)

# ==================================================

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    started = Column(DateTime)
    ended = Column(DateTime)
    created = Column(DateTime)
    remote_ip = Column(Text)
    user_agent = Column(Text)

    mt_hit_id = Column(Text)
    mt_assignment_id = Column(Text)
    mt_worker_id = Column(Text)
    mt_submit_to = Column(Text)
    mt_approved = Column(Boolean)

    participant_id = Column(Integer, ForeignKey("participants.id"))
    participant = relationship("Participant", backref=backref("experiments", order_by=id))

    def __init__(self, name, participant_id, started=None, ended=None):
        self.name = name
        self.created = datetime.now()
        self.started = started
        self.ended = ended
        self.participant_id = participant_id
        self.approved = False

    def __repr__(self):
        return "<Experiment({0}, {1}, {2})>".format(self.id, self.name, self.participant_id)

    def __copy__(self):
        return Experiment(self.name, None, started=self.started, ended=self.ended)

    def is_mt(self):
        return (self.mt_hit_id is not None) and (len(self.mt_hit_id) > 0)

    def confirm_code(self):
        return self.name[-1::-2]

# ==================================================

class TestAnswer(Base):
    __tablename__ = "test_answers"

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    created = Column(DateTime)

    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    experiment = relationship("Experiment", backref=backref("test_answers", order_by=id))

    def __init__(self, experiment_id, question, answer):
        self.experiment_id = experiment_id
        self.question = question
        self.answer = answer
        self.created = datetime.now()

    def __repr__(self):
        return "<TestAnswer({0}, {1}, {2})>".format(self.id, self.question, self.answer)

# ==================================================

class Trial(Base):
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True)
    language = Column(Text)
    program_base = Column(Text)
    program_version = Column(Text)
    response = Column(Text)
    started = Column(DateTime)
    ended = Column(DateTime)
    restarted = Column(Integer)
    created = Column(DateTime)

    image_width = Column(Integer)
    image_height = Column(Integer)
    image_x = Column(Integer)
    image_y = Column(Integer)

    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    experiment = relationship("Experiment", backref=backref("trials", order_by=id))

    def __init__(self, experiment_id, language, program_base, program_version,
            response=None, started=None, ended=None):

        self.experiment_id = experiment_id
        self.language = language
        self.program_base = program_base
        self.program_version = program_version
        self.created = datetime.now()
        self.response = response
        self.started = started
        self.ended = ended
        self.restarted = 0

    def __repr__(self):
        return "<Trial({0}, {1}, {2}_{3})>".format(self.id, self.experiment_id,
                self.program_base, self.program_version)

    def __copy__(self):
        return Trial(None, self.program_base, self.program_version, response=self.response,
                     started=self.started, ended=self.ended)

    def language_ext(self):
        if self.language == "python":
            return "py"
        elif self.language == "java":
            return "java"

        raise ValueError("Unsupported language {0}".format(self.language))

# ==================================================

class TrialResponse(Base):
    __tablename__ = "trial_responses"

    id = Column(Integer, primary_key=True)
    response = Column(Text)
    timestamp = Column(FractionalDateTime)
    created = Column(DateTime)

    trial_id = Column(Integer, ForeignKey("trials.id"))
    trial = relationship("Trial", backref=backref("responses", order_by=id))

    def __init__(self, trial_id, response, timestamp):
        self.trial_id = trial_id
        self.created = datetime.now()
        self.response = response
        self.timestamp = timestamp

    def __repr__(self):
        return "<TrialResponse({0}, {1}, {2})>".format(self.id, self.trial_id, self.timestamp)

    def __copy__(self):
        return TrialResponse(self.trial_id, self.response, self.timestamp)

# ==================================================

class QualificationResults(Base):
    __tablename__ = "qualification_results"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Text)
    language = Column(Text)
    result = Column(Text)
    started = Column(DateTime)
    ended = Column(DateTime)
    created = Column(DateTime)

    def __init__(self, worker_id, language, started, ended, result):
        self.worker_id = worker_id
        self.language = language
        self.started = started
        self.ended = ended
        self.result = result
        self.created = datetime.now()

    def __repr__(self):
        return "<QualificationResults({0}, {1}, {2})>".format(self.id, self.worker_id, self.result)

# ==================================================

db_engine = None

# class SAEnginePlugin(plugins.SimplePlugin):
#     def __init__(self, bus, db_path):
#         plugins.SimplePlugin.__init__(self, bus)
#         self.db_path = db_path
#         self.bus.subscribe("bind", self.bind)
#  
#     def start(self):
#         db_engine = create_engine(self.db_path)
#         Base.metadata.create_all(db_engine)
#  
#     def stop(self):
#         if db_engine:
#             db_engine.dispose()
#             db_engine = None
#  
#     def bind(self):
#         Session.configure(bind=db_engine)
 
class SATool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.bind_session,
                               priority=20)
    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)
 
    def bind_session(self):
        Session.configure(bind=db_engine)
        cherrypy.request.db = Session()
 
    def commit_transaction(self):
        session = cherrypy.request.db
        cherrypy.request.db = None
        try:
            session.commit()
        except:
            session.rollback()  
            raise
        finally:
            session.close()

# ================================================== 

class EyecodeMTWeb(object):

    def __init__(self):
        self.lookup = None

    def render_template(self, name, **kwargs):
        if self.lookup is None:
            template_dir = cherrypy.request.app.config["dirs"]["templates"]
            self.lookup = TemplateLookup(directories=[template_dir])

        kwargs.update(cherrypy.request.app.config["params"])
        return self.lookup.get_template("{0}.mako".format(name)).render(**kwargs)


    @cherrypy.expose
    def qualification(self, language, workerId, started="", ended="", **kwargs):
        if len(started) == 0:
            qresults = list(cherrypy.request.db.query(QualificationResults).filter(QualificationResults.worker_id == workerId))

            if len(qresults) > 0:
                return "You have already taken the qualification test (result: {0})".format(qresults[0].result)
            else:
                return self.render_template("qualification", language=language, workerId=workerId)
        else:
            try:
                started = parser.parse(started)
                ended = parser.parse(ended)
            except:
                started = None
                ended = datetime.now()

            qresult = QualificationResults(workerId, language, started, ended, "unknown")
            cherrypy.request.db.add(qresult)

            # Only allow 10 minutes (60 * 10 = 600 seconds)
            if started and ((ended - started).total_seconds() > 600):
                qresult.result = "timeout"
                return self.render_template("qual_results", term="sad", msg="timeout")

            # Check answers
            expected = None
            if language == "python":
                expected = { "var": 1, "fun": 3, "print": 2, "list": 0, "loop": 0 }
            elif language == "java":
                expected = { "var": 0, "fun": 2, "print": 3, "list": 3, "loop": 1 }
            else:
                raise ValueError("Unrecognized language: {0}".format(language))

            if len(kwargs) > len(expected):
                raise ValueError("Too many answers returned")

            for (q, a) in expected.iteritems():
                if q in kwargs:
                    if int(kwargs[q]) != a:
                        qresult.result = "fail"
                        return self.render_template("qual_results", term="sad", msg="fail")
                else:
                    raise ValueError("Unexpected question: {0}".format(q))

            qresult.result = "pass"
            return self.render_template("qual_results", term="happy", msg="pass")

    @cherrypy.expose
    def pre_test(self, language, hitId="", assignmentId="", workerId="",
            submitTo="", **kwargs):
        """
        Welcomes user, creates a new experiment, and collects pre-test answers.
        """
        # Dummy participant
        part = Participant("Dummy")
        cherrypy.request.db.add(part)

        # Create experiment
        experiment = Experiment(random_string(25), -1)
        experiment.participant = part
        experiment.started = datetime.now()
        experiment.remote_ip = cherrypy.request.headers.get("X-Forwarded-For", "")
        experiment.user_agent = cherrypy.request.headers.get("User-Agent", "")

        experiment.mt_hit_id = hitId
        experiment.mt_assignment_id = assignmentId
        experiment.mt_worker_id = workerId
        experiment.mt_submit_to = submitTo

        cherrypy.request.db.add(experiment)

        # Create trials in advance
        programs_dir = cherrypy.request.app.config["dirs"]["programs"]
        for (prog_base, prog_version) in get_program_order(programs_dir):
            trial = Trial(-1, language, prog_base, prog_version)
            trial.experiment = experiment
            cherrypy.request.db.add(trial)

        # Record pre-test answers
        for (k, v) in kwargs.iteritems():
            ans = TestAnswer(-1, str(k), str(v))
            ans.experiment = experiment
            cherrypy.request.db.add(ans)

        # Need this so experiment.id will be something
        cherrypy.request.db.commit()

        # Redirect to list of programs
        params = urlencode({"id": experiment.id, "nonce": experiment.name})
        raise cherrypy.HTTPRedirect("index?{0}".format(params))

    @cherrypy.expose
    def index(self, id=None, nonce=None, hitId="", assignmentId="",
            workerId="", submitTo="", language=""):
        """
        Shows which programs have been completed for an experiment.
        Redirects to pre-test if no experiment id is given.
        """
        if id is None:
            if len(workerId) > 0:
                # Make sure an MT worker doesn't do it twice
                if cherrypy.request.db.query(Experiment).filter(Experiment.mt_worker_id == workerId).count() > 0:
                    return self.render_template("sorry")

                # And make sure their qualified
                qresults = list(cherrypy.request.db.query(QualificationResults).filter(QualificationResults.worker_id == workerId))
                if len(qresults) == 0:
                    return "You must take the qualification test before proceeding"

                if (len(qresults) != 1) or (qresults[0].result != "pass"):
                    return self.render_template("qual_results", term="sad", msg=qresults[0].result)

            if len(language) == 0:
                language = cherrypy.request.app.config["params"]["default_language"]

            # Start pre-test (pass MT parameters through)
            return self.render_template("pre_test", hitId=hitId,
                    assignmentId=assignmentId, workerId=workerId,
                    submitTo=submitTo, language=language)
        else:
            experiment = cherrypy.request.db.query(Experiment).get(id)
            assert experiment.name == nonce, "Nonce does not match"
            return self.render_template("index", experiment=experiment, words=words)

    @cherrypy.expose
    def start_trial(self, id, nonce):
        """
        Starts a trial. If the trial has already been started (e.g., the
        user hit the back button), the restart count is incremented.
        """
        trial = cherrypy.request.db.query(Trial).get(id)
        assert trial.experiment.name == nonce, "Nonce does not match"
        
        if trial.started:
            # Trial has already been started
            trial.restarted += 1

        trial.started = datetime.now()
        trial.ended = None

        params = cherrypy.request.app.config["params"]
        trial.image_width = params["image_width"]
        trial.image_height = params["image_height"]

        return self.render_template("trial", trial=trial, nonce=nonce)

    @cherrypy.expose
    def end_trial(self, id, nonce, image_x, image_y,
            response, responses_js="[]"):
        """
        Ends a trial with a final response.
        Records intermediary responses from a JSON array (respones_js)
        If not all programs have been completed, returns to experiment
        index. Otherwise, continues on to the post-test.
        """
        trial = cherrypy.request.db.query(Trial).get(id)
        assert trial.experiment.name == nonce, "Nonce does not match"

        # Make a note if trial has already been run
        if trial.ended:
            trial.restarted += 1

        trial.ended = datetime.now()
        trial.response = response

        # Should be a float at some point
        trial.image_x = int(float(image_x))
        trial.image_y = int(float(image_y))

        # Parse and record all intermediary responses
        # (dates are in UTC)
        for int_resp in json.loads(responses_js):
            utc_timestamp, resp_str = int_resp

            # Javascript UTC timestamps are in milliseconds, but Python expects seconds
            tr_resp = TrialResponse(trial.id, resp_str,
                    datetime.utcfromtimestamp(utc_timestamp / 1000.0))

            cherrypy.request.db.add(tr_resp)

        experiment = trial.experiment

        # Check if all trials have been completed
        params = urlencode({"id": experiment.id, "nonce": nonce})
        if any(map(lambda t: t.ended is None, experiment.trials)):
            # Go back to experiment index
            raise cherrypy.HTTPRedirect("index?{0}".format(params))
        else:
            # Go on to post-test
            return self.render_template("post_test", experiment=experiment)

    @cherrypy.expose
    def post_test(self, id, nonce, **kwargs):
        """
        Records answers to post-test questions and ends the experiment.
        """
        experiment = cherrypy.request.db.query(Experiment).get(id)
        assert experiment.name == nonce, "Nonce does not match"

        # Record post-test answers
        for (k, v) in kwargs.iteritems():
            ans = TestAnswer(experiment.id, str(k), str(v))
            cherrypy.request.db.add(ans)

        experiment.ended = datetime.now()

        confirm_code = experiment.confirm_code()
        
        return self.render_template("thanks", experiment=experiment,
                confirm_code=confirm_code)

# ================================================== 

conf_path = os.path.join(base_dir, "web-mt.conf")
cherrypy.config.update(conf_path)

# Connect database plugin
db_path = cherrypy.config["db_path"]

# Create local database if necessary
if db_path.startswith("sqlite:///"):
    sqlite_path = db_path[10:]
    if not os.path.exists(sqlite_path):
        from db import DB
        sqlite_db = DB()
        sqlite_db.connect_to_db(db_path)
        sqlite_db.erase_db()
        del sqlite_db

db_engine = create_engine(db_path, pool_recycle=3600)
cherrypy.tools.db = SATool()

if cherrypy.config.has_key("quickstart") and cherrypy.config["quickstart"]:

    # Start development server locally on port 8080
    cherrypy.quickstart(EyecodeMTWeb(), config=conf_path)
else:

    # Prepare for WSGI integration with Apache
    application = cherrypy.Application(EyecodeMTWeb(), script_name=None, config=conf_path)
