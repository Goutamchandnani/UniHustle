from app import create_app
from app.models import Job
from app.extensions import db

app = create_app('development')

with app.app_context():
    print("--- Inspecting Irrelevant Jobs ---")
    
    # Search for the job in the screenshot
    bad_job = Job.query.filter(Job.title.ilike('%Associate Director%')).first()
    
    if bad_job:
        print(f"Found Job: {bad_job.title}")
        print(f"Description Snippet: {bad_job.description[:200]}...")
        
        # Check why it matched 'Barista' or 'Cafe'
        keywords = ['barista', 'cafe']
        found_triggers = []
        
        desc_lower = bad_job.description.lower()
        title_lower = bad_job.title.lower()
        
        for k in keywords:
            if k in title_lower:
                found_triggers.append(f"Title matched '{k}'")
            if k in desc_lower:
                found_triggers.append(f"Description matched '{k}'")
                
        print(f"Triggers found: {found_triggers}")
        
    else:
        print("Could not find the specific job 'Associate Director' in DB.")
        
    print("--- End Inspection ---")
