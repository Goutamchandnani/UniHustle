from app import create_app
from app.tasks import scrape_jobs_task, calculate_matches_task
from app.models import StudentPreferences, Student
from app.scrapers.reed import ReedScraper
import logging

# Setup basic logging to see output
logging.basicConfig(level=logging.INFO)

app = create_app()

with app.app_context():
    print("--- Triggering Update for User Preferences ---")
    
    # 1. Fetch preferences for our test user
    # Assuming the user we just onboarded is the latest or specific email
    # Let's just fetch ALL unique preferences to be safe as per the task logic
    prefs = StudentPreferences.query.with_entities(StudentPreferences.preferred_roles).all()
    keywords = set()
    for p in prefs:
        if p.preferred_roles:
            roles = [r.strip() for r in p.preferred_roles.split(',')]
            keywords.update(roles)
    
    print(f"Found Keywords: {keywords}")
    
    if not keywords:
        print("No keywords found! Defaulting...")
        keywords = {'barista', 'admin'}

    # 2. Run Scraper for these keywords IMMEDIATELY
    print("Running Scraper...")
    scraper = ReedScraper()
    # Limit to reasonable number for test
    scraper.run(keywords=list(keywords))
    
    # 3. Run Matcher
    print("Running Matcher...")
    calculate_matches_task()
    
    print("--- Update Complete ---")
