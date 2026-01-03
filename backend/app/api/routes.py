from flask import jsonify, request, current_app
import requests
from app.api import api_bp
from app.extensions import db
from app.models import Job, Student, Timetable, ScheduleSlot, Application, JobMatch
from app.services.matching import MatchingEngine
from app.services.scheduler import ScheduleAnalyzer
from .schemas import JobSchema, ApplicationSchema, ScheduleSlotSchema
from datetime import datetime

from flask_jwt_extended import jwt_required, current_user

# Helper replaced by current_user.student_profile via JWT
from app.tasks import scrape_jobs_task, calculate_matches_task

@api_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    student = current_user.student_profile
    if not student:
        return jsonify({"error": "No student profile found"}), 404

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int) # Increased default from 20 to 100 for "See All" feel

    # Base Query
    query = Job.query.filter_by(is_active=True)

    # Filtering
    salary_min = request.args.get('salary_min', type=float)
    if salary_min:
        query = query.filter(Job.salary_min >= salary_min)
        
    # Strict Role Filtering (per user request)
    if student.preferences and student.preferences.preferred_roles:
        roles = [r.strip() for r in student.preferences.preferred_roles.split(',') if r.strip()]
        if roles:
            from sqlalchemy import or_
            # Construct a flexible OR filter: Title OR Description must contain one of the keywords
            # For strictness, per user feedback, we MUST only check Title. 
            # Description often contains "barista coffee available" which causes false positives for "Director" roles.
            role_filters = []
            for role in roles:
                role_filters.append(Job.title.ilike(f"%{role}%"))
                # role_filters.append(Job.description.ilike(f"%{role}%")) # REMOVED for strictness
            
            if role_filters:
                query = query.filter(or_(*role_filters))

    # Strict Location Filtering REMOVED -> Handled by Matching Score (Distance Penalty)
    # This allows "Nearby" jobs to appear (with lower scores) instead of being hidden.
    # if student.preferences and student.preferences.preferred_locations:
    #    ...

    # Sorting (integration with JobMatch)
    # Join with JobMatch to sort by score
    query = query.outerjoin(JobMatch, (JobMatch.job_id == Job.id) & (JobMatch.student_id == student.id))
    
    sort_by = request.args.get('sort_by', 'match_score')
    if sort_by == 'match_score':
        query = query.order_by(JobMatch.score.desc().nullslast())
    elif sort_by == 'posted_at':
        query = query.order_by(Job.posted_at.desc())
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    # Serialize
    # We want to include match score in the output
    results = []
    job_schema = JobSchema()
    
    for job in paginated.items:
        job_dump = job_schema.dump(job)
        
        # Attach match info manually since it's on the joined table/not in Job model direct
        match = JobMatch.query.filter_by(student_id=student.id, job_id=job.id).first()
        if match:
             job_dump['match_score'] = match.score
        
        results.append(job_dump)

    return jsonify({
        'jobs': results,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

@api_bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_detail(job_id):
    student = current_user.student_profile
    job = Job.query.get_or_404(job_id)
    
    # Calculate fresh match analysis on the fly
    # Matcher Setup
    matcher = MatchingEngine()
    
    # Safe timetable access
    timetable_slots = []
    if student.timetable and student.timetable.slots:
        timetable_slots = [{"day": s.day_of_week, "start": s.start_time, "end": s.end_time} for s in student.timetable.slots]
    
    # Skills parsing (CSV to set)
    student_skills = set()
    if student.skills:
        student_skills = set([s.strip().lower() for s in student.skills.split(',')])

    student_profile = {
        "location": {"lat": student.latitude or 51.5, "lng": student.longitude or -0.1},
        "timetable": timetable_slots,
        "min_salary": student.preferences.min_salary if student.preferences else 0, # Safeguard preferences too
        "skills": student_skills,
        "preferences": {}
    }
    
    job_data = {
         "location": {"lat": job.latitude or 51.5, "lng": job.longitude or -0.1},
         "shifts": [{"day": s.day_of_week, "start": s.start_time, "end": s.end_time} for s in job.shifts],
         "salary_min": job.salary_min or 0,
         "salary_max": job.salary_max or 0,
         "salary_type": job.salary_type, # Pass salary type
         "skills": set(), # Helper for now, or parse job.description
         "title": job.title,
         "description": job.description # Important for keyword matching
    }

    match_result = matcher.calculate_match(student_profile, job_data)
    
    schema = JobSchema()
    result = schema.dump(job)
    result['match_analysis'] = match_result # Add full analysis
    
    return jsonify(result)

@api_bp.route('/jobs/<int:job_id>/save', methods=['POST'])
@jwt_required()
def save_job(job_id):
    student = current_user.student_profile
    app = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
    if not app:
        app = Application(student_id=student.id, job_id=job_id, status='Saved')
        db.session.add(app)
    else:
        app.status = 'Saved'
    
    db.session.commit()
    return jsonify({"message": "Job saved"}), 201

@api_bp.route('/schedule', methods=['GET', 'PUT'])
@jwt_required()
def handle_schedule():
    student = current_user.student_profile
    timetable = student.timetable
    if not timetable and request.method == 'PUT':
        # Create default timetable if missing
        from app.models import Timetable
        timetable = Timetable(student_id=student.id, academic_term='Term 1')
        db.session.add(timetable)
        db.session.commit()
        # Refresh student to get relationship? Or just use object.
    
    if request.method == 'GET':
        if not timetable:
             return jsonify([])
             
        schema = ScheduleSlotSchema(many=True)
        return jsonify(schema.dump(timetable.slots))
    
    if request.method == 'PUT':
        data = request.json
        if not timetable: # Should be created above, but double check
             return jsonify({"error": "Timetable could not be created"}), 500

        # Clear existing
        ScheduleSlot.query.filter_by(timetable_id=timetable.id).delete()
        
        # Add new
        for slot in data:
            new_slot = ScheduleSlot(
                timetable_id=timetable.id,
                day_of_week=slot['day_of_week'],
                start_time=datetime.strptime(slot['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(slot['end_time'], '%H:%M').time(),
                activity_type=slot.get('activity_type', 'Class')
            )
            db.session.add(new_slot)
        
        db.session.commit()
        return jsonify({"message": "Schedule updated"}), 200

@api_bp.route('/applications', methods=['POST'])
@jwt_required()
def apply_for_job():
    student = current_user.student_profile
    data = request.json
    job_id = data.get('job_id')
    
    if not job_id:
         return jsonify({"error": "Job ID is required"}), 400

    # Check for existing
    existing_app = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
    
    if existing_app:
        if existing_app.status == 'Saved':
             # Upgrade to Applied
             existing_app.status = 'Applied'
             existing_app.applied_at = datetime.utcnow()
             db.session.commit()
             return jsonify({"message": "Application submitted successfully"}), 200
        else:
             return jsonify({"message": "Already applied for this job"}), 400
    
    # Create new
    new_app = Application(student_id=student.id, job_id=job_id, status='Applied')
    db.session.add(new_app)
    db.session.commit()
    
    return jsonify({"message": "Application submitted successfully"}), 201

@api_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    student = current_user.student_profile
    apps = Application.query.filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()
    
    # Custom dump
    results = []
    for app in apps:
        results.append({
            "id": app.id,
            "job_id": app.job_id,
            "status": app.status,
            "applied_at": app.applied_at,
            "job_title": app.job.title,
            "company": app.job.company_name
        })
    return jsonify(results)

@api_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    student = current_user.student_profile
    
    # Calculate stats
    total_apps = Application.query.filter_by(student_id=student.id).count()
    saved_jobs = Application.query.filter_by(student_id=student.id, status='Saved').count()
    
    # Matches count (mock logic: match score > 80)
    # Ideally efficient query, here using simple count for prototype
    matches_count = JobMatch.query.filter_by(student_id=student.id).filter(JobMatch.score >= 80).count()

    return jsonify({
        "matches": matches_count,
        "applications": total_apps,
        "interviews": 0, # Placeholder
        "saved": saved_jobs,
        "student_name": student.first_name
    })

@api_bp.route('/preferences', methods=['GET', 'PUT'])
@jwt_required()
def handle_preferences():
    student = current_user.student_profile
    prefs = student.preferences
    
    if not prefs:
        # Lazy create
        from app.models import StudentPreferences
        prefs = StudentPreferences(student_id=student.id)
        db.session.add(prefs)
        db.session.commit() # Commit to get ID? Or just wait.

    if request.method == 'GET':
        return jsonify({
            "min_salary": prefs.min_salary,
            "max_commute_time": prefs.max_commute_time,
            "preferred_roles": prefs.preferred_roles,
            "preferred_locations": prefs.preferred_locations
        })
    
    if request.method == 'PUT':
        data = request.json
        
        # Debug Logging
        with open('api_debug.log', 'a') as f:
             f.write(f"PUT /preferences for Student ID: {student.id} ({student.first_name} {student.last_name})\n")
             f.write(f"Data: {data}\n")
             
        if 'min_salary' in data:
            prefs.min_salary = data['min_salary']
        if 'max_commute_time' in data:
            prefs.max_commute_time = data['max_commute_time']
        if 'preferred_roles' in data:
            # Assume list or comma-string from frontend, store as CSV
            roles = data['preferred_roles']
            if isinstance(roles, list):
                prefs.preferred_roles = ",".join(roles)
            else:
                prefs.preferred_roles = roles
        
        if 'preferred_locations' in data:
            locs = data['preferred_locations']
            if isinstance(locs, list):
                prefs.preferred_locations = ",".join(locs)
            else:
                prefs.preferred_locations = locs
            
                prefs.preferred_locations = locs
            
                prefs.preferred_locations = locs
            
        db.session.commit()
        
        # Trigger update in background via Threading + Eager execution
        import threading
        def run_update():
             with current_app.app_context():
                 try:
                     print("Starting background update...")
                     # In EAGER mode, .delay() runs synchronously in this thread
                     # which is what we want (async from HTTP request, sync in background thread)
                     scrape_jobs_task.delay() 
                     # calculate_matches_task is called by scrape_jobs_task, but we call it again to be double sure
                     # calculate_matches_task.delay() 
                     print("Background update complete.")
                 except Exception as e:
                     print(f"Background update failed: {e}")

        threading.Thread(target=run_update).start()

        return jsonify({"message": "Preferences updated. Refresh in a few seconds to see new matches!"}), 200

@api_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def handle_profile():
    student = current_user.student_profile
    
    if request.method == 'GET':
        return jsonify({
            "first_name": student.first_name,
            "last_name": student.last_name,
            "university": student.university,
            "course": student.course,
            "year_of_study": student.year_of_study,
            "visa_status": student.visa_status,
            "weekly_hours_limit": student.weekly_hours_limit,
            "postcode": student.postcode
        })
    
    if request.method == 'PUT':
        data = request.json
        if 'university' in data: student.university = data['university']
        if 'course' in data: student.course = data['course']
        if 'year_of_study' in data: student.year_of_study = data['year_of_study']
        if 'visa_status' in data: student.visa_status = data['visa_status']
        if 'weekly_hours_limit' in data: student.weekly_hours_limit = data['weekly_hours_limit']
        
        if 'postcode' in data and data['postcode']:
            student.postcode = data['postcode']
            # Geocode
            try:
                pc = data['postcode'].replace(' ', '')
                res = requests.get(f"https://api.postcodes.io/postcodes/{pc}")
                if res.status_code == 200:
                    geo = res.json()['result']
                    student.latitude = geo['latitude']
                    student.longitude = geo['longitude']
            except Exception as e:
                print(f"Geocoding failed: {e}")

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
