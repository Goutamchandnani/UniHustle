from app import create_app
from app.scrapers.reed import ReedScraper
from app.models import Job
from app.extensions import db

app = create_app('development')

with app.app_context():
    print("--- Starting Debug Scrape ---")
    scraper = ReedScraper()
    # Search for 'barista' in 'Birmingham' explicitly
    jobs = scraper.fetch_jobs(keywords=['barista'], location='Birmingham')
    
    print(f"Found {len(jobs)} jobs for 'barista' in Birmingham")
    
    # bham_count is now redundant since we searched BY location, but keeping verify
    bham_count = 0
    
    bham_count = 0
    for job in jobs:
        loc = job.get('locationName', '').lower()
        if 'birmingham' in loc:
            bham_count += 1
            
    print(f"Found {bham_count} jobs in Birmingham")
    
    if len(jobs) > 0:
        print("First job sample:", jobs[0])
    
    print("--- End Debug Scrape ---")
