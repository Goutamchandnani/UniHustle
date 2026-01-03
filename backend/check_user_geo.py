from app import create_app
from app.models import Student, StudentPreferences
from app.extensions import db

app = create_app('development')

with app.app_context():
    print("--- User Geo Check ---")
    
    # Get the user (Gautam)
    # Using 'ilike' to find 'Gautam' or 'Goutam'
    student = Student.query.filter(Student.first_name.ilike('Gautam')).first()
    
    if student:
        print(f"User: {student.first_name} {student.last_name} (ID: {student.id})")
        print(f"Postcode: {student.postcode}")
        print(f"Coords: Lat={student.latitude}, Lng={student.longitude}")
        
        if student.preferences:
            print(f"Preferred Locs: {student.preferences.preferred_locations}")
    else:
        print("User 'Gautam' not found.")
        
    print("--- End Check ---")
