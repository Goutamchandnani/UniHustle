from app import create_app
from app.models import Student, Job, StudentPreferences
from app.services.matching import MatchingEngine

app = create_app('development')

with app.app_context():
    print("--- Single Job Debug ---")
    
    # 1. Get Student
    # Using 'ilike' to find 'Gautam'
    student = Student.query.filter(Student.first_name.ilike('Gautam')).first()
    if not student:
        print("Student not found")
        exit()
        
    print(f"Student: {student.first_name} (ID: {student.id})")
    
    # 2. Get Birmingham Job
    job = Job.query.filter(Job.location.ilike('%Birmingham%')).first()
    if not job:
        print("No Birmingham job found")
        exit()
        
    print(f"Job: '{job.title}' @ '{job.location}' (ID: {job.id})")
    
    # 3. Construct Profile (as force_match does)
    # BEWARE: force_match HARDCODED this! I will simulate BOTH database and hardcoded.
    
    # DB Version
    db_roles = [r.strip() for r in (student.preferences.preferred_roles or "").split(',')]
    profile_db = {
        "location": {"lat": student.latitude, "lng": student.longitude},
        "preferences": {
            "roles": db_roles,
            "locations": ["birmingham"],
            "max_commute_time": 45
        }
    }
    
    # Hardcoded Version (from force_match.py)
    profile_force = {
        "location": {"lat": student.latitude or 51.5, "lng": student.longitude or -0.1},
        "preferences": {
            "roles": ['barista', 'cafe'], # Hardcoded
            "locations": ['birmingham'],
            "max_commute_time": 45
        }
    }
    
    job_data = {
        "location": {"lat": job.latitude, "lng": job.longitude, "name": job.location},
        "shifts": [],
        "salary_min": job.salary_min or 0,
        "salary_max": job.salary_max or 0,
        "salary_type": job.salary_type,
        "skills": set(),
        "title": job.title,
        "description": job.description
    }
    
    engine = MatchingEngine()
    
    print("\n--- Test 1: Using DB Preferences ---")
    print(f"Roles: {profile_db['preferences']['roles']}")
    res_db = engine.calculate_match(profile_db, job_data)
    print(f"Result: {res_db}")
    
    print("\n--- Test 2: Using Hardcoded Preferences ---")
    print(f"Roles: {profile_force['preferences']['roles']}")
    res_force = engine.calculate_match(profile_force, job_data)
    print(f"Result: {res_force}")
    
    print("\n--- Why is Pref Score 0? ---")
    # Manual check
    roles = profile_db['preferences']['roles']
    title = job_data['title'].lower()
    matches = [r.lower() in title for r in roles]
    print(f"Title Lower: '{title}'")
    print(f"Roles Lower: {[r.lower() for r in roles]}")
    print(f"Matches: {matches}")
    print(f"Any(Matches): {any(matches)}")
    
    print("--- End ---")
