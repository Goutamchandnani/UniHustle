from app import create_app
from app.models import Student, Job, JobMatch, StudentPreferences
from app.extensions import db

app = create_app('development')

with app.app_context():
    with open('db_results.txt', 'w') as f:
        f.write("--- DB Check ---\n")
        
        # 1. Student
        student = Student.query.filter(Student.first_name.ilike('Gautam')).first()
        if not student:
            f.write("Student not found.\n")
            exit()
            
        f.write(f"Student: {student.first_name} (ID: {student.id})\n")
        f.write(f"Geo: {student.latitude}, {student.longitude}\n")
        
        # 2. Birmingham Job Sample
        bham_jobs = Job.query.filter(Job.location.ilike('%Birmingham%')).all()
        f.write(f"Total Birmingham Jobs: {len(bham_jobs)}\n")
        
        if bham_jobs:
            sample = bham_jobs[0]
            f.write(f"Sample Job: {sample.title} (ID: {sample.id})\n")
            f.write(f"Sample Geo: {sample.latitude}, {sample.longitude}\n")
            
            match = JobMatch.query.filter_by(student_id=student.id, job_id=sample.id).first()
            if match:
                f.write(f"Score: {match.score}\n")
                f.write(f"Breakdown: {match.breakdown}\n")
        
        # 4. Simulate API Query (Top 5 Matches)
        top_matches = Job.query.join(JobMatch, (JobMatch.job_id == Job.id) & (JobMatch.student_id == student.id))\
            .filter(Job.is_active == True)\
            .order_by(JobMatch.score.desc())\
            .limit(5).all()
            
        f.write("--- Top 5 API Results ---\n")
        for j in top_matches:
             m = JobMatch.query.filter_by(student_id=student.id, job_id=j.id).first()
             f.write(f"#{j.id} {j.title} @ {j.location} | Score: {m.score}\n")
             f.write(f"   Breakdown: {m.breakdown}\n") # Diagnostic
             # Extract location_data
             import json
             try:
                 bd = json.loads(m.breakdown)
                 if 'location_data' in bd:
                     ld = bd['location_data']
                     f.write(f"   [TIER {ld.get('tier')}] Badge: {ld.get('badge')}\n")
             except:
                 pass
             
        if bham_jobs:
            sample = bham_jobs[0]
            f.write(f"--- Sample Bham Job Check ---\n")
            f.write(f"ID: {sample.id} | Active: {sample.is_active}\n")
            m = JobMatch.query.filter_by(student_id=student.id, job_id=sample.id).first()
            if m:
                f.write(f"Score: {m.score}\n")
            
        f.write("--- End ---\n")
