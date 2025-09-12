from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Made nullable for wallet users
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # KYC fields
    kyc_status = db.Column(db.String(20), default='pending')  # 'pending', 'in_review', 'approved', 'rejected'
    kyc_submitted_at = db.Column(db.DateTime, nullable=True)
    kyc_verified_at = db.Column(db.DateTime, nullable=True)
    kyc_rejection_reason = db.Column(db.Text, nullable=True)
    
    # Personal information for KYC
    date_of_birth = db.Column(db.Date, nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Document fields
    id_document_type = db.Column(db.String(50), nullable=True)  # 'passport', 'national_id', 'drivers_license'
    id_document_number = db.Column(db.String(100), nullable=True)
    id_document_front_url = db.Column(db.String(500), nullable=True)  # IPFS hash or URL
    id_document_back_url = db.Column(db.String(500), nullable=True)  # IPFS hash or URL
    selfie_url = db.Column(db.String(500), nullable=True)  # IPFS hash or URL
    
    # Address verification
    address_street = db.Column(db.String(200), nullable=True)
    address_city = db.Column(db.String(100), nullable=True)
    address_state = db.Column(db.String(100), nullable=True)
    address_country = db.Column(db.String(100), nullable=True)
    address_postal_code = db.Column(db.String(20), nullable=True)
    address_proof_url = db.Column(db.String(500), nullable=True)  # Utility bill, bank statement, etc.

    # Relationships
    skills = db.relationship('Skill', back_populates='user', cascade='all, delete-orphan')
    contributions = db.relationship('Contribution', back_populates='user', cascade='all, delete-orphan')
    tokens = db.relationship('Token', back_populates='user', uselist=False, cascade='all, delete-orphan')
    created_bonds = db.relationship('Bond', back_populates='creator', foreign_keys='Bond.creator_id')
    investments = db.relationship('BondInvestment', back_populates='investor')

    def __init__(self, email, password=None, name=None, location=None, bio=None, wallet_address=None, auth_method='traditional',
                 date_of_birth=None, nationality=None, phone_number=None):
        self.email = email
        self.name = name
        self.location = location
        self.bio = bio
        self.wallet_address = wallet_address
        self.auth_method = auth_method
        self.date_of_birth = date_of_birth
        self.nationality = nationality
        self.phone_number = phone_number

        if password and auth_method == 'traditional':
            self.password_hash = generate_password_hash(password)
        elif auth_method == 'wallet':
            self.password_hash = None  # Wallet users don't have password hash
            self.is_wallet_verified = True  # Assume verified for now
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def submit_kyc(self, kyc_data):
        """Submit KYC information for verification"""
        self.kyc_status = 'in_review'
        self.kyc_submitted_at = datetime.utcnow()
        
        # Update personal information
        if 'date_of_birth' in kyc_data:
            self.date_of_birth = kyc_data['date_of_birth']
        if 'nationality' in kyc_data:
            self.nationality = kyc_data['nationality']
        if 'phone_number' in kyc_data:
            self.phone_number = kyc_data['phone_number']
        
        # Update document information
        if 'id_document_type' in kyc_data:
            self.id_document_type = kyc_data['id_document_type']
        if 'id_document_number' in kyc_data:
            self.id_document_number = kyc_data['id_document_number']
        if 'id_document_front_url' in kyc_data:
            self.id_document_front_url = kyc_data['id_document_front_url']
        if 'id_document_back_url' in kyc_data:
            self.id_document_back_url = kyc_data['id_document_back_url']
        if 'selfie_url' in kyc_data:
            self.selfie_url = kyc_data['selfie_url']
        
        # Update address information
        if 'address_street' in kyc_data:
            self.address_street = kyc_data['address_street']
        if 'address_city' in kyc_data:
            self.address_city = kyc_data['address_city']
        if 'address_state' in kyc_data:
            self.address_state = kyc_data['address_state']
        if 'address_country' in kyc_data:
            self.address_country = kyc_data['address_country']
        if 'address_postal_code' in kyc_data:
            self.address_postal_code = kyc_data['address_postal_code']
        if 'address_proof_url' in kyc_data:
            self.address_proof_url = kyc_data['address_proof_url']
    
    def approve_kyc(self):
        """Approve KYC verification"""
        self.kyc_status = 'approved'
        self.kyc_verified_at = datetime.utcnow()
        self.kyc_rejection_reason = None
    
    def reject_kyc(self, reason):
        """Reject KYC verification with reason"""
        self.kyc_status = 'rejected'
        self.kyc_rejection_reason = reason
        self.kyc_verified_at = None
    
    def is_kyc_complete(self):
        """Check if KYC is approved"""
        return self.kyc_status == 'approved'
    
    def is_kyc_pending(self):
        """Check if KYC is pending or in review"""
        return self.kyc_status in ['pending', 'in_review']
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'location': self.location,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'skills': [skill.name for skill in self.skills],
            'token_balance': self.tokens.balance if self.tokens else 0,
            'wallet_address': self.wallet_address,
            'auth_method': self.auth_method,
            'is_wallet_verified': self.is_wallet_verified,
            # KYC fields
            'kyc_status': self.kyc_status,
            'kyc_submitted_at': self.kyc_submitted_at.isoformat() if self.kyc_submitted_at else None,
            'kyc_verified_at': self.kyc_verified_at.isoformat() if self.kyc_verified_at else None,
            'kyc_rejection_reason': self.kyc_rejection_reason,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'nationality': self.nationality,
            'phone_number': self.phone_number,
            'id_document_type': self.id_document_type,
            'id_document_number': self.id_document_number,
            'address_country': self.address_country
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