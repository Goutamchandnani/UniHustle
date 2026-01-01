from app.services.matching import MatchingEngine

def test_matching():
    engine = MatchingEngine()

    # User Profile
    student = {
        "location": {"lat": 51.5074, "lng": -0.1278}, # Central London
        "skills": {"python", "communication", "retail"},
        "min_salary": 12.00,
        "preferences": {"roles": ["Barista", "Assistant"]},
        "timetable": [ # Monday morning class
             {"day": "Monday", "start": "09:00", "end": "12:00"}
        ]
    }

    # Job A: Perfect Match
    # Clean schedule, Close, Good Pay, Matches Preferences
    job_a = {
        "title": "Barista Assistant",
        "location": {"lat": 51.5074, "lng": -0.1278}, # Same location (0 miles)
        "skills": {"communication", "retail"},
        "salary_min": 13.00,
        "salary_max": 15.00,
        "shifts": [{"day": "Tuesday", "start": "09:00", "end": "17:00"}], # No conflict
        "description": "Great job for students"
    }

    # Job B: Poor Match
    # Schedule Conflict, Far, Low Pay, Mismatched Skills
    job_b = {
        "title": "Senior Developer",
        "location": {"lat": 52.4862, "lng": -1.8904}, # Birmingham (100+ miles)
        "skills": {"java", "architecture"},
        "salary_min": 10.00,
        "shifts": [{"day": "Monday", "start": "10:00", "end": "11:00"}], # Conflict!
        "description": "Hard work"
    }

    print("\n--- Job A Analysis (Expected High Score) ---")
    result_a = engine.calculate_match(student, job_a)
    print(f"Total Score: {result_a['total_score']}%")
    print(f"Breakdown: {result_a['breakdown']}")

    print("\n--- Job B Analysis (Expected Low Score) ---")
    result_b = engine.calculate_match(student, job_b)
    print(f"Total Score: {result_b['total_score']}%")
    print(f"Breakdown: {result_b['breakdown']}")
    print(f"Schedule Analysis: {result_b['schedule_analysis']}")

if __name__ == "__main__":
    test_matching()
