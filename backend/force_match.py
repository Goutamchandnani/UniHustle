from app import create_app
from app.models import Student, StudentPreferences, Job, JobMatch
from app.services.matching import MatchingEngine
from app.extensions import db
import json
from datetime import datetime

app = create_app('development')

with app.app_context():
    print("--- Forcing Match Update ---")
    
    # 1. Update Prefs
    student = Student.query.join(StudentPreferences).filter(StudentPreferences.preferred_locations.ilike('%Birmingham%')).first()
    if not student:
        print("Student not found!")
        exit()
        
    print(f"Updating prefs for {student.first_name}...")
    student.preferences.preferred_roles = "Barista, Cafe Assistant"
    student.preferences.preferred_locations = "Birmingham" # Ensure legacy field matches
    student.preferences.primary_city = "Birmingham"
    student.preferences.open_to_other_cities = True # Let's test nearby?
    db.session.commit()
    print("Preferences set to: Barista/Cafe, Primary: Birmingham")
    print("Preferences set to: Barista, Cafe Assistant")
    
    # 2. Run Matcher
    engine = MatchingEngine()
    jobs = Job.query.filter_by(is_active=True).all()
    print(f"Matching against {len(jobs)} active jobs...")
    
    count = 0
    for job in jobs:
        # Simplified profile construction
        student_profile = {
            "location": {"lat": student.latitude or 51.5, "lng": student.longitude or -0.1},
            "timetable": [], # Skip for speed
            "min_salary": student.preferences.min_salary,
            "skills": set(),
            "preferences": {
                "roles": ['barista', 'cafe'],
                "locations": ['birmingham'],
                "primary_city": "Birmingham",
                "preferred_locations": "Birmingham",
                "open_to_other_cities": True,
                "max_commute_time": 45
            }
        }
        
        job_data = {
            "location": {"lat": job.latitude or 55.0, "lng": job.longitude or -1.0, "name": job.location},
            "shifts": [],
            "salary_min": job.salary_min or 0,
            "salary_max": job.salary_max or 0,
            "salary_type": job.salary_type,
            "skills": set(),
            "title": job.title,
            "description": job.description
        }
        
        res = engine.calculate_match(student_profile, job_data)
        
        location_name = job_data['location'].get('name', '')
        if 'barista' in job_data['title'].lower() and 'birmingham' in location_name.lower():
             print(f"TARGET JOB RESULT '{job_data['title']}' @ '{location_name}': {res}")
             
        # Save
        match = JobMatch.query.filter_by(student_id=student.id, job_id=job.id).first()
        if not match:
            match = JobMatch(student_id=student.id, job_id=job.id)
            db.session.add(match)
            
        match.score = res['total_score']
        match.breakdown = json.dumps(res['breakdown'])
        match.last_calculated = datetime.utcnow()
        count += 1
        
    db.session.commit()
    print(f"Successfully updated {count} match records.")
    print("--- Done ---")
