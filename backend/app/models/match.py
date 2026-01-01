from app.extensions import db
from datetime import datetime

class JobMatch(db.Model):
    __tablename__ = 'job_matches'

    # Composite Primary Key or just use a unique constraint with a surrogate ID
    # Here we use student_id + job_id as the primary identifier logical key
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    score = db.Column(db.Float, nullable=False) # 0.0 to 100.0
    
    # Store breakdown of the score (JSON)
    # e.g., {'schedule': 35, 'location': 20, 'skills': 15, 'salary': 5, 'preferences': 10}
    breakdown = db.Column(db.Text) 
    
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one match record per student-job pair
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='uq_student_job_match'),
        db.Index('idx_match_score', 'score'), # Index for fast sorting by score
    )

    def __repr__(self):
        return f'<JobMatch Student:{self.student_id} Job:{self.job_id} Score:{self.score}>'
