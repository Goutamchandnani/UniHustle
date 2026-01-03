from app.services.matching import MatchingEngine

engine = MatchingEngine()

# Test Case 1: Simple
user_prefs = {'roles': ['Barista']}
job_data = {'title': 'Barista'}

score = engine._calculate_preference_score(user_prefs, job_data)
print(f"Test 1 'Barista' vs 'Barista': Score={score}")

# Test Case 2: From Real World (Simulated)
# Maybe the job title has extra stuff?
job_data_2 = {'title': 'Barista - Flexible shifts'}
score_2 = engine._calculate_preference_score(user_prefs, job_data_2)
print(f"Test 2 'Barista' vs 'Barista - Flexible...': Score={score_2}")

# Test Case 3: Case sensitivity
user_prefs_3 = {'roles': ['barista']} # Lowercase in list?
job_data_3 = {'title': 'Barista'}
score_3 = engine._calculate_preference_score(user_prefs_3, job_data_3)
print(f"Test 3 'barista' vs 'Barista': Score={score_3}")

# Test Case 4: The value from DB might be weird
print("--- Checking force_match.py logic ---")
# In force_match we split: [r.strip() for r in str.split(',')]
csv = "Barista, Cafe"
roles = [r.strip() for r in csv.split(',')]
print(f"Parsed Roles: {roles}")
score_4 = engine._calculate_preference_score({'roles': roles}, {'title': 'Barista'})
print(f"Test 4 DB Sim: Score={score_4}")
