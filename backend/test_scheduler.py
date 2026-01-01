from app.services.scheduler import ScheduleAnalyzer

def test_scheduler():
    analyzer = ScheduleAnalyzer(commute_time_mins=30)

    # 1. Student Timetable
    timetable = [
        {"day": "Monday", "start": "09:00", "end": "11:00"}, # Lecture
        {"day": "Monday", "start": "14:00", "end": "16:00"}, # Lab
        {"day": "Wednesday", "start": "10:00", "end": "12:00"},
    ]

    # Test Case A: Perfect Fit (Tuesday Shift)
    job_a = [{"day": "Tuesday", "start": "09:00", "end": "17:00"}]
    print("\n--- Job A (Tuesday - Perfect) ---")
    print(analyzer.analyze_fit(timetable, job_a))

    # Test Case B: Direct Conflict (Monday Morning)
    job_b = [{"day": "Monday", "start": "10:00", "end": "14:00"}]
    print("\n--- Job B (Monday - Direct Conflict with 9-11 class) ---")
    print(analyzer.analyze_fit(timetable, job_b))

    # Test Case C: Tight Commute (Monday Lunch)
    # Class ends 11:00. Shift starts 11:30. Commute is 30m. Buffer is 0m. (Fail/Tight)
    job_c = [{"day": "Monday", "start": "11:30", "end": "13:30"}]
    print("\n--- Job C (Monday - Tight Commute) ---")
    print(analyzer.analyze_fit(timetable, job_c))

    # Test Case D: Good Fit (Monday Evening)
    # Class ends 16:00. Shift starts 17:00. 1h gap. (Perfect)
    job_d = [{"day": "Monday", "start": "17:00", "end": "20:00"}]
    print("\n--- Job D (Monday - Evening Good) ---")
    print(analyzer.analyze_fit(timetable, job_d))

if __name__ == "__main__":
    test_scheduler()
