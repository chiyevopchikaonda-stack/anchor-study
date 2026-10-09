from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    university = db.Column(db.String(150), nullable=False)
    course = db.Column(db.String(150), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship(
        "Subject",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    study_plans = db.relationship(
        "StudyPlan",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    tasks = db.relationship(
        "Task",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    notes = db.relationship(
        "Note",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
   
    goals = db.relationship(
        "Goal",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    scriptures = db.relationship(
        "Scripture",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    prayer_entries = db.relationship(
        "PrayerEntry",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    reflections = db.relationship(
        "Reflection",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
)
    theme = db.Column(
    db.String(30),
    nullable=False,
    default="anchor_classic",
    server_default="anchor_classic"
)
    doodle_style = db.Column(
    db.String(20),
    nullable=False,
    default="off",
    server_default="off"
)






class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    study_plans = db.relationship(
        "StudyPlan",
        backref="subject",
        lazy=True,
        cascade="all, delete-orphan"
    )

    notes = db.relationship(
        "Note",
        backref="subject",
        lazy=True,
        cascade="all, delete-orphan"
    )


class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    study_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject.id"),
        nullable=False
    )


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default="Medium", nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject.id"),
        nullable=True
    )
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    progress = db.Column(db.Integer, default=0, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

class Scripture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), nullable=False)
    verse_text = db.Column(db.Text, nullable=False)
    reflection = db.Column(db.Text, nullable=True)
    favorite = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

class PrayerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="Personal", nullable=False)
    answered = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

class Reflection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
