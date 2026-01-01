from app import create_app, db
from app.models import User, Student, StudentPreferences

app = create_app()

with app.app_context():
    # Find our auth user
    user = User.query.filter_by(email='auth_final@test.com').first()
    if user and user.student_profile:
        student = user.student_profile
        
        # Set Profile Data for Matching
        student.latitude = 51.5074 # London
        student.longitude = -0.1278
        student.skills = "Python, Communication, Retail"
        
        # Set Preferences
        if not student.preferences:
            prefs = StudentPreferences(student_id=student.id)
            db.session.add(prefs)
            student.preferences = prefs
        
        student.preferences.min_salary = 12.0
        
        db.session.commit()
        print(f"Updated profile for {user.email}")
    else:
        print("User not found matching auth_final@test.com")
