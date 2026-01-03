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

        # 2. Location Score (TIERED SYSTEM)
        # Initialize City Matcher with user preferences
        from .location_matcher import CityLocationMatcher
        loc_matcher = CityLocationMatcher(student_profile.get('preferences', {}))
        
        # Calculate Tiered Score
        # We pass job_data because it contains 'is_remote' and raw 'location' dict
        loc_result = loc_matcher.calculate_location_score(job_data)
        
        location_score = loc_result['score']
        location_meta = {
            'tier': loc_result['tier'],
            'badge': loc_result['badge'],
            'badge_color': loc_result['badge_color'],
            'reason': loc_result['reason']
        }
        
        if loc_result.get('excluded'):
             # If strictly excluded, force total score to 0? Or just penalty?
             # User requested "hidden by default", so implies it still exists but Low.
             # But if score is 0, let's keep it 0.
             pass

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

        # "Dealbreaker" Logic: If role preference is completely missed, punish the total score significantly.
        # This ensures users see "only" (or mostly) what they asked for.
        if pref_score == 0 and student_profile.get('preferences', {}).get('roles'):
             total_score *= 0.1 # 90% penalty for role mismatch

        # Location Dealbreaker: If location is impossible (score 0), punish heavily too.
        # New: Using Tier 6 (Excluded) to trigger this
        if location_score == 0:
             total_score *= 0.1 # Bury distant jobs
             
        # Add Location Meta to Breakdown for Frontend
        breakdown = {
            "schedule": schedule_score,
            "location": location_score,
            "skills": skills_score,
            "salary": salary_score,
            "preferences": pref_score,
            "location_data": location_meta 
        }

        return {
            "total_score": round(total_score, 1),
            "breakdown": breakdown,
            "schedule_analysis": schedule_result['analysis']
        }

    # Legacy method kept for backward compat if needed, or removed.
    def _calculate_location_score(self, user_loc: Dict, job_loc: Dict, max_commute: int = 45, preferred_locs: List[str] = None) -> int:
         return 0 # Deprecated

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
            matches = [role.lower() in title for role in desired_roles]
            if not any(matches):
                if 'barista' in title: # Only log if it should have matched!
                     print(f"DEBUG PREF FAIL: Roles={desired_roles} vs Title='{title}'")
                score = 0 # Strict mismatch
                
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
