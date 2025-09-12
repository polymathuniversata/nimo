"""
DEPRECATED: Legacy USDC Integration Service

⚠️  DEPRECATED - DO NOT USE ⚠️

This service has been replaced by Cardano native token services.
All functionality has been migrated to:

- services/cardano_service.py - Core Cardano blockchain operations
- services/blockchain_token_service.py - Token management
- services/token_service.py - Unified token operations

This file is kept for backward compatibility but will be removed in a future version.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from flask import current_app

# Import Cardano services
from services.cardano_service import CardanoService
from services.blockchain_token_service import BlockchainTokenService
from services.token_service import TokenService

class USDCIntegration:
    """
    DEPRECATED: Legacy USDC integration service

    This class now acts as a compatibility layer that redirects
    all operations to the new Cardano-based services.
    """

    # Legacy constants (kept for compatibility)
    USDC_DECIMALS = 6

    def __init__(self, network: str = None):
        """Initialize with Cardano services"""
        current_app.logger.warning(
            "USDCIntegration is deprecated. Use CardanoService, BlockchainTokenService, or TokenService instead."
        )

        # Initialize Cardano services
        self.cardano_service = CardanoService()
        self.token_service = BlockchainTokenService()
        self.unified_token_service = TokenService()

        # Legacy network mapping (for compatibility)
        self.network = network or os.getenv('BLOCKCHAIN_NETWORK', 'cardano-preprod')

        # Legacy configuration (deprecated)
        self.base_config = {
            'cardano-preprod': {
                'chain_id': 0,
                'rpc_url': os.getenv('CARDANO_PREPROD_RPC_URL', 'https://cardano-preprod.blockfrost.io/api/v0'),
                'usdc_address': '',  # No longer used
                'explorer_url': 'https://preprod.cardanoscan.io'
            },
            'cardano-mainnet': {
                'chain_id': 1,
                'rpc_url': os.getenv('CARDANO_MAINNET_RPC_URL', 'https://cardano-mainnet.blockfrost.io/api/v0'),
                'usdc_address': '',  # No longer used
                'explorer_url': 'https://cardanoscan.io'
            }
        }

        # Legacy properties (deprecated)
        self.nimo_to_usdc_rate = Decimal('0.01')
        self.min_confidence_for_usdc = float(os.getenv('METTA_MIN_CONFIDENCE_FOR_USDC', '0.8'))
        self.usdc_enabled = False  # Always disabled for legacy compatibility
        
    def _load_service_account(self):
        """DEPRECATED: Service account loading - redirect to Cardano service"""
        current_app.logger.warning("_load_service_account is deprecated. Use CardanoService instead.")
        return None

    def is_connected(self) -> bool:
        """Check if connected to blockchain network"""
        return self.cardano_service.is_connected()

    def get_usdc_balance(self, address: str) -> Decimal:
        """DEPRECATED: Get balance - redirect to Cardano service"""
        current_app.logger.warning("get_usdc_balance is deprecated. Use BlockchainTokenService.get_token_balance instead.")
        try:
            # Try to get ADA balance as a substitute
            balance_result = self.cardano_service.get_balance(address)
            if balance_result.get('success'):
                # Return ADA balance in lovelace (1 ADA = 1,000,000 lovelace)
                ada_balance = balance_result.get('ada_balance', 0)
                return Decimal(str(ada_balance)) / Decimal('1000000')  # Convert to ADA
            return Decimal('0')
        except Exception as e:
            current_app.logger.error(f"Error getting balance for {address}: {e}")
            return Decimal('0')

    def convert_nimo_to_usdc_amount(self, nimo_amount: int) -> Decimal:
        """DEPRECATED: Convert NIMO to USDC - redirect to token service"""
        current_app.logger.warning("convert_nimo_to_usdc_amount is deprecated. Use TokenService for conversions.")
        # Return equivalent ADA amount (rough approximation)
        return Decimal(str(nimo_amount)) * Decimal('0.001')  # 1 NIMO ≈ 0.001 ADA

    def convert_usdc_to_wei(self, usdc_amount: Decimal) -> int:
        """DEPRECATED: Convert USDC to wei - not applicable for Cardano"""
        current_app.logger.warning("convert_usdc_to_wei is deprecated. Cardano uses lovelace (1 ADA = 1,000,000 lovelace).")
        # Convert to lovelace equivalent
        return int(usdc_amount * Decimal('1000000'))

    def estimate_gas_for_transfer(self, to_address: str, usdc_amount: Decimal) -> Dict:
        """DEPRECATED: Estimate gas - redirect to Cardano service"""
        current_app.logger.warning("estimate_gas_for_transfer is deprecated. Use CardanoService.estimate_fee instead.")
        try:
            # Use Cardano fee estimation
            fee_result = self.cardano_service.estimate_transaction_fee()
            if fee_result.get('success'):
                return {
                    'gas_estimate': fee_result.get('estimated_fee', 0),
                    'gas_price_wei': 0,  # Not applicable for Cardano
                    'gas_price_gwei': 0,  # Not applicable for Cardano
                    'total_gas_cost_wei': 0,  # Not applicable for Cardano
                    'total_gas_cost_eth': 0,  # Not applicable for Cardano
                    'ada_amount': float(usdc_amount),  # Treat as ADA amount
                    'ada_lovelace': int(usdc_amount * Decimal('1000000')),
                    'estimated_fee_ada': fee_result.get('estimated_fee_ada', 0)
                }
            return {'error': 'Fee estimation failed'}
        except Exception as e:
            return {'error': str(e)}

    def send_usdc_reward(self,
                        to_address: str,
                        nimo_amount: int,
                        contribution_id: str,
                        metta_proof: str) -> Optional[str]:
        """DEPRECATED: Send reward - redirect to token service"""
        current_app.logger.warning("send_usdc_reward is deprecated. Use BlockchainTokenService.send_reward instead.")
        try:
            # Use unified token service for rewards
            reward_result = self.unified_token_service.send_reward(
                to_address=to_address,
                amount=nimo_amount,
                contribution_id=contribution_id,
                reward_type='nimo'
            )
            if reward_result.get('success'):
                return reward_result.get('tx_hash')
            return None
        except Exception as e:
            current_app.logger.error(f"Error sending reward: {e}")
            return None

    def batch_send_usdc_rewards(self, rewards: List[Dict]) -> List[Optional[str]]:
        """DEPRECATED: Batch send rewards - redirect to token service"""
        current_app.logger.warning("batch_send_usdc_rewards is deprecated. Use BlockchainTokenService.batch_send_rewards instead.")
        results = []
        for reward in rewards:
            tx_hash = self.send_usdc_reward(
                reward['to_address'],
                reward['nimo_amount'],
                reward['contribution_id'],
                reward.get('metta_proof', '')
            )
            results.append(tx_hash)
        return results

    def verify_usdc_payment(self, tx_hash: str) -> Dict:
        """DEPRECATED: Verify payment - redirect to Cardano service"""
        current_app.logger.warning("verify_usdc_payment is deprecated. Use CardanoService.verify_transaction instead.")
        try:
            return self.cardano_service.verify_transaction(tx_hash)
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
        """DEPRECATED: Get reward calculation - redirect to token service"""
        current_app.logger.warning("get_reward_calculation is deprecated. Use TokenService.calculate_reward instead.")
        try:
            return self.unified_token_service.calculate_reward(
                nimo_amount=nimo_amount,
                confidence=confidence,
                contribution_type=contribution_type
            )
        except Exception as e:
            # Fallback to legacy calculation
            return {
                'nimo_amount': nimo_amount,
                'base_usdc_amount': 0,  # Deprecated
                'confidence': confidence,
                'confidence_multiplier': 1.0,
                'final_usdc_amount': 0,  # Deprecated
                'pays_usdc': False,  # Always false for legacy
                'min_confidence_required': self.min_confidence_for_usdc,
                'usdc_enabled': False,  # Always disabled
                'contribution_type': contribution_type,
                'error': str(e)
            }

    def get_service_account_info(self) -> Dict:
        """DEPRECATED: Get service account info - redirect to Cardano service"""
        current_app.logger.warning("get_service_account_info is deprecated. Use CardanoService.get_wallet_info instead.")
        try:
            return self.cardano_service.get_wallet_info()
        except Exception as e:
            return {'error': str(e)}

    def get_network_status(self) -> Dict:
        """Get network status and configuration"""
        try:
            status_result = self.cardano_service.get_network_status()
            if status_result.get('success'):
                status = status_result
                status.update({
                    'usdc_enabled': False,  # Always disabled for legacy
                    'min_confidence_for_usdc': self.min_confidence_for_usdc,
                    'nimo_to_usdc_rate': float(self.nimo_to_usdc_rate),
                    'migration_note': 'USDC integration migrated to Cardano native tokens'
                })
                return status
            return {
                'network': self.network,
                'connected': False,
                'error': 'Network status unavailable',
                'usdc_enabled': False,
                'migration_note': 'USDC integration migrated to Cardano native tokens'
            }
        except Exception as e:
            return {
                'network': self.network,
                'connected': False,
                'error': str(e),
                'usdc_enabled': False,
                'migration_note': 'USDC integration migrated to Cardano native tokens'
            }

    def get_balance(self, address: str) -> Dict:
        """DEPRECATED: Get balance - redirect to token service"""
        current_app.logger.warning("get_balance is deprecated. Use BlockchainTokenService.get_token_balance instead.")
        try:
            # This method might be called by legacy code
            balance_result = self.token_service.get_token_balance_by_address(address)
            return balance_result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'balance': '0',
                'formatted_balance': '0 USDC'
            }

    def send_usdc(self, from_address: str, to_address: str, amount: str, reason: str) -> Dict:
        """DEPRECATED: Send USDC - redirect to token service"""
        current_app.logger.warning("send_usdc is deprecated. Use BlockchainTokenService.send_tokens instead.")
        try:
            # Convert amount to appropriate format
            amount_decimal = Decimal(amount)

            # Use token service to send
            send_result = self.unified_token_service.send_tokens(
                from_address=from_address,
                to_address=to_address,
                amount=int(amount_decimal * Decimal('1000000')),  # Convert to lovelace
                token_type='ada'
            )

            return {
                'success': send_result.get('success', False),
                'tx_hash': send_result.get('tx_hash'),
                'amount': amount,
                'recipient': to_address,
                'reason': reason
            }
        except Exception as e:
            current_app.logger.error(f"Error sending tokens: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global instance (deprecated)
usdc_integration = USDCIntegration()