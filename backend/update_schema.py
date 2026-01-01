from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Helper to add column if not exists (Postgres specific "IF NOT EXISTS" works in ADD COLUMN)
    # But SQLite/Generic SQL fallback:
    
    print("Updating 'students' table...")
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS skills TEXT"))
            conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION"))
            conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION"))
            conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS postcode VARCHAR(10)"))
            conn.commit()
        print("Success: Added skills, latitude, longitude columns.")
    except Exception as e:
        print(f"Error: {e}")
