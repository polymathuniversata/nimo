"""
Identity verification routes for Nimo Platform

These endpoints handle DID (Decentralized Identifier) verification,
identity linking, and enhanced contribution verification with identity trust.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
import logging

from services.metta_integration import MeTTaIntegration
from services.did_verification import DIDVerificationError
from services.metta_security import MeTTaSecurityError

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
identity_bp = Blueprint('identity', __name__, url_prefix='/api/identity')

# Initialize MeTTa integration (with DID support)
metta_integration = MeTTaIntegration()


@identity_bp.route('/verify-did', methods=['POST'])
@jwt_required()
def verify_did():
    """
    Verify a user's decentralized identifier
    
    Request Body:
    {
        "did": "did:eth:0x...",
        "proof": {  // Optional cryptographic proof
            "signature": "0x...",
            "timestamp": "2023-...",
            "challenge": "..."
        }
    }
    
    Response:
    {
        "success": true,
        "data": {
            "user_id": "user123",
            "identity_verified": true,
            "confidence": 0.8,
            "did_verification": {...},
            "metta_atoms": [...],
            "reputation_bonus": 10
        }
    }
    """
    try:
        # Get current user from JWT
        current_user = get_jwt_identity()
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        did = data.get('did')
        proof = data.get('proof')  # Optional
        
        if not did:
            return jsonify({
                "success": False,
                "error": "DID is required"
            }), 400
        
        # Verify DID and integrate with MeTTa
        result = metta_integration.verify_user_did(current_user, did, proof)
        
        # Log verification attempt
        logger.info(f"DID verification for user {current_user}: {result.get('identity_verified', False)}")
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except DIDVerificationError as e:
        logger.warning(f"DID verification failed for user {current_user}: {e}")
        return jsonify({
            "success": False,
            "error": f"DID verification failed: {str(e)}"
        }), 400
        
    except MeTTaSecurityError as e:
        logger.error(f"Security error in DID verification for user {current_user}: {e}")
        return jsonify({
            "success": False,
            "error": "Security validation failed"
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in DID verification: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@identity_bp.route('/verify-ens', methods=['POST'])
@jwt_required()
def verify_ens():
    """
    Verify an ENS (Ethereum Name Service) name
    
    Request Body:
    {
        "ens_name": "vitalik.eth"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "ens_name": "vitalik.eth",
            "verified": true,
            "ethereum_address": "0x...",
            "avatar": "...",
            "records": {...}
        }
    }
    """
    try:
        # Get current user from JWT
        current_user = get_jwt_identity()
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        ens_name = data.get('ens_name')
        
        if not ens_name:
            return jsonify({
                "success": False,
                "error": "ENS name is required"
            }), 400
        
        # Verify ENS name
        result = metta_integration.did_integration.did_verifier.verify_ens_name(ens_name)
        
        # Log verification attempt
        logger.info(f"ENS verification for user {current_user}: {ens_name} -> {result.get('verified', False)}")
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except DIDVerificationError as e:
        logger.warning(f"ENS verification failed: {e}")
        return jsonify({
            "success": False,
            "error": f"ENS verification failed: {str(e)}"
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in ENS verification: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@identity_bp.route('/contribution/verify-with-identity', methods=['POST'])
@jwt_required()
def verify_contribution_with_identity():
    """
    Verify a contribution with enhanced identity-based trust scoring
    
    Request Body:
    {
        "contribution_id": "contrib123",
        "contribution_data": {  // Optional, if not in database
            "user_id": "user123",
            "category": "education",
            "title": "Python Workshop",
            "evidence": [...],
            "metadata": {...}
        }
    }
    
    Response:
    {
        "success": true,
        "data": {
            "status": "verified",
            "confidence": 0.9,
            "identity_enhanced": true,
            "token_award": 75,
            "reputation_impact": 15,
            "explanation": "...",
            "verification_timestamp": "..."
        }
    }
    """
    try:
        # Get current user from JWT
        current_user = get_jwt_identity()
        
        # Parse request data
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
                "error": "Contribution ID is required"
            }), 400
        
        # Perform identity-enhanced contribution verification
        result = metta_integration.verify_contribution_with_identity(
            contribution_id, contribution_data
        )
        
        # Log verification attempt
        logger.info(f"Identity-enhanced contribution verification by user {current_user}: "
                   f"contrib={contribution_id}, verified={result.get('status') == 'verified'}")
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except MeTTaSecurityError as e:
        logger.error(f"Security error in contribution verification: {e}")
        return jsonify({
            "success": False,
            "error": "Security validation failed"
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in contribution verification: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@identity_bp.route('/trust-score/<user_id>', methods=['GET'])
@jwt_required()
def get_identity_trust_score(user_id: str):
    """
    Get identity trust score for a user
    
    Response:
    {
        "success": true,
        "data": {
            "user_id": "user123",
            "has_verified_did": true,
            "trust_score": 0.85,
            "reputation_bonus": 10,
            "identity_method": "eth",
            "verification_time": "..."
        }
    }
    """
    try:
        # Get current user from JWT
        current_user = get_jwt_identity()
        
        # Note: In production, add proper authorization checks
        # For now, users can query any user's trust score
        
        # Query MeTTa reasoning system for identity trust score
        from services.metta_runner import run_metta_query
        
        # Check if user has verified DID
        has_did_query = f'!(HasVerifiedDID "{user_id}")'
        has_did = run_metta_query(has_did_query)
        
        trust_score = 0.0
        reputation_bonus = 0
        identity_method = None
        
        if has_did:
            # Get trust score
            trust_query = f'!(IdentityTrustScore "{user_id}")'
            trust_result = run_metta_query(trust_query)
            trust_score = float(trust_result) if trust_result else 0.0
            
            # Get reputation bonus
            bonus_query = f'!(IdentityReputationBonus "{user_id}")'
            bonus_result = run_metta_query(bonus_query)
            reputation_bonus = int(bonus_result) if bonus_result else 0
            
            # Try to get DID method
            try:
                method_query = f'!(DIDVerification "{user_id}" $_ $method)'
                method_result = run_metta_query(method_query)
                if method_result:
                    identity_method = str(method_result).strip('"')
            except Exception:
                pass
        
        result = {
            "user_id": user_id,
            "has_verified_did": bool(has_did),
            "trust_score": trust_score,
            "reputation_bonus": reputation_bonus,
            "identity_method": identity_method,
            "queried_by": current_user,
            "query_timestamp": metta_integration._get_current_timestamp()
        }
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error querying identity trust score: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@identity_bp.route('/supported-methods', methods=['GET'])
def get_supported_did_methods():
    """
    Get list of supported DID methods
    
    Response:
    {
        "success": true,
        "data": {
            "supported_methods": {
                "eth": "Ethereum address-based DID",
                "key": "Key-based DID",
                "web": "Web-based DID",
                "ens": "Ethereum Name Service"
            },
            "resolvers": [...]
        }
    }
    """
    try:
        from services.did_verification import DIDVerifier
        
        return jsonify({
            "success": True,
            "data": {
                "supported_methods": DIDVerifier.SUPPORTED_METHODS,
                "did_resolvers": DIDVerifier.DID_RESOLVERS,
                "features": [
                    "DID document resolution",
                    "ENS name resolution",
                    "Cryptographic proof validation",
                    "MeTTa reasoning integration",
                    "Identity trust scoring"
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting supported DID methods: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


# Error handlers
@identity_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@identity_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405