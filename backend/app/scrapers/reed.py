import requests
from flask import current_app
from .base import BaseScraper

class ReedScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name='Reed.co.uk')
        self.api_url = "https://www.reed.co.uk/api/1.0/search"
    
    def fetch_jobs(self, keywords=None):
        api_key = current_app.config.get('REED_API_KEY')
        if not api_key:
            print("Warning: REED_API_KEY not found in config.")
            return []

        # Categories to search
        categories = keywords if keywords else [
            'part time student', 
            'retail part time', 
            'barista part time', 
            'tutor part time', 
            'warehouse part time', 
            'admin part time'
        ]
        
        all_results = []
        fetched_ids = set()

        for term in categories:
            print(f"Fetching Reed jobs for: {term}")
            params = {
                'keywords': term,
                'locationName': 'London',
                'distanceFromLocation': 15, # Increased radius slightly
                'contractType': 'PartTime'
            }
            
            try:
                response = requests.get(
                    self.api_url, 
                    params=params, 
                    auth=(api_key, '')
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get('results', [])
                
                count = 0
                for job in results:
                    job_id = job.get('jobId')
                    if job_id not in fetched_ids:
                        all_results.append(job)
                        fetched_ids.add(job_id)
                        count += 1
                
                print(f"  - Found {count} new jobs for '{term}'")
                
            except requests.exceptions.RequestException as e:
                print(f"Reed API Request Failed for '{term}': {e}")
                
        return all_results
    def normalize_job(self, raw_data):
        from .normalization import _parse_salary, _parse_date, _extract_shifts

        normalized = {
            'title': raw_data.get('jobTitle'),
            'company_name': raw_data.get('employerName'),
            'description': raw_data.get('jobDescription'),
            'location': raw_data.get('locationName'),
            'salary_min': _parse_salary(raw_data.get('minimumSalary')),
            'salary_max': _parse_salary(raw_data.get('maximumSalary')),
            'currency': raw_data.get('currency', 'GBP'),
            'source': self.source_name,
            'external_id': str(raw_data.get('jobId')),
            'external_url': raw_data.get('jobUrl'),
            'posted_at': _parse_date(raw_data.get('date')),
            'is_active': True
        }
        
        # Extract shifts
        normalized['shifts'] = _extract_shifts(normalized['description'])
        
        return normalized
