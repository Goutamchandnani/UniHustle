from app import create_app, db
from app.models import Job, User
from flask import json

app = create_app()

with app.app_context():
    # 1. Get Test User
    user = User.query.filter_by(email='auth_final@test.com').first()
    student = user.student_profile
    print(f"Testing with Student: {student.first_name} (ID: {student.id})")
    
    # 2. Get a Job ID
    job = Job.query.filter_by(is_active=True).first()
    if not job:
        print("No active jobs found to test.")
        exit()
        
    print(f"Testing Job Detail for Job ID: {job.id}")
    
    # 3. Simulate Logic from routes.py (Manual Run to check for crashes)
    try:
        from app.services.matching import MatchingEngine
        matcher = MatchingEngine()
        
        # Replicating routes.py logic
        timetable_slots = []
        if student.timetable and student.timetable.slots:
            timetable_slots = [{"day": s.day_of_week, "start": s.start_time, "end": s.end_time} for s in student.timetable.slots]
        
        student_skills = set()
        if student.skills:
             student_skills = set([s.strip().lower() for s in student.skills.split(',')])

        student_profile = {
            "location": {"lat": student.latitude or 51.5, "lng": student.longitude or -0.1},
            "timetable": timetable_slots,
            "min_salary": student.preferences.min_salary if student.preferences else 0,
            "skills": student_skills,
            "preferences": {}
        }
        
        job_data = {
             "location": {"lat": job.latitude or 51.5, "lng": job.longitude or -0.1},
             "shifts": [{"day": s.day_of_week, "start": s.end_time, "end": s.end_time} for s in job.shifts], # Note: start_time access
             "salary_min": job.salary_min or 0,
             "salary_max": job.salary_max or 0,
             "salary_type": job.salary_type,
             "skills": set(), 
             "title": job.title,
             "description": job.description
        }
        
        print("Profile Prepared. Calculating Match...")
        match_result = matcher.calculate_match(student_profile, job_data)
        print("Match Result:", match_result)
        
    except Exception as e:
        print("CRASHED:", e)
        import traceback
        traceback.print_exc()
