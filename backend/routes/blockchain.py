from flask import Blueprint, jsonify
from flask import current_app

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/contracts', methods=['GET'])
def get_contract_addresses():
    """Get deployed contract addresses for current network"""
    network = current_app.config.get('BLOCKCHAIN_NETWORK', 'cardano-preprod')

    if network == 'cardano-preprod':
        contracts = {
            'network': 'cardano-preprod',
            'chainId': 0,  # Cardano preprod
            'rpcUrl': 'https://cardano-preprod.blockfrost.io/api/v0',
            'contracts': {
                'nimoIdentity': current_app.config.get('NIMO_IDENTITY_CONTRACT_CARDANO_PREPROD', ''),
                'nimoToken': current_app.config.get('NIMO_TOKEN_CONTRACT_CARDANO_PREPROD', ''),
                'usdc': current_app.config.get('USDC_CONTRACT_CARDANO_PREPROD', '')  # Will be Cardano native token
            }
        }
    elif network == 'cardano-mainnet':
        contracts = {
            'network': 'cardano-mainnet',
            'chainId': 1,  # Cardano mainnet
            'rpcUrl': 'https://cardano-mainnet.blockfrost.io/api/v0',
            'contracts': {
                'nimoIdentity': current_app.config.get('NIMO_IDENTITY_CONTRACT_CARDANO_MAINNET', ''),
                'nimoToken': current_app.config.get('NIMO_TOKEN_CONTRACT_CARDANO_MAINNET', ''),
                'usdc': current_app.config.get('USDC_CONTRACT_CARDANO_MAINNET', '')  # Will be Cardano native token
            }
        }
    else:
        return jsonify({'error': f'Unknown network: {network}'}), 400

    return jsonify(contracts)