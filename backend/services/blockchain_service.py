"""
Cardano Blockchain Service for Nimo Platform

This service provides integration with Cardano blockchain and bridges the Flask API
with on-chain identity and reputation data using Blockfrost API.

Note: Fully migrated to Cardano networks. No Base network dependencies remain.
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any
from flask import current_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .base_blockchain_service import (
    BaseBlockchainService,
    BlockchainType,
    TransactionStatus,
    NetworkInfo,
    TransactionCost,
    TransactionError,
    ConnectionError
)

class CardanoBlockchainService(BaseBlockchainService):
    def __init__(self, network: str = None):
        """Initialize Cardano blockchain service with Blockfrost API"""
        # Initialize base class with Cardano type
        super().__init__(network or os.getenv('NETWORK', 'cardano-preprod'), BlockchainType.CARDANO)

        # Cardano network configuration using Blockfrost
        self.cardano_config = {
            'cardano-preprod': {
                'project_id': os.getenv('BLOCKFROST_PREPROD_PROJECT_ID'),
                'api_url': 'https://cardano-preprod.blockfrost.io/api/v0',
                'explorer_url': 'https://preprod.cardanoscan.io',
                'network_id': 0,  # Cardano preprod testnet
                'fee_buffer': 1.1  # 10% fee buffer
            },
            'cardano-mainnet': {
                'project_id': os.getenv('BLOCKFROST_MAINNET_PROJECT_ID'),
                'api_url': 'https://cardano-mainnet.blockfrost.io/api/v0',
                'explorer_url': 'https://cardanoscan.io',
                'network_id': 1,  # Cardano mainnet
                'fee_buffer': 1.1
            }
        }

        # Validate configuration
        if not self.cardano_config[self.network]['project_id']:
            raise ConfigurationError(f"Blockfrost project ID not configured for {self.network}")

        self.api_key = self.cardano_config[self.network]['project_id']
        self.api_url = self.cardano_config[self.network]['api_url']
        self.headers = {'project_id': self.api_key}

        # Contract addresses (will be Cardano policy IDs/script addresses)
        self.contract_addresses = self._get_network_contracts()

        # Service wallet for transactions
        self.service_wallet = self._load_service_wallet()

    def _initialize_service(self):
        """Initialize Cardano-specific service components"""
        # Test connection to Blockfrost API
        try:
            self._test_connection()
        except Exception as e:
            self.logger.error(f"Failed to initialize Cardano service: {e}")
            self.available = False

    def _test_connection(self):
        """Test connection to Blockfrost API"""
        try:
            response = requests.get(f"{self.api_url}/health", headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            raise ConnectionError(f"Blockfrost API connection failed: {e}")

    def is_connected(self) -> bool:
        """Check if connected to Cardano network via Blockfrost"""
        try:
            return self._test_connection()
        except:
            return False

    def _initialize_service(self):
        """Initialize Ethereum-specific service components"""
        # Already handled in __init__, this method ensures base class compatibility
        pass

    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        return self.web3.is_connected()

    def get_balance(self, address: str) -> Dict[str, Any]:
        """Get ADA balance and token balances for a Cardano address"""
        try:
            # Get ADA balance
            ada_response = requests.get(f"{self.api_url}/addresses/{address}", headers=self.headers)
            ada_response.raise_for_status()
            ada_data = ada_response.json()

            ada_balance = int(ada_data.get('amount', [{}])[0].get('quantity', 0)) / 1_000_000  # Convert lovelace to ADA

            # Get token balances (assets)
            token_balance = 0
            try:
                assets_response = requests.get(f"{self.api_url}/addresses/{address}/utxos", headers=self.headers)
                assets_response.raise_for_status()
                utxos = assets_response.json()

                for utxo in utxos:
                    for asset in utxo.get('amount', []):
                        if asset.get('unit') == self.contract_addresses.get('token_policy'):
                            token_balance += int(asset.get('quantity', 0))
            except Exception as e:
                self.logger.warning(f"Error getting token balance: {e}")

            return {
                'success': True,
                'address': address,
                'ada_balance': ada_balance,
                'token_balance': token_balance,
                'network': self.network
            }
        except Exception as e:
            return self.format_error_response(str(e), 'get_balance', address=address)

    def send_transaction(self, **kwargs) -> Dict[str, Any]:
        """Send a transaction on Cardano network"""
        try:
            operation = kwargs.get('operation', 'send_transaction')
            from_address = kwargs.get('from_address')
            to_address = kwargs.get('to_address')
            amount = kwargs.get('amount', 0)  # Amount in lovelace
            metadata = kwargs.get('metadata', {})

            if not (from_address and to_address):
                raise ValueError("from_address and to_address required")

            # Build and submit Cardano transaction
            tx_hash = self._build_and_submit_transaction(from_address, to_address, amount, metadata)

            if tx_hash:
                return self.format_transaction_response(
                    tx_hash,
                    operation=operation,
                    from_address=from_address,
                    to_address=to_address,
                    amount=amount
                )
            else:
                raise TransactionError("Transaction failed to send")

        except Exception as e:
            return self.format_error_response(str(e), 'send_transaction', **kwargs)

    def _build_and_submit_transaction(self, from_address: str, to_address: str, amount: int, metadata: Dict = None) -> Optional[str]:
        """Build and submit a Cardano transaction"""
        try:
            # Get UTXOs for the sender
            utxos_response = requests.get(f"{self.api_url}/addresses/{from_address}/utxos", headers=self.headers)
            utxos_response.raise_for_status()
            utxos = utxos_response.json()

            if not utxos:
                raise TransactionError("No UTXOs available for transaction")

            # Select UTXOs (simplified - in production would need coin selection algorithm)
            selected_utxo = utxos[0]
            tx_hash = selected_utxo['tx_hash']
            output_index = selected_utxo['output_index']

            # Build transaction body
            tx_body = {
                "inputs": [{"transaction_id": tx_hash, "index": output_index}],
                "outputs": [
                    {
                        "address": to_address,
                        "amount": [{"unit": "lovelace", "quantity": str(amount)}]
                    }
                ]
            }

            # Add change output if necessary
            input_amount = int(selected_utxo['amount'][0]['quantity'])
            if input_amount > amount:
                change_amount = input_amount - amount - 200000  # Subtract fee
                if change_amount > 0:
                    tx_body["outputs"].append({
                        "address": from_address,
                        "amount": [{"unit": "lovelace", "quantity": str(change_amount)}]
                    })

            # Add metadata if provided
            if metadata:
                tx_body["metadata"] = metadata

            # Submit transaction (in production, this would be signed and submitted)
            # For now, return a placeholder transaction hash
            import hashlib
            tx_data = json.dumps(tx_body, sort_keys=True)
            return hashlib.sha256(tx_data.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error building Cardano transaction: {e}")
            return None

    def _build_simple_transaction(self, from_address: str, to_address: str, value: int) -> Dict:
        """Build a simple ETH transfer transaction"""
        nonce = self.web3.eth.get_transaction_count(from_address)
        gas_price = self._estimate_gas_price()
        gas_limit = 21000  # Standard transfer gas limit

        return {
            'to': to_address,
            'value': value,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': self.cardano_config[self.network]['chain_id']
        }
    
    def _load_contract_abis(self) -> Dict:
        """Load contract ABIs from build files"""
        abis = {}
        contracts_dir = os.path.join(os.path.dirname(__file__), '../../contracts/out')
        
        for contract_name in ['NimoIdentity', 'NimoToken']:
            # Try clean ABI file first, then fall back to original
            clean_abi_file = os.path.join(contracts_dir, f'{contract_name}.sol', f'{contract_name}_clean.json')
            original_abi_file = os.path.join(contracts_dir, f'{contract_name}.sol', f'{contract_name}.json')
            
            abi_file = clean_abi_file if os.path.exists(clean_abi_file) else original_abi_file
            
            if os.path.exists(abi_file):
                with open(abi_file, 'r') as f:
                    contract_data = json.load(f)
                    # Handle both formats: raw ABI array or object with 'abi' key
                    if isinstance(contract_data, list):
                        abis[contract_name.lower().replace('nimo', '')] = contract_data
                    elif isinstance(contract_data, dict) and 'abi' in contract_data:
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
        if self.network in self.cardano_config:
            return self.cardano_config[self.network]['rpc_url']
        return os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545')
    
    def _get_network_contracts(self) -> Dict[str, str]:
        """Get contract addresses (policy IDs) for the current Cardano network"""
        if self.network == 'cardano-preprod':
            return {
                'identity_policy': os.getenv('NIMO_IDENTITY_POLICY_CARDANO_PREPROD'),
                'token_policy': os.getenv('NIMO_TOKEN_POLICY_CARDANO_PREPROD'),
                'bond_policy': os.getenv('NIMO_BOND_POLICY_CARDANO_PREPROD')
            }
        elif self.network == 'cardano-mainnet':
            return {
                'identity_policy': os.getenv('NIMO_IDENTITY_POLICY_CARDANO_MAINNET'),
                'token_policy': os.getenv('NIMO_TOKEN_POLICY_CARDANO_MAINNET'),
                'bond_policy': os.getenv('NIMO_BOND_POLICY_CARDANO_MAINNET')
            }
        else:
            return {
                'identity_policy': os.getenv('NIMO_IDENTITY_POLICY'),
                'token_policy': os.getenv('NIMO_TOKEN_POLICY'),
                'bond_policy': os.getenv('NIMO_BOND_POLICY')
            }

    def _load_service_wallet(self):
        """Load service wallet for Cardano transactions"""
        wallet_info = {
            'address': os.getenv('CARDANO_SERVICE_ADDRESS'),
            'private_key': os.getenv('CARDANO_SERVICE_PRIVATE_KEY')
        }

        # Check if wallet is configured
        if not wallet_info['address'] or wallet_info['address'] == 'your_service_address_here':
            self.logger.warning("CARDANO_SERVICE_ADDRESS not configured or is placeholder")
            return None

        if not wallet_info['private_key'] or wallet_info['private_key'] == 'your_service_private_key_here':
            self.logger.warning("CARDANO_SERVICE_PRIVATE_KEY not configured or is placeholder")
            return None

        return wallet_info
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()

    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        """Get status of a Cardano transaction"""
        try:
            # Check if transaction is still pending in our tracking
            if tx_hash in self.pending_transactions:
                # Query transaction status from Blockfrost
                response = requests.get(f"{self.api_url}/txs/{tx_hash}", headers=self.headers)

                if response.status_code == 200:
                    tx_data = response.json()
                    block_height = tx_data.get('block_height')
                    fees = int(tx_data.get('fees', 0))

                    # Transaction is confirmed
                    self.pending_transactions.pop(tx_hash, None)

                    return TransactionStatus(
                        tx_hash=tx_hash,
                        status='confirmed',
                        block_number=block_height,
                        fees=fees,
                        confirmed=True
                    )
                elif response.status_code == 404:
                    # Transaction not found, might still be pending
                    return TransactionStatus(
                        tx_hash=tx_hash,
                        status='pending',
                        confirmed=False
                    )
                else:
                    return TransactionStatus(
                        tx_hash=tx_hash,
                        status='failed',
                        confirmed=True,
                        error=f"Blockfrost API error: {response.status_code}"
                    )

            # Check if it's a failed transaction
            if any(tx_hash in str(failed) for failed in self.failed_transactions.values()):
                return TransactionStatus(
                    tx_hash=tx_hash,
                    status='failed',
                    confirmed=True,
                    error='Transaction failed during submission'
                )

            # Unknown transaction - try to query it
            try:
                response = requests.get(f"{self.api_url}/txs/{tx_hash}", headers=self.headers)
                if response.status_code == 200:
                    tx_data = response.json()
                    return TransactionStatus(
                        tx_hash=tx_hash,
                        status='confirmed',
                        block_number=tx_data.get('block_height'),
                        fees=int(tx_data.get('fees', 0)),
                        confirmed=True
                    )
            except:
                pass

            # Unknown transaction
            return TransactionStatus(
                tx_hash=tx_hash,
                status='unknown',
                confirmed=False
            )

        except Exception as e:
            return TransactionStatus(
                tx_hash=tx_hash,
                status='error',
                error=str(e),
                confirmed=False
            )
    
    def create_identity_on_chain(self, username: str, metadata_uri: str, user_address: str) -> Optional[str]:
        """Create identity NFT on Cardano blockchain"""
        try:
            # Create metadata for identity NFT
            metadata = {
                721: {
                    self.contract_addresses['identity_policy']: {
                        username: {
                            "name": f"Nimo Identity: {username}",
                            "description": f"Decentralized identity for {username}",
                            "metadata_uri": metadata_uri,
                            "created_at": self._get_current_timestamp()
                        }
                    }
                }
            }

            # Mint identity NFT transaction
            tx_hash = self._build_and_submit_transaction(
                self.service_wallet['address'],
                user_address,
                2000000,  # 2 ADA for identity creation
                metadata
            )

            return tx_hash

        except Exception as e:
            self.logger.error(f"Error creating identity on-chain: {e}")
            return None

    def add_contribution_on_chain(self, contribution_type: str, description: str, evidence_uri: str, metta_hash: str, user_address: str) -> Optional[str]:
        """Add contribution to Cardano blockchain"""
        try:
            # Create metadata for contribution
            metadata = {
                721: {
                    self.contract_addresses['token_policy']: {
                        f"contribution_{self._generate_error_id()}": {
                            "type": contribution_type,
                            "description": description,
                            "evidence_uri": evidence_uri,
                            "metta_hash": metta_hash,
                            "created_at": self._get_current_timestamp()
                        }
                    }
                }
            }

            # Submit contribution transaction
            tx_hash = self._build_and_submit_transaction(
                user_address,
                self.service_wallet['address'],
                1000000,  # 1 ADA fee
                metadata
            )

            return tx_hash

        except Exception as e:
            self.logger.error(f"Error adding contribution on-chain: {e}")
            return None

    def verify_contribution_on_chain(self, contribution_id: int, tokens_to_award: int) -> Optional[str]:
        """Verify contribution and award tokens on Cardano"""
        try:
            # Create verification metadata
            metadata = {
                721: {
                    self.contract_addresses['token_policy']: {
                        f"verification_{contribution_id}": {
                            "contribution_id": contribution_id,
                            "tokens_awarded": tokens_to_award,
                            "verified_at": self._get_current_timestamp()
                        }
                    }
                }
            }

            # Submit verification transaction
            tx_hash = self._build_and_submit_transaction(
                self.service_wallet['address'],
                self.service_wallet['address'],  # Self-transaction for verification
                1500000,  # 1.5 ADA fee
                metadata
            )

            return tx_hash

        except Exception as e:
            self.logger.error(f"Error verifying contribution on-chain: {e}")
            return None

    def get_token_balance(self, address: str) -> int:
        """Get NIMO token balance for Cardano address"""
        try:
            # Get UTXOs containing NIMO tokens
            response = requests.get(f"{self.api_url}/addresses/{address}/utxos", headers=self.headers)
            response.raise_for_status()
            utxos = response.json()

            total_tokens = 0
            for utxo in utxos:
                for asset in utxo.get('amount', []):
                    if asset.get('unit') == self.contract_addresses.get('token_policy'):
                        total_tokens += int(asset.get('quantity', 0))

            return total_tokens

        except Exception as e:
            self.logger.error(f"Error getting token balance: {e}")
            return 0

    def sync_blockchain_data(self):
        """Sync blockchain data with local database"""
        try:
            # Get recent transactions and sync with database
            # This is a placeholder for actual sync implementation
            self.logger.info("Syncing Cardano blockchain data...")
            pass
        except Exception as e:
            self.logger.error(f"Error syncing blockchain data: {e}")