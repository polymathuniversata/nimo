"""
Cardano Blockchain Service for Nimo Platform

This service provides integration with Cardano blockchain using Blockfrost API
and PyCardano, replacing the previous Ethereum/USDC integration.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio
from enum import Enum

try:
    from pycardano import (
        BlockFrostChainContext, 
        Network,
        PaymentSigningKey,
        PaymentVerificationKey,
        Address,
        TransactionBuilder,
        TransactionOutput,
        Value,
        AssetName,
        ScriptHash,
        MultiAsset,
        Asset,
        UTxO,
        TransactionInput,
        TransactionId,
        PlutusV2Script,
        PlutusData,
        Redeemer,
        RedeemerTag
    )
    from pycardano.crypto.bech32 import encode, decode
    PYCARDANO_AVAILABLE = True
except ImportError:
    print("PyCardano not installed. Install with: pip install pycardano")
    PYCARDANO_AVAILABLE = False
    # Create mock classes for type hints when PyCardano is not available
    class PaymentSigningKey: pass
    class PaymentVerificationKey: pass
    class Address: pass
    class BlockFrostChainContext: pass

from flask import current_app

class CardanoNetwork(Enum):
    """Cardano network types"""
    MAINNET = "mainnet"
    PREVIEW = "preview"
    PREPROD = "preprod"

@dataclass
class CardanoConfig:
    """Cardano network configuration"""
    network: CardanoNetwork
    blockfrost_project_id: str
    blockfrost_base_url: str
    faucet_url: Optional[str] = None
    min_ada_utxo: int = 1000000  # 1 ADA minimum UTXO

class CardanoService:
    """Service for integrating with Cardano blockchain using Blockfrost API"""
    
    # Standard Cardano constants
    ADA_DECIMALS = 6  # 1 ADA = 1,000,000 Lovelace
    MIN_ADA_UTXO = 1000000  # Minimum ADA in UTXO (1 ADA)
    
    def __init__(self, network: str = None, blockfrost_project_id: str = None):
        """Initialize Cardano service with Blockfrost API"""
        
        if not PYCARDANO_AVAILABLE:
            self.available = False
            self.error = "PyCardano not available"
            return
        
        # Network configuration
        self.network_name = network or os.getenv('CARDANO_NETWORK', 'preview')
        self.network_configs = {
            'mainnet': CardanoConfig(
                network=CardanoNetwork.MAINNET,
                blockfrost_project_id=os.getenv('BLOCKFROST_PROJECT_ID_MAINNET', ''),
                blockfrost_base_url='https://cardano-mainnet.blockfrost.io/api',
            ),
            'preview': CardanoConfig(
                network=CardanoNetwork.PREVIEW,
                blockfrost_project_id=os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW', ''),
                blockfrost_base_url='https://cardano-preview.blockfrost.io/api',
                faucet_url='https://docs.cardano.org/cardano-testnets/tools/faucet'
            ),
            'preprod': CardanoConfig(
                network=CardanoNetwork.PREPROD,
                blockfrost_project_id=os.getenv('BLOCKFROST_PROJECT_ID_PREPROD', ''),
                blockfrost_base_url='https://cardano-preprod.blockfrost.io/api',
                faucet_url='https://docs.cardano.org/cardano-testnets/tools/faucet'
            )
        }
        
        self.config = self.network_configs.get(self.network_name)
        if not self.config:
            self.available = False
            self.error = f"Unknown network: {self.network_name}"
            return
        
        # Override Blockfrost project ID if provided
        if blockfrost_project_id:
            self.config.blockfrost_project_id = blockfrost_project_id
        
        if not self.config.blockfrost_project_id:
            self.available = False
            self.error = f"Blockfrost project ID not configured for {self.network_name}"
            # Still initialize basic settings even without API keys
            self._initialize_basic_settings()
            return
        
        # Initialize chain context
        try:
            cardano_network = Network.MAINNET if self.network_name == 'mainnet' else Network.TESTNET
            self.chain_context = BlockFrostChainContext(
                project_id=self.config.blockfrost_project_id,
                network=cardano_network,
                base_url=self.config.blockfrost_base_url
            )
            self.available = True
            self.error = None
        except Exception as e:
            self.available = False
            self.error = f"Failed to initialize Cardano chain context: {e}"
            self._initialize_basic_settings()
            return
        
        # Initialize all settings
        self._initialize_basic_settings()
    
    def _initialize_basic_settings(self):
        """Initialize basic settings that don't require blockchain connection"""
        # Logging (initialize first)
        self.logger = logging.getLogger(f'cardano_service_{self.network_name}')
        
        # Service wallet (for platform operations)
        self.service_signing_key = self._load_service_key()
        self.service_address = None
        if self.service_signing_key:
            verification_key = PaymentVerificationKey.from_signing_key(self.service_signing_key)
            self.service_address = Address(verification_key.hash())
        
        # Nimo native token settings
        self.nimo_token_policy_id = os.getenv('NIMO_TOKEN_POLICY_ID', '')
        self.nimo_token_asset_name = os.getenv('NIMO_TOKEN_ASSET_NAME', 'NIMO')
        self.ada_to_nimo_rate = Decimal(os.getenv('ADA_TO_NIMO_RATE', '100'))  # 1 ADA = 100 NIMO
    
    def _load_service_key(self) -> Optional[PaymentSigningKey]:
        """Load service wallet signing key"""
        try:
            # Try to load from environment variable (hex format)
            key_hex = os.getenv('CARDANO_SERVICE_PRIVATE_KEY')
            if key_hex and key_hex != 'your_cardano_private_key_here':
                return PaymentSigningKey.from_primitive(bytes.fromhex(key_hex))
            
            # Try to load from file
            key_file = os.getenv('CARDANO_SERVICE_KEY_FILE', 'service_key.skey')
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    key_data = json.load(f)
                    return PaymentSigningKey.from_primitive(bytes.fromhex(key_data['cborHex']))
            
            self.logger.warning("Service signing key not configured")
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading service key: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if connected to Cardano network"""
        if not self.available:
            return False
        
        try:
            # Try to get latest block to test connection
            latest_block = self.chain_context.last_block_slot
            return latest_block is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def lovelace_to_ada(self, lovelace: int) -> Decimal:
        """Convert Lovelace to ADA"""
        return Decimal(lovelace) / Decimal(10 ** self.ADA_DECIMALS)
    
    def ada_to_lovelace(self, ada: Decimal) -> int:
        """Convert ADA to Lovelace"""
        return int(ada * Decimal(10 ** self.ADA_DECIMALS))
    
    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """Get ADA and native token balance for address"""
        try:
            if not self.available:
                return {'error': self.error}
            
            # Parse address
            addr = Address.from_bech32(address)
            
            # Get UTXOs for address
            utxos = self.chain_context.utxos(addr)
            
            # Calculate balances
            total_ada_lovelace = 0
            native_tokens = {}
            
            for utxo in utxos:
                # ADA balance
                total_ada_lovelace += utxo.output.amount.coin
                
                # Native tokens
                if utxo.output.amount.multi_asset:
                    for policy_id, assets in utxo.output.amount.multi_asset.data.items():
                        policy_hex = policy_id.to_primitive().hex()
                        if policy_hex not in native_tokens:
                            native_tokens[policy_hex] = {}
                        
                        for asset_name, quantity in assets.data.items():
                            asset_hex = asset_name.to_primitive().hex()
                            if asset_hex in native_tokens[policy_hex]:
                                native_tokens[policy_hex][asset_hex] += quantity
                            else:
                                native_tokens[policy_hex][asset_hex] = quantity
            
            # Get NIMO tokens specifically
            nimo_balance = 0
            if self.nimo_token_policy_id in native_tokens:
                nimo_asset_name_hex = AssetName(self.nimo_token_asset_name.encode()).to_primitive().hex()
                nimo_balance = native_tokens[self.nimo_token_policy_id].get(nimo_asset_name_hex, 0)
            
            return {
                'success': True,
                'address': address,
                'ada_lovelace': total_ada_lovelace,
                'ada': float(self.lovelace_to_ada(total_ada_lovelace)),
                'nimo_tokens': nimo_balance,
                'native_tokens': native_tokens,
                'utxo_count': len(utxos)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting balance for {address}: {e}")
            return {'error': str(e)}
    
    def send_ada(self, 
                 from_address: str,
                 to_address: str, 
                 ada_amount: Decimal,
                 signing_key: PaymentSigningKey = None,
                 metadata: Dict = None) -> Dict[str, Any]:
        """Send ADA from one address to another"""
        try:
            if not self.available:
                return {'error': self.error}
            
            # Use service key if no signing key provided
            if not signing_key:
                signing_key = self.service_signing_key
                if not signing_key:
                    return {'error': 'No signing key available'}
            
            # Parse addresses
            from_addr = Address.from_bech32(from_address)
            to_addr = Address.from_bech32(to_address)
            
            # Convert ADA to Lovelace
            lovelace_amount = self.ada_to_lovelace(ada_amount)
            
            # Build transaction
            builder = TransactionBuilder(self.chain_context)
            
            # Add output
            builder.add_output(
                TransactionOutput(to_addr, Value(lovelace_amount))
            )
            
            # Add metadata if provided
            if metadata:
                builder.auxiliary_data = metadata
            
            # Build and sign transaction
            transaction = builder.build_and_sign([signing_key], from_addr)
            
            # Submit transaction
            tx_hash = self.chain_context.submit_tx(transaction)
            
            self.logger.info(f"ADA transfer sent: {ada_amount} ADA from {from_address} to {to_address}, tx: {tx_hash}")
            
            return {
                'success': True,
                'tx_hash': str(tx_hash),
                'amount_ada': float(ada_amount),
                'amount_lovelace': lovelace_amount,
                'from_address': from_address,
                'to_address': to_address,
                'network': self.network_name
            }
            
        except Exception as e:
            self.logger.error(f"Error sending ADA: {e}")
            return {'error': str(e)}
    
    def mint_nimo_tokens(self,
                        to_address: str,
                        amount: int,
                        reason: str,
                        metta_proof: str) -> Dict[str, Any]:
        """Mint NIMO tokens for verified contributions"""
        try:
            if not self.available:
                return {'error': self.error}
            
            if not self.service_signing_key or not self.nimo_token_policy_id:
                return {'error': 'Service key or token policy not configured'}
            
            # Parse recipient address
            to_addr = Address.from_bech32(to_address)
            
            # Create token asset
            policy_id = ScriptHash.from_primitive(bytes.fromhex(self.nimo_token_policy_id))
            asset_name = AssetName(self.nimo_token_asset_name.encode())
            
            # Create multi-asset for minting
            multi_asset = MultiAsset({
                policy_id: Asset({asset_name: amount})
            })
            
            # Build transaction with minting
            builder = TransactionBuilder(self.chain_context)
            
            # Add output with tokens
            builder.add_output(
                TransactionOutput(
                    to_addr, 
                    Value(self.MIN_ADA_UTXO, multi_asset)
                )
            )
            
            # Add metadata with proof
            metadata = {
                "674": {  # CIP-25 metadata standard
                    "reason": reason,
                    "metta_proof": metta_proof,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            # Build and sign transaction
            transaction = builder.build_and_sign([self.service_signing_key], self.service_address)
            
            # Submit transaction
            tx_hash = self.chain_context.submit_tx(transaction)
            
            self.logger.info(f"NIMO tokens minted: {amount} NIMO to {to_address}, tx: {tx_hash}")
            
            return {
                'success': True,
                'tx_hash': str(tx_hash),
                'amount': amount,
                'to_address': to_address,
                'token_name': self.nimo_token_asset_name,
                'policy_id': self.nimo_token_policy_id,
                'reason': reason
            }
            
        except Exception as e:
            self.logger.error(f"Error minting NIMO tokens: {e}")
            return {'error': str(e)}
    
    def send_nimo_tokens(self,
                        from_address: str,
                        to_address: str,
                        amount: int,
                        signing_key: PaymentSigningKey = None) -> Dict[str, Any]:
        """Send NIMO tokens between addresses"""
        try:
            if not self.available:
                return {'error': self.error}
            
            # Use service key if no signing key provided
            if not signing_key:
                signing_key = self.service_signing_key
                if not signing_key:
                    return {'error': 'No signing key available'}
            
            # Parse addresses
            from_addr = Address.from_bech32(from_address)
            to_addr = Address.from_bech32(to_address)
            
            # Create token asset
            policy_id = ScriptHash.from_primitive(bytes.fromhex(self.nimo_token_policy_id))
            asset_name = AssetName(self.nimo_token_asset_name.encode())
            
            # Create multi-asset for transfer
            multi_asset = MultiAsset({
                policy_id: Asset({asset_name: amount})
            })
            
            # Build transaction
            builder = TransactionBuilder(self.chain_context)
            
            # Add output with tokens
            builder.add_output(
                TransactionOutput(
                    to_addr,
                    Value(self.MIN_ADA_UTXO, multi_asset)
                )
            )
            
            # Build and sign transaction
            transaction = builder.build_and_sign([signing_key], from_addr)
            
            # Submit transaction
            tx_hash = self.chain_context.submit_tx(transaction)
            
            self.logger.info(f"NIMO tokens sent: {amount} NIMO from {from_address} to {to_address}, tx: {tx_hash}")
            
            return {
                'success': True,
                'tx_hash': str(tx_hash),
                'amount': amount,
                'from_address': from_address,
                'to_address': to_address,
                'token_name': self.nimo_token_asset_name
            }
            
        except Exception as e:
            self.logger.error(f"Error sending NIMO tokens: {e}")
            return {'error': str(e)}
    
    def get_reward_calculation(self,
                             nimo_amount: int,
                             confidence: float,
                             contribution_type: str) -> Dict[str, Any]:
        """Calculate ADA and NIMO reward amounts"""
        
        # Base ADA reward calculation
        base_ada_amount = Decimal(nimo_amount) / self.ada_to_nimo_rate
        
        # Apply confidence multiplier
        confidence_multiplier = max(0.5, min(2.0, confidence + 0.5))  # 0.5x to 2.0x multiplier
        final_ada_amount = base_ada_amount * Decimal(str(confidence_multiplier))
        
        # Minimum thresholds
        min_ada_reward = Decimal('0.1')  # 0.1 ADA minimum
        min_confidence_for_ada = 0.7
        
        pays_ada = (final_ada_amount >= min_ada_reward and 
                   confidence >= min_confidence_for_ada)
        
        return {
            'nimo_amount': nimo_amount,
            'base_ada_amount': float(base_ada_amount),
            'confidence': confidence,
            'confidence_multiplier': confidence_multiplier,
            'final_ada_amount': float(final_ada_amount),
            'pays_ada': pays_ada,
            'min_confidence_required': min_confidence_for_ada,
            'contribution_type': contribution_type,
            'ada_to_nimo_rate': float(self.ada_to_nimo_rate)
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get status of a Cardano transaction"""
        try:
            if not self.available:
                return {'error': self.error}
            
            # Query transaction from Blockfrost
            tx_data = self.chain_context.api.transaction(tx_hash)
            
            if tx_data:
                return {
                    'tx_hash': tx_hash,
                    'status': 'confirmed',
                    'block_height': tx_data.get('block_height'),
                    'block_time': tx_data.get('block_time'),
                    'fees': tx_data.get('fees'),
                    'confirmed': True
                }
            else:
                return {
                    'tx_hash': tx_hash,
                    'status': 'not_found',
                    'confirmed': False
                }
                
        except Exception as e:
            return {
                'tx_hash': tx_hash,
                'status': 'error',
                'error': str(e),
                'confirmed': False
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information"""
        try:
            if not self.available:
                return {
                    'network': self.network_name,
                    'connected': False,
                    'error': self.error
                }
            
            # Get latest block info
            latest_block_slot = self.chain_context.last_block_slot
            
            return {
                'network': self.network_name,
                'connected': self.is_connected(),
                'latest_block_slot': latest_block_slot,
                'blockfrost_url': self.config.blockfrost_base_url,
                'faucet_url': self.config.faucet_url,
                'service_address': str(self.service_address) if self.service_address else None,
                'nimo_token_policy': self.nimo_token_policy_id,
                'nimo_token_name': self.nimo_token_asset_name,
                'ada_to_nimo_rate': float(self.ada_to_nimo_rate)
            }
        except Exception as e:
            return {
                'network': self.network_name,
                'connected': False,
                'error': str(e)
            }
    
    def get_faucet_info(self) -> Dict[str, Any]:
        """Get testnet faucet information"""
        if self.network_name == 'mainnet':
            return {'error': 'Faucet not available on mainnet'}
        
        return {
            'network': self.network_name,
            'faucet_url': self.config.faucet_url,
            'instructions': [
                '1. Go to the Cardano testnet faucet',
                '2. Enter your testnet address',
                '3. Click "Receive test ada"',
                '4. Funds will arrive within minutes'
            ],
            'note': 'Test ADA has no monetary value and is only for testing purposes'
        }
    
    def estimate_transaction_cost(self, operation: str, params: Dict = None) -> Dict[str, Any]:
        """Estimate transaction fees for different operations"""
        try:
            if not self.available:
                return {'error': self.error}
            
            # Rough fee estimates based on transaction complexity
            fee_estimates = {
                'send_ada': 170000,  # ~0.17 ADA
                'send_tokens': 200000,  # ~0.20 ADA
                'mint_tokens': 250000,  # ~0.25 ADA
                'smart_contract': 500000  # ~0.50 ADA
            }
            
            estimated_fee = fee_estimates.get(operation, 200000)
            
            return {
                'operation': operation,
                'estimated_fee_lovelace': estimated_fee,
                'estimated_fee_ada': float(self.lovelace_to_ada(estimated_fee)),
                'network': self.network_name,
                'note': 'Estimates are approximate. Actual fees may vary.'
            }
            
        except Exception as e:
            return {
                'operation': operation,
                'error': str(e)
            }

# Global instance
cardano_service = CardanoService()