from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

from app import db
from models.bond import Bond, BondMilestone, BondInvestment
from models.user import Token, TokenTransaction

bond_bp = Blueprint('bond', __name__)

@bond_bp.route('/', methods=['GET'])
@jwt_required()
def get_bonds():
    # Query parameters
    cause = request.args.get('cause')
    status = request.args.get('status', 'active')
    creator_id = request.args.get('creator_id')
    
    # Base query
    query = Bond.query
    
    # Apply filters
    if cause:
        query = query.filter_by(cause=cause)
    if status:
        query = query.filter_by(status=status)
    if creator_id:
        query = query.filter_by(creator_id=creator_id)
    
    # Execute query
    bonds = query.order_by(Bond.created_at.desc()).all()
    
    return jsonify([bond.to_dict() for bond in bonds]), 200


@bond_bp.route('/', methods=['POST'])
@jwt_required()
def create_bond():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'value']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Generate a unique bond ID
        bond_id = f"{data.get('cause', 'bond')}-{str(uuid.uuid4())[:8]}"
        
        # Create new bond
        new_bond = Bond(
            bond_id=bond_id,
            creator_id=current_user_id,
            title=data['title'],
            description=data.get('description'),
            cause=data.get('cause'),
            value=int(data['value']),
            image_url=data.get('image_url')
        )
        
        db.session.add(new_bond)
        
        # Add milestones if provided
        if data.get('milestones'):
            for milestone_data in data['milestones']:
                milestone = BondMilestone(
                    bond_id=new_bond.id,
                    milestone=milestone_data['milestone'],
                    evidence=milestone_data.get('evidence')
                )
                db.session.add(milestone)
        
        db.session.commit()
        
        return jsonify(new_bond.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bond_bp.route('/<int:bond_id>', methods=['GET'])
@jwt_required()
def get_bond(bond_id):
    bond = Bond.query.get(bond_id)
    
    if not bond:
        return jsonify({"error": "Bond not found"}), 404
    
    bond_data = bond.to_dict()
    
    # Add milestones
    bond_data['milestones'] = [milestone.to_dict() for milestone in bond.milestones]
    
    # Add investments
    bond_data['investments'] = [investment.to_dict() for investment in bond.investments]
    
    return jsonify(bond_data), 200


@bond_bp.route('/<int:bond_id>/invest', methods=['POST'])
@jwt_required()
def invest_in_bond(bond_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate amount
    if not data.get('amount'):
        return jsonify({"error": "Investment amount is required"}), 400
    
    try:
        amount = int(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Amount must be a valid number"}), 400
    
    # Get the bond
    bond = Bond.query.get(bond_id)
    if not bond:
        return jsonify({"error": "Bond not found"}), 404
    
    if bond.status != 'active':
        return jsonify({"error": f"Bond is not active (status: {bond.status})"}), 400
    
    # Check investor's token balance
    token = Token.query.filter_by(user_id=current_user_id).first()
    if not token or token.balance < amount:
        return jsonify({"error": "Insufficient token balance"}), 400
    
    try:
        # Create the investment
        investment = BondInvestment(
            bond_id=bond_id,
            investor_id=current_user_id,
            amount=amount
        )
        db.session.add(investment)
        
        # Deduct tokens from investor
        token.balance -= amount
        transaction = TokenTransaction(
            token_id=token.id,
            amount=amount,
            transaction_type='debit',
            description=f"Investment in bond {bond.bond_id}: {bond.title}"
        )
        db.session.add(transaction)
        
        # Add tokens to creator (in a real system, might hold in escrow until milestones achieved)
        creator_token = Token.query.filter_by(user_id=bond.creator_id).first()
        if not creator_token:
            creator_token = Token(user_id=bond.creator_id, initial_balance=0)
            db.session.add(creator_token)
            db.session.flush()
        
        creator_token.balance += amount
        creator_transaction = TokenTransaction(
            token_id=creator_token.id,
            amount=amount,
            transaction_type='credit',
            description=f"Investment received for bond {bond.bond_id}"
        )
        db.session.add(creator_transaction)
        
        db.session.commit()
        
        return jsonify({
            "message": "Investment successful",
            "investment": investment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bond_bp.route('/<int:bond_id>/milestones/<int:milestone_id>/verify', methods=['POST'])
@jwt_required()
def verify_milestone(bond_id, milestone_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # In a real system, we would check if the current user has verification privileges
    
    # Get the milestone
    milestone = BondMilestone.query.filter_by(id=milestone_id, bond_id=bond_id).first()
    if not milestone:
        return jsonify({"error": "Milestone not found"}), 404
    
    if milestone.is_verified:
        return jsonify({"error": "Milestone already verified"}), 400
    
    try:
        # Verify the milestone
        milestone.verify(data.get('verifier', f"User #{current_user_id}"))
        
        # Check if all milestones are verified and update bond status if needed
        bond = Bond.query.get(bond_id)
        all_milestones_verified = all(m.is_verified for m in bond.milestones)
        
        if all_milestones_verified and len(bond.milestones) > 0:
            bond.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            "message": "Milestone verified successfully",
            "milestone": milestone.to_dict(),
            "all_completed": all_milestones_verified
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500