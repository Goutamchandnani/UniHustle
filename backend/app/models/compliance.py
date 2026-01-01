from app.extensions import db
from datetime import datetime

class WorkLog(db.Model):
    __tablename__ = 'work_logs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    week_start_date = db.Column(db.Date, nullable=False) # Monday of the week
    hours_worked = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(32), default='Pending') # Pending, Verified, Paid
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_student_week', 'student_id', 'week_start_date'),
    )

    def __repr__(self):
        return f'<WorkLog Student:{self.student_id} Week:{self.week_start_date} Hours:{self.hours_worked}>'
