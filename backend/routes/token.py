from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from models.user import Token, TokenTransaction

token_bp = Blueprint('token', __name__)

@token_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    current_user_id = int(get_jwt_identity())  # Convert string to int
    
    token = Token.query.filter_by(user_id=current_user_id).first()
    
    if not token:
        # Initialize token record if it doesn't exist
        token = Token(user_id=current_user_id, initial_balance=0)
        db.session.add(token)
        db.session.commit()
    
    return jsonify({
        "balance": token.balance,
        "updated_at": token.updated_at.isoformat()
    }), 200


@token_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = int(get_jwt_identity())  # Convert string to int
    
    # Get user's token record
    token = Token.query.filter_by(user_id=current_user_id).first()
    
    if not token:
        return jsonify({"transactions": []}), 200
    
    # Get transactions
    transactions = TokenTransaction.query.filter_by(token_id=token.id) \
        .order_by(TokenTransaction.created_at.desc()).all()
    
    return jsonify({
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "description": t.description,
                "type": t.transaction_type,
                "created_at": t.created_at.isoformat()
            } for t in transactions
        ]
    }), 200


@token_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_tokens():
    current_user_id = int(get_jwt_identity())  # Convert string to int
    data = request.get_json()
    
    # Validate required fields
    if not data.get('recipient_id') or not data.get('amount'):
        return jsonify({"error": "Recipient ID and amount are required"}), 400
    
    # Validate amount
    try:
        amount = int(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Amount must be a valid number"}), 400
    
    # Get sender's token record
    sender_token = Token.query.filter_by(user_id=current_user_id).first()
    
    if not sender_token or sender_token.balance < amount:
        return jsonify({"error": "Insufficient token balance"}), 400
    
    # Get recipient's token record
    recipient_token = Token.query.filter_by(user_id=data['recipient_id']).first()
    
    if not recipient_token:
        return jsonify({"error": "Recipient not found"}), 404
    
    try:
        # Deduct from sender
        sender_token.balance -= amount
        sender_transaction = TokenTransaction(
            token_id=sender_token.id,
            amount=amount,
            transaction_type='debit',
            description=f"Transfer to user #{data['recipient_id']}"
        )
        db.session.add(sender_transaction)
        
        # Add to recipient
        recipient_token.balance += amount
        recipient_transaction = TokenTransaction(
            token_id=recipient_token.id,
            amount=amount,
            transaction_type='credit',
            description=f"Transfer from user #{current_user_id}"
        )
        db.session.add(recipient_transaction)
        
        db.session.commit()
        
        return jsonify({
            "message": "Transfer successful",
            "new_balance": sender_token.balance
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500