from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'student', 'employer', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)
    employer_profile = db.relationship('EmployerProfile', backref='user', uselist=False)

bookmarks = db.Table('bookmarks',
    db.Column('student_id', db.Integer, db.ForeignKey('student_profile.id'), primary_key=True),
    db.Column('internship_id', db.Integer, db.ForeignKey('internship.id'), primary_key=True)
)

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    university = db.Column(db.String(150))
    major = db.Column(db.String(100))
    bio = db.Column(db.Text)
    skills = db.Column(db.String(255))
    applications = db.relationship('Application', backref='student', lazy=True)
    saved_internships = db.relationship('Internship', secondary=bookmarks, lazy='subquery',
        backref=db.backref('saved_by', lazy=True))

class EmployerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(150))
    internships = db.relationship('Internship', backref='employer', lazy=True, cascade="all, delete-orphan")

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer_profile.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150))
    duration = db.Column(db.String(100))
    skills_required = db.Column(db.String(255))
    deadline = db.Column(db.DateTime)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Open') # 'Open', 'Closed'
    applications = db.relationship('Application', backref='internship', lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    status = db.Column(db.String(50), default='Submitted') # 'Submitted', 'Under Review', 'Accepted', 'Rejected'
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_letter = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))
    feedback = db.relationship('Feedback', backref='application', uselist=False, cascade="all, delete-orphan")

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    rating = db.Column(db.Integer) # e.g. 1-5
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
