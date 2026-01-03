import requests
import re
from app import create_app
from app.models import Job
from app.extensions import db

app = create_app('development')

# Simple cache for city names to avoid API spam
CITY_COORDS = {
    'birmingham': (52.4862, -1.8904),
    'birmingham, west midlands': (52.4862, -1.8904),
    'london': (51.5074, -0.1278),
    'greater london': (51.5074, -0.1278),
    'canary wharf': (51.5054, -0.0235),
    'manchester': (53.4808, -2.2426),
    'leeds': (53.8008, -1.5491),
}

def get_postcode_coords(postcode):
    try:
        resp = requests.get(f"https://api.postcodes.io/postcodes/{postcode}")
        if resp.status_code == 200:
            data = resp.json()['result']
            return data['latitude'], data['longitude']
    except Exception as e:
        print(f"Postcode API error for {postcode}: {e}")
    return None

with app.app_context():
    print("--- Starting Geocode Backfill ---")
    
    # 1. Find jobs with missing coords (lat=0 or None)
    # Using a small epsilon for float comparison or checking None
    jobs = Job.query.filter((Job.latitude == None) | (Job.latitude == 0)).all()
    print(f"Found {len(jobs)} jobs needing geocoding.")
    
    updated_count = 0
    
    for job in jobs:
        loc = job.location.lower().strip()
        
        # Strategy 1: City Name Lookup
        if loc in CITY_COORDS:
            lat, lng = CITY_COORDS[loc]
            job.latitude = lat
            job.longitude = lng
            updated_count += 1
            # print(f"Updated '{job.title}' ({loc}) -> City Map")
            continue
            
        # Strategy 2: Postcode Regex (UK Postcode roughly)
        # e.g. "SW1V 2LP" or "SW1V2LP"
        # Simple regex: Start with 1-2 letters, 1-2 digits, maybe space, 1 digit, 2 letters
        postcode_match = re.search(r'([A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2})', job.location, re.IGNORECASE)
        
        if postcode_match:
            pcm = postcode_match.group(0).replace(' ', '') # Clean for API
            coords = get_postcode_coords(pcm)
            if coords:
                job.latitude = coords[0]
                job.longitude = coords[1]
                updated_count += 1
                # print(f"Updated '{job.title}' ({job.location}) -> Postcode API")
            else:
                print(f"Failed to geocode postcode: {job.location}")
        else:
            # Fallback: Just try cleaning name matches strictly?
            # Maybe it contains "Birmingham" inside a longer string
            found_city = False
            for city, (lat, lng) in CITY_COORDS.items():
                if city in loc:
                    job.latitude = lat
                    job.longitude = lng
                    updated_count += 1
                    found_city = True
                    break
            
            if not found_city:
                print(f"Could not geocode location: '{job.location}'")

    db.session.commit()
    print(f"Backfill Complete. Updated {updated_count} jobs.")
