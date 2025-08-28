"""
Cardano Integration Routes for Nimo Platform

These endpoints handle ADA transfers, NIMO token operations, and Cardano blockchain interactions.
Replaces the previous USDC-based reward system.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
import logging
from decimal import Decimal

from services.cardano_service import cardano_service
from services.metta_integration_enhanced import get_metta_service
from app import db
from models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
cardano_bp = Blueprint('cardano', __name__, url_prefix='/api/cardano')

# Initialize services
metta_integration = get_metta_service()


@cardano_bp.route('/status', methods=['GET'])
@jwt_required()
def get_cardano_status():
    """
    Get Cardano integration status and configuration
    
    Response:
    {
        "success": true,
        "data": {
            "network_info": {...},
            "service_account": {...},
            "available": true,
            "configuration": {...}
        }
    }
    """
    try:
        network_info = cardano_service.get_network_info()
        
        return jsonify({
            "success": True,
            "data": {
                "network_info": network_info,
                "available": cardano_service.available,
                "configuration": {
                    "ada_to_nimo_rate": float(cardano_service.ada_to_nimo_rate),
                    "min_ada_utxo": cardano_service.MIN_ADA_UTXO,
                    "ada_decimals": cardano_service.ADA_DECIMALS,
                    "network": cardano_service.network_name
                },
                "faucet_info": cardano_service.get_faucet_info() if cardano_service.network_name != 'mainnet' else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting Cardano status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@cardano_bp.route('/balance/<address>', methods=['GET'])
@jwt_required()
def get_address_balance(address: str):
    """
    Get ADA and NIMO token balance for a specific address
    
    Response:
    {
        "success": true,
        "data": {
            "address": "addr_test1...",
            "ada_balance": 100.5,
            "nimo_balance": 1250,
            "network": "preview"
        }
    }
    """
    try:
        if not cardano_service.available:
            return jsonify({
                "success": False,
                "error": f"Cardano service unavailable: {cardano_service.error}"
            }), 503
        
        # Basic address validation (Cardano bech32 format)
        if not (address.startswith('addr') or address.startswith('addr_test')):
            return jsonify({
                "success": False,
                "error": "Invalid Cardano address format"
            }), 400
        
        balance_info = cardano_service.get_address_balance(address)
        
        if 'error' in balance_info:
            return jsonify({
                "success": False,
                "error": balance_info['error']
            }), 400
        
        return jsonify({
            "success": True,
            "data": {
                "address": address,
                "ada_balance": balance_info['ada'],
                "ada_lovelace": balance_info['ada_lovelace'],
                "nimo_balance": balance_info['nimo_tokens'],
                "utxo_count": balance_info['utxo_count'],
                "native_tokens": balance_info.get('native_tokens', {}),
                "network": cardano_service.network_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting balance for {address}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get balance"
        }), 500


@cardano_bp.route('/calculate-reward', methods=['POST'])
@jwt_required()
def calculate_cardano_reward():
    """
    Calculate ADA reward for a given contribution scenario
    
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
            "base_ada_amount": 1.00,
            "confidence": 0.85,
            "confidence_multiplier": 1.35,
            "final_ada_amount": 1.35,
            "pays_ada": true,
            "min_confidence_required": 0.7
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
        
        calculation = cardano_service.get_reward_calculation(
            nimo_amount=int(nimo_amount),
            confidence=float(confidence),
            contribution_type=contribution_type
        )
        
        return jsonify({
            "success": True,
            "data": calculation
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating Cardano reward: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@cardano_bp.route('/estimate-fees', methods=['POST'])
@jwt_required()
def estimate_transaction_fees():
    """
    Estimate transaction fees for Cardano operations
    
    Request Body:
    {
        "operation": "send_ada",
        "params": {
            "amount": 10.5
        }
    }
    
    Response:
    {
        "success": true,
        "data": {
            "operation": "send_ada",
            "estimated_fee_ada": 0.17,
            "estimated_fee_lovelace": 170000
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
        
        operation = data.get('operation')
        params = data.get('params', {})
        
        if not operation:
            return jsonify({
                "success": False,
                "error": "operation is required"
            }), 400
        
        estimation = cardano_service.estimate_transaction_cost(operation, params)
        
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
        logger.error(f"Error estimating transaction fees: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@cardano_bp.route('/send-ada', methods=['POST'])
@jwt_required()
def send_ada():
    """
    Send ADA to a recipient address
    
    Request Body:
    {
        "amount": "10.5",
        "recipient_address": "addr_test1...",
        "reason": "Contribution reward"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "tx_hash": "abc123...",
            "amount_ada": 10.5,
            "recipient": "addr_test1...",
            "network": "preview"
        }
    }
    """
    try:
        if not cardano_service.available:
            return jsonify({
                "success": False,
                "error": f"Cardano service unavailable: {cardano_service.error}"
            }), 503
        
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['amount', 'recipient_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        amount_str = data['amount']
        recipient_address = data['recipient_address']
        reason = data.get('reason', 'ADA Transfer')

        # Validate amount
        try:
            amount = Decimal(str(amount_str))
            if amount <= 0:
                return jsonify({
                    "success": False,
                    "error": "Amount must be greater than 0"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid amount format"
            }), 400

        # Validate recipient address
        if not (recipient_address.startswith('addr') or recipient_address.startswith('addr_test')):
            return jsonify({
                "success": False,
                "error": "Invalid recipient address format"
            }), 400

        # Note: This requires user's Cardano address and signing key
        # For now, we'll use the service account (in a real implementation, 
        # users would need to connect their Cardano wallets)
        from_address = str(cardano_service.service_address) if cardano_service.service_address else None
        if not from_address:
            return jsonify({
                "success": False,
                "error": "Service wallet not configured"
            }), 503

        # Send ADA
        tx_result = cardano_service.send_ada(
            from_address=from_address,
            to_address=recipient_address,
            ada_amount=amount
        )

        if 'error' in tx_result:
            return jsonify({
                "success": False,
                "error": tx_result['error']
            }), 400

        return jsonify({
            "success": True,
            "data": {
                "tx_hash": tx_result['tx_hash'],
                "amount_ada": float(amount),
                "amount_lovelace": tx_result['amount_lovelace'],
                "recipient": recipient_address,
                "network": cardano_service.network_name,
                "reason": reason
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to send ADA: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to send ADA"
        }), 500


@cardano_bp.route('/mint-nimo', methods=['POST'])
@jwt_required()
def mint_nimo_tokens():
    """
    Mint NIMO tokens for verified contributions
    
    Request Body:
    {
        "recipient_address": "addr_test1...",
        "amount": 100,
        "reason": "Verified contribution",
        "metta_proof": "metta_hash_or_proof"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "tx_hash": "abc123...",
            "amount": 100,
            "recipient": "addr_test1...",
            "token_name": "NIMO"
        }
    }
    """
    try:
        if not cardano_service.available:
            return jsonify({
                "success": False,
                "error": f"Cardano service unavailable: {cardano_service.error}"
            }), 503
        
        # Only allow admin users or service to mint tokens
        # current_user_id = int(get_jwt_identity())
        # user = User.query.get(current_user_id)
        # if not user or not user.is_admin:  # Assuming we add is_admin field
        #     return jsonify({"success": False, "error": "Unauthorized"}), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['recipient_address', 'amount', 'reason', 'metta_proof']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        recipient_address = data['recipient_address']
        amount = data['amount']
        reason = data['reason']
        metta_proof = data['metta_proof']

        # Validate amount
        if not isinstance(amount, int) or amount <= 0:
            return jsonify({
                "success": False,
                "error": "Amount must be a positive integer"
            }), 400

        # Mint tokens
        mint_result = cardano_service.mint_nimo_tokens(
            to_address=recipient_address,
            amount=amount,
            reason=reason,
            metta_proof=metta_proof
        )

        if 'error' in mint_result:
            return jsonify({
                "success": False,
                "error": mint_result['error']
            }), 400

        return jsonify({
            "success": True,
            "data": mint_result
        }), 200

    except Exception as e:
        logger.error(f"Failed to mint NIMO tokens: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to mint NIMO tokens"
        }), 500


@cardano_bp.route('/send-nimo', methods=['POST'])
@jwt_required()
def send_nimo_tokens():
    """
    Send NIMO tokens between addresses
    
    Request Body:
    {
        "recipient_address": "addr_test1...",
        "amount": 50,
        "reason": "Token transfer"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "tx_hash": "abc123...",
            "amount": 50,
            "recipient": "addr_test1...",
            "token_name": "NIMO"
        }
    }
    """
    try:
        if not cardano_service.available:
            return jsonify({
                "success": False,
                "error": f"Cardano service unavailable: {cardano_service.error}"
            }), 503
        
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['recipient_address', 'amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        recipient_address = data['recipient_address']
        amount = data['amount']

        # Validate amount
        if not isinstance(amount, int) or amount <= 0:
            return jsonify({
                "success": False,
                "error": "Amount must be a positive integer"
            }), 400

        # For now, use service address as from_address
        # In production, users would connect their own Cardano wallets
        from_address = str(cardano_service.service_address) if cardano_service.service_address else None
        if not from_address:
            return jsonify({
                "success": False,
                "error": "Service wallet not configured"
            }), 503

        # Send tokens
        send_result = cardano_service.send_nimo_tokens(
            from_address=from_address,
            to_address=recipient_address,
            amount=amount
        )

        if 'error' in send_result:
            return jsonify({
                "success": False,
                "error": send_result['error']
            }), 400

        return jsonify({
            "success": True,
            "data": send_result
        }), 200

    except Exception as e:
        logger.error(f"Failed to send NIMO tokens: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to send NIMO tokens"
        }), 500


@cardano_bp.route('/tx-status/<tx_hash>', methods=['GET'])
@jwt_required()
def get_transaction_status(tx_hash: str):
    """
    Get status of a Cardano transaction
    
    Response:
    {
        "success": true,
        "data": {
            "tx_hash": "abc123...",
            "status": "confirmed",
            "block_height": 12345,
            "confirmed": true
        }
    }
    """
    try:
        if not tx_hash:
            return jsonify({
                "success": False,
                "error": "Invalid transaction hash"
            }), 400
        
        status = cardano_service.get_transaction_status(tx_hash)
        
        return jsonify({
            "success": True,
            "data": status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction status {tx_hash}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get transaction status"
        }), 500


@cardano_bp.route('/contribution-reward-preview', methods=['POST'])
@jwt_required()
def preview_contribution_reward():
    """
    Preview the complete reward (NIMO + ADA) for a contribution using MeTTa reasoning
    
    Request Body:
    {
        "contribution_id": "contrib123",
        "contribution_data": {
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
            "ada_reward": {
                "pays_ada": true,
                "amount": 0.75,
                "confidence_multiplier": 1.4
            },
            "total_reward": {
                "nimo_tokens": 75,
                "ada_amount": 0.75,
                "estimated_total_ada": 1.50
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
                    "ada_reward": {"pays_ada": False, "reason": "Contribution not verified"},
                    "total_reward": {"nimo_tokens": 0, "ada_amount": 0, "estimated_total_ada": 0}
                }
            }), 200
        
        # Calculate ADA reward
        contribution_type = contribution_data.get('category') if contribution_data else 'general'
        ada_calculation = cardano_service.get_reward_calculation(
            nimo_amount=metta_result.get('token_award', 0),
            confidence=metta_result.get('confidence', 0),
            contribution_type=contribution_type
        )
        
        # Calculate total ADA value (NIMO tokens converted to ADA + direct ADA reward)
        nimo_ada_value = float(metta_result.get('token_award', 0)) / float(cardano_service.ada_to_nimo_rate)
        ada_reward_amount = ada_calculation.get('final_ada_amount', 0)
        total_ada = nimo_ada_value + ada_reward_amount
        
        return jsonify({
            "success": True,
            "data": {
                "metta_analysis": {
                    "verified": metta_result.get('verified'),
                    "confidence": metta_result.get('confidence'),
                    "nimo_tokens": metta_result.get('token_award'),
                    "explanation": metta_result.get('explanation')
                },
                "ada_reward": {
                    "pays_ada": ada_calculation.get('pays_ada'),
                    "amount": ada_reward_amount,
                    "confidence_multiplier": ada_calculation.get('confidence_multiplier')
                },
                "total_reward": {
                    "nimo_tokens": metta_result.get('token_award', 0),
                    "ada_amount": ada_reward_amount,
                    "nimo_ada_equivalent": nimo_ada_value,
                    "estimated_total_ada": total_ada
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error previewing contribution reward: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@cardano_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_current_user_balance():
    """
    Get ADA and NIMO balance for current user's address
    Note: This requires user to have a Cardano address associated with their account
    
    Response:
    {
        "success": true,
        "data": {
            "ada_balance": 10.5,
            "nimo_balance": 150,
            "address": "addr_test1...",
            "network": "preview"
        }
    }
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        # For now, we'll need to add cardano_address field to User model
        # This is a placeholder - in production, users would connect their Cardano wallets
        cardano_address = getattr(user, 'cardano_address', None)
        
        if not cardano_address:
            return jsonify({
                "success": False,
                "error": "User has no associated Cardano address. Please connect your Cardano wallet."
            }), 400

        # Get balance
        balance_info = cardano_service.get_address_balance(cardano_address)
        
        if 'error' in balance_info:
            return jsonify({
                "success": False,
                "error": balance_info['error']
            }), 400

        return jsonify({
            "success": True,
            "data": {
                "ada_balance": balance_info['ada'],
                "nimo_balance": balance_info['nimo_tokens'],
                "address": cardano_address,
                "network": cardano_service.network_name,
                "utxo_count": balance_info['utxo_count']
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get user balance: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve balance"
        }), 500


@cardano_bp.route('/faucet-info', methods=['GET'])
def get_faucet_info():
    """
    Get testnet faucet information (no auth required for testnet)
    
    Response:
    {
        "success": true,
        "data": {
            "network": "preview",
            "faucet_url": "https://docs.cardano.org/cardano-testnets/tools/faucet",
            "instructions": [...]
        }
    }
    """
    try:
        faucet_info = cardano_service.get_faucet_info()
        
        if 'error' in faucet_info:
            return jsonify({
                "success": False,
                "error": faucet_info['error']
            }), 400
        
        return jsonify({
            "success": True,
            "data": faucet_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting faucet info: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get faucet information"
        }), 500


# Error handlers
@cardano_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@cardano_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405