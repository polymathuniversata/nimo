"""
Blockchain-First User Service with Enhanced OOP Design

Handles user management operations using blockchain as the primary data source
with database caching for performance optimization. Implements proper OOP principles
with abstraction, encapsulation, inheritance, and modularity.
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from flask import current_app
from app import db
from models.user import User, Skill
from services.base_blockchain_service import BaseBlockchainService, BlockchainType, BlockchainServiceError
from services.blockchain_service import BlockchainService
from services.ipfs_service import IPFSService
from services.blockchain_cache_service import BlockchainCacheService

class UserVerificationStatus(Enum):
    """User verification status on blockchain"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"

@dataclass
class UserProfile:
    """Complete user profile data structure"""
    user_id: int
    email: str
    name: str
    location: Optional[str]
    bio: Optional[str]
    skills: List[str]
    wallet_address: Optional[str]
    blockchain_verified: bool
    on_chain_reputation: int
    token_balance: int
    contribution_count: int
    verification_rate: float

@dataclass
class UserCreationResult:
    """Result of user creation operation"""
    success: bool
    user_id: Optional[int]
    tx_hash: Optional[str]
    ipfs_hash: Optional[str]
    error: Optional[str]

class BlockchainUserServiceError(BlockchainServiceError):
    """Base exception for blockchain user service errors"""
    def __init__(self, message: str, operation: str = None, user_id: int = None):
        self.user_id = user_id
        super().__init__(message, "BlockchainUserService", operation)

class UserNotFoundError(BlockchainUserServiceError):
    """Exception raised when user is not found"""
    pass

class UserAlreadyExistsError(BlockchainUserServiceError):
    """Exception raised when user already exists"""
    pass

class BlockchainUserService(BaseBlockchainService):
    """
    Enhanced Blockchain-First User Service

    Inherits from BaseBlockchainService and implements proper OOP design
    with abstraction, encapsulation, and modularity for user management operations.
    """

    def __init__(self, network: str = "mainnet", blockchain_type: BlockchainType = BlockchainType.ETHEREUM):
        """Initialize blockchain user service with proper inheritance"""
        # Initialize service dependencies first
        self._blockchain_service = BlockchainService()
        self._ipfs_service = IPFSService()
        self._cache_service = BlockchainCacheService()
        self._cache_enabled = True

        # Service configuration
        self._max_skills_per_user = 10
        self._profile_cache_ttl = 600  # 10 minutes
        
        # Call parent initialization after dependencies are set up
        super().__init__(network, blockchain_type)

    def _initialize_service(self):
        """Initialize blockchain-specific service components"""
        self.logger.info(f"Initializing BlockchainUserService for {self.network} network")

        # Validate dependencies
        if not self._blockchain_service:
            raise BlockchainUserServiceError("Blockchain service not available")

        if not self._ipfs_service:
            self.logger.warning("IPFS service not available - metadata storage disabled")

    def is_connected(self) -> bool:
        """Check if connected to blockchain network"""
        try:
            return self._blockchain_service.is_connected()
        except Exception as e:
            self.logger.error(f"Connection check failed: {e}")
            return False

    def get_transaction_status(self, tx_hash: str):
        """Get status of a transaction"""
        return self._blockchain_service.get_transaction_status(tx_hash)

    def get_network_info(self):
        """Get current network information"""
        return self._blockchain_service.get_network_info()

    def estimate_transaction_cost(self, operation: str, params: Dict = None):
        """Estimate transaction cost for an operation"""
        return self._blockchain_service.estimate_transaction_cost(operation, params)

    def get_balance(self, address: str):
        """Get balance for an address"""
        return self._blockchain_service.get_balance(address)

    def send_transaction(self, **kwargs):
        """Send a transaction (implementation-specific)"""
        return self._blockchain_service.send_transaction(**kwargs)

    def create_user_on_chain(self, user_data: Dict[str, Any]) -> UserCreationResult:
        """
        Create user identity on blockchain with proper error handling

        Args:
            user_data: User data dictionary

        Returns:
            UserCreationResult with operation outcome

        Raises:
            BlockchainUserServiceError: If user creation fails
        """
        try:
            # Validate required fields
            self._validate_user_data(user_data)

            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                raise UserAlreadyExistsError("User already exists", user_id=existing_user.id)

            # Prepare user metadata for IPFS
            metadata = self._prepare_user_metadata(user_data)

            # Store metadata on IPFS
            ipfs_hash = self._ipfs_service.store_json(metadata)
            if not ipfs_hash:
                raise BlockchainUserServiceError("Failed to store user metadata on IPFS")

            # Create identity on blockchain
            username = self._generate_username(user_data['email'])
            tx_result = self._blockchain_service.create_identity_on_chain(
                username=username,
                metadata_uri=f"ipfs://{ipfs_hash}"
            )

            if not tx_result or not tx_result.get('success'):
                raise BlockchainUserServiceError("Failed to create identity on blockchain")

            # Create local cache record
            new_user = self._create_local_user_record(user_data)

            # Track transaction
            self._track_transaction(tx_result.get('tx_hash'), 'create_user', user_data)

            self.logger.info(f"User created successfully: {new_user.id}, tx: {tx_result.get('tx_hash')}")

            return UserCreationResult(
                success=True,
                user_id=new_user.id,
                tx_hash=tx_result.get('tx_hash'),
                ipfs_hash=ipfs_hash,
                error=None
            )

        except BlockchainUserServiceError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating user on chain: {e}")
            raise BlockchainUserServiceError(f"User creation failed: {str(e)}", operation="create_user")

    def get_user_from_chain(self, user_id: int) -> Dict[str, Any]:
        """
        Get user data from blockchain with database cache

        Args:
            user_id: User ID to retrieve

        Returns:
            Dictionary with user data or error response
        """
        try:
            # Try database cache first
            if self._cache_enabled:
                user = User.query.get(user_id)
                if user:
                    return self._format_success_response(user.to_dict(), source='cache')

            # Fallback to blockchain (would need username mapping)
            raise UserNotFoundError("User not found in cache", user_id=user_id)

        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting user from chain: {e}")
            raise BlockchainUserServiceError(f"Failed to get user: {str(e)}", operation="get_user", user_id=user_id)

    def update_user_on_chain(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user data on blockchain with proper validation

        Args:
            user_id: User ID to update
            update_data: Updated user data

        Returns:
            Dictionary with update result
        """
        try:
            # Get existing user
            user = User.query.get(user_id)
            if not user:
                raise UserNotFoundError("User not found", user_id=user_id)

            # Validate update data
            self._validate_update_data(update_data)

            # Update local cache first
            self._update_local_user_record(user, update_data)

            # Prepare updated metadata
            metadata = self._prepare_user_metadata_from_user(user)

            # Store updated metadata on IPFS
            ipfs_hash = self._ipfs_service.store_json(metadata)
            if not ipfs_hash:
                raise BlockchainUserServiceError("Failed to store updated metadata on IPFS")

            # Update identity on blockchain (if supported by contract)
            db.session.commit()

            # Invalidate cache
            self._invalidate_user_cache(user_id)

            self.logger.info(f"User updated successfully: {user_id}")

            return self._format_success_response({
                'user_id': user_id,
                'ipfs_hash': ipfs_hash,
                'message': 'User updated successfully'
            })

        except (UserNotFoundError, BlockchainUserServiceError):
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating user on chain: {e}")
            raise BlockchainUserServiceError(f"User update failed: {str(e)}", operation="update_user", user_id=user_id)

    def get_user_profile(self, user_id: int) -> UserProfile:
        """
        Get complete user profile with blockchain verification

        Args:
            user_id: User ID to retrieve profile for

        Returns:
            UserProfile object with complete profile data
        """
        try:
            # Try cache first
            if self._cache_enabled:
                cached_profile = self._cache_service.get_user_profile(user_id)
                if cached_profile:
                    return UserProfile(**cached_profile)

            user = User.query.get(user_id)
            if not user:
                raise UserNotFoundError("User not found", user_id=user_id)

            # Get blockchain verification status
            blockchain_status = self._get_blockchain_verification_status(user)

            # Get token balance
            token_balance = self._get_user_token_balance(user_id)

            # Get contribution statistics
            contribution_stats = self._get_user_contribution_stats(user_id)

            # Build complete profile
            profile = UserProfile(
                user_id=user_id,
                email=user.email,
                name=user.name,
                location=user.location,
                bio=user.bio,
                skills=[skill.name for skill in user.skills],
                wallet_address=user.wallet_address,
                blockchain_verified=blockchain_status['verified'],
                on_chain_reputation=blockchain_status['reputation'],
                token_balance=token_balance,
                contribution_count=contribution_stats['total'],
                verification_rate=contribution_stats['rate']
            )

            # Cache the profile
            if self._cache_enabled:
                self._cache_service.set_user_profile(user_id, profile.__dict__, self._profile_cache_ttl)

            return profile

        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting user profile: {e}")
            raise BlockchainUserServiceError(f"Failed to get profile: {str(e)}", operation="get_profile", user_id=user_id)

    def verify_wallet_connection(self, user_id: int, wallet_address: str) -> Dict[str, Any]:
        """
        Verify and connect wallet to user account

        Args:
            user_id: User ID to connect wallet to
            wallet_address: Wallet address to connect

        Returns:
            Dictionary with verification result
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise UserNotFoundError("User not found", user_id=user_id)

            # Validate wallet address format
            if not self.validate_address(wallet_address):
                raise BlockchainUserServiceError("Invalid wallet address format")

            # Update wallet address
            user.wallet_address = wallet_address
            user.is_wallet_verified = True

            db.session.commit()

            # Invalidate cache
            self._invalidate_user_cache(user_id)

            self.logger.info(f"Wallet connected successfully: {user_id} -> {wallet_address}")

            return self._format_success_response({
                'message': 'Wallet connected successfully',
                'wallet_address': wallet_address
            })

        except (UserNotFoundError, BlockchainUserServiceError):
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error verifying wallet connection: {e}")
            raise BlockchainUserServiceError(f"Wallet verification failed: {str(e)}", operation="verify_wallet", user_id=user_id)

    def get_user_contributions_count(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's contribution statistics

        Args:
            user_id: User ID to get statistics for

        Returns:
            Dictionary with contribution statistics
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise UserNotFoundError("User not found", user_id=user_id)

            stats = self._get_user_contribution_stats(user_id)

            return self._format_success_response({
                'stats': stats
            })

        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting user contributions count: {e}")
            raise BlockchainUserServiceError(f"Failed to get contribution stats: {str(e)}", operation="get_contributions", user_id=user_id)

    def get_user_token_balance(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's token balance from blockchain

        Args:
            user_id: User ID to get balance for

        Returns:
            Dictionary with balance information
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise UserNotFoundError("User not found", user_id=user_id)

            # Try cache first
            if self._cache_enabled:
                cached_balance = self._cache_service.get_token_balance(user_id)
                if cached_balance:
                    return self._format_success_response(cached_balance, source='cache')

            # Get balance from blockchain or database
            balance_data = self._get_user_balance_data(user)

            # Cache the balance
            if self._cache_enabled:
                self._cache_service.set_token_balance(user_id, balance_data)

            return self._format_success_response(balance_data, source='blockchain')

        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting user token balance: {e}")
            raise BlockchainUserServiceError(f"Failed to get token balance: {str(e)}", operation="get_balance", user_id=user_id)

    # Private helper methods for encapsulation
    def _validate_user_data(self, user_data: Dict[str, Any]):
        """Validate user data for creation"""
        if not user_data.get('email'):
            raise BlockchainUserServiceError("Email is required")
        if not user_data.get('name'):
            raise BlockchainUserServiceError("Name is required")

        # Validate email format
        if '@' not in user_data['email']:
            raise BlockchainUserServiceError("Invalid email format")

        # Validate skills limit
        skills = user_data.get('skills', [])
        if len(skills) > self._max_skills_per_user:
            raise BlockchainUserServiceError(f"Too many skills: maximum {self._max_skills_per_user} allowed")

    def _validate_update_data(self, update_data: Dict[str, Any]):
        """Validate user update data"""
        allowed_fields = {'name', 'location', 'bio', 'skills'}
        for field in update_data:
            if field not in allowed_fields:
                raise BlockchainUserServiceError(f"Invalid update field: {field}")

        # Validate skills limit
        if 'skills' in update_data and len(update_data['skills']) > self._max_skills_per_user:
            raise BlockchainUserServiceError(f"Too many skills: maximum {self._max_skills_per_user} allowed")

    def _prepare_user_metadata(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare user metadata for IPFS storage"""
        return {
            'email': user_data['email'],
            'name': user_data['name'],
            'location': user_data.get('location'),
            'bio': user_data.get('bio'),
            'skills': user_data.get('skills', []),
            'created_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }

    def _prepare_user_metadata_from_user(self, user: User) -> Dict[str, Any]:
        """Prepare user metadata from User model"""
        return {
            'email': user.email,
            'name': user.name,
            'location': user.location,
            'bio': user.bio,
            'skills': [skill.name for skill in user.skills],
            'updated_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }

    def _generate_username(self, email: str) -> str:
        """Generate username from email"""
        return email.split('@')[0]

    def _create_local_user_record(self, user_data: Dict[str, Any]) -> User:
        """Create local user record in database"""
        new_user = User(
            email=user_data['email'],
            name=user_data['name'],
            location=user_data.get('location'),
            bio=user_data.get('bio'),
            wallet_address=user_data.get('wallet_address')
        )

        # Add skills
        for skill_name in user_data.get('skills', []):
            skill = Skill(user_id=new_user.id, name=skill_name)
            new_user.skills.append(skill)

        db.session.add(new_user)
        db.session.commit()

        return new_user

    def _update_local_user_record(self, user: User, update_data: Dict[str, Any]):
        """Update local user record"""
        if 'name' in update_data:
            user.name = update_data['name']
        if 'location' in update_data:
            user.location = update_data['location']
        if 'bio' in update_data:
            user.bio = update_data['bio']

        # Update skills if provided
        if 'skills' in update_data:
            # Remove existing skills
            Skill.query.filter_by(user_id=user.id).delete()

            # Add new skills
            for skill_name in update_data['skills']:
                skill = Skill(user_id=user.id, name=skill_name)
                db.session.add(skill)

    def _get_blockchain_verification_status(self, user: User) -> Dict[str, Any]:
        """Get blockchain verification status for user"""
        if not user.wallet_address or not self.is_connected():
            return {'verified': False, 'reputation': 0}

        try:
            # Get identity from blockchain
            username = user.email.split('@')[0]
            identity_data = self._blockchain_service.get_identity_from_chain(username)

            if identity_data:
                return {
                    'verified': identity_data.get('is_active', False),
                    'reputation': identity_data.get('reputation_score', 0)
                }

        except Exception as e:
            self.logger.warning(f"Could not get blockchain identity: {e}")

        return {'verified': False, 'reputation': 0}

    def _get_user_token_balance(self, user_id: int) -> int:
        """Get user's token balance"""
        try:
            from services.token_service import get_token_service
            token_service = get_token_service()
            balance_info = token_service.get_token_balance(user_id)
            return balance_info.balance
        except Exception as e:
            self.logger.warning(f"Could not get token balance: {e}")
            return 0

    def _get_user_contribution_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user's contribution statistics"""
        try:
            from models.contribution import Contribution

            total_contributions = Contribution.query.filter_by(user_id=user_id).count()
            verified_contributions = Contribution.query.filter_by(user_id=user_id)\
                .filter(Contribution.verifications.any()).count()

            return {
                'total': total_contributions,
                'verified': verified_contributions,
                'rate': (verified_contributions / total_contributions) if total_contributions > 0 else 0
            }

        except Exception as e:
            self.logger.warning(f"Could not get contribution stats: {e}")
            return {'total': 0, 'verified': 0, 'rate': 0}

    def _get_user_balance_data(self, user: User) -> Dict[str, Any]:
        """Get user's balance data from blockchain or database"""
        if user.wallet_address and self.is_connected():
            balance_result = self.get_balance(user.wallet_address)

            if balance_result.get('success'):
                return {
                    'address': user.wallet_address,
                    'token_balance': balance_result.get('token_balance', 0),
                    'eth_balance': balance_result.get('balance_eth', 0),
                    'source': 'blockchain'
                }

        # Fallback to database cache
        if user.tokens:
            return {
                'address': user.wallet_address,
                'token_balance': user.tokens.balance,
                'source': 'database'
            }

        return {
            'address': user.wallet_address,
            'token_balance': 0,
            'source': 'default'
        }

    def _invalidate_user_cache(self, user_id: int):
        """Invalidate all caches for a user"""
        if self._cache_enabled:
            try:
                self._cache_service.invalidate_user_profile(user_id)
                self._cache_service.invalidate_token_balance(user_id)
            except Exception as e:
                self.logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")

    def _format_success_response(self, data: Any, source: str = None) -> Dict[str, Any]:
        """Format successful response"""
        response = {
            'success': True,
            **(data if isinstance(data, dict) else {'data': data})
        }
        if source:
            response['source'] = source
        return response

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'success': False,
            'error': message
        }