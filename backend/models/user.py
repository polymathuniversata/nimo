from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', back_populates='user', cascade='all, delete-orphan')
    contributions = db.relationship('Contribution', back_populates='user', cascade='all, delete-orphan')
    tokens = db.relationship('Token', back_populates='user', uselist=False, cascade='all, delete-orphan')
    created_bonds = db.relationship('Bond', back_populates='creator', foreign_keys='Bond.creator_id')
    investments = db.relationship('BondInvestment', back_populates='investor')

    def __init__(self, email, password, name, location=None, bio=None):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.location = location
        self.bio = bio
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'location': self.location,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'skills': [skill.name for skill in self.skills],
            'token_balance': self.tokens.balance if self.tokens else 0
        }


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    # Relationship
    user = db.relationship('User', back_populates='skills')
    
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='tokens')
    transactions = db.relationship('TokenTransaction', back_populates='token', cascade='all, delete-orphan')
    
    def __init__(self, user_id, initial_balance=0):
        self.user_id = user_id
        self.balance = initial_balance


class TokenTransaction(db.Model):
    __tablename__ = 'token_transactions'

    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    transaction_type = db.Column(db.String(20), nullable=False)  # 'credit' or 'debit'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    token = db.relationship('Token', back_populates='transactions')
    
    def __init__(self, token_id, amount, transaction_type, description=None):
        self.token_id = token_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description