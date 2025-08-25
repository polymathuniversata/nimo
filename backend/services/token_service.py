from app import db
from models.user import Token, TokenTransaction
from models.contribution import Contribution, Verification

def award_tokens_for_verification(user_id, verification_id):
    """Award tokens to a user when their contribution is verified"""
    # Get the token record for the user
    token = Token.query.filter_by(user_id=user_id).first()
    
    if not token:
        # Initialize token record if it doesn't exist
        token = Token(user_id=user_id, initial_balance=0)
        db.session.add(token)
        db.session.flush()
    
    # Get the verification
    verification = Verification.query.get(verification_id)
    if not verification:
        raise ValueError("Verification not found")
    
    # Get the contribution
    contribution = Contribution.query.get(verification.contribution_id)
    if not contribution:
        raise ValueError("Contribution not found")
    
    # Determine token amount based on contribution type
    token_amount = calculate_token_award(contribution.contribution_type)
    
    # Update token balance
    token.balance += token_amount
    
    # Record the transaction
    transaction = TokenTransaction(
        token_id=token.id,
        amount=token_amount,
        transaction_type='credit',
        description=f"Award for verified contribution: {contribution.title}"
    )
    db.session.add(transaction)
    
    return token_amount


def calculate_token_award(contribution_type):
    """Calculate token award amount based on contribution type"""
    # Default award amount
    base_amount = 50
    
    # Multipliers for different contribution types
    multipliers = {
        'coding': 1.5,
        'education': 1.2,
        'volunteer': 1.0,
        'activism': 1.3,
        'leadership': 1.4,
        'entrepreneurship': 1.6
    }
    
    # Apply multiplier if contribution type is known
    multiplier = multipliers.get(contribution_type, 1.0) if contribution_type else 1.0
    
    return int(base_amount * multiplier)