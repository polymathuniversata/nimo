"""
Wallet Service for Nimo Platform

This service provides comprehensive wallet management functionality including:
- Wallet creation, import, and export
- Balance tracking and updates
- Transaction management
- Multi-signature wallet support
- Hardware wallet integration
- Security features and validation
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Union
from decimal import Decimal
from datetime import datetime, timedelta
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from mnemonic import Mnemonic
import requests
from flask import current_app

from models.wallet import (
    Wallet, WalletBalance, WalletTransaction, 
    MultisigWallet, MultisigOwner, MultisigTransaction, MultisigConfirmation
)
from models.user import User
from services.blockchain_service import BlockchainService
from app import db

class WalletService:
    def __init__(self, blockchain_service: BlockchainService):
        self.blockchain_service = blockchain_service
        self.web3 = blockchain_service.web3
        
        # Price API configuration
        self.price_api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.price_cache = {}
        self.price_cache_timeout = 300  # 5 minutes
        
        # Token configurations for different networks
        self.token_configs = {
            'base-sepolia': {
                'NIMO': {
                    'address': os.getenv('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA'),
                    'decimals': 18,
                    'coingecko_id': None  # Custom token, no CoinGecko ID
                },
                'USDC': {
                    'address': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',  # Base Sepolia USDC
                    'decimals': 6,
                    'coingecko_id': 'usd-coin'
                }
            },
            'base-mainnet': {
                'NIMO': {
                    'address': os.getenv('NIMO_TOKEN_CONTRACT_BASE_MAINNET'),
                    'decimals': 18,
                    'coingecko_id': None
                },
                'USDC': {
                    'address': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  # Base Mainnet USDC
                    'decimals': 6,
                    'coingecko_id': 'usd-coin'
                }
            }
        }
        
        # Initialize mnemonic generator
        self.mnemonic = Mnemonic("english")
    
    # Wallet Creation and Management
    
    def create_hot_wallet(self, user_id: int, name: str = None, network: str = 'base-sepolia', 
                         mnemonic_phrase: str = None) -> Dict[str, any]:
        """
        Create a new hot wallet for a user
        
        Args:
            user_id: User ID
            name: Wallet name
            network: Blockchain network
            mnemonic_phrase: Optional mnemonic phrase (if not provided, generates new one)
            
        Returns:
            Dict with wallet information and mnemonic phrase
        """
        try:
            # Generate mnemonic and derive account
            if not mnemonic_phrase:
                mnemonic_phrase = self.mnemonic.generate(strength=128)  # 12 words
            
            # Validate mnemonic
            if not self.mnemonic.check(mnemonic_phrase):
                raise ValueError("Invalid mnemonic phrase")
            
            # Derive account from mnemonic
            account = Account.from_mnemonic(mnemonic_phrase)
            
            # Check if wallet already exists
            existing_wallet = Wallet.query.filter_by(
                user_id=user_id, 
                wallet_address=account.address
            ).first()
            
            if existing_wallet:
                return {
                    'success': False,
                    'error': 'Wallet with this address already exists'
                }
            
            # Create wallet record
            wallet = Wallet(
                user_id=user_id,
                wallet_address=account.address,
                wallet_type='hot',
                name=name or f"Hot Wallet ({network})",
                network=network,
                private_key=account.key.hex(),
                derivation_path="m/44'/60'/0'/0/0"  # Standard Ethereum derivation path
            )
            
            # Set as primary if user has no other wallets
            user_wallets = Wallet.query.filter_by(user_id=user_id).count()
            if user_wallets == 0:
                wallet.is_primary = True
            
            db.session.add(wallet)
            db.session.commit()
            
            # Initialize default token balances
            self._initialize_wallet_balances(wallet)
            
            # Update user's blockchain_address if not set
            user = User.query.get(user_id)
            if user and not hasattr(user, 'blockchain_address'):
                user.blockchain_address = account.address
                db.session.commit()
            
            return {
                'success': True,
                'wallet': wallet.to_dict(),
                'mnemonic_phrase': mnemonic_phrase,  # Return only once, securely
                'warning': 'Store your mnemonic phrase securely. This is the only time it will be displayed.'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating hot wallet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_wallet_from_private_key(self, user_id: int, private_key: str, name: str = None, 
                                     network: str = 'base-sepolia') -> Dict[str, any]:
        """Import wallet from private key"""
        try:
            # Validate and create account from private key
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            account = Account.from_key(private_key)
            
            # Check if wallet already exists
            existing_wallet = Wallet.query.filter_by(
                user_id=user_id,
                wallet_address=account.address
            ).first()
            
            if existing_wallet:
                return {
                    'success': False,
                    'error': 'Wallet already exists'
                }
            
            # Create wallet
            wallet = Wallet(
                user_id=user_id,
                wallet_address=account.address,
                wallet_type='hot',
                name=name or f"Imported Wallet ({network})",
                network=network,
                private_key=account.key.hex()
            )
            
            db.session.add(wallet)
            db.session.commit()
            
            # Initialize balances
            self._initialize_wallet_balances(wallet)
            
            return {
                'success': True,
                'wallet': wallet.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error importing wallet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_wallet_from_mnemonic(self, user_id: int, mnemonic_phrase: str, name: str = None,
                                  network: str = 'base-sepolia', derivation_path: str = None) -> Dict[str, any]:
        """Import wallet from mnemonic phrase"""
        try:
            # Validate mnemonic
            if not self.mnemonic.check(mnemonic_phrase):
                raise ValueError("Invalid mnemonic phrase")
            
            # Use custom derivation path or default
            if not derivation_path:
                derivation_path = "m/44'/60'/0'/0/0"  # Standard Ethereum path
            
            # Derive account
            account = Account.from_mnemonic(mnemonic_phrase, account_path=derivation_path)
            
            # Check if wallet exists
            existing_wallet = Wallet.query.filter_by(
                user_id=user_id,
                wallet_address=account.address
            ).first()
            
            if existing_wallet:
                return {
                    'success': False,
                    'error': 'Wallet already exists'
                }
            
            # Create wallet
            wallet = Wallet(
                user_id=user_id,
                wallet_address=account.address,
                wallet_type='hot',
                name=name or f"Imported HD Wallet ({network})",
                network=network,
                private_key=account.key.hex(),
                derivation_path=derivation_path
            )
            
            db.session.add(wallet)
            db.session.commit()
            
            # Initialize balances
            self._initialize_wallet_balances(wallet)
            
            return {
                'success': True,
                'wallet': wallet.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error importing wallet from mnemonic: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_watch_only_wallet(self, user_id: int, wallet_address: str, name: str = None,
                                network: str = 'base-sepolia') -> Dict[str, any]:
        """Create a watch-only wallet"""
        try:
            # Validate address
            if not Web3.is_address(wallet_address):
                raise ValueError("Invalid wallet address")
            
            # Normalize address
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            # Check if wallet exists
            existing_wallet = Wallet.query.filter_by(
                user_id=user_id,
                wallet_address=wallet_address
            ).first()
            
            if existing_wallet:
                return {
                    'success': False,
                    'error': 'Wallet already exists'
                }
            
            # Create watch-only wallet
            wallet = Wallet(
                user_id=user_id,
                wallet_address=wallet_address,
                wallet_type='watch',
                name=name or f"Watch-Only Wallet ({network})",
                network=network,
                description="Read-only wallet for monitoring balances and transactions"
            )
            
            db.session.add(wallet)
            db.session.commit()
            
            # Initialize balances
            self._initialize_wallet_balances(wallet)
            
            return {
                'success': True,
                'wallet': wallet.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating watch-only wallet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Balance Management
    
    def _initialize_wallet_balances(self, wallet: Wallet):
        """Initialize default token balances for a wallet"""
        network_tokens = self.token_configs.get(wallet.network, {})
        
        # Always add ETH balance
        eth_balance = WalletBalance(
            wallet_id=wallet.id,
            token_symbol='ETH',
            token_address=None,
            token_decimals=18,
            balance=0
        )
        db.session.add(eth_balance)
        
        # Add configured tokens
        for token_symbol, config in network_tokens.items():
            token_balance = WalletBalance(
                wallet_id=wallet.id,
                token_symbol=token_symbol,
                token_address=config['address'],
                token_decimals=config['decimals'],
                balance=0
            )
            db.session.add(token_balance)
        
        db.session.commit()
    
    async def update_wallet_balances(self, wallet_id: int) -> Dict[str, any]:
        """Update all balances for a wallet"""
        try:
            wallet = Wallet.query.get(wallet_id)
            if not wallet:
                return {'success': False, 'error': 'Wallet not found'}
            
            updated_balances = {}
            
            # Update ETH balance
            eth_balance = await self._get_eth_balance(wallet.wallet_address)
            eth_balance_record = WalletBalance.query.filter_by(
                wallet_id=wallet_id,
                token_symbol='ETH'
            ).first()
            
            if eth_balance_record:
                # Get USD price
                eth_usd_price = await self._get_token_price('ethereum')
                eth_usd_value = None
                if eth_usd_price:
                    eth_value_decimal = float(eth_balance) / (10 ** 18)
                    eth_usd_value = eth_value_decimal * eth_usd_price
                
                eth_balance_record.update_balance(eth_balance, eth_usd_value)
                updated_balances['ETH'] = eth_balance_record.to_dict()
            
            # Update token balances
            network_tokens = self.token_configs.get(wallet.network, {})
            for token_symbol, config in network_tokens.items():
                if config['address']:
                    token_balance = await self._get_token_balance(
                        wallet.wallet_address,
                        config['address'],
                        config['decimals']
                    )
                    
                    token_balance_record = WalletBalance.query.filter_by(
                        wallet_id=wallet_id,
                        token_symbol=token_symbol
                    ).first()
                    
                    if token_balance_record:
                        # Get USD price if available
                        token_usd_price = None
                        if config.get('coingecko_id'):
                            token_usd_price = await self._get_token_price(config['coingecko_id'])
                        
                        token_usd_value = None
                        if token_usd_price:
                            token_value_decimal = float(token_balance) / (10 ** config['decimals'])
                            token_usd_value = token_value_decimal * token_usd_price
                        
                        token_balance_record.update_balance(token_balance, token_usd_value)
                        updated_balances[token_symbol] = token_balance_record.to_dict()
            
            # Update wallet activity timestamp
            wallet.update_activity()
            
            return {
                'success': True,
                'balances': updated_balances,
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error updating wallet balances: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_eth_balance(self, address: str) -> int:
        """Get ETH balance for address"""
        try:
            balance = self.web3.eth.get_balance(address)
            return balance
        except Exception as e:
            current_app.logger.error(f"Error getting ETH balance: {e}")
            return 0
    
    async def _get_token_balance(self, wallet_address: str, token_address: str, decimals: int) -> int:
        """Get token balance for address"""
        try:
            # ERC-20 balanceOf function signature
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=[{
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }]
            )
            
            balance = contract.functions.balanceOf(wallet_address).call()
            return balance
            
        except Exception as e:
            current_app.logger.error(f"Error getting token balance: {e}")
            return 0
    
    async def _get_token_price(self, token_id: str) -> float:
        """Get token price from CoinGecko with caching"""
        try:
            # Check cache
            cache_key = f"price_{token_id}"
            if cache_key in self.price_cache:
                cached_data = self.price_cache[cache_key]
                if datetime.utcnow() - cached_data['timestamp'] < timedelta(seconds=self.price_cache_timeout):
                    return cached_data['price']
            
            # Fetch from API
            response = requests.get(
                self.price_api_url,
                params={
                    'ids': token_id,
                    'vs_currencies': 'usd'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if token_id in data:
                    price = data[token_id]['usd']
                    
                    # Cache the price
                    self.price_cache[cache_key] = {
                        'price': price,
                        'timestamp': datetime.utcnow()
                    }
                    
                    return price
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting token price: {e}")
            return None
    
    # Transaction Management
    
    async def send_transaction(self, wallet_id: int, to_address: str, amount: str, 
                             token_symbol: str = 'ETH', gas_price: int = None) -> Dict[str, any]:
        """Send a transaction from wallet"""
        try:
            wallet = Wallet.query.get(wallet_id)
            if not wallet:
                return {'success': False, 'error': 'Wallet not found'}
            
            if wallet.wallet_type != 'hot':
                return {'success': False, 'error': 'Can only send from hot wallets'}
            
            # Validate addresses
            if not Web3.is_address(to_address):
                return {'success': False, 'error': 'Invalid recipient address'}
            
            to_address = Web3.to_checksum_address(to_address)
            
            # Get wallet private key
            private_key = wallet.decrypt_private_key()
            account = Account.from_key(private_key)
            
            # Prepare transaction
            if token_symbol == 'ETH':
                # ETH transfer
                tx = await self._prepare_eth_transaction(
                    account, to_address, amount, gas_price
                )
            else:
                # Token transfer
                tx = await self._prepare_token_transaction(
                    account, to_address, amount, token_symbol, wallet.network, gas_price
                )
            
            if not tx['success']:
                return tx
            
            # Send transaction
            signed_txn = self.web3.eth.account.sign_transaction(tx['transaction'], private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Record transaction
            transaction = WalletTransaction(
                wallet_id=wallet_id,
                tx_hash=tx_hash_hex,
                from_address=account.address,
                to_address=to_address,
                value=Web3.to_wei(amount, 'ether') if token_symbol == 'ETH' else 0,
                transaction_type='send',
                token_symbol=token_symbol if token_symbol != 'ETH' else None,
                token_amount=Web3.to_wei(amount, 'ether') if token_symbol != 'ETH' else None,
                status='pending',
                timestamp=datetime.utcnow()
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'success': True,
                'transaction_hash': tx_hash_hex,
                'transaction': transaction.to_dict(wallet.wallet_address)
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error sending transaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _prepare_eth_transaction(self, account, to_address: str, amount: str, 
                                     gas_price: int = None) -> Dict[str, any]:
        """Prepare ETH transaction"""
        try:
            value = Web3.to_wei(amount, 'ether')
            nonce = self.web3.eth.get_transaction_count(account.address)
            
            if not gas_price:
                gas_price = self.blockchain_service._estimate_gas_price()
            
            transaction = {
                'to': to_address,
                'value': value,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.blockchain_service.base_config[self.blockchain_service.network]['chain_id']
            }
            
            return {
                'success': True,
                'transaction': transaction
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error preparing ETH transaction: {e}"
            }
    
    async def _prepare_token_transaction(self, account, to_address: str, amount: str, 
                                       token_symbol: str, network: str, gas_price: int = None) -> Dict[str, any]:
        """Prepare token transfer transaction"""
        try:
            token_config = self.token_configs.get(network, {}).get(token_symbol)
            if not token_config:
                return {'success': False, 'error': f'Token {token_symbol} not configured for network {network}'}
            
            # Convert amount to token units
            amount_wei = Web3.to_wei(amount, 'ether') * (10 ** token_config['decimals']) // (10 ** 18)
            
            # ERC-20 transfer function
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(token_config['address']),
                abi=[{
                    "constant": False,
                    "inputs": [
                        {"name": "_to", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "transfer",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }]
            )
            
            nonce = self.web3.eth.get_transaction_count(account.address)
            
            if not gas_price:
                gas_price = self.blockchain_service._estimate_gas_price()
            
            transaction = contract.functions.transfer(to_address, amount_wei).build_transaction({
                'from': account.address,
                'gas': 100000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.blockchain_service.base_config[self.blockchain_service.network]['chain_id']
            })
            
            return {
                'success': True,
                'transaction': transaction
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error preparing token transaction: {e}"
            }
    
    # Transaction History and Monitoring
    
    async def sync_wallet_transactions(self, wallet_id: int, start_block: int = None) -> Dict[str, any]:
        """Sync wallet transactions from blockchain"""
        try:
            wallet = Wallet.query.get(wallet_id)
            if not wallet:
                return {'success': False, 'error': 'Wallet not found'}
            
            # Get latest block if no start block specified
            if not start_block:
                latest_block = self.web3.eth.get_block('latest')
                start_block = latest_block['number'] - 10000  # Last 10k blocks
            
            synced_transactions = []
            
            # Sync ETH transactions
            eth_txs = await self._get_eth_transactions(wallet.wallet_address, start_block)
            synced_transactions.extend(eth_txs)
            
            # Sync token transactions
            network_tokens = self.token_configs.get(wallet.network, {})
            for token_symbol, config in network_tokens.items():
                if config['address']:
                    token_txs = await self._get_token_transactions(
                        wallet.wallet_address,
                        config['address'],
                        token_symbol,
                        config['decimals'],
                        start_block
                    )
                    synced_transactions.extend(token_txs)
            
            # Store new transactions
            new_transactions = []
            for tx_data in synced_transactions:
                existing_tx = WalletTransaction.query.filter_by(
                    tx_hash=tx_data['tx_hash']
                ).first()
                
                if not existing_tx:
                    transaction = WalletTransaction(
                        wallet_id=wallet_id,
                        **tx_data
                    )
                    db.session.add(transaction)
                    new_transactions.append(transaction)
            
            db.session.commit()
            
            return {
                'success': True,
                'synced_count': len(new_transactions),
                'transactions': [tx.to_dict(wallet.wallet_address) for tx in new_transactions]
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error syncing wallet transactions: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_eth_transactions(self, address: str, start_block: int) -> List[Dict]:
        """Get ETH transactions for address"""
        # This is a placeholder - in production, you'd use services like:
        # - Etherscan API
        # - Alchemy/Infura enhanced APIs
        # - Graph Protocol indexers
        # - Direct blockchain scanning
        
        transactions = []
        # Implementation would fetch and parse ETH transactions
        return transactions
    
    async def _get_token_transactions(self, address: str, token_address: str, 
                                    token_symbol: str, decimals: int, start_block: int) -> List[Dict]:
        """Get token transactions for address"""
        # Similar to ETH transactions, this would use external APIs or indexing services
        transactions = []
        # Implementation would fetch and parse token Transfer events
        return transactions
    
    # Wallet Information and Statistics
    
    def get_wallet_summary(self, wallet_id: int) -> Dict[str, any]:
        """Get comprehensive wallet summary"""
        try:
            wallet = Wallet.query.get(wallet_id)
            if not wallet:
                return {'success': False, 'error': 'Wallet not found'}
            
            # Get balances with USD values
            total_usd_value = 0
            balances = {}
            
            for balance in wallet.balances:
                balance_dict = balance.to_dict()
                balances[balance.token_symbol] = balance_dict
                
                if balance.balance_usd:
                    total_usd_value += float(balance.balance_usd)
            
            # Get recent transactions
            recent_transactions = WalletTransaction.query.filter_by(
                wallet_id=wallet_id
            ).order_by(WalletTransaction.timestamp.desc()).limit(10).all()
            
            # Calculate transaction statistics
            total_sent = WalletTransaction.query.filter_by(
                wallet_id=wallet_id,
                transaction_type='send',
                status='confirmed'
            ).count()
            
            total_received = WalletTransaction.query.filter_by(
                wallet_id=wallet_id,
                transaction_type='receive',
                status='confirmed'
            ).count()
            
            return {
                'success': True,
                'wallet': wallet.to_dict(),
                'total_usd_value': total_usd_value,
                'balances': balances,
                'recent_transactions': [
                    tx.to_dict(wallet.wallet_address) for tx in recent_transactions
                ],
                'statistics': {
                    'total_transactions': len(wallet.transactions),
                    'total_sent': total_sent,
                    'total_received': total_received,
                    'last_activity': wallet.last_activity_at.isoformat() if wallet.last_activity_at else None
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting wallet summary: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_wallets(self, user_id: int) -> Dict[str, any]:
        """Get all wallets for a user"""
        try:
            wallets = Wallet.query.filter_by(user_id=user_id, is_active=True).all()
            
            wallet_summaries = []
            total_portfolio_usd = 0
            
            for wallet in wallets:
                wallet_dict = wallet.to_dict()
                
                # Calculate wallet USD value
                wallet_usd_value = 0
                for balance in wallet.balances:
                    if balance.balance_usd:
                        wallet_usd_value += float(balance.balance_usd)
                
                wallet_dict['total_usd_value'] = wallet_usd_value
                total_portfolio_usd += wallet_usd_value
                
                wallet_summaries.append(wallet_dict)
            
            return {
                'success': True,
                'wallets': wallet_summaries,
                'total_portfolio_usd': total_portfolio_usd,
                'wallet_count': len(wallets)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user wallets: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Security and Validation
    
    def validate_wallet_access(self, user_id: int, wallet_id: int) -> bool:
        """Validate user has access to wallet"""
        wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
        return wallet is not None
    
    def estimate_transaction_fee(self, wallet_id: int, to_address: str, amount: str,
                               token_symbol: str = 'ETH') -> Dict[str, any]:
        """Estimate transaction fee"""
        try:
            wallet = Wallet.query.get(wallet_id)
            if not wallet:
                return {'success': False, 'error': 'Wallet not found'}
            
            # Get current gas price
            gas_price = self.blockchain_service._estimate_gas_price()
            
            # Estimate gas limit
            if token_symbol == 'ETH':
                gas_limit = 21000  # Standard ETH transfer
            else:
                gas_limit = 100000  # ERC-20 transfer
            
            # Calculate fee
            total_fee_wei = gas_price * gas_limit
            total_fee_eth = Web3.from_wei(total_fee_wei, 'ether')
            total_fee_gwei = Web3.from_wei(total_fee_wei, 'gwei')
            
            # Get ETH price for USD conversion
            eth_price = await self._get_token_price('ethereum')
            fee_usd = float(total_fee_eth) * eth_price if eth_price else None
            
            return {
                'success': True,
                'gas_price_gwei': Web3.from_wei(gas_price, 'gwei'),
                'gas_limit': gas_limit,
                'total_fee_wei': total_fee_wei,
                'total_fee_eth': float(total_fee_eth),
                'total_fee_gwei': float(total_fee_gwei),
                'total_fee_usd': fee_usd
            }
            
        except Exception as e:
            current_app.logger.error(f"Error estimating transaction fee: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Multisig Wallet Support
    
    def create_multisig_wallet(self, user_id: int, owners: List[str], required_signatures: int,
                             name: str = None, network: str = 'base-sepolia') -> Dict[str, any]:
        """Create a multisig wallet (placeholder for future implementation)"""
        # This would integrate with a multisig wallet factory contract
        # For now, return a placeholder response
        return {
            'success': False,
            'error': 'Multisig wallet creation not yet implemented'
        }
    
    def get_network_info(self) -> Dict[str, any]:
        """Get current network information"""
        return self.blockchain_service.get_network_info()