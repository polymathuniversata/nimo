from app import db
from datetime import datetime

class BlockchainTransaction(db.Model):
    __tablename__ = 'blockchain_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contribution_id = db.Column(db.Integer, db.ForeignKey('contributions.id'))
    tx_hash = db.Column(db.String(128), unique=True, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # contribution, identity, token, bond, verification, token_mint
    tx_type = db.Column(db.String(50), nullable=False)  # legacy alias for transaction_type
    reference_id = db.Column(db.Integer)  # ID of the related object
    data = db.Column(db.Text)  # JSON data
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    
    def __init__(self, tx_hash, transaction_type=None, tx_type=None, user_id=None, contribution_id=None, reference_id=None, data=None):
        self.tx_hash = tx_hash
        # Use transaction_type if provided, otherwise fall back to tx_type
        self.transaction_type = transaction_type or tx_type or 'unknown'
        self.tx_type = self.transaction_type  # Keep legacy field in sync
        self.user_id = user_id
        self.contribution_id = contribution_id
        self.reference_id = reference_id
        self.data = data
    
    def confirm(self):
        self.status = 'confirmed'
        self.confirmed_at = datetime.utcnow()
    
    def fail(self):
        self.status = 'failed'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tx_hash': self.tx_hash,
            'tx_type': self.tx_type,
            'reference_id': self.reference_id,
            'data': self.data,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }

class Bond(db.Model):
    __tablename__ = 'bonds'

    id = db.Column(db.Integer, primary_key=True)
    bond_id = db.Column(db.String(50), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cause = db.Column(db.String(50))  # e.g. climate, education, economic-empowerment
    value = db.Column(db.Integer, nullable=False)  # Total value in tokens
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    # Relationships
    creator = db.relationship('User', back_populates='created_bonds', foreign_keys=[creator_id])
    milestones = db.relationship('BondMilestone', back_populates='bond', cascade='all, delete-orphan')
    investments = db.relationship('BondInvestment', back_populates='bond', cascade='all, delete-orphan')
    
    def __init__(self, bond_id, creator_id, title, value, description=None, cause=None, image_url=None):
        self.bond_id = bond_id
        self.creator_id = creator_id
        self.title = title
        self.description = description
        self.cause = cause
        self.value = value
        self.image_url = image_url
    
    def to_dict(self):
        total_investment = sum([i.amount for i in self.investments])
        verified_milestones = sum(1 for m in self.milestones if m.is_verified)
        
        return {
            'id': self.id,
            'bond_id': self.bond_id,
            'creator_id': self.creator_id,
            'creator_name': self.creator.name,
            'title': self.title,
            'description': self.description,
            'cause': self.cause,
            'value': self.value,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'total_investment': total_investment,
            'funding_percentage': (total_investment / self.value * 100) if self.value > 0 else 0,
            'milestone_count': len(self.milestones),
            'verified_milestones': verified_milestones,
            'progress_percentage': (verified_milestones / len(self.milestones) * 100) if len(self.milestones) > 0 else 0
        }


class BondMilestone(db.Model):
    __tablename__ = 'bond_milestones'

    id = db.Column(db.Integer, primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bonds.id'), nullable=False)
    milestone = db.Column(db.String(200), nullable=False)
    evidence = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String(100))
    verified_at = db.Column(db.DateTime)
    
    # Relationship
    bond = db.relationship('Bond', back_populates='milestones')
    
    def __init__(self, bond_id, milestone, evidence=None):
        self.bond_id = bond_id
        self.milestone = milestone
        self.evidence = evidence
    
    def verify(self, verifier):
        self.is_verified = True
        self.verified_by = verifier
        self.verified_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'bond_id': self.bond_id,
            'milestone': self.milestone,
            'evidence': self.evidence,
            'created_at': self.created_at.isoformat(),
            'is_verified': self.is_verified,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }


class BondInvestment(db.Model):
    __tablename__ = 'bond_investments'

    id = db.Column(db.Integer, primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bonds.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bond = db.relationship('Bond', back_populates='investments')
    investor = db.relationship('User', back_populates='investments')
    
    def __init__(self, bond_id, investor_id, amount):
        self.bond_id = bond_id
        self.investor_id = investor_id
        self.amount = amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'bond_id': self.bond_id,
            'bond_title': self.bond.title,
            'investor_id': self.investor_id,
            'investor_name': self.investor.name,
            'amount': self.amount,
            'created_at': self.created_at.isoformat()
        }