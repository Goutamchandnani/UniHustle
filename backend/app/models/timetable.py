from app.extensions import db

class Timetable(db.Model):
    __tablename__ = 'timetables'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    academic_term = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)

    slots = db.relationship('ScheduleSlot', backref='timetable', lazy='dynamic', cascade='all, delete-orphan')

class ScheduleSlot(db.Model):
    __tablename__ = 'schedule_slots'

    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False) # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    activity_type = db.Column(db.String(64)) # Lecture, Seminar, Lab, Personal
    location = db.Column(db.String(128))
    
    # Required for conflict detection: buffer time for commute (optional per slot)
    commute_buffer_mins = db.Column(db.Integer, default=30)
