"""
Blockchain Service for Nimo Platform

This service provides integration with Ethereum smart contracts
and bridges the Flask API with on-chain identity and reputation data.
"""

import json
import os
from typing import Dict, List, Optional
from web3 import Web3
from eth_account import Account
from flask import current_app

class BlockchainService:
    def __init__(self, web3_provider_url: str = None, contract_addresses: Dict = None, network: str = None):
        """Initialize blockchain service with Web3 provider and contract addresses"""
        # Base network configuration (defined first)
        self.base_config = {
            'base-sepolia': {
                'chain_id': 84532,
                'rpc_url': 'https://sepolia.base.org',
                'explorer_url': 'https://sepolia.basescan.org',
                'gas_price_gwei': 1.0,  # Base Sepolia has lower gas costs
                'gas_limit_multiplier': 1.2
            },
            'base-mainnet': {
                'chain_id': 8453,
                'rpc_url': 'https://mainnet.base.org',
                'explorer_url': 'https://basescan.org',
                'gas_price_gwei': 0.1,  # Base mainnet has very low gas costs
                'gas_limit_multiplier': 1.1
            }
        }
        
        self.network = network or os.getenv('NETWORK', 'base-sepolia')
        self.web3_provider_url = web3_provider_url or self._get_network_rpc_url()
        self.web3 = Web3(Web3.HTTPProvider(self.web3_provider_url))
        
        # Enhanced contract addresses with network support
        self.contract_addresses = contract_addresses or self._get_network_contracts()
        
        # Load contract ABIs
        self.contract_abis = self._load_contract_abis()
        
        # Initialize contracts
        self.identity_contract = self._get_contract('identity')
        self.token_contract = self._get_contract('token')
        
        # Service account for contract interactions
        self.service_account = self._load_service_account()
        
        # Transaction monitoring
        self.pending_transactions = {}
        self.failed_transactions = {}
        
        # Gas optimization settings
        self.gas_optimization_enabled = True
        self.batch_processing_enabled = True
    
    def _load_contract_abis(self) -> Dict:
        """Load contract ABIs from build files"""
        abis = {}
        contracts_dir = os.path.join(os.path.dirname(__file__), '../../contracts/out')
        
        for contract_name in ['NimoIdentity', 'NimoToken']:
            abi_file = os.path.join(contracts_dir, f'{contract_name}.sol', f'{contract_name}.json')
            if os.path.exists(abi_file):
                with open(abi_file, 'r') as f:
                    contract_data = json.load(f)
                    abis[contract_name.lower().replace('nimo', '')] = contract_data['abi']
        
        return abis
    
    def _get_contract(self, contract_type: str):
        """Get contract instance"""
        if contract_type not in self.contract_addresses or not self.contract_addresses[contract_type]:
            return None
        
        address = self.contract_addresses[contract_type]
        abi = self.contract_abis.get(contract_type)
        
        if not abi:
            return None
        
        return self.web3.eth.contract(address=address, abi=abi)
    
    def _get_network_rpc_url(self) -> str:
        """Get RPC URL for the current network"""
        if self.network in self.base_config:
            return self.base_config[self.network]['rpc_url']
        return os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545')
    
    def _get_network_contracts(self) -> Dict[str, str]:
        """Get contract addresses for the current network"""
        if self.network == 'base-sepolia':
            return {
                'identity': os.getenv('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA'),
                'token': os.getenv('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA')
            }
        elif self.network == 'base-mainnet':
            return {
                'identity': os.getenv('NIMO_IDENTITY_CONTRACT_BASE_MAINNET'),
                'token': os.getenv('NIMO_TOKEN_CONTRACT_BASE_MAINNET')
            }
        else:
            return {
                'identity': os.getenv('NIMO_IDENTITY_CONTRACT'),
                'token': os.getenv('NIMO_TOKEN_CONTRACT')
            }

    def _load_service_account(self):
        """Load service account for contract interactions"""
        private_key = os.getenv('BLOCKCHAIN_SERVICE_PRIVATE_KEY')
        if private_key:
            return Account.from_key(private_key)
        return None
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        return self.web3.is_connected()
    
    def _estimate_gas_price(self) -> int:
        """Estimate optimal gas price for Base network"""
        if not self.gas_optimization_enabled:
            return self.web3.to_wei(self.base_config[self.network]['gas_price_gwei'], 'gwei')
        
        try:
            # Get current gas price from network
            current_gas_price = self.web3.eth.gas_price
            
            # For Base network, gas prices are typically very low
            # Apply a small buffer for faster confirmation
            optimal_gas_price = int(current_gas_price * 1.1)
            
            # Ensure we don't exceed reasonable limits for Base
            max_gas_price = self.web3.to_wei(2.0, 'gwei')  # 2 gwei max for Base
            
            return min(optimal_gas_price, max_gas_price)
        except Exception as e:
            current_app.logger.warning(f"Gas price estimation failed, using default: {e}")
            return self.web3.to_wei(self.base_config[self.network]['gas_price_gwei'], 'gwei')
    
    def _estimate_gas_limit(self, transaction_data: Dict) -> int:
        """Estimate gas limit for transaction with Base network optimization"""
        try:
            estimated_gas = self.web3.eth.estimate_gas(transaction_data)
            
            # Apply network-specific multiplier
            multiplier = self.base_config[self.network]['gas_limit_multiplier']
            gas_limit = int(estimated_gas * multiplier)
            
            # Base network has a block gas limit, ensure we don't exceed it
            max_gas_limit = 30_000_000  # Base network block gas limit
            
            return min(gas_limit, max_gas_limit)
        except Exception as e:
            current_app.logger.warning(f"Gas limit estimation failed, using default: {e}")
            return 300000  # Default gas limit
    
    def _build_transaction(self, contract_function, from_address: str, value: int = 0) -> Dict:
        """Build optimized transaction for Base network"""
        # Build base transaction
        transaction = contract_function.build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address),
            'value': value,
            'chainId': self.base_config[self.network]['chain_id']
        })
        
        # Add optimized gas settings
        transaction['gasPrice'] = self._estimate_gas_price()
        transaction['gas'] = self._estimate_gas_limit(transaction)
        
        return transaction
    
    def _send_transaction(self, transaction: Dict, private_key: str = None) -> Optional[str]:
        """Send transaction with monitoring and retry logic"""
        try:
            # Use service account key if no private key provided
            key = private_key or self.service_account.key
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Track transaction
            self.pending_transactions[tx_hash_hex] = {
                'hash': tx_hash_hex,
                'timestamp': self._get_current_timestamp(),
                'status': 'pending'
            }
            
            current_app.logger.info(f"Transaction sent: {tx_hash_hex}")
            return tx_hash_hex
        
        except Exception as e:
            current_app.logger.error(f"Transaction failed: {e}")
            # Track failed transaction
            failed_tx = {
                'error': str(e),
                'timestamp': self._get_current_timestamp(),
                'transaction_data': transaction
            }
            self.failed_transactions[self._generate_error_id()] = failed_tx
            return None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def create_identity_on_chain(self, username: str, metadata_uri: str, user_address: str) -> Optional[str]:
        """Create identity NFT on blockchain with Base network optimization"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            # Build optimized transaction
            function = self.identity_contract.functions.createIdentity(username, metadata_uri)
            transaction = self._build_transaction(function, user_address)
            
            # Send transaction with monitoring
            return self._send_transaction(transaction)
            
        except Exception as e:
            current_app.logger.error(f"Error creating identity on-chain: {e}")
            return None
    
    def add_contribution_on_chain(self, 
                                contribution_type: str, 
                                description: str, 
                                evidence_uri: str, 
                                metta_hash: str,
                                user_address: str) -> Optional[str]:
        """Add contribution to blockchain with Base network optimization"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            function = self.identity_contract.functions.addContribution(
                contribution_type, description, evidence_uri, metta_hash
            )
            
            transaction = self._build_transaction(function, user_address)
            return self._send_transaction(transaction)
            
        except Exception as e:
            current_app.logger.error(f"Error adding contribution on-chain: {e}")
            return None
    
    def verify_contribution_on_chain(self, contribution_id: int, tokens_to_award: int) -> Optional[str]:
        """Verify contribution and award tokens on blockchain"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            function = self.identity_contract.functions.verifyContribution(
                contribution_id, tokens_to_award
            )
            
            transaction = function.build_transaction({
                'from': self.service_account.address,
                'nonce': self.web3.eth.get_transaction_count(self.service_account.address),
                'gas': 150000,
                'gasPrice': self.web3.to_wei('20', 'gwei')
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            current_app.logger.error(f"Error verifying contribution on-chain: {e}")
            return None
    
    def execute_metta_rule_on_chain(self, rule: str, identity_id: int, tokens_to_award: int) -> Optional[str]:
        """Execute MeTTa rule through smart contract"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            function = self.identity_contract.functions.executeMeTTaRule(
                rule, identity_id, tokens_to_award
            )
            
            transaction = function.build_transaction({
                'from': self.service_account.address,
                'nonce': self.web3.eth.get_transaction_count(self.service_account.address),
                'gas': 200000,
                'gasPrice': self.web3.to_wei('20', 'gwei')
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            current_app.logger.error(f"Error executing MeTTa rule on-chain: {e}")
            return None
    
    def mint_tokens_for_contribution(self, 
                                   to_address: str, 
                                   amount: int, 
                                   reason: str, 
                                   metta_proof: str) -> Optional[str]:
        """Mint reputation tokens for verified contributions"""
        if not self.token_contract or not self.service_account:
            return None
        
        try:
            function = self.token_contract.functions.mintForContribution(
                to_address, amount, reason, metta_proof
            )
            
            transaction = function.build_transaction({
                'from': self.service_account.address,
                'nonce': self.web3.eth.get_transaction_count(self.service_account.address),
                'gas': 150000,
                'gasPrice': self.web3.to_wei('20', 'gwei')
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            current_app.logger.error(f"Error minting tokens: {e}")
            return None
    
    def create_impact_bond_on_chain(self,
                                  title: str,
                                  description: str,
                                  target_amount: int,
                                  maturity_date: int,
                                  milestones: List[str],
                                  creator_address: str) -> Optional[str]:
        """Create impact bond on blockchain"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            function = self.identity_contract.functions.createImpactBond(
                title, description, target_amount, maturity_date, milestones
            )
            
            transaction = function.build_transaction({
                'from': creator_address,
                'nonce': self.web3.eth.get_transaction_count(creator_address),
                'gas': 400000,
                'gasPrice': self.web3.to_wei('20', 'gwei')
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            current_app.logger.error(f"Error creating impact bond on-chain: {e}")
            return None
    
    def get_identity_from_chain(self, username: str) -> Optional[Dict]:
        """Get identity data from blockchain"""
        if not self.identity_contract:
            return None
        
        try:
            identity_data = self.identity_contract.functions.getIdentityByUsername(username).call()
            
            return {
                'username': identity_data[0],
                'metadata_uri': identity_data[1],
                'reputation_score': identity_data[2],
                'token_balance': identity_data[3],
                'is_active': identity_data[4],
                'created_at': identity_data[5]
            }
        except Exception as e:
            current_app.logger.error(f"Error getting identity from chain: {e}")
            return None
    
    def get_token_balance(self, address: str) -> int:
        """Get token balance for address"""
        if not self.token_contract:
            return 0
        
        try:
            return self.token_contract.functions.balanceOf(address).call()
        except Exception as e:
            current_app.logger.error(f"Error getting token balance: {e}")
            return 0
    
    def listen_for_events(self, event_filter, callback):
        """Listen for blockchain events"""
        try:
            for event in event_filter.get_new_entries():
                callback(event)
        except Exception as e:
            current_app.logger.error(f"Error listening for events: {e}")
    
    def batch_verify_contributions(self, contributions: List[Dict]) -> List[Optional[str]]:
        """Batch verify multiple contributions for gas efficiency"""
        if not self.batch_processing_enabled or not self.identity_contract:
            # Fall back to individual transactions
            return [self.verify_contribution_on_chain(c['id'], c['tokens']) for c in contributions]
        
        try:
            # Prepare batch data
            contribution_ids = [c['id'] for c in contributions]
            token_amounts = [c['tokens'] for c in contributions]
            
            function = self.identity_contract.functions.batchVerifyContributions(
                contribution_ids, token_amounts
            )
            
            transaction = self._build_transaction(function, self.service_account.address)
            return [self._send_transaction(transaction)] * len(contributions)  # Same tx hash for all
            
        except Exception as e:
            current_app.logger.error(f"Batch verification failed, falling back to individual: {e}")
            # Fall back to individual transactions
            return [self.verify_contribution_on_chain(c['id'], c['tokens']) for c in contributions]
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """Get status of a transaction"""
        try:
            # Check if transaction is still pending
            if tx_hash in self.pending_transactions:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    # Transaction is confirmed
                    status = 'success' if receipt['status'] == 1 else 'failed'
                    self.pending_transactions.pop(tx_hash, None)
                    
                    return {
                        'hash': tx_hash,
                        'status': status,
                        'block_number': receipt['blockNumber'],
                        'gas_used': receipt['gasUsed'],
                        'confirmed': True
                    }
                else:
                    return {
                        'hash': tx_hash,
                        'status': 'pending',
                        'confirmed': False
                    }
            
            # Check if it's a failed transaction
            if any(tx_hash in str(failed) for failed in self.failed_transactions.values()):
                return {
                    'hash': tx_hash,
                    'status': 'failed',
                    'confirmed': True,
                    'error': 'Transaction failed during submission'
                }
            
            # Unknown transaction
            return {
                'hash': tx_hash,
                'status': 'unknown',
                'confirmed': False
            }
            
        except Exception as e:
            return {
                'hash': tx_hash,
                'status': 'error',
                'error': str(e),
                'confirmed': False
            }
    
    def setup_event_listeners(self):
        """Set up event listeners for important contract events"""
        if not self.identity_contract:
            return
        
        try:
            # Listen for identity creation events
            identity_filter = self.identity_contract.events.IdentityCreated.create_filter(
                fromBlock='latest'
            )
            
            # Listen for contribution verification events  
            verification_filter = self.identity_contract.events.ContributionVerified.create_filter(
                fromBlock='latest'
            )
            
            return {
                'identity_created': identity_filter,
                'contribution_verified': verification_filter
            }
            
        except Exception as e:
            current_app.logger.error(f"Error setting up event listeners: {e}")
            return {}
    
    def process_contract_events(self, event_filters: Dict, callback_handlers: Dict):
        """Process contract events with callback handlers"""
        for event_name, event_filter in event_filters.items():
            try:
                for event in event_filter.get_new_entries():
                    if event_name in callback_handlers:
                        callback_handlers[event_name](event)
            except Exception as e:
                current_app.logger.error(f"Error processing {event_name} events: {e}")
    
    def get_network_info(self) -> Dict:
        """Get current network information"""
        try:
            latest_block = self.web3.eth.get_block('latest')
            gas_price = self.web3.eth.gas_price
            
            return {
                'network': self.network,
                'chain_id': self.base_config[self.network]['chain_id'],
                'connected': self.is_connected(),
                'latest_block': latest_block['number'],
                'current_gas_price': gas_price,
                'current_gas_price_gwei': self.web3.from_wei(gas_price, 'gwei'),
                'explorer_url': self.base_config[self.network]['explorer_url'],
                'contract_addresses': self.contract_addresses
            }
        except Exception as e:
            return {
                'network': self.network,
                'connected': False,
                'error': str(e)
            }
    
    def estimate_transaction_cost(self, operation: str, params: Dict = None) -> Dict:
        """Estimate transaction cost for different operations"""
        try:
            if operation == 'create_identity':
                function = self.identity_contract.functions.createIdentity("test", "ipfs://test")
            elif operation == 'add_contribution':
                function = self.identity_contract.functions.addContribution("test", "test", "ipfs://test", "0x123")
            elif operation == 'verify_contribution':
                function = self.identity_contract.functions.verifyContribution(1, 50)
            else:
                return {'error': 'Unknown operation'}
            
            # Estimate gas
            gas_estimate = function.estimate_gas({'from': self.service_account.address})
            gas_price = self._estimate_gas_price()
            
            # Calculate costs
            gas_cost_wei = gas_estimate * gas_price
            gas_cost_eth = self.web3.from_wei(gas_cost_wei, 'ether')
            gas_cost_gwei = self.web3.from_wei(gas_cost_wei, 'gwei')
            
            return {
                'operation': operation,
                'gas_estimate': gas_estimate,
                'gas_price_wei': gas_price,
                'gas_price_gwei': self.web3.from_wei(gas_price, 'gwei'),
                'total_cost_wei': gas_cost_wei,
                'total_cost_eth': float(gas_cost_eth),
                'total_cost_gwei': float(gas_cost_gwei)
            }
            
        except Exception as e:
            return {
                'operation': operation,
                'error': str(e)
            }

    def sync_blockchain_data(self):
        """Sync blockchain data with local database"""
        # This method would implement synchronization logic
        # between blockchain state and local database
        try:
            # Get recent events and sync with database
            # This is a placeholder for the actual implementation
            current_app.logger.info("Syncing blockchain data...")
            pass
        except Exception as e:
            current_app.logger.error(f"Error syncing blockchain data: {e}")