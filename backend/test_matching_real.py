from app.services.matching import MatchingEngine

def test_matching_logic():
    engine = MatchingEngine()
    
    print("--- Testing Skills ---")
    # Case 1: Direct match (Job has explicit skills)
    score = engine._calculate_skills_score(
        user_skills={'python', 'flask'}, 
        job_skills={'python', 'react'}, 
        description=""
    )
    print(f"Direct Match (Python/Flask vs Python/React): {score} (Expected ~50)")

    # Case 2: Description match (Job has no explicit skills)
    desc = "We need someone good with Python and communication."
    score = engine._calculate_skills_score(
        user_skills={'python'}, 
        job_skills=set(), 
        description=desc
    )
    print(f"Desc Match ('Python' in desc): {score} (Expected 60 or more)")

    print("\n--- Testing Salary ---")
    # Case 1: Hourly vs Hourly
    score = engine._calculate_salary_score(min_needed=15.0, job_min=20.0, job_max=25.0, salary_type='hourly')
    print(f"Hourly Ideal (Need 15, Job 20): {score} (Expected 100)")
    
    # Case 2: Hourly vs Yearly
    # 30k / 1950 = ~15.38/hr
    score = engine._calculate_salary_score(min_needed=15.0, job_min=30000.0, job_max=35000.0, salary_type='yearly')
    print(f"Yearly Norm (Need 15, Job 30k): {score} (Expected 100)")
    
    score = engine._calculate_salary_score(min_needed=20.0, job_min=30000.0, job_max=35000.0, salary_type='yearly')
    print(f"Yearly Norm Fail (Need 20, Job 30k=~15.38): {score} (Expected 0)")

    print("\n--- Testing Location ---")
    # Case 1: Close
    # Approx 1 mile apart
    u_loc = {'lat': 51.5074, 'lng': -0.1278} # London
    j_loc = {'lat': 51.5174, 'lng': -0.1278} # Close
    score = engine._calculate_location_score(u_loc, j_loc)
    print(f"Location Close: {score} (Expected 100 or 85)")
    
    # Case 2: Far
    j_loc_far = {'lat': 52.5074, 'lng': -0.1278} # Far
    score = engine._calculate_location_score(u_loc, j_loc_far)
    print(f"Location Far: {score} (Expected 0)")

if __name__ == "__main__":
    test_matching_logic()
