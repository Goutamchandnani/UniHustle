import requests
from flask import current_app
from .base import BaseScraper

class ReedScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name='Reed.co.uk')
        self.api_url = "https://www.reed.co.uk/api/1.0/search"
    
    def fetch_jobs(self, keywords=None, location=None):
        api_key = current_app.config.get('REED_API_KEY')
        if not api_key:
            print("Warning: REED_API_KEY not found in config.")
            return []

        # Categories to search
        categories = keywords if keywords else [
            'part time student'
        ]
        
        all_results = []
        fetched_ids = set()

        for term in categories:
            print(f"Fetching Reed jobs for: '{term}' in '{location or 'UK'}'")
            params = {
                'keywords': term,
                'keywords': term,
                'contractType': 'PartTime',
                'resultsToTake': 100 # Fetch max allowed per page
            }
            if location:
                params['locationName'] = location
                params['distanceFromLocation'] = 10 # 10 miles radius
            
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
        
        # Remote Detection logic
        title_lower = normalized['title'].lower() if normalized['title'] else ''
        loc_lower = normalized['location'].lower() if normalized['location'] else ''
        
        if 'remote' in title_lower or 'work from home' in title_lower or 'remote' in loc_lower:
             normalized['is_remote'] = True
             normalized['remote_type'] = 'full_remote'
        else:
             normalized['is_remote'] = False
             normalized['remote_type'] = None
             
        return normalized
