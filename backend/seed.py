from app import create_app, db
from app.models import User, Student, Job, JobShift, Timetable, ScheduleSlot, JobMatch, Application
from faker import Faker
import random
from datetime import datetime, time, timedelta

fake = Faker()
app = create_app('default')

def seed_data():
    with app.app_context():
        # Clear existing data (optional, be careful in prod)
        db.drop_all()
        db.create_all()
        print("Database cleared and recreated.")

        # Create Students
        students = []
        for i in range(5):
            email = f'student{i+1}@uni.ac.uk'
            user = User(email=email, is_student=True)
            user.set_password('password')
            db.session.add(user)
            db.session.flush() # get ID

            student = Student(
                user_id=user.id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                university='University of London',
                course=random.choice(['Computer Science', 'Business', 'Psychology']),
                year_of_study=random.randint(1, 3),
                weekly_hours_limit=20
            )
            db.session.add(student)
            students.append(student)
            
            # Create Timetable for Student
            timetable = Timetable(student=student, academic_term='Fall 2025')
            db.session.add(timetable)
            db.session.flush()

            # Add random class slots
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            for day in days:
                if random.choice([True, False]): # Randomly have class
                    start_hour = random.randint(9, 15)
                    slot = ScheduleSlot(
                        timetable_id=timetable.id,
                        day_of_week=day,
                        start_time=time(start_hour, 0),
                        end_time=time(start_hour + 2, 0),
                        activity_type='Lecture',
                        location='Main Campus'
                    )
                    db.session.add(slot)
        
        print("Students and Timetables seeded.")

        # Create Jobs
        jobs = []
        job_titles = ['Barista', 'Retail Assistant', 'Tutor', 'Library Assistant', 'Data Entry']
        for _ in range(10):
            job = Job(
                title=random.choice(job_titles),
                company_name=fake.company(),
                description=fake.text(),
                salary_min=random.uniform(10.5, 15.0),
                salary_max=random.uniform(15.0, 20.0),
                location='London',
                source='Internal'
            )
            db.session.add(job)
            jobs.append(job)
            db.session.flush()

            # Add Shifts
            for day in ['Saturday', 'Sunday']:
                shift = JobShift(
                    job_id=job.id,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(16, 0)
                )
                db.session.add(shift)

        print("Jobs and Shifts seeded.")

        db.session.commit()
        
        # Create Dummy Matches
        for student in students:
            for job in jobs:
                score = random.uniform(60, 95)
                match = JobMatch(
                    student_id=student.id,
                    job_id=job.id,
                    score=score,
                    breakdown='{"schedule": 35, "location": 20}'
                )
                db.session.add(match)
        
        db.session.commit()
        print("Matches seeded. Detailed data generation complete.")

if __name__ == '__main__':
    seed_data()
