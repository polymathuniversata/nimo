"""
Blockchain-First Token Service

Handles token operations using blockchain as the primary data source
with database caching for performance optimization.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import current_app

from app import db
from models.user import User, Token, TokenTransaction
from services.blockchain_service import BlockchainService

class BlockchainTokenService:
    """Service for managing tokens on blockchain with database caching"""

    def __init__(self):
        """Initialize blockchain token service"""
        self.blockchain_service = BlockchainService()
        self.cache_enabled = True

    def get_token_balance(self, user_id: int) -> Dict[str, Any]:
        """Get user's token balance from blockchain"""
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                return self._error_response("User not found")

            if not user.wallet_address:
                return self._error_response("User has no wallet address")

            # Get balance from blockchain
            if self.blockchain_service.is_connected():
                balance_result = self.blockchain_service.get_balance(user.wallet_address)

                if balance_result.get('success'):
                    token_balance = balance_result.get('token_balance', 0)

                    # Update cache
                    if self.cache_enabled:
                        self._update_token_cache(user_id, token_balance)

                    return {
                        'success': True,
                        'balance': token_balance,
                        'wallet_address': user.wallet_address,
                        'source': 'blockchain'
                    }

            # Fallback to cache
            if self.cache_enabled and user.tokens:
                return {
                    'success': True,
                    'balance': user.tokens.balance,
                    'wallet_address': user.wallet_address,
                    'source': 'cache'
                }

            return {
                'success': True,
                'balance': 0,
                'wallet_address': user.wallet_address,
                'source': 'default'
            }

        except Exception as e:
            current_app.logger.error(f"Error getting token balance: {e}")
            return self._error_response(str(e))

    def transfer_tokens(self, from_user_id: int, to_user_id: int, amount: int, description: str = None) -> Dict[str, Any]:
        """Transfer tokens between users on blockchain"""
        try:
            # Get users
            from_user = User.query.get(from_user_id)
            to_user = User.query.get(to_user_id)

            if not from_user or not to_user:
                return self._error_response("User not found")

            if not from_user.wallet_address or not to_user.wallet_address:
                return self._error_response("Users must have wallet addresses")

            # Check balance
            balance_result = self.get_token_balance(from_user_id)
            if not balance_result.get('success') or balance_result.get('balance', 0) < amount:
                return self._error_response("Insufficient balance")

            # Perform transfer on blockchain
            transfer_result = self.blockchain_service.send_transaction(
                operation='transfer',
                from_address=from_user.wallet_address,
                to_address=to_user.wallet_address,
                value=amount,
                contract_function=self.blockchain_service.token_contract.functions.transfer(
                    to_user.wallet_address, amount
                ) if self.blockchain_service.token_contract else None
            )

            if not transfer_result.get('success'):
                return transfer_result

            # Update cache
            if self.cache_enabled:
                self._update_token_cache(from_user_id, balance_result['balance'] - amount)
                to_balance_result = self.get_token_balance(to_user_id)
                to_balance = to_balance_result.get('balance', 0) if to_balance_result.get('success') else 0
                self._update_token_cache(to_user_id, to_balance + amount)

                # Record transactions
                self._record_transaction(from_user_id, -amount, 'debit', description or f'Transfer to {to_user.name}')
                self._record_transaction(to_user_id, amount, 'credit', description or f'Transfer from {from_user.name}')

            db.session.commit()

            return {
                'success': True,
                'tx_hash': transfer_result.get('tx_hash'),
                'from_user': from_user_id,
                'to_user': to_user_id,
                'amount': amount,
                'message': 'Tokens transferred successfully'
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error transferring tokens: {e}")
            return self._error_response(str(e))

    def award_tokens_for_contribution(self, user_id: int, contribution_id: int, amount: int, reason: str = None) -> Dict[str, Any]:
        """Award tokens for verified contribution"""
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                return self._error_response("User not found")

            if not user.wallet_address:
                return self._error_response("User has no wallet address")

            # Mint tokens on blockchain
            tx_hash = self.blockchain_service.mint_tokens_for_contribution(
                to_address=user.wallet_address,
                amount=amount,
                reason=reason or f"Contribution verification reward",
                metta_proof=f"contribution-{contribution_id}"
            )

            if not tx_hash:
                return self._error_response("Failed to mint tokens on blockchain")

            # Update cache
            if self.cache_enabled:
                current_balance = self.get_token_balance(user_id).get('balance', 0)
                self._update_token_cache(user_id, current_balance + amount)
                self._record_transaction(user_id, amount, 'credit', reason or f'Contribution reward for ID {contribution_id}')

            db.session.commit()

            return {
                'success': True,
                'tx_hash': tx_hash,
                'user_id': user_id,
                'amount': amount,
                'message': 'Tokens awarded successfully'
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error awarding tokens: {e}")
            return self._error_response(str(e))

    def get_transaction_history(self, user_id: int, limit: int = 50) -> Dict[str, Any]:
        """Get user's token transaction history"""
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                return self._error_response("User not found")

            # Get transactions from cache
            if self.cache_enabled and user.tokens:
                transactions = TokenTransaction.query.filter_by(token_id=user.tokens.id)\
                    .order_by(TokenTransaction.created_at.desc())\
                    .limit(limit)\
                    .all()

                transaction_list = []
                for tx in transactions:
                    transaction_list.append({
                        'id': tx.id,
                        'amount': tx.amount,
                        'description': tx.description,
                        'transaction_type': tx.transaction_type,
                        'created_at': tx.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'transactions': transaction_list,
                    'source': 'cache'
                }

            return {
                'success': True,
                'transactions': [],
                'source': 'none'
            }

        except Exception as e:
            current_app.logger.error(f"Error getting transaction history: {e}")
            return self._error_response(str(e))

    def initialize_user_tokens(self, user_id: int, initial_balance: int = 0) -> Dict[str, Any]:
        """Initialize token balance for new user"""
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                return self._error_response("User not found")

            # Check if tokens already exist
            if user.tokens:
                return {
                    'success': True,
                    'message': 'Tokens already initialized',
                    'balance': user.tokens.balance
                }

            # Create token record
            token = Token(user_id=user_id, balance=initial_balance)
            db.session.add(token)
            db.session.commit()

            return {
                'success': True,
                'balance': initial_balance,
                'message': 'Tokens initialized successfully'
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error initializing user tokens: {e}")
            return self._error_response(str(e))

    def get_token_stats(self) -> Dict[str, Any]:
        """Get overall token statistics"""
        try:
            # Get stats from database
            total_users_with_tokens = Token.query.count()
            total_supply = Token.query.with_entities(db.func.sum(Token.balance)).scalar() or 0

            # Get recent transactions
            recent_transactions = TokenTransaction.query\
                .order_by(TokenTransaction.created_at.desc())\
                .limit(10)\
                .all()

            recent_tx_list = []
            for tx in recent_transactions:
                recent_tx_list.append({
                    'id': tx.id,
                    'amount': tx.amount,
                    'description': tx.description,
                    'transaction_type': tx.transaction_type,
                    'created_at': tx.created_at.isoformat()
                })

            return {
                'success': True,
                'stats': {
                    'total_users_with_tokens': total_users_with_tokens,
                    'total_supply': total_supply,
                    'recent_transactions': recent_tx_list
                }
            }

        except Exception as e:
            current_app.logger.error(f"Error getting token stats: {e}")
            return self._error_response(str(e))

    def _update_token_cache(self, user_id: int, new_balance: int):
        """Update token balance in cache"""
        try:
            user = User.query.get(user_id)
            if user and user.tokens:
                user.tokens.balance = new_balance
                user.tokens.updated_at = datetime.utcnow()
            elif user:
                # Create token record if it doesn't exist
                token = Token(user_id=user_id, balance=new_balance)
                db.session.add(token)
        except Exception as e:
            current_app.logger.warning(f"Error updating token cache: {e}")

    def _record_transaction(self, user_id: int, amount: int, transaction_type: str, description: str):
        """Record token transaction in cache"""
        try:
            user = User.query.get(user_id)
            if user and user.tokens:
                transaction = TokenTransaction(
                    token_id=user.tokens.id,
                    amount=abs(amount),
                    transaction_type=transaction_type,
                    description=description
                )
                db.session.add(transaction)
        except Exception as e:
            current_app.logger.warning(f"Error recording transaction: {e}")

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'success': False,
            'error': message
        }