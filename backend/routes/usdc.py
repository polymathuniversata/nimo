"""
USDC Integration Routes for Nimo Platform

These endpoints handle USDC reward calculations, payments, and monitoring.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
import logging

from services.usdc_integration import USDCIntegration
from services.metta_integration import MeTTaIntegration
from app import db
from models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
usdc_bp = Blueprint('usdc', __name__, url_prefix='/api/usdc')

# Initialize services
usdc_integration = USDCIntegration()
metta_integration = MeTTaIntegration()


@usdc_bp.route('/status', methods=['GET'])
@jwt_required()
def get_usdc_status():
    """
    Get USDC integration status and configuration
    
    Response:
    {
        "success": true,
        "data": {
            "network_status": {...},
            "service_account": {...},
            "enabled": true,
            "configuration": {...}
        }
    }
    """
    try:
        network_status = usdc_integration.get_network_status()
        service_account_info = usdc_integration.get_service_account_info()
        
        return jsonify({
            "success": True,
            "data": {
                "network_status": network_status,
                "service_account": service_account_info,
                "enabled": usdc_integration.usdc_enabled,
                "configuration": {
                    "nimo_to_usdc_rate": float(usdc_integration.nimo_to_usdc_rate),
                    "min_confidence_for_usdc": usdc_integration.min_confidence_for_usdc,
                    "usdc_decimals": usdc_integration.USDC_DECIMALS
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting USDC status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@usdc_bp.route('/balance/<address>', methods=['GET'])
@jwt_required()
def get_usdc_balance(address: str):
    """
    Get USDC balance for a specific address
    
    Response:
    {
        "success": true,
        "data": {
            "address": "0x...",
            "balance_usdc": 100.50,
            "network": "base-sepolia"
        }
    }
    """
    try:
        # Basic address validation
        if not address.startswith('0x') or len(address) != 42:
            return jsonify({
                "success": False,
                "error": "Invalid Ethereum address format"
            }), 400
        
        balance = usdc_integration.get_usdc_balance(address)
        
        return jsonify({
            "success": True,
            "data": {
                "address": address,
                "balance_usdc": float(balance),
                "network": usdc_integration.network,
                "usdc_contract": usdc_integration.base_config[usdc_integration.network]['usdc_address']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting USDC balance for {address}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get balance"
        }), 500


@usdc_bp.route('/calculate-reward', methods=['POST'])
@jwt_required()
def calculate_usdc_reward():
    """
    Calculate USDC reward for a given contribution scenario
    
    Request Body:
    {
        "nimo_amount": 100,
        "confidence": 0.85,
        "contribution_type": "coding"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "nimo_amount": 100,
            "base_usdc_amount": 1.00,
            "confidence": 0.85,
            "confidence_multiplier": 1.05,
            "final_usdc_amount": 1.05,
            "pays_usdc": true,
            "min_confidence_required": 0.8
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        nimo_amount = data.get('nimo_amount')
        confidence = data.get('confidence')
        contribution_type = data.get('contribution_type', 'general')
        
        if nimo_amount is None or confidence is None:
            return jsonify({
                "success": False,
                "error": "nimo_amount and confidence are required"
            }), 400
        
        if not isinstance(nimo_amount, (int, float)) or nimo_amount < 0:
            return jsonify({
                "success": False,
                "error": "nimo_amount must be a positive number"
            }), 400
        
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            return jsonify({
                "success": False,
                "error": "confidence must be between 0 and 1"
            }), 400
        
        calculation = usdc_integration.get_reward_calculation(
            nimo_amount=int(nimo_amount),
            confidence=float(confidence),
            contribution_type=contribution_type
        )
        
        return jsonify({
            "success": True,
            "data": calculation
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating USDC reward: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@usdc_bp.route('/estimate-gas', methods=['POST'])
@jwt_required()
def estimate_gas_for_reward():
    """
    Estimate gas cost for USDC reward transfer
    
    Request Body:
    {
        "to_address": "0x...",
        "usdc_amount": 1.50
    }
    
    Response:
    {
        "success": true,
        "data": {
            "gas_estimate": 65000,
            "gas_price_gwei": 1.2,
            "total_gas_cost_eth": 0.000078,
            "usdc_amount": 1.50
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        to_address = data.get('to_address')
        usdc_amount = data.get('usdc_amount')
        
        if not to_address or not usdc_amount:
            return jsonify({
                "success": False,
                "error": "to_address and usdc_amount are required"
            }), 400
        
        # Basic address validation
        if not to_address.startswith('0x') or len(to_address) != 42:
            return jsonify({
                "success": False,
                "error": "Invalid to_address format"
            }), 400
        
        from decimal import Decimal
        estimation = usdc_integration.estimate_gas_for_transfer(
            to_address=to_address,
            usdc_amount=Decimal(str(usdc_amount))
        )
        
        if 'error' in estimation:
            return jsonify({
                "success": False,
                "error": estimation['error']
            }), 400
        
        return jsonify({
            "success": True,
            "data": estimation
        }), 200
        
    except Exception as e:
        logger.error(f"Error estimating gas for USDC transfer: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@usdc_bp.route('/verify-payment/<tx_hash>', methods=['GET'])
@jwt_required()
def verify_usdc_payment(tx_hash: str):
    """
    Verify a USDC payment transaction
    
    Response:
    {
        "success": true,
        "data": {
            "verified": true,
            "tx_hash": "0x...",
            "block_number": 12345,
            "transfer_event": {
                "from": "0x...",
                "to": "0x...",
                "value_usdc": 1.50
            }
        }
    }
    """
    try:
        if not tx_hash.startswith('0x'):
            return jsonify({
                "success": False,
                "error": "Invalid transaction hash format"
            }), 400
        
        verification_result = usdc_integration.verify_usdc_payment(tx_hash)
        
        return jsonify({
            "success": True,
            "data": verification_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error verifying USDC payment {tx_hash}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to verify payment"
        }), 500


@usdc_bp.route('/contribution-reward-preview', methods=['POST'])
@jwt_required()
def preview_contribution_reward():
    """
    Preview the complete reward (NIMO + USDC) for a contribution using MeTTa reasoning
    
    Request Body:
    {
        "contribution_id": "contrib123",
        "contribution_data": {  // Optional
            "category": "coding",
            "title": "Smart Contract Development",
            "evidence": [...]
        }
    }
    
    Response:
    {
        "success": true,
        "data": {
            "metta_analysis": {
                "verified": true,
                "confidence": 0.9,
                "nimo_tokens": 75
            },
            "usdc_reward": {
                "pays_usdc": true,
                "amount_usd": 0.90,
                "confidence_multiplier": 1.1
            },
            "total_reward": {
                "nimo_tokens": 75,
                "usdc_amount": 0.90,
                "estimated_total_usd": 1.65
            }
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        contribution_id = data.get('contribution_id')
        contribution_data = data.get('contribution_data')
        
        if not contribution_id:
            return jsonify({
                "success": False,
                "error": "contribution_id is required"
            }), 400
        
        # Get MeTTa analysis
        metta_result = metta_integration.validate_contribution(contribution_id, contribution_data)
        
        if not metta_result.get('verified'):
            return jsonify({
                "success": True,
                "data": {
                    "metta_analysis": metta_result,
                    "usdc_reward": {"pays_usdc": False, "reason": "Contribution not verified"},
                    "total_reward": {"nimo_tokens": 0, "usdc_amount": 0, "estimated_total_usd": 0}
                }
            }), 200
        
        # Calculate USDC reward
        contribution_type = contribution_data.get('category') if contribution_data else 'general'
        usdc_calculation = usdc_integration.get_reward_calculation(
            nimo_amount=metta_result.get('token_award', 0),
            confidence=metta_result.get('confidence', 0),
            contribution_type=contribution_type
        )
        
        # Calculate total USD value
        nimo_usd_value = metta_result.get('token_award', 0) * float(usdc_integration.nimo_to_usdc_rate)
        usdc_amount = usdc_calculation.get('final_usdc_amount', 0)
        total_usd = nimo_usd_value + usdc_amount
        
        return jsonify({
            "success": True,
            "data": {
                "metta_analysis": {
                    "verified": metta_result.get('verified'),
                    "confidence": metta_result.get('confidence'),
                    "nimo_tokens": metta_result.get('token_award'),
                    "explanation": metta_result.get('explanation')
                },
                "usdc_reward": {
                    "pays_usdc": usdc_calculation.get('pays_usdc'),
                    "amount_usd": usdc_amount,
                    "confidence_multiplier": usdc_calculation.get('confidence_multiplier')
                },
                "total_reward": {
                    "nimo_tokens": metta_result.get('token_award', 0),
                    "usdc_amount": usdc_amount,
                    "nimo_usd_equivalent": nimo_usd_value,
                    "estimated_total_usd": total_usd
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error previewing contribution reward: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@usdc_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_current_user_usdc_balance():
    """
    Get USDC balance for current user's wallet

    Response:
    {
        "success": true,
        "data": {
            "balance": "100.50",
            "formatted_balance": "100.50 USDC",
            "wallet_address": "0x...",
            "network": "base-sepolia"
        }
    }
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or not user.wallet_address:
            return jsonify({
                "success": False,
                "error": "User has no associated wallet address"
            }), 400

        # Get USDC balance
        balance_info = usdc_integration.get_balance(user.wallet_address)

        return jsonify({
            "success": True,
            "data": {
                "balance": balance_info.get('balance', '0'),
                "formatted_balance": balance_info.get('formatted_balance', '0 USDC'),
                "wallet_address": user.wallet_address,
                "network": usdc_integration.network
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get USDC balance: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve USDC balance"
        }), 500


@usdc_bp.route('/send', methods=['POST'])
@jwt_required()
def send_usdc():
    """
    Send USDC to a recipient address

    Request Body:
    {
        "amount": "10.50",
        "recipient_address": "0x...",
        "reason": "Contribution reward"
    }

    Response:
    {
        "success": true,
        "data": {
            "tx_hash": "0x...",
            "amount": "10.50",
            "recipient": "0x...",
            "gas_used": "21000",
            "network": "base-sepolia"
        }
    }
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or not user.wallet_address:
            return jsonify({
                "success": False,
                "error": "User has no associated wallet address"
            }), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['amount', 'recipient_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        amount = data['amount']
        recipient_address = data['recipient_address']
        reason = data.get('reason', 'USDC Transfer')

        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return jsonify({
                    "success": False,
                    "error": "Amount must be greater than 0"
                }), 400
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid amount format"
            }), 400

        # Send USDC
        tx_result = usdc_integration.send_usdc(
            from_address=user.wallet_address,
            to_address=recipient_address,
            amount=amount,
            reason=reason
        )

        return jsonify({
            "success": True,
            "data": {
                "tx_hash": tx_result.get('tx_hash'),
                "amount": amount,
                "recipient": recipient_address,
                "gas_used": tx_result.get('gas_used', '0'),
                "network": usdc_integration.network,
                "reason": reason
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to send USDC: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to send USDC"
        }), 500


# Error handlers
@usdc_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@usdc_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405