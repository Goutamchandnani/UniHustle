import json

class CityLocationMatcher:
    """
    City-based location matching with intelligent prioritization.
    Matches jobs based on Primary City, Preferred Cities, Nearby, etc.
    """
    
    # UK Cities grouped by proximity/region
    CITY_REGIONS = {
        'London': {
            'nearby': ['Reading', 'Oxford', 'Brighton', 'Cambridge', 'Guildford', 'Watford', 'St Albans'],
            'region': 'South East England'
        },
        'Manchester': {
            'nearby': ['Liverpool', 'Leeds', 'Sheffield', 'Bolton', 'Salford', 'Stockport'],
            'region': 'North West England'
        },
        'Birmingham': {
            'nearby': ['Coventry', 'Wolverhampton', 'Leicester', 'Nottingham', 'Solihull', 'West Bromwich'],
            'region': 'Midlands'
        },
        'Edinburgh': {
            'nearby': ['Glasgow', 'Dundee', 'Aberdeen', 'Stirling'],
            'region': 'Scotland'
        },
        'Bristol': {
            'nearby': ['Bath', 'Cardiff', 'Exeter', 'Gloucester'],
            'region': 'South West England'
        },
        'Leeds': {
            'nearby': ['Manchester', 'Sheffield', 'York', 'Bradford', 'Hull'],
            'region': 'Yorkshire'
        },
        'Newcastle': {
            'nearby': ['Sunderland', 'Durham', 'Middlesbrough'],
            'region': 'North East England'
        },
        'Cardiff': {
            'nearby': ['Bristol', 'Swansea', 'Newport'],
            'region': 'Wales'
        },
    }
    
    def __init__(self, prefs):
        """
        Initialize with StudentPreferences object or dict.
        """
        if isinstance(prefs, dict):
             self.primary_city = prefs.get('primary_city')
             
             # Handle preferred_cities (string or list)
             Raw_pref = prefs.get('preferred_locations')
             if isinstance(Raw_pref, str):
                 self.preferred_cities = [c.strip() for c in Raw_pref.split(',')] if Raw_pref else []
             else:
                 self.preferred_cities = Raw_pref or []
                 
             self.open_to_other = prefs.get('open_to_other_cities', False)
        else:
             # SQLAlchemy Object
             self.primary_city = prefs.primary_city
             
             Raw_pref = prefs.preferred_locations
             if hasattr(Raw_pref, 'split'):
                 self.preferred_cities = [c.strip() for c in Raw_pref.split(',')] if Raw_pref else []
             else:
                 self.preferred_cities = []
                 
             self.open_to_other = prefs.open_to_other_cities
             
        # Fallback: If primary_city is missing but preferred_cities has items, use first one
        if not self.primary_city and self.preferred_cities:
            self.primary_city = self.preferred_cities[0]
            
        # Ensure primary is in preferred
        if self.primary_city and self.primary_city not in self.preferred_cities:
            self.preferred_cities.append(self.primary_city)

    def calculate_location_score(self, job_data):
        """
        Calculate location match score (0-100) based on city
        Returns dict with score and metadata.
        """
        # job_data is a dict from MatchingEngine
        is_remote = job_data.get('is_remote', False)
        job_city_raw = job_data.get('location', {}).get('name', '') or ''
        
        # Simple extraction of City from string "Barista - Flexible shifts @ Oxford" ? 
        # No, usually job_data['location']['name'] is "Oxford" or "Oxford, UK"
        # We need to clean it.
        job_city = job_city_raw.split(',')[0].strip() # "Birmingham, West Midlands" -> "Birmingham"
        
        # PRIORITY 1: Remote jobs (always show, always high score)
        if is_remote:
            return {
                'score': 100,
                'priority': 'highest',
                'tier': 1,
                'reason': '🏠 Work from anywhere',
                'badge': 'REMOTE',
                'badge_color': 'purple'
            }
        
        # PRIORITY 2: Preferred cities (exact match)
        # Check against basic string match logic
        if self._is_city_match(job_city, self.preferred_cities):
            # Is it the PRIMARY city?
            if self._is_city_match(job_city, [self.primary_city]):
                return {
                    'score': 100,
                    'priority': 'highest',
                    'tier': 1,
                    'reason': f'📍 In {job_city} (your city)',
                    'badge': 'YOUR CITY',
                    'badge_color': 'green'
                }
            else:
                # Preferred but not primary
                return {
                    'score': 95,
                    'priority': 'high',
                    'tier': 2,
                    'reason': f'📍 In {job_city} (preferred location)',
                    'badge': 'PREFERRED',
                    'badge_color': 'blue'
                }
        
        # PRIORITY 3: Nearby cities (commutable distance)
        # Get nearby for PRIMARY city
        region_info = self._get_region_info(self.primary_city)
        if region_info:
            nearby_cities = region_info['nearby']
            
            if self._is_city_match(job_city, nearby_cities):
                if self.open_to_other:
                    return {
                        'score': 70,
                        'priority': 'medium',
                        'tier': 3,
                        'reason': f'📍 {job_city} (near {self.primary_city})',
                        'badge': 'NEARBY',
                        'badge_color': 'yellow'
                    }
                else:
                    # User didn't opt-in to other cities -> Lower score but track it
                    return {
                        'score': 40,
                        'priority': 'low',
                        'tier': 4,
                        'reason': f'📍 {job_city} (outside preferred area)',
                        'badge': 'NEARBY',
                        'badge_color': 'gray',
                        'hidden_by_default': True 
                    }
        
        # PRIORITY 5: Different region entirely
        if self.open_to_other:
            return {
                'score': 30,
                'priority': 'very-low',
                'tier': 5,
                'reason': f'📍 {job_city} (different region)',
                'badge': 'OTHER',
                'badge_color': 'gray',
                'hidden_by_default': True
            }
        else:
            # Exclude by default
            return {
                'score': 0,
                'priority': 'excluded',
                'tier': 6,
                'reason': f'📍 {job_city} (too far)',
                'badge': 'TOO FAR',
                'badge_color': 'gray',
                'hidden_by_default': True,
                'excluded': True
            }
            
    def _is_city_match(self, job_city, target_list):
        if not job_city or not target_list: return False
        job_city_lower = job_city.lower()
        for target in target_list:
            if target and target.lower() in job_city_lower:
                return True
        return False
        
    def _get_region_info(self, city):
        """Find region info for a city (checking keys)"""
        if not city: return None
        # Direct match
        if city in self.CITY_REGIONS:
            return self.CITY_REGIONS[city]
            
        # Check if city is listed as 'nearby' in another region? (Reverse lookup could be useful)
        # For now, simplistic.
        return None
