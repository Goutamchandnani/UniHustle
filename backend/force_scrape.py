from app import create_app
from app.tasks import scrape_jobs_task
from app.extensions import db

app = create_app('development')

with app.app_context():
    print("--- Forcing Full Scrape & Save ---")
    try:
        # This will run the scraper (with new location logic) AND save to DB
        result = scrape_jobs_task() 
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    print("--- Done ---")
