import logging
from datetime import datetime
from time import mktime
from sqlalchemy import create_engine, Column, Integer, BigInteger, Text, DateTime, ForeignKey, TypeDecorator, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()
Session = sessionmaker()

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
        self.mt_approved = False

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

    def fixations(self):
        return [e for e in self.gaze_events if e.event_type == GazeEvent.FIXATION]

    def saccades(self):
        return [e for e in self.gaze_events if e.event_type == GazeEvent.SACCADE]

    def gaze_points(self):
        return [e for e in self.gaze_events if e.event_type == GazeEvent.GAZE]

    def language_ext(self):
        if self.language == "python":
            return "py"
        elif self.language == "java":
            return "java"

        raise ValueError("Unsupported language {0}".format(self.language))

# ==================================================

class GazeEvent(Base):
    __tablename__ = "gaze_events"

    # Event types
    UNCLASSIFIED = 0
    FIXATION = 1
    SACCADE = 2
    GAZE = 3

    id = Column(Integer, primary_key=True)
    timestamp = Column(FractionalDateTime)
    event_type = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    duration_ms = Column(Integer)
    created = Column(DateTime)

    trial_id = Column(Integer, ForeignKey("trials.id"))
    trial = relationship("Trial", backref=backref("gaze_events", order_by=id))

    def __init__(self, trial_id, event_type, x, y, timestamp, duration_ms):
        self.trial_id = trial_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.x = x
        self.y = y
        self.duration_ms = duration_ms
        self.created = datetime.now()

    def __str__(self):
        return "<GazeEvent({0}, {1}, {2})>".format(self.x, self.y, self.timestamp)

    def __copy__(self):
        return GazeEvent(self.trial_id, self.event_type, self.x, self.y,
                         self.timestamp, self.duration_ms)

# ==================================================

class TrialResponse(Base):
    __tablename__ = "trial_responses"

    id = Column(Integer, primary_key=True)
    response = Column(Text)
    #timestamp = Column(FractionalDateTime)
    timestamp = Column(BigInteger)
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

    def date(self):
        return datetime.utcfromtimestamp(self.timestamp / float(1e6))

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

class DB:
    def __init__(self):
        self.logger = logging.getLogger("eyecode.db")
        self.engine = None
        self.session = None

    def connect_to_db(self, path, echo=True):
        self.logger.debug("connect_to_db({0})".format(path))

        self.logger.info("Connecting to database at {0}".format(path))
        self.engine = create_engine(path, echo=echo)

        Session.configure(bind=self.engine)
        self.session = Session()

    def erase_db(self):
        self.logger.debug("erase_db()")
        assert self.engine is not None, "Not connected to database"

        self.logger.info("Recreating database -- all data is being erased")
        Base.metadata.create_all(self.engine)
