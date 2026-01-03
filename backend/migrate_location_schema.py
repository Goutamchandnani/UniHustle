from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app('development')

def run_migration():
    with app.app_context():
        print("Running schema migration...")
        
        # Jobs table updates
        try:
            with db.engine.connect() as conn:
                # Add columns if not exist - simpler to just try and fail if exists
                try:
                    conn.execute(text("ALTER TABLE jobs ADD COLUMN is_remote BOOLEAN DEFAULT FALSE"))
                    conn.execute(text("ALTER TABLE jobs ADD COLUMN remote_type VARCHAR(50)"))
                    conn.commit()
                    print("Added is_remote and remote_type to jobs")
                except Exception as e:
                    print(f"Jobs Table Update: {e}")

        except Exception as e:
            print(f"Jobs outer error: {e}")

        # Student Preferences table updates
        try:
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE student_preferences ADD COLUMN primary_city VARCHAR(100)"))
                    conn.execute(text("ALTER TABLE student_preferences ADD COLUMN open_to_other_cities BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                    print("Added primary_city and open_to_other_cities to student_preferences")
                except Exception as e:
                     print(f"Student Prefs Table Update: {e}")
        except Exception as e:
            print(f"Student Prefs outer error: {e}")
            
        print("Migration complete.")

if __name__ == "__main__":
    run_migration()
