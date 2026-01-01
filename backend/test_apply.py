from app import create_app, db
from app.models import Application, User, Job

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='auth_final@test.com').first()
    student = user.student_profile
    job = Job.query.filter_by(is_active=True).first()
    
    print(f"Testing application for {student.first_name} -> Job {job.id}")
    
    # Simulate API Call Logic
    existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if existing:
        print("Application already exists, clearing it for test...")
        db.session.delete(existing)
        db.session.commit()
        
    print("Creating new application...")
    new_app = Application(student_id=student.id, job_id=job.id, status='Applied')
    db.session.add(new_app)
    db.session.commit()
    
    print("Success! Verified record created.")
    
    check = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    print(f"Record: {check}")
