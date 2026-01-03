from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app('development')

with app.app_context():
    print("--- Checking Schema ---")
    try:
        # For SQLite
        res = db.session.execute(text("PRAGMA table_info(student_preferences)")).fetchall()
        print("Student Preferences Columns:")
        for r in res:
            print(f" - {r[1]}")
            
        print("\nJobs Columns:")
        res = db.session.execute(text("PRAGMA table_info(jobs)")).fetchall()
        for r in res:
            print(f" - {r[1]}")
            
    except Exception as e:
        print(f"Error checking schema: {e}")
