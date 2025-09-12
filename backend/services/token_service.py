"""
Token Service with OOP Principles

Handles token award logic, balance management, and transaction tracking
using proper object-oriented design with abstraction, encapsulation, and modularity.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from flask import current_app
from app import db
from models.user import Token, TokenTransaction
from models.contribution import Contribution, Verification
from services.blockchain_cache_service import BlockchainCacheService

class ContributionType(Enum):
    """Supported contribution types for token awards"""
    CODING = "coding"
    EDUCATION = "education"
    VOLUNTEER = "volunteer"
    ACTIVISM = "activism"
    LEADERSHIP = "leadership"
    ENTREPRENEURSHIP = "entrepreneurship"
    OTHER = "other"

@dataclass
class TokenAward:
    """Token award calculation result"""
    amount: int
    contribution_type: ContributionType
    multiplier: float
    base_amount: int
    description: str

@dataclass
class TokenBalance:
    """User token balance information"""
    user_id: int
    balance: int
    total_earned: int
    total_spent: int
    last_updated: datetime

class TokenAwardStrategy(ABC):
    """Abstract strategy for calculating token awards"""

    @abstractmethod
    def calculate_award(self, contribution_type: str, contribution_data: Dict[str, Any]) -> TokenAward:
        """Calculate token award for a contribution"""
        pass

class StandardTokenAwardStrategy(TokenAwardStrategy):
    """Standard token award calculation strategy"""

    def __init__(self, base_amount: int = 50):
        self.base_amount = base_amount
        self.multipliers = {
            ContributionType.CODING.value: 1.5,
            ContributionType.EDUCATION.value: 1.2,
            ContributionType.VOLUNTEER.value: 1.0,
            ContributionType.ACTIVISM.value: 1.3,
            ContributionType.LEADERSHIP.value: 1.4,
            ContributionType.ENTREPRENEURSHIP.value: 1.6,
            ContributionType.OTHER.value: 1.0
        }

    def calculate_award(self, contribution_type: str, contribution_data: Dict[str, Any]) -> TokenAward:
        """Calculate token award using standard multipliers"""
        contrib_type = ContributionType(contribution_type or ContributionType.OTHER.value)
        multiplier = self.multipliers.get(contrib_type.value, 1.0)
        amount = int(self.base_amount * multiplier)

        return TokenAward(
            amount=amount,
            contribution_type=contrib_type,
            multiplier=multiplier,
            base_amount=self.base_amount,
            description=f"Award for {contrib_type.value} contribution"
        )

class TokenServiceError(Exception):
    """Base exception for token service errors"""
    def __init__(self, message: str, service: str = "TokenService", operation: str = None):
        self.message = message
        self.service = service
        self.operation = operation
        super().__init__(f"{service}: {message}")

class InsufficientBalanceError(TokenServiceError):
    """Exception raised when user has insufficient token balance"""
    pass

class InvalidContributionError(TokenServiceError):
    """Exception raised when contribution data is invalid"""
    pass

class TokenService:
    """
    Token Service with proper OOP design

    Handles token award logic, balance management, and transaction tracking
    using abstraction, encapsulation, and modularity principles.
    """

    def __init__(self, award_strategy: TokenAwardStrategy = None, cache_service: BlockchainCacheService = None):
        """Initialize token service with dependency injection"""
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.award_strategy = award_strategy or StandardTokenAwardStrategy()
        self.cache_service = cache_service or BlockchainCacheService()
        self.cache_enabled = True

    def award_tokens_for_verification(self, user_id: int, verification_id: int) -> Dict[str, Any]:
        """
        Award tokens to a user when their contribution is verified

        Args:
            user_id: ID of the user to award tokens
            verification_id: ID of the verification

        Returns:
            Dictionary with award details

        Raises:
            TokenServiceError: If token award fails
        """
        try:
            # Validate inputs
            if not user_id or not verification_id:
                raise InvalidContributionError("User ID and verification ID are required")

            # Get or create token record
            token = self._get_or_create_token_record(user_id)

            # Get verification and contribution data
            verification = Verification.query.get(verification_id)
            if not verification:
                raise InvalidContributionError("Verification not found")

            contribution = Contribution.query.get(verification.contribution_id)
            if not contribution:
                raise InvalidContributionError("Contribution not found")

            # Calculate token award
            award = self.award_strategy.calculate_award(
                contribution.contribution_type,
                contribution.to_dict() if hasattr(contribution, 'to_dict') else {}
            )

            # Update token balance
            old_balance = token.balance
            token.balance += award.amount

            # Record the transaction
            transaction = TokenTransaction(
                token_id=token.id,
                amount=award.amount,
                transaction_type='credit',
                description=f"Award for verified contribution: {contribution.title}"
            )

            db.session.add(transaction)
            db.session.commit()

            # Invalidate cache
            self._invalidate_user_cache(user_id)

            self.logger.info(f"Awarded {award.amount} tokens to user {user_id} for contribution {contribution.id}")

            return {
                'success': True,
                'user_id': user_id,
                'award_amount': award.amount,
                'new_balance': token.balance,
                'old_balance': old_balance,
                'contribution_type': award.contribution_type.value,
                'description': award.description
            }

        except TokenServiceError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error awarding tokens: {e}")
            raise TokenServiceError(f"Failed to award tokens: {str(e)}", operation="award_tokens")

    def get_token_balance(self, user_id: int) -> TokenBalance:
        """
        Get user's token balance with caching

        Args:
            user_id: ID of the user

        Returns:
            TokenBalance object with balance information
        """
        try:
            # Try cache first
            if self.cache_enabled:
                cached_balance = self.cache_service.get_token_balance(user_id)
                if cached_balance:
                    return TokenBalance(**cached_balance)

            # Get from database
            token = Token.query.filter_by(user_id=user_id).first()
            if not token:
                # Return zero balance for new users
                balance = TokenBalance(
                    user_id=user_id,
                    balance=0,
                    total_earned=0,
                    total_spent=0,
                    last_updated=datetime.utcnow()
                )
            else:
                # Calculate totals from transactions
                total_earned = db.session.query(db.func.sum(TokenTransaction.amount))\
                    .filter_by(token_id=token.id, transaction_type='credit').scalar() or 0
                total_spent = db.session.query(db.func.sum(TokenTransaction.amount))\
                    .filter_by(token_id=token.id, transaction_type='debit').scalar() or 0

                balance = TokenBalance(
                    user_id=user_id,
                    balance=token.balance,
                    total_earned=total_earned,
                    total_spent=total_spent,
                    last_updated=datetime.utcnow()
                )

            # Cache the result
            if self.cache_enabled:
                self.cache_service.set_token_balance(user_id, balance.__dict__)

            return balance

        except Exception as e:
            self.logger.error(f"Error getting token balance: {e}")
            raise TokenServiceError(f"Failed to get token balance: {str(e)}", operation="get_balance")

    def transfer_tokens(self, from_user_id: int, to_user_id: int, amount: int, description: str = None) -> Dict[str, Any]:
        """
        Transfer tokens between users

        Args:
            from_user_id: ID of sender
            to_user_id: ID of receiver
            amount: Amount to transfer
            description: Optional transfer description

        Returns:
            Dictionary with transfer details

        Raises:
            InsufficientBalanceError: If sender has insufficient balance
        """
        try:
            if amount <= 0:
                raise TokenServiceError("Transfer amount must be positive")

            # Get token records
            from_token = self._get_or_create_token_record(from_user_id)
            to_token = self._get_or_create_token_record(to_user_id)

            # Check balance
            if from_token.balance < amount:
                raise InsufficientBalanceError(f"Insufficient balance: {from_token.balance} < {amount}")

            # Perform transfer
            from_token.balance -= amount
            to_token.balance += amount

            # Record transactions
            debit_tx = TokenTransaction(
                token_id=from_token.id,
                amount=-amount,
                transaction_type='debit',
                description=description or f"Transfer to user {to_user_id}"
            )

            credit_tx = TokenTransaction(
                token_id=to_token.id,
                amount=amount,
                transaction_type='credit',
                description=description or f"Transfer from user {from_user_id}"
            )

            db.session.add(debit_tx)
            db.session.add(credit_tx)
            db.session.commit()

            # Invalidate caches
            self._invalidate_user_cache(from_user_id)
            self._invalidate_user_cache(to_user_id)

            self.logger.info(f"Transferred {amount} tokens from user {from_user_id} to user {to_user_id}")

            return {
                'success': True,
                'from_user_id': from_user_id,
                'to_user_id': to_user_id,
                'amount': amount,
                'from_balance': from_token.balance,
                'to_balance': to_token.balance
            }

        except (InsufficientBalanceError, TokenServiceError):
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error transferring tokens: {e}")
            raise TokenServiceError(f"Failed to transfer tokens: {str(e)}", operation="transfer")

    def get_transaction_history(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get user's token transaction history

        Args:
            user_id: ID of the user
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip

        Returns:
            List of transaction dictionaries
        """
        try:
            # Try cache first
            if self.cache_enabled:
                cached_history = self.cache_service.get_transaction_history(user_id, limit)
                if cached_history:
                    return cached_history

            # Get token record
            token = Token.query.filter_by(user_id=user_id).first()
            if not token:
                return []

            # Get transactions
            transactions = TokenTransaction.query\
                .filter_by(token_id=token.id)\
                .order_by(TokenTransaction.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()

            # Convert to dictionaries
            history = []
            for tx in transactions:
                history.append({
                    'id': tx.id,
                    'amount': tx.amount,
                    'transaction_type': tx.transaction_type,
                    'description': tx.description,
                    'created_at': tx.created_at.isoformat() if tx.created_at else None
                })

            # Cache the result
            if self.cache_enabled:
                self.cache_service.set_transaction_history(user_id, history, limit)

            return history

        except Exception as e:
            self.logger.error(f"Error getting transaction history: {e}")
            raise TokenServiceError(f"Failed to get transaction history: {str(e)}", operation="get_history")

    def _get_or_create_token_record(self, user_id: int) -> Token:
        """Get existing token record or create new one"""
        token = Token.query.filter_by(user_id=user_id).first()
        if not token:
            token = Token(user_id=user_id, balance=0)
            db.session.add(token)
            db.session.flush()  # Get the ID without committing
        return token

    def _invalidate_user_cache(self, user_id: int):
        """Invalidate all caches for a user"""
        if self.cache_enabled:
            try:
                self.cache_service.invalidate_token_balance(user_id)
                self.cache_service.invalidate_transaction_history(user_id)
            except Exception as e:
                self.logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and statistics"""
        try:
            total_users = Token.query.count()
            total_supply = db.session.query(db.func.sum(Token.balance)).scalar() or 0

            return {
                'service': 'TokenService',
                'total_users': total_users,
                'total_supply': total_supply,
                'cache_enabled': self.cache_enabled,
                'award_strategy': self.award_strategy.__class__.__name__
            }

        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return {
                'service': 'TokenService',
                'error': str(e)
            }

# Factory function for creating token service instances
def create_token_service(award_strategy: TokenAwardStrategy = None, cache_service: BlockchainCacheService = None) -> TokenService:
    """Factory function to create TokenService with dependencies"""
    return TokenService(award_strategy, cache_service)

# Singleton instance for backward compatibility
_token_service_instance = None

def get_token_service() -> TokenService:
    """Get singleton token service instance (for backward compatibility)"""
    global _token_service_instance
    if _token_service_instance is None:
        _token_service_instance = TokenService()
    return _token_service_instance

# Backward compatibility functions
def award_tokens_for_verification(user_id, verification_id):
    """Backward compatibility wrapper"""
    service = get_token_service()
    return service.award_tokens_for_verification(user_id, verification_id)

def calculate_token_award(contribution_type):
    """Backward compatibility wrapper"""
    strategy = StandardTokenAwardStrategy()
    award = strategy.calculate_award(contribution_type, {})
    return award.amount