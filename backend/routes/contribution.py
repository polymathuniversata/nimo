from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from models.contribution import Contribution, Verification
from models.user import Token, TokenTransaction
from services.token_service import award_tokens_for_verification

contribution_bp = Blueprint('contribution', __name__)

@contribution_bp.route('/', methods=['GET'])
@jwt_required()
def get_contributions():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    verified = request.args.get('verified')
    
    # Base query
    query = Contribution.query.filter_by(user_id=current_user_id)
    
    # Apply filters
    if verified is not None:
        if verified.lower() == 'true':
            query = query.filter(Contribution.verifications.any())
        elif verified.lower() == 'false':
            query = query.filter(~Contribution.verifications.any())
    
    # Execute query
    contributions = query.order_by(Contribution.created_at.desc()).all()
    
    return jsonify([contrib.to_dict() for contrib in contributions]), 200


@contribution_bp.route('/', methods=['POST'])
@jwt_required()
def add_contribution():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({"error": "Title is required"}), 400
    
    try:
        # Create new contribution
        new_contribution = Contribution(
            user_id=current_user_id,
            title=data['title'],
            description=data.get('description'),
            contribution_type=data.get('type'),
            evidence=data.get('evidence')
        )
        
        db.session.add(new_contribution)
        db.session.commit()
        
        return jsonify(new_contribution.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/<int:contrib_id>', methods=['GET'])
@jwt_required()
def get_contribution(contrib_id):
    contribution = Contribution.query.get(contrib_id)
    
    if not contribution:
        return jsonify({"error": "Contribution not found"}), 404
    
    return jsonify(contribution.to_dict()), 200


@contribution_bp.route('/<int:contrib_id>/verify', methods=['POST'])
@jwt_required()
def verify_contribution(contrib_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # In a real system, we would check if the current user has verification privileges
    
    # Validate required fields
    if not data.get('organization'):
        return jsonify({"error": "Organization is required"}), 400
    
    contribution = Contribution.query.get(contrib_id)
    if not contribution:
        return jsonify({"error": "Contribution not found"}), 404
    
    try:
        # Create verification
        verification = Verification(
            contribution_id=contrib_id,
            organization=data['organization'],
            verifier_name=data.get('verifier_name'),
            comments=data.get('comments')
        )
        
        db.session.add(verification)
        db.session.flush()
        
        # Award tokens to the contribution creator
        award_tokens_for_verification(contribution.user_id, verification.id)
        
        db.session.commit()
        
        return jsonify({
            "message": "Contribution verified successfully",
            "verification": verification.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500