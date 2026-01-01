from typing import Dict, List, Any, Set
from .scheduler import ScheduleAnalyzer
import math

class MatchingEngine:
    def __init__(self):
        self.scheduler = ScheduleAnalyzer()
        
        # Weights - Tuned for "Fair Match" with Location Priority
        self.WEIGHTS = {
            'location': 0.45,  # Increased Priority
            'schedule': 0.25,
            'skills': 0.15,
            'preferences': 0.10,
            'salary': 0.05
        }

    def calculate_match(self, student_profile: Dict, job_data: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive match score (0-100) and breakdown.
        """
        # 1. Schedule Score (35%)
        schedule_result = self.scheduler.analyze_fit(
            student_profile.get('timetable', []), 
            job_data.get('shifts', [])
        )
        schedule_score = schedule_result['score']

        # 2. Location Score (25%)
        location_score = self._calculate_location_score(
            student_profile.get('location', {}),
            job_data.get('location', {})
        )

        # 3. Skills Score (20%)
        skills_score = self._calculate_skills_score(
            set(student_profile.get('skills', [])),
            set(job_data.get('skills', [])), # Assuming pre-extracted or passed
            job_data.get('description', '')
        )

        # 4. Salary/Hours Score (10%)
        salary_score = self._calculate_salary_score(
            student_profile.get('min_salary', 0),
            job_data.get('salary_min'),
            job_data.get('salary_max'),
            job_data.get('salary_type', 'hourly')
        )

        # 5. Preferences Score (10%)
        pref_score = self._calculate_preference_score(
            student_profile.get('preferences', {}),
            job_data
        )

        # Weighted Total
        total_score = (
            (schedule_score * self.WEIGHTS['schedule']) +
            (location_score * self.WEIGHTS['location']) +
            (skills_score * self.WEIGHTS['skills']) +
            (salary_score * self.WEIGHTS['salary']) +
            (pref_score * self.WEIGHTS['preferences'])
        )

        return {
            "total_score": round(total_score, 1),
            "breakdown": {
                "schedule": schedule_score,
                "location": location_score,
                "skills": skills_score,
                "salary": salary_score,
                "preferences": pref_score
            },
            "schedule_analysis": schedule_result['analysis']
        }

    def _calculate_location_score(self, user_loc: Dict, job_loc: Dict) -> int:
        """
        Score based on distance.
        Expects lat/lng in dicts. Returns 0-100.
        """
        if not user_loc or not job_loc or not user_loc.get('lat') or not job_loc.get('lat'):
            return 50 # Neutral if location unknown
        
        distance = self._haversine_distance(
            user_loc['lat'], user_loc['lng'],
            job_loc['lat'], job_loc['lng']
        )
        
        if distance < 1: return 100
        if distance < 3: return 85
        if distance < 5: return 70
        if distance < 10: return 50
        return 0

    def _calculate_skills_score(self, user_skills: Set[str], job_skills: Set[str], description: str) -> int:
        """
        Score based on skill overlap.
        If job has no specific skills, tries to find user skills in description.
        """
        # Normalize inputs
        user_skills = {s.lower() for s in user_skills} if user_skills else set()
        job_skills = {s.lower() for s in job_skills} if job_skills else set()
        
        # 1. Direct Skill Match (if job has explicit skills)
        if job_skills:
            if not user_skills: return 0
            overlap = user_skills.intersection(job_skills)
            score = (len(overlap) / len(job_skills)) * 100
            return min(100, int(score))

        # 2. Keyword Extraction Match (Fallback)
        # Check if any user skills appear in the description
        if not user_skills: return 100 # If user lists no skills, assume they are open? Or 50 neutral.
        
        found = 0
        desc_lower = description.lower() if description else ""
        
        # Common keywords to look for if user has generic skills
        # This part can be expanded with NLP later.
        
        for skill in user_skills:
            # Simple substring match - inaccurate but better than nothing for v1
            if skill in desc_lower:
                found += 1
        
        if found > 0:
            # If we found matches, score relative to how many skills user has
            # e.g. User has 5 skills, we found 2 in desc -> 40% match? 
            # Maybe too harsh. Let's say if we found ANY, it's a good sign.
            # Let's scale it: 1 match = 60, 2 = 80, 3+ = 100
            if found >= 3: return 100
            if found == 2: return 80
            return 60
            
        return 40 # No matches found, but maybe job is simple

    def _calculate_salary_score(self, min_needed: float, job_min: float, job_max: float, salary_type: str = 'hourly') -> int:
        """
        Score based on salary meeting expectations.
        Normalizes everything to hourly rate.
        """
        if not min_needed: return 100 # No requirement
        if not job_min: return 50 # Unknown salary
        
        # Normalize Job Salary to Hourly
        # Assumption: Yearly = 52 weeks * 37.5 hours = ~1950 hours
        HOURS_PER_YEAR = 1950
        
        normalized_min = job_min
        if salary_type and salary_type.lower() == 'yearly':
            normalized_min = job_min / HOURS_PER_YEAR
            
        normalized_max = job_max
        if job_max and salary_type and salary_type.lower() == 'yearly':
            normalized_max = job_max / HOURS_PER_YEAR
        
        # Logic
        # 1. Base rate meets need
        if normalized_min >= min_needed: return 100
        
        # 2. Max rate meets need (potential)
        if normalized_max and normalized_max >= min_needed: return 85
        
        # 3. Close calls (within 10%)
        if normalized_min >= min_needed * 0.9: return 60
        
        # 4. Way off
        return 0

    def _calculate_preference_score(self, prefs: Dict, job: Dict) -> int:
        """
        Simple keyword match for role/industry preferences.
        """
        score = 100
        
        # Role preference
        desired_roles = prefs.get('roles', [])
        if desired_roles:
            title = job.get('title', '').lower()
            if not any(role.lower() in title for role in desired_roles):
                score -= 50
                
        # Industry/Type (placeholder logic)
        return max(0, score)

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in miles."""
        R = 3958.8 # Earth radius in miles
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
