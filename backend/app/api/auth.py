from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,  current_user
from app.models import User, Student
from app.extensions import db, jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token, user_id=user.id, email=user.email), 200

    return jsonify({"msg": "Bad username or password"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 409

    # Create User
    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    # Create Student (Basic)
    student = Student(user_id=new_user.id, first_name=data.get('firstName', 'New'), last_name=data.get('lastName', 'User'))
    db.session.add(student)
    db.session.commit()
    
    access_token = create_access_token(identity=str(new_user.id))
    return jsonify(access_token=access_token, message="User created successfully"), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    # Helper to get current user data
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    student = Student.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": student.first_name if student else None,
        "last_name": student.last_name if student else None
    })

# Helper for other routes to look up user
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()
