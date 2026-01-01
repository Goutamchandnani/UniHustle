from app import create_app, db
from app.scrapers.reed import ReedScraper
from app.models import Job

app = create_app()

def test_scraper():
    with app.app_context():
        print("Starting Reed Scraper test...")
        scraper = ReedScraper()
        scraper.run()
        
        count = Job.query.count()
        print(f"Total jobs in database: {count}")
        
        # Print sample
        last_job = Job.query.order_by(Job.id.desc()).first()
        if last_job:
            print(f"Sample Job: {last_job.title} at {last_job.company_name}")
            print(f"Salary: {last_job.salary_min}-{last_job.salary_max}")

if __name__ == "__main__":
    test_scraper()
