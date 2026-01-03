from app.extensions import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    company_name = db.Column(db.String(128))
    description = db.Column(db.Text)
    
    # Salary
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    currency = db.Column(db.String(3), default='GBP')
    salary_type = db.Column(db.String(20), default='hourly') # hourly, yearly
    
    # Location
    location = db.Column(db.String(128))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_remote = db.Column(db.Boolean, default=False)
    remote_type = db.Column(db.String(50)) # 'full_remote', 'hybrid'
    
    # Source (for aggregation)
    source = db.Column(db.String(64), default='Internal') # Custom, Reed, Indeed
    external_id = db.Column(db.String(128), index=True) # ID from external API
    external_url = db.Column(db.String(512))
    
    # Meta
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.Index('idx_job_location', 'location'),
        db.Index('idx_job_salary', 'salary_min'),
        db.Index('idx_job_active', 'is_active'),
    )

    # Relationships
    shifts = db.relationship('JobShift', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='job', lazy='dynamic')

    def __repr__(self):
        return f'<Job {self.title} @ {self.company_name}>'

class JobShift(db.Model):
    __tablename__ = 'job_shifts'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    # Flexible shifts?
    is_flexible = db.Column(db.Boolean, default=False)
