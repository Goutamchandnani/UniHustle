import requests
import json

# Configuration
BASE_URL = 'http://localhost:5000/api'
EMAIL = 'auth_final@test.com'
PASSWORD = 'password123'

def get_auth_token():
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': EMAIL,
        'password': PASSWORD
    })
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Login failed: {response.text}")
        return None

def test_application_flow():
    token = get_auth_token()
    if not token:
        return

    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Get a Job ID (e.g., job 1)
    job_id = 1
    
    print(f"--- 1. Applying for Job {job_id} ---")
    resp = requests.post(f'{BASE_URL}/applications', json={'job_id': job_id}, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    # 2. Try applying again (Duplicate check)
    print(f"\n--- 2. Applying for Job {job_id} Again (Duplicate Check) ---")
    resp = requests.post(f'{BASE_URL}/applications', json={'job_id': job_id}, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    # 3. Get Applications List
    print(f"\n--- 3. Fetching My Applications ---")
    resp = requests.get(f'{BASE_URL}/applications', headers=headers)
    print(f"Status: {resp.status_code}")
    apps = resp.json()
    print(f"Found {len(apps)} applications:")
    for app in apps:
        print(f" - [{app['status']}] {app['job_title']} (ID: {app['job_id']})")

if __name__ == "__main__":
    test_application_flow()
