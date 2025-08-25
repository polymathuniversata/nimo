from app import db

# Import all models to make them available for migrations
from models.user import User, Skill, Token, TokenTransaction
from models.contribution import Contribution, Verification
from models.bond import Bond, BondMilestone, BondInvestment

# Initialize models module
__all__ = [
    'User', 'Skill', 'Token', 'TokenTransaction',
    'Contribution', 'Verification',
    'Bond', 'BondMilestone', 'BondInvestment'
]