from app.extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    status = db.Column(db.String(64), default='Applied') # Applied, Interview, Offer, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Application Job:{self.job_id} Student:{self.student_id} Status:{self.status}>'
