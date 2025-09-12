"""
DEPRECATED: USDC Integration Routes for Nimo Platform

⚠️  DEPRECATED - DO NOT USE ⚠️

These endpoints have been migrated to Cardano blockchain.
All USDC functionality has been replaced with native ADA and NIMO tokens.

For new implementations, use:
- /api/cardano/* routes for blockchain operations
- /api/token/* routes for token management

This file is kept for backward compatibility but will be removed in a future version.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
usdc_bp = Blueprint('usdc', __name__, url_prefix='/api/usdc')

# Deprecation notice
DEPRECATION_MESSAGE = {
    "warning": "USDC endpoints are deprecated",
    "message": "This endpoint has been migrated to Cardano blockchain. Please use /api/cardano/ or /api/token/ endpoints instead.",
    "migration_guide": "https://github.com/polymathuniversata/nimo/docs/deployment/CARDANO_MIGRATION_GUIDE.md",
    "deprecated_since": "2025-09-02",
    "removal_date": "2026-03-01"
}


@usdc_bp.route('/status', methods=['GET'])
@jwt_required()
def get_usdc_status():
    """DEPRECATED: Use /api/cardano/status instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/balance/<address>', methods=['GET'])
@jwt_required()
def get_usdc_balance(address: str):
    """DEPRECATED: Use /api/cardano/balance/<address> instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/calculate-reward', methods=['POST'])
@jwt_required()
def calculate_usdc_reward():
    """DEPRECATED: Use /api/token/calculate-reward instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/estimate-gas', methods=['POST'])
@jwt_required()
def estimate_gas_for_reward():
    """DEPRECATED: Use /api/cardano/estimate-fee instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/verify-payment/<tx_hash>', methods=['GET'])
@jwt_required()
def verify_usdc_payment(tx_hash: str):
    """DEPRECATED: Use /api/cardano/verify-transaction/<tx_hash> instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/contribution-reward-preview', methods=['POST'])
@jwt_required()
def preview_contribution_reward():
    """DEPRECATED: Use /api/token/contribution-reward-preview instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_current_user_usdc_balance():
    """DEPRECATED: Use /api/cardano/balance instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


@usdc_bp.route('/send', methods=['POST'])
@jwt_required()
def send_usdc():
    """DEPRECATED: Use /api/cardano/send instead"""
    return jsonify(DEPRECATION_MESSAGE), 410


# Error handlers
@usdc_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "deprecation": DEPRECATION_MESSAGE
    }), 404


@usdc_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "deprecation": DEPRECATION_MESSAGE
    }), 405