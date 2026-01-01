from app import create_app, db
from app.models import User, StudentPreferences

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='auth_final@test.com').first()
    student = user.student_profile
    
    print(f"Checking preferences for {student.first_name}...")
    
    # Simulate API PUT
    if not student.preferences:
        print("Creating preferences...")
        prefs = StudentPreferences(student_id=student.id)
        db.session.add(prefs)
    else:
        prefs = student.preferences
        
    print(f"Old Commute Time: {prefs.max_commute_time}")
    
    # Update
    prefs.max_commute_time = 45
    db.session.commit()
    
    print(f"New Commute Time: {prefs.max_commute_time}")
    print("Verification Successful if New Time is 45.")
