from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import db
from models.user import User, Skill, Token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 409
    
    try:
        # Create new user
        new_user = User(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            location=data.get('location'),
            bio=data.get('bio')
        )
        db.session.add(new_user)
        db.session.flush()  # Flush to get the new user ID
        
        # Add skills if provided
        if data.get('skills'):
            for skill_name in data['skills']:
                skill = Skill(user_id=new_user.id, name=skill_name)
                db.session.add(skill)
        
        # Initialize token balance
        token = Token(user_id=new_user.id, initial_balance=0)
        db.session.add(token)
        
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Verify user and password
    if not user or not user.verify_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200