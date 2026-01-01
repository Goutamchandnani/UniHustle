from app import create_app, db
from app.models import User, Student, Job
from config import config

app = create_app('default')

def init_db():
    with app.app_context():
        # Create tables
        db.drop_all()
        db.create_all()
        print("Database tables created.")

        # Create a test user if it doesn't exist
        if not User.query.filter_by(email='test@student.com').first():
            user = User(email='test@student.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create Student Profile
            student = Student(
                user_id=user.id,
                first_name='Test',
                last_name='Student',
                university='University of London',
                course='Computer Science'
            )
            db.session.add(student)
            db.session.commit()
            
            # Create a Timetable for the student
            from app.models import Timetable
            timetable = Timetable(student_id=student.id, academic_term='Fall 2025')
            db.session.add(timetable)
            db.session.commit()
            
            print("Test user and student profile created.")
        else:
            print("Test user already exists.")

import traceback

if __name__ == '__main__':
    try:
        init_db()
    except Exception:
        traceback.print_exc()
