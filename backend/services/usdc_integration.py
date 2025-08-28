"""
USDC Integration Service for Nimo Platform

This service handles USDC token interactions on Base network,
integrating with MeTTa reasoning for automated reward payments.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from flask import current_app

class USDCIntegration:
    """Service for integrating USDC payments with MeTTa rewards system"""
    
    # USDC has 6 decimals (not 18 like ETH)
    USDC_DECIMALS = 6
    
    # Standard USDC ERC20 ABI (minimal required functions)
    USDC_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_from", "type": "address"},
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transferFrom",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_spender", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        }
    ]
    
    def __init__(self, network: str = None):
        """Initialize USDC integration service"""
        self.network = network or os.getenv('BLOCKCHAIN_NETWORK', 'base-sepolia')
        
        # Network configurations
        self.base_config = {
            'base-sepolia': {
                'chain_id': 84532,
                'rpc_url': os.getenv('BASE_SEPOLIA_RPC_URL', 'https://sepolia.base.org'),
                'usdc_address': os.getenv('USDC_CONTRACT_BASE_SEPOLIA', '0x036CbD53842c5426634e7929541eC2318f3dCF7e'),
                'explorer_url': 'https://sepolia.basescan.org'
            },
            'base-mainnet': {
                'chain_id': 8453,
                'rpc_url': os.getenv('BASE_MAINNET_RPC_URL', 'https://mainnet.base.org'),
                'usdc_address': os.getenv('USDC_CONTRACT_BASE_MAINNET', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'),
                'explorer_url': 'https://basescan.org'
            },
            'polygon-mumbai': {
                'chain_id': 80001,
                'rpc_url': os.getenv('WEB3_PROVIDER_URL', 'https://polygon-mumbai.g.alchemy.com/v2/demo'),
                'usdc_address': os.getenv('USDC_CONTRACT_POLYGON_MUMBAI', '0x4CE536b148BF86Ce30E2A28E610e3B2df973d9Af'),
                'explorer_url': 'https://mumbai.polygonscan.com'
            }
        }
        
        # Initialize Web3
        self.web3 = Web3(Web3.HTTPProvider(self.base_config[self.network]['rpc_url']))
        
        # Initialize USDC contract
        usdc_address = self.base_config[self.network]['usdc_address']
        self.usdc_contract = self.web3.eth.contract(
            address=usdc_address,
            abi=self.USDC_ABI
        )
        
        # Service account for payments
        self.service_account = self._load_service_account()
        
        # Conversion rates and thresholds
        self.nimo_to_usdc_rate = Decimal('0.01')  # 1 NIMO token = $0.01 USDC
        self.min_confidence_for_usdc = float(os.getenv('METTA_MIN_CONFIDENCE_FOR_USDC', '0.8'))
        self.usdc_enabled = os.getenv('METTA_ENABLE_USDC_PAYMENTS', 'False').lower() == 'true'
        
    def _load_service_account(self):
        """Load service account for USDC payments"""
        private_key = os.getenv('BLOCKCHAIN_SERVICE_PRIVATE_KEY')
        if private_key and private_key != 'your_service_private_key_here':
            return Account.from_key(private_key)
        return None
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain network"""
        return self.web3.is_connected()
    
    def get_usdc_balance(self, address: str) -> Decimal:
        """Get USDC balance for address in human-readable format"""
        try:
            balance_wei = self.usdc_contract.functions.balanceOf(address).call()
            return Decimal(balance_wei) / Decimal(10 ** self.USDC_DECIMALS)
        except Exception as e:
            current_app.logger.error(f"Error getting USDC balance for {address}: {e}")
            return Decimal('0')
    
    def convert_nimo_to_usdc_amount(self, nimo_amount: int) -> Decimal:
        """Convert NIMO token amount to USDC amount"""
        return Decimal(nimo_amount) * self.nimo_to_usdc_rate
    
    def convert_usdc_to_wei(self, usdc_amount: Decimal) -> int:
        """Convert USDC amount to wei (6 decimal places)"""
        return int(usdc_amount * Decimal(10 ** self.USDC_DECIMALS))
    
    def estimate_gas_for_transfer(self, to_address: str, usdc_amount: Decimal) -> Dict:
        """Estimate gas cost for USDC transfer"""
        try:
            if not self.service_account:
                return {'error': 'Service account not configured'}
            
            usdc_wei = self.convert_usdc_to_wei(usdc_amount)
            
            # Estimate gas for transfer
            gas_estimate = self.usdc_contract.functions.transfer(
                to_address, usdc_wei
            ).estimate_gas({'from': self.service_account.address})
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Calculate costs in ETH (Base network uses ETH for gas)
            gas_cost_wei = gas_estimate * gas_price
            gas_cost_eth = self.web3.from_wei(gas_cost_wei, 'ether')
            
            return {
                'gas_estimate': gas_estimate,
                'gas_price_wei': gas_price,
                'gas_price_gwei': self.web3.from_wei(gas_price, 'gwei'),
                'total_gas_cost_wei': gas_cost_wei,
                'total_gas_cost_eth': float(gas_cost_eth),
                'usdc_amount': float(usdc_amount),
                'usdc_wei': usdc_wei
            }
        except Exception as e:
            return {'error': str(e)}
    
    def send_usdc_reward(self, 
                        to_address: str, 
                        nimo_amount: int, 
                        contribution_id: str, 
                        metta_proof: str) -> Optional[str]:
        """Send USDC reward based on NIMO token calculation"""
        if not self.usdc_enabled:
            current_app.logger.info(f"USDC payments disabled, skipping reward for contribution {contribution_id}")
            return None
        
        if not self.service_account:
            current_app.logger.error("Service account not configured for USDC payments")
            return None
        
        try:
            # Convert NIMO to USDC amount
            usdc_amount = self.convert_nimo_to_usdc_amount(nimo_amount)
            usdc_wei = self.convert_usdc_to_wei(usdc_amount)
            
            # Check if we have sufficient balance
            service_balance = self.get_usdc_balance(self.service_account.address)
            if service_balance < usdc_amount:
                current_app.logger.error(f"Insufficient USDC balance. Need {usdc_amount}, have {service_balance}")
                return None
            
            # Build transaction
            transaction = self.usdc_contract.functions.transfer(
                to_address, usdc_wei
            ).build_transaction({
                'from': self.service_account.address,
                'nonce': self.web3.eth.get_transaction_count(self.service_account.address),
                'chainId': self.base_config[self.network]['chain_id']
            })
            
            # Estimate and set gas
            gas_estimate = self.web3.eth.estimate_gas(transaction)
            transaction['gas'] = int(gas_estimate * 1.2)  # 20% buffer
            transaction['gasPrice'] = self.web3.eth.gas_price
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.service_account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            tx_hash_hex = tx_hash.hex()
            
            current_app.logger.info(
                f"USDC reward sent: {usdc_amount} USDC to {to_address} "
                f"for contribution {contribution_id}, tx: {tx_hash_hex}"
            )
            
            return tx_hash_hex
            
        except Exception as e:
            current_app.logger.error(f"Error sending USDC reward: {e}")
            return None
    
    def batch_send_usdc_rewards(self, rewards: List[Dict]) -> List[Optional[str]]:
        """Send multiple USDC rewards in batch (if supported by network)"""
        # For now, send individual transactions
        # TODO: Implement multicall or batch transaction support
        results = []
        
        for reward in rewards:
            tx_hash = self.send_usdc_reward(
                reward['to_address'],
                reward['nimo_amount'],
                reward['contribution_id'],
                reward['metta_proof']
            )
            results.append(tx_hash)
        
        return results
    
    def verify_usdc_payment(self, tx_hash: str) -> Dict:
        """Verify USDC payment transaction"""
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                # Parse transfer event
                transfer_event = None
                for log in receipt['logs']:
                    if log['address'].lower() == self.usdc_contract.address.lower():
                        # This is a USDC transfer event
                        decoded = self.usdc_contract.events.Transfer().process_log(log)
                        transfer_event = {
                            'from': decoded['args']['from'],
                            'to': decoded['args']['to'],
                            'value_wei': decoded['args']['value'],
                            'value_usdc': float(Decimal(decoded['args']['value']) / Decimal(10 ** self.USDC_DECIMALS))
                        }
                        break
                
                return {
                    'success': True,
                    'tx_hash': tx_hash,
                    'block_number': receipt['blockNumber'],
                    'gas_used': receipt['gasUsed'],
                    'transfer_event': transfer_event,
                    'explorer_url': f"{self.base_config[self.network]['explorer_url']}/tx/{tx_hash}"
                }
            else:
                return {
                    'success': False,
                    'tx_hash': tx_hash,
                    'error': 'Transaction failed'
                }
        except Exception as e:
            return {
                'success': False,
                'tx_hash': tx_hash,
                'error': str(e)
            }
    
    def get_reward_calculation(self, 
                             nimo_amount: int, 
                             confidence: float, 
                             contribution_type: str) -> Dict:
        """Calculate reward amounts including USDC conversion"""
        # Base USDC amount from NIMO tokens
        base_usdc_amount = self.convert_nimo_to_usdc_amount(nimo_amount)
        
        # Apply confidence multiplier for USDC rewards
        if confidence >= self.min_confidence_for_usdc:
            # High confidence contributions get full USDC reward
            usdc_multiplier = min(1.5, confidence + 0.2)  # Cap at 1.5x, min confidence boost
        else:
            # Low confidence contributions get reduced/no USDC reward
            usdc_multiplier = max(0.1, confidence - 0.2)  # Minimum 10% if very low confidence
        
        final_usdc_amount = base_usdc_amount * Decimal(str(usdc_multiplier))
        
        # Minimum USDC payout threshold
        min_usdc_payout = Decimal('0.01')  # $0.01 minimum
        pays_usdc = (final_usdc_amount >= min_usdc_payout and 
                    confidence >= self.min_confidence_for_usdc and 
                    self.usdc_enabled)
        
        return {
            'nimo_amount': nimo_amount,
            'base_usdc_amount': float(base_usdc_amount),
            'confidence': confidence,
            'confidence_multiplier': usdc_multiplier,
            'final_usdc_amount': float(final_usdc_amount),
            'pays_usdc': pays_usdc,
            'min_confidence_required': self.min_confidence_for_usdc,
            'usdc_enabled': self.usdc_enabled,
            'contribution_type': contribution_type
        }
    
    def get_service_account_info(self) -> Dict:
        """Get service account information"""
        if not self.service_account:
            return {'error': 'Service account not configured'}
        
        try:
            eth_balance = self.web3.eth.get_balance(self.service_account.address)
            usdc_balance = self.get_usdc_balance(self.service_account.address)
            
            return {
                'address': self.service_account.address,
                'eth_balance_wei': eth_balance,
                'eth_balance': float(self.web3.from_wei(eth_balance, 'ether')),
                'usdc_balance': float(usdc_balance),
                'network': self.network,
                'chain_id': self.base_config[self.network]['chain_id'],
                'usdc_contract': self.base_config[self.network]['usdc_address']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_network_status(self) -> Dict:
        """Get network status and configuration"""
        try:
            latest_block = self.web3.eth.get_block('latest')
            gas_price = self.web3.eth.gas_price
            
            return {
                'network': self.network,
                'connected': self.is_connected(),
                'chain_id': self.base_config[self.network]['chain_id'],
                'latest_block': latest_block['number'],
                'gas_price_wei': gas_price,
                'gas_price_gwei': float(self.web3.from_wei(gas_price, 'gwei')),
                'usdc_contract': self.base_config[self.network]['usdc_address'],
                'usdc_enabled': self.usdc_enabled,
                'min_confidence_for_usdc': self.min_confidence_for_usdc,
                'nimo_to_usdc_rate': float(self.nimo_to_usdc_rate),
                'explorer_url': self.base_config[self.network]['explorer_url']
            }
        except Exception as e:
            return {
                'network': self.network,
                'connected': False,
                'error': str(e)
            }

# Global instance
usdc_integration = USDCIntegration()