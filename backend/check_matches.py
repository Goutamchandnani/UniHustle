from app import create_app, db
from app.models import JobMatch, Job, Student

app = create_app()

with app.app_context():
    count = JobMatch.query.count()
    print(f"Total Matches: {count}")
    
    matches = JobMatch.query.order_by(JobMatch.score.desc()).limit(5).all()
    print(f"Top {len(matches)} Matches:")
    for m in matches:
        job = Job.query.get(m.job_id)
        student = Student.query.get(m.student_id)
        print(f"Student: {student.first_name} | Job: {job.title} | Score: {m.score}")
        print(f"  Breakdown: {m.breakdown}")
