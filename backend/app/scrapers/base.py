from abc import ABC, abstractmethod
from app.models import Job, JobShift
from app.extensions import db
from .normalization import normalize_job_data, is_duplicate_job
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, source_name):
        self.source_name = source_name
        self.jobs_found = 0
        self.jobs_saved = 0

    @abstractmethod
    def fetch_jobs(self):
        """
        Fetch raw job data from the source.
        Should return a list of raw job dictionaries.
        """
        pass

    @abstractmethod
    def normalize_job(self, raw_job):
        """
        Normalize raw job data into a dictionary matching the Job model.
        Must return a dict with keys: title, company_name, etc.
        """
        pass

    def run(self, **kwargs):
        """
        Main execution method: fetch -> normalize -> deduplicate -> save.
        """
        logger.info(f"Starting scraper for {self.source_name}...")
        try:
            raw_jobs = self.fetch_jobs(**kwargs)
            self.jobs_found = len(raw_jobs)
            logger.info(f"Fetched {self.jobs_found} raw jobs from {self.source_name}.")

            for raw_job in raw_jobs:
                self.process_job(raw_job)

            self.commit()
            logger.info(f"Scraper finished. Saved {self.jobs_saved} new jobs.")
            
        except Exception as e:
            logger.error(f"Error running scraper for {self.source_name}: {e}")
            db.session.rollback()

    def process_job(self, raw_job):
        """
        Normalize and save a single job if it's not a duplicate.
        """
        try:
            job_data = self.normalize_job(raw_job)
            
            if not is_duplicate_job(job_data):
                self.save_job(job_data)
                self.jobs_saved += 1
            else:
                logger.debug(f"Duplicate job found: {job_data.get('title')}")
                
        except Exception as e:
            logger.error(f"Error processing job: {e}")

    def save_job(self, job_data):
        """
        Create Job and JobShift objects and add to session.
        """
        shifts_data = job_data.pop('shifts', [])
        
        job = Job(**job_data)
        db.session.add(job)
        db.session.flush() # Get ID

        for shift in shifts_data:
            new_shift = JobShift(job_id=job.id, **shift)
            db.session.add(new_shift)

    def commit(self):
        db.session.commit()
