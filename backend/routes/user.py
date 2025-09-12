from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from models.user import User, Skill
from services.blockchain_user_service import BlockchainUserService

user_bp = Blueprint('user', __name__)

# Initialize blockchain-first service
blockchain_user_service = BlockchainUserService()

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    # Check if requesting own profile or has admin permission (could be added later)
    current_user_id = int(get_jwt_identity())

    # Use blockchain-first service
    result = blockchain_user_service.get_user_from_chain(user_id)

    if not result.get('success'):
        return jsonify({"error": result.get('error', 'User not found')}), 404

    return jsonify(result['user']), 200


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = int(get_jwt_identity())

    # Use blockchain-first service
    result = blockchain_user_service.get_user_profile(current_user_id)

    if not result.get('success'):
        return jsonify({"error": result.get('error', 'User not found')}), 404

    return jsonify(result['profile']), 200


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = int(get_jwt_identity())

    data = request.get_json()

    # Use blockchain-first service
    result = blockchain_user_service.update_user_on_chain(current_user_id, data)

    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Update failed')}), 500

    # Get updated user data
    profile_result = blockchain_user_service.get_user_profile(current_user_id)
    if profile_result.get('success'):
        return jsonify(profile_result['profile']), 200
    else:
        return jsonify({"message": "User updated successfully"}), 200


@user_bp.route('/me/wallet', methods=['POST'])
@jwt_required()
def connect_wallet():
    """Connect wallet to user account"""
    current_user_id = int(get_jwt_identity())

    data = request.get_json()
    wallet_address = data.get('wallet_address')

    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400

    # Use blockchain-first service
    result = blockchain_user_service.verify_wallet_connection(current_user_id, wallet_address)

    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Wallet connection failed')}), 500

    return jsonify(result), 200


@user_bp.route('/me/balance', methods=['GET'])
@jwt_required()
def get_user_balance():
    """Get user's token balance"""
    current_user_id = int(get_jwt_identity())

    # Use blockchain-first service
    result = blockchain_user_service.get_user_token_balance(current_user_id)

    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Failed to get balance')}), 500

    return jsonify(result['balance']), 200


@user_bp.route('/me/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user's contribution and token statistics"""
    current_user_id = int(get_jwt_identity())

    # Get contribution stats
    contrib_result = blockchain_user_service.get_user_contributions_count(current_user_id)
    balance_result = blockchain_user_service.get_user_token_balance(current_user_id)

    if not contrib_result.get('success') or not balance_result.get('success'):
        return jsonify({"error": "Failed to get user statistics"}), 500

    stats = {
        'contributions': contrib_result['stats'],
        'balance': balance_result['balance']
    }

    return jsonify(stats), 200