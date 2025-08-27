from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from cryptography.fernet import Fernet
import os

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False, index=True)
    wallet_type = db.Column(db.String(20), nullable=False, default='hot')  # 'hot', 'hardware', 'multisig'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Encrypted private key (for hot wallets only)
    encrypted_private_key = db.Column(db.Text)
    
    # Network information
    network = db.Column(db.String(20), nullable=False, default='base-sepolia')  # 'base-sepolia', 'base-mainnet', 'ethereum'
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False)
    derivation_path = db.Column(db.String(100))  # For HD wallets
    
    # Security features
    require_confirmation = db.Column(db.Boolean, default=True)
    spending_limit_daily = db.Column(db.Numeric(20, 8), default=0)  # Daily spending limit in ETH
    last_activity_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('wallets', lazy=True, cascade='all, delete-orphan'))
    transactions = db.relationship('WalletTransaction', back_populates='wallet', cascade='all, delete-orphan')
    balances = db.relationship('WalletBalance', back_populates='wallet', cascade='all, delete-orphan')
    
    def __init__(self, user_id, wallet_address, wallet_type='hot', name=None, network='base-sepolia', 
                 private_key=None, description=None):
        self.user_id = user_id
        self.wallet_address = wallet_address
        self.wallet_type = wallet_type
        self.name = name or f"{wallet_type.title()} Wallet"
        self.network = network
        self.description = description
        
        # Encrypt private key if provided (for hot wallets)
        if private_key and wallet_type == 'hot':
            self.encrypted_private_key = self._encrypt_private_key(private_key)
    
    def _encrypt_private_key(self, private_key: str) -> str:
        """Encrypt private key using system encryption key"""
        encryption_key = os.getenv('WALLET_ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("WALLET_ENCRYPTION_KEY environment variable not set")
        
        fernet = Fernet(encryption_key.encode())
        encrypted_key = fernet.encrypt(private_key.encode())
        return encrypted_key.decode()
    
    def decrypt_private_key(self) -> str:
        """Decrypt private key (use carefully and only when necessary)"""
        if not self.encrypted_private_key or self.wallet_type != 'hot':
            raise ValueError("Cannot decrypt private key for this wallet type")
        
        encryption_key = os.getenv('WALLET_ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("WALLET_ENCRYPTION_KEY environment variable not set")
        
        fernet = Fernet(encryption_key.encode())
        decrypted_key = fernet.decrypt(self.encrypted_private_key.encode())
        return decrypted_key.decode()
    
    def set_as_primary(self):
        """Set this wallet as the primary wallet for the user"""
        # Remove primary status from other wallets
        db.session.query(Wallet).filter_by(user_id=self.user_id, is_primary=True).update({'is_primary': False})
        self.is_primary = True
        db.session.commit()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_private=False):
        balances_dict = {}
        for balance in self.balances:
            balances_dict[balance.token_symbol] = {
                'balance': str(balance.balance),
                'balance_usd': str(balance.balance_usd) if balance.balance_usd else None,
                'last_updated': balance.updated_at.isoformat()
            }
        
        wallet_dict = {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'wallet_type': self.wallet_type,
            'name': self.name,
            'description': self.description,
            'network': self.network,
            'is_active': self.is_active,
            'is_primary': self.is_primary,
            'derivation_path': self.derivation_path,
            'require_confirmation': self.require_confirmation,
            'spending_limit_daily': str(self.spending_limit_daily),
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'created_at': self.created_at.isoformat(),
            'balances': balances_dict,
            'transaction_count': len(self.transactions)
        }
        
        # Only include private key info if explicitly requested and for hot wallets
        if include_private and self.wallet_type == 'hot' and self.encrypted_private_key:
            wallet_dict['has_private_key'] = True
        
        return wallet_dict


class WalletBalance(db.Model):
    __tablename__ = 'wallet_balances'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    token_symbol = db.Column(db.String(10), nullable=False)  # 'ETH', 'NIMO', 'USDC', etc.
    token_address = db.Column(db.String(42))  # Contract address for tokens (null for native ETH)
    token_decimals = db.Column(db.Integer, default=18)
    
    # Balance information
    balance = db.Column(db.Numeric(36, 18), default=0, nullable=False)  # Raw balance
    balance_formatted = db.Column(db.String(50))  # Human-readable balance
    balance_usd = db.Column(db.Numeric(20, 8))  # USD value
    
    # Metadata
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallet = db.relationship('Wallet', back_populates='balances')
    
    # Unique constraint to prevent duplicate token balances per wallet
    __table_args__ = (db.UniqueConstraint('wallet_id', 'token_symbol', 'token_address', name='unique_wallet_token_balance'),)
    
    def __init__(self, wallet_id, token_symbol, token_address=None, token_decimals=18, balance=0):
        self.wallet_id = wallet_id
        self.token_symbol = token_symbol
        self.token_address = token_address
        self.token_decimals = token_decimals
        self.balance = balance
        self.balance_formatted = self._format_balance()
    
    def _format_balance(self) -> str:
        """Format balance for human readability"""
        try:
            # Convert to decimal and format
            balance_decimal = float(self.balance) / (10 ** self.token_decimals)
            
            # Format based on token type
            if self.token_symbol in ['USDC', 'USDT']:
                return f"{balance_decimal:.2f}"
            elif self.token_symbol == 'ETH':
                return f"{balance_decimal:.6f}"
            else:
                return f"{balance_decimal:.4f}"
        except:
            return "0.0000"
    
    def update_balance(self, new_balance, usd_value=None):
        """Update balance and USD value"""
        self.balance = new_balance
        self.balance_formatted = self._format_balance()
        if usd_value is not None:
            self.balance_usd = usd_value
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'token_symbol': self.token_symbol,
            'token_address': self.token_address,
            'token_decimals': self.token_decimals,
            'balance_raw': str(self.balance),
            'balance_formatted': self.balance_formatted,
            'balance_usd': str(self.balance_usd) if self.balance_usd else None,
            'last_updated': self.last_updated.isoformat()
        }


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    
    # Transaction identifiers
    tx_hash = db.Column(db.String(66), unique=True, nullable=False, index=True)
    block_number = db.Column(db.BigInteger)
    transaction_index = db.Column(db.Integer)
    
    # Transaction details
    from_address = db.Column(db.String(42), nullable=False)
    to_address = db.Column(db.String(42), nullable=False)
    value = db.Column(db.Numeric(36, 18), default=0)  # ETH value
    gas_used = db.Column(db.BigInteger)
    gas_price = db.Column(db.BigInteger)
    transaction_fee = db.Column(db.Numeric(36, 18))
    
    # Token information (if token transfer)
    token_symbol = db.Column(db.String(10))
    token_address = db.Column(db.String(42))
    token_amount = db.Column(db.Numeric(36, 18))
    token_decimals = db.Column(db.Integer, default=18)
    
    # Transaction type and status
    transaction_type = db.Column(db.String(20), nullable=False)  # 'send', 'receive', 'contract', 'token_transfer'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'failed'
    
    # Metadata
    nonce = db.Column(db.Integer)
    input_data = db.Column(db.Text)  # Transaction input data
    logs = db.Column(db.Text)  # JSON string of transaction logs
    
    # MeTTa integration
    metta_proof = db.Column(db.Text)  # MeTTa proof if transaction is related to contributions
    contribution_id = db.Column(db.Integer, db.ForeignKey('contributions.id'))
    
    # Timestamps
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    
    # Relationships
    wallet = db.relationship('Wallet', back_populates='transactions')
    
    def __init__(self, wallet_id, tx_hash, from_address, to_address, value=0, 
                 transaction_type='send', timestamp=None, **kwargs):
        self.wallet_id = wallet_id
        self.tx_hash = tx_hash
        self.from_address = from_address
        self.to_address = to_address
        self.value = value
        self.transaction_type = transaction_type
        self.timestamp = timestamp or datetime.utcnow()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_confirmation(self, status, block_number=None, gas_used=None, transaction_fee=None):
        """Update transaction confirmation status"""
        self.status = status
        if block_number:
            self.block_number = block_number
        if gas_used:
            self.gas_used = gas_used
        if transaction_fee:
            self.transaction_fee = transaction_fee
        if status == 'confirmed':
            self.confirmed_at = datetime.utcnow()
        db.session.commit()
    
    def is_incoming(self, wallet_address: str) -> bool:
        """Check if transaction is incoming to the wallet"""
        return self.to_address.lower() == wallet_address.lower()
    
    def is_outgoing(self, wallet_address: str) -> bool:
        """Check if transaction is outgoing from the wallet"""
        return self.from_address.lower() == wallet_address.lower()
    
    def get_direction(self, wallet_address: str) -> str:
        """Get transaction direction relative to wallet"""
        if self.is_incoming(wallet_address):
            return 'in'
        elif self.is_outgoing(wallet_address):
            return 'out'
        else:
            return 'unknown'
    
    def to_dict(self, wallet_address=None):
        # Determine transaction direction
        direction = 'unknown'
        if wallet_address:
            direction = self.get_direction(wallet_address)
        
        return {
            'id': self.id,
            'tx_hash': self.tx_hash,
            'block_number': self.block_number,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'value': str(self.value),
            'gas_used': self.gas_used,
            'gas_price': self.gas_price,
            'transaction_fee': str(self.transaction_fee) if self.transaction_fee else None,
            'token_symbol': self.token_symbol,
            'token_address': self.token_address,
            'token_amount': str(self.token_amount) if self.token_amount else None,
            'transaction_type': self.transaction_type,
            'status': self.status,
            'direction': direction,
            'timestamp': self.timestamp.isoformat(),
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'contribution_id': self.contribution_id,
            'has_metta_proof': bool(self.metta_proof)
        }


class MultisigWallet(db.Model):
    __tablename__ = 'multisig_wallets'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    
    # Multisig configuration
    required_signatures = db.Column(db.Integer, nullable=False, default=2)
    total_owners = db.Column(db.Integer, nullable=False, default=3)
    
    # Contract information
    contract_address = db.Column(db.String(42), unique=True, nullable=False)
    factory_address = db.Column(db.String(42))
    creation_tx_hash = db.Column(db.String(66))
    
    # Status
    is_deployed = db.Column(db.Boolean, default=False)
    deployment_block = db.Column(db.BigInteger)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deployed_at = db.Column(db.DateTime)
    
    # Relationships
    wallet = db.relationship('Wallet', backref=db.backref('multisig_config', uselist=False))
    owners = db.relationship('MultisigOwner', back_populates='multisig_wallet', cascade='all, delete-orphan')
    pending_transactions = db.relationship('MultisigTransaction', back_populates='multisig_wallet', cascade='all, delete-orphan')
    
    def __init__(self, wallet_id, contract_address, required_signatures=2, total_owners=3):
        self.wallet_id = wallet_id
        self.contract_address = contract_address
        self.required_signatures = required_signatures
        self.total_owners = total_owners
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_address': self.contract_address,
            'required_signatures': self.required_signatures,
            'total_owners': self.total_owners,
            'is_deployed': self.is_deployed,
            'deployment_block': self.deployment_block,
            'owners': [owner.to_dict() for owner in self.owners],
            'pending_transactions_count': len(self.pending_transactions)
        }


class MultisigOwner(db.Model):
    __tablename__ = 'multisig_owners'

    id = db.Column(db.Integer, primary_key=True)
    multisig_wallet_id = db.Column(db.Integer, db.ForeignKey('multisig_wallets.id'), nullable=False)
    
    # Owner information
    owner_address = db.Column(db.String(42), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Optional link to Nimo user
    name = db.Column(db.String(100))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    multisig_wallet = db.relationship('MultisigWallet', back_populates='owners')
    user = db.relationship('User', backref='multisig_ownerships')
    
    def to_dict(self):
        return {
            'id': self.id,
            'owner_address': self.owner_address,
            'user_id': self.user_id,
            'name': self.name,
            'is_active': self.is_active,
            'added_at': self.added_at.isoformat()
        }


class MultisigTransaction(db.Model):
    __tablename__ = 'multisig_transactions'

    id = db.Column(db.Integer, primary_key=True)
    multisig_wallet_id = db.Column(db.Integer, db.ForeignKey('multisig_wallets.id'), nullable=False)
    
    # Transaction details
    to_address = db.Column(db.String(42), nullable=False)
    value = db.Column(db.Numeric(36, 18), default=0)
    data = db.Column(db.Text)  # Transaction data
    nonce = db.Column(db.Integer, nullable=False)
    
    # Status
    is_executed = db.Column(db.Boolean, default=False)
    execution_tx_hash = db.Column(db.String(66))
    confirmations_required = db.Column(db.Integer, nullable=False)
    confirmations_count = db.Column(db.Integer, default=0)
    
    # Metadata
    description = db.Column(db.Text)
    created_by = db.Column(db.String(42), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    multisig_wallet = db.relationship('MultisigWallet', back_populates='pending_transactions')
    confirmations = db.relationship('MultisigConfirmation', back_populates='transaction', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'to_address': self.to_address,
            'value': str(self.value),
            'data': self.data,
            'nonce': self.nonce,
            'is_executed': self.is_executed,
            'execution_tx_hash': self.execution_tx_hash,
            'confirmations_required': self.confirmations_required,
            'confirmations_count': self.confirmations_count,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'confirmations': [conf.to_dict() for conf in self.confirmations]
        }


class MultisigConfirmation(db.Model):
    __tablename__ = 'multisig_confirmations'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('multisig_transactions.id'), nullable=False)
    
    # Confirmation details
    owner_address = db.Column(db.String(42), nullable=False)
    signature = db.Column(db.Text, nullable=False)
    
    # Timestamps
    confirmed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transaction = db.relationship('MultisigTransaction', back_populates='confirmations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'owner_address': self.owner_address,
            'signature': self.signature,
            'confirmed_at': self.confirmed_at.isoformat()
        }