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
    def __init__(self, web3_provider_url: str = None, contract_addresses: Dict = None):
        """Initialize blockchain service with Web3 provider and contract addresses"""
        self.web3_provider_url = web3_provider_url or os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545')
        self.web3 = Web3(Web3.HTTPProvider(self.web3_provider_url))
        
        # Contract addresses (deployed contracts)
        self.contract_addresses = contract_addresses or {
            'identity': os.getenv('NIMO_IDENTITY_CONTRACT'),
            'token': os.getenv('NIMO_TOKEN_CONTRACT')
        }
        
        # Load contract ABIs
        self.contract_abis = self._load_contract_abis()
        
        # Initialize contracts
        self.identity_contract = self._get_contract('identity')
        self.token_contract = self._get_contract('token')
        
        # Service account for contract interactions
        self.service_account = self._load_service_account()
    
    def _load_contract_abis(self) -> Dict:
        """Load contract ABIs from build files"""
        abis = {}
        contracts_dir = os.path.join(os.path.dirname(__file__), '../../contracts/build')
        
        for contract_name in ['NimoIdentity', 'NimoToken']:
            abi_file = os.path.join(contracts_dir, f'{contract_name}.json')
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
    
    def _load_service_account(self):
        """Load service account for contract interactions"""
        private_key = os.getenv('BLOCKCHAIN_SERVICE_PRIVATE_KEY')
        if private_key:
            return Account.from_key(private_key)
        return None
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        return self.web3.is_connected()
    
    def create_identity_on_chain(self, username: str, metadata_uri: str, user_address: str) -> Optional[str]:
        """Create identity NFT on blockchain"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            # Build transaction
            function = self.identity_contract.functions.createIdentity(username, metadata_uri)
            transaction = function.build_transaction({
                'from': user_address,
                'nonce': self.web3.eth.get_transaction_count(user_address),
                'gas': 300000,
                'gasPrice': self.web3.to_wei('20', 'gwei')
            })
            
            # This would typically be signed by the user's wallet
            # For demo purposes, we'll use service account
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            current_app.logger.error(f"Error creating identity on-chain: {e}")
            return None
    
    def add_contribution_on_chain(self, 
                                contribution_type: str, 
                                description: str, 
                                evidence_uri: str, 
                                metta_hash: str,
                                user_address: str) -> Optional[str]:
        """Add contribution to blockchain"""
        if not self.identity_contract or not self.service_account:
            return None
        
        try:
            function = self.identity_contract.functions.addContribution(
                contribution_type, description, evidence_uri, metta_hash
            )
            
            transaction = function.build_transaction({
                'from': user_address,
                'nonce': self.web3.eth.get_transaction_count(user_address),
                'gas': 200000,
                'gasPrice': self.web3.to_wei('20', 'gwei')
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
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
    
    def sync_blockchain_data(self):
        """Sync blockchain data with local database"""
        # This method would implement synchronization logic
        # between blockchain state and local database
        pass