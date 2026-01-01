from app import create_app, db
from app.models import Job

app = create_app()

def check_diversity():
    with app.app_context():
        # Get last 20 jobs
        jobs = Job.query.order_by(Job.id.desc()).limit(20).all()
        
        print(f"--- Checking Last 20 Scraped Jobs ---")
        for job in jobs:
            print(f"- {job.title} ({job.company_name})")

if __name__ == "__main__":
    check_diversity()
