import re
from datetime import datetime, time
from app.models import Job

def normalize_job_data(raw_data, source):
    """
    Standardize keys and values from different sources.
    """
    # Basic mapping
    normalized = {
        'title': raw_data.get('jobTitle') or raw_data.get('title'),
        'company_name': raw_data.get('employerName') or raw_data.get('company'),
        'description': raw_data.get('jobDescription') or raw_data.get('description'),
        'location': raw_data.get('locationName') or raw_data.get('location'),
        'salary_min': _parse_salary(raw_data.get('minimumSalary')),
        'salary_max': _parse_salary(raw_data.get('maximumSalary')),
        'currency': raw_data.get('currency', 'GBP'),
        'source': source,
        'external_id': str(raw_data.get('jobId') or raw_data.get('id')),
        'external_url': raw_data.get('jobUrl') or raw_data.get('url'),
        'posted_at': _parse_date(raw_data.get('date')),
        'is_active': True
    }
    
    # Extract shifts from description if not provided explicitly
    normalized['shifts'] = _extract_shifts(normalized['description'])
    
    return normalized

def is_duplicate_job(job_data):
    """
    Check if job exists based on external_id or title+company+location.
    """
    # 1. Check strict external ID match
    if Job.query.filter_by(source=job_data['source'], external_id=job_data['external_id']).first():
        return True

    # 2. Check fuzzy match (Title + Company + close Location)
    # Ideally use trigram similarity, but simple exact match for now
    match = Job.query.filter(
        Job.title == job_data['title'],
        Job.company_name == job_data['company_name']
    ).first()
    
    return match is not None

def _parse_salary(value):
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def _parse_date(date_str):
    if not date_str:
        return datetime.utcnow()
    # Add date parsing logic here (e.g. DD/MM/YYYY)
    return datetime.utcnow()

def _extract_shifts(text):
    """
    Extract shift patterns from text using Regex.
    Returns list of dicts: [{'day_of_week': 'Monday', 'start_time': '09:00', 'end_time': '17:00'}]
    """
    if not text:
        return []

    shifts = []
    
    # Pattern: "Monday to Friday, 9am to 5pm" or "Weekends 10:00-16:00"
    # This is a basic implementation. NLP would be better.
    
    # Example Regex for "9am - 5pm"
    time_pattern = r'(\d{1,2}(?::\d{2})?)\s*(am|pm)?\s*(?:-|to)\s*(\d{1,2}(?::\d{2})?)\s*(am|pm)?'
    
    # Simplified placeholder logic for demo
    # In production, use spaCy or a comprehensive library
    
    # Heuristic: If "weekend" found
    if 'weekend' in text.lower():
         shifts.append({
             'day_of_week': 'Saturday',
             'start_time': time(10, 0),
             'end_time': time(16, 0)
         })
         shifts.append({
             'day_of_week': 'Sunday',
             'start_time': time(10, 0),
             'end_time': time(16, 0)
         })
         
    return shifts
