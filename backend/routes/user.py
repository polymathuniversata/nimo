from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from models.user import User, Skill

user_bp = Blueprint('user', __name__)

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    # Check if requesting own profile or has admin permission (could be added later)
    current_user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    # Update basic user information
    if data.get('name'):
        user.name = data['name']
    if data.get('location'):
        user.location = data['location']
    if data.get('bio'):
        user.bio = data['bio']
    
    # Update skills if provided
    if data.get('skills'):
        # Remove existing skills
        Skill.query.filter_by(user_id=user.id).delete()
        
        # Add new skills
        for skill_name in data['skills']:
            skill = Skill(user_id=user.id, name=skill_name)
            db.session.add(skill)
    
    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500