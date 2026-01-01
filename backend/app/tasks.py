from app.extensions import celery, db
from app.scrapers.reed import ReedScraper
from app.models import Job, Student, JobMatch, Application, JobShift
from app.services.matching import MatchingEngine
from datetime import datetime, timedelta

import logging
import json

logger = logging.getLogger(__name__)

@celery.task(bind=True)
def scrape_jobs_task(self):
    """
    Periodic task to scrape jobs from all sources.
    """
    logger.info("Starting scheduled job scrape...")
    try:
        # 1. Scrape Reed with Dynamic Keywords from Students
        from app.models import StudentPreferences
        
        # Get all unique preferred roles across all students
        prefs = StudentPreferences.query.with_entities(StudentPreferences.preferred_roles).all()
        keywords = set()
        for p in prefs:
            if p.preferred_roles:
                # Splitting by comma if stored as CSV
                roles = [r.strip() for r in p.preferred_roles.split(',')]
                keywords.update(roles)
        
        # Add default fallback keywords to ensure we always get some jobs
        defaults = {'part time student', 'retail part time', 'barista', 'tutor'}
        keywords.update(defaults)
        
        logger.info(f"Scraping for keywords: {keywords}")

        scraper = ReedScraper()
        scraper.run(keywords=list(keywords))
        
        # 2. Trigger matching update
        calculate_matches_task.delay()
        
        return "Scraping completed and matching triggered."
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        # self.retry(exc=e, countdown=60) # Optional retry logic

@celery.task
def calculate_matches_task():
    """
    Recalculate matches for active students against recent/all jobs.
    Heavy task! In production, optimize to only check new jobs vs all students.
    """
    logger.info("Starting match calculation...")
    engine = MatchingEngine()
    
    students = Student.query.all()
    # Optimization: Only match against active jobs from last 7 days
    recent_jobs = Job.query.filter_by(is_active=True).all() 

    match_count = 0
    
    for student in students:
        # Build profile from actual student data
        # Parse skills (assume comma-separated string)
        skill_set = set()
        if student.skills:
            skill_set = {s.strip() for s in student.skills.split(',')}
        
        # Safe Timetable
        slots = []
        if student.timetable:
            slots = [{"day": s.day_of_week, "start": s.start_time, "end": s.end_time} for s in student.timetable.slots]

        student_profile = {
            "location": {
                "lat": student.latitude or 51.5074, 
                "lng": student.longitude or -0.1278
            }, 
            "timetable": slots,
            "min_salary": student.preferences.min_salary if student.preferences else 10.0,
            "skills": skill_set,
            "preferences": {
                "roles": [r.strip() for r in student.preferences.preferred_roles.split(',')] if student.preferences and student.preferences.preferred_roles else []
            }
        }
        
        for job in recent_jobs:
            try:
                # Explicitly fetch shifts to avoid DetachedInstanceError with dynamic relationship
                shifts = JobShift.query.filter_by(job_id=job.id).all()
                
                job_data = {
                    "location": {"lat": job.latitude or 51.5, "lng": job.longitude or -0.1},
                    "shifts": [{"day": s.day_of_week, "start": s.start_time, "end": s.end_time} for s in shifts],
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_type": job.salary_type, 
                    "skills": set(), 
                    "title": job.title,
                    "description": job.description 
                }
                
                # Calculate match
                result = engine.calculate_match(student_profile, job_data)
                score = result['total_score']
                
                # Upsert Match Record
                match_record = JobMatch.query.filter_by(student_id=student.id, job_id=job.id).first()
                if not match_record:
                    match_record = JobMatch(student_id=student.id, job_id=job.id)
                    db.session.add(match_record)
                
                match_record.score = score
                match_record.breakdown = json.dumps(result['breakdown']) # Ensure breakdown is JSON string
                match_record.last_calculated = datetime.utcnow()
                
                db.session.commit() # Commit per match to avoid rollback issues wiping everything
                match_count += 1

            except Exception as e:
                db.session.rollback()
                logger.error(f"Error processing job {job.id}: {e}")
                print(f"Error processing job {job.id}: {e}")
                continue
            
    # db.session.commit() # Removed bulk commit
    logger.info(f"Updated {match_count} match records.")
    return f"Updated {match_count} matches."

@celery.task
def cleanup_old_jobs_task():
    """
    Archive jobs older than 30 days.
    """
    cutoff = datetime.utcnow() - timedelta(days=30)
    old_jobs = Job.query.filter(Job.posted_at < cutoff, Job.is_active == True).all()
    
    for job in old_jobs:
        job.is_active = False
        
    db.session.commit()
    return f"Archived {len(old_jobs)} old jobs."

@celery.task
def send_daily_digest(student_id):
    """
    Send email with top matches.
    """
    # Placeholder for Email Service
    logger.info(f"Sending digest to student {student_id}")
    return "Email sent (simulated)"
