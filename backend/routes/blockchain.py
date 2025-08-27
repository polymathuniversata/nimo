from flask import Blueprint, jsonify
from flask import current_app

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/contracts', methods=['GET'])
def get_contract_addresses():
    """Get deployed contract addresses for current network"""
    network = current_app.config.get('BLOCKCHAIN_NETWORK', 'base-sepolia')

    if network == 'base-sepolia':
        contracts = {
            'network': 'base-sepolia',
            'chainId': 84532,
            'rpcUrl': 'https://sepolia.base.org',
            'contracts': {
                'nimoIdentity': current_app.config.get('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA', ''),
                'nimoToken': current_app.config.get('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA', ''),
                'usdc': current_app.config.get('USDC_CONTRACT_BASE_SEPOLIA', '')
            }
        }
    elif network == 'base-mainnet':
        contracts = {
            'network': 'base-mainnet',
            'chainId': 8453,
            'rpcUrl': 'https://mainnet.base.org',
            'contracts': {
                'nimoIdentity': current_app.config.get('NIMO_IDENTITY_CONTRACT_BASE_MAINNET', ''),
                'nimoToken': current_app.config.get('NIMO_TOKEN_CONTRACT_BASE_MAINNET', ''),
                'usdc': current_app.config.get('USDC_CONTRACT_BASE_MAINNET', '')
            }
        }
    else:
        return jsonify({'error': f'Unknown network: {network}'}), 400

    return jsonify(contracts)