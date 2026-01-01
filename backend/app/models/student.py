from app.extensions import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    university = db.Column(db.String(128))
    course = db.Column(db.String(128))
    year_of_study = db.Column(db.Integer)
    visa_status = db.Column(db.String(64), default='Home') # Home, Tier 4, etc.
    weekly_hours_limit = db.Column(db.Integer, default=20) # For international students
    
    # Matching Profile
    skills = db.Column(db.Text) # Comma-separated list of skills
    postcode = db.Column(db.String(10)) # For geo-coding
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    timetable = db.relationship('Timetable', backref='student', uselist=False, lazy=True)
    preferences = db.relationship('StudentPreferences', backref='student', uselist=False, lazy=True)
    applications = db.relationship('Application', backref='student', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'

class StudentPreferences(db.Model):
    __tablename__ = 'student_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    preferred_locations = db.Column(db.Text) # JSON or comma-separated
    preferred_roles = db.Column(db.Text) # JSON or comma-separated
    min_salary = db.Column(db.Float)
    max_commute_time = db.Column(db.Integer) # in minutes
