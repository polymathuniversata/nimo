#!/usr/bin/env python3
"""
NIMO Token Deployment Script for Cardano

This script deploys the NIMO token minting policy and creates the initial token mint.
Requires PyCardano and Blockfrost configuration.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

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
        PlutusV2Script,
        PlutusData,
        AuxiliaryData,
        Metadata,
        NativeScript,
        ScriptPubkey,
        InvalidAfter
    )
    PYCARDANO_AVAILABLE = True
except ImportError:
    print("PyCardano not installed. Install with: pip install pycardano")
    PYCARDANO_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NimoTokenDeployer:
    """Deploys NIMO token policy and handles initial minting"""
    
    def __init__(self, network: str = "preview"):
        """Initialize deployer with network configuration"""
        
        if not PYCARDANO_AVAILABLE:
            raise ImportError("PyCardano required for deployment")
        
        self.network = network
        self.config = self._load_config()
        
        # Initialize chain context
        cardano_network = Network.MAINNET if network == 'mainnet' else Network.TESTNET
        self.chain_context = BlockFrostChainContext(
            project_id=self.config['blockfrost_project_id'],
            network=cardano_network,
            base_url=self.config['blockfrost_url']
        )
        
        # Load service keys
        self.signing_key = self._load_signing_key()
        self.verification_key = PaymentVerificationKey.from_signing_key(self.signing_key)
        self.service_address = Address(self.verification_key.hash())
        
        logger.info(f"Initialized deployer for {network} network")
        logger.info(f"Service address: {self.service_address}")
    
    def _load_config(self) -> Dict[str, str]:
        """Load network configuration"""
        if self.network == "mainnet":
            return {
                'blockfrost_project_id': os.getenv('BLOCKFROST_PROJECT_ID_MAINNET'),
                'blockfrost_url': 'https://cardano-mainnet.blockfrost.io/api'
            }
        elif self.network == "preprod":
            return {
                'blockfrost_project_id': os.getenv('BLOCKFROST_PROJECT_ID_PREPROD'),
                'blockfrost_url': 'https://cardano-preprod.blockfrost.io/api'
            }
        else:  # preview (default)
            return {
                'blockfrost_project_id': os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW'),
                'blockfrost_url': 'https://cardano-preview.blockfrost.io/api'
            }
    
    def _load_signing_key(self) -> PaymentSigningKey:
        """Load signing key from environment or file"""
        # Try environment variable first
        key_hex = os.getenv('CARDANO_SERVICE_PRIVATE_KEY')
        if key_hex and key_hex != 'your_cardano_private_key_here':
            return PaymentSigningKey.from_primitive(bytes.fromhex(key_hex))
        
        # Try key file
        key_file = Path('service_key.skey')
        if key_file.exists():
            with open(key_file, 'r') as f:
                key_data = json.load(f)
                return PaymentSigningKey.from_primitive(bytes.fromhex(key_data['cborHex']))
        
        # Generate new key for testing
        logger.warning("No service key found, generating new key for testing")
        signing_key = PaymentSigningKey.generate()
        
        # Save for future use
        key_data = {
            "type": "PaymentSigningKeyShelley_ed25519",
            "description": "Payment Signing Key",
            "cborHex": signing_key.to_primitive().hex()
        }
        
        with open('service_key.skey', 'w') as f:
            json.dump(key_data, f, indent=2)
        
        logger.info(f"Generated new service key, saved to service_key.skey")
        logger.info(f"Service address: {Address(PaymentVerificationKey.from_signing_key(signing_key).hash())}")
        logger.info("Please fund this address with test ADA before deployment")
        
        return signing_key
    
    def create_native_script_policy(self) -> Dict[str, Any]:
        """Create a native script minting policy"""
        
        # Create a simple signature-based policy
        # In production, you might want a more complex policy with time locks
        key_hash = self.verification_key.hash()
        
        # Create native script that requires our signature
        native_script = NativeScript(
            ScriptPubkey(key_hash)
        )
        
        # Get policy ID
        policy_id = native_script.hash()
        
        logger.info(f"Created native script policy")
        logger.info(f"Policy ID: {policy_id}")
        
        return {
            'policy_id': str(policy_id),
            'native_script': native_script,
            'script_hash': policy_id
        }
    
    def mint_initial_tokens(self, 
                          policy_info: Dict[str, Any], 
                          initial_amount: int = 1000000) -> str:
        """Mint initial NIMO tokens"""
        
        policy_id = ScriptHash.from_primitive(bytes.fromhex(policy_info['policy_id']))
        native_script = policy_info['native_script']
        
        # Create asset name
        asset_name = AssetName(b"NIMO")
        
        # Create the token to mint
        token_to_mint = MultiAsset({
            policy_id: Asset({asset_name: initial_amount})
        })
        
        # Create transaction metadata
        metadata = {
            "721": {  # CIP-25 NFT Metadata Standard
                str(policy_id): {
                    "NIMO": {
                        "name": "NIMO Token",
                        "description": "Reputation token for the Nimo Platform",
                        "image": "ipfs://QmNimoTokenImage",
                        "website": "https://nimo.platform",
                        "ticker": "NIMO",
                        "decimals": 0,
                        "version": "1.0.0"
                    }
                }
            },
            "674": {  # Custom metadata
                "msg": [f"Initial NIMO token mint - {datetime.now(timezone.utc).isoformat()}"],
                "platform": "Nimo",
                "network": self.network,
                "purpose": "reputation_system"
            }
        }
        
        # Build transaction
        builder = TransactionBuilder(self.chain_context)
        
        # Add minting
        builder.mint = token_to_mint
        builder.native_scripts = [native_script]
        
        # Add output (mint to service address)
        builder.add_output(
            TransactionOutput(
                self.service_address,
                Value(coin=2000000, multi_asset=token_to_mint)  # 2 ADA + tokens
            )
        )
        
        # Add metadata
        aux_data = AuxiliaryData(Metadata(metadata))
        builder.auxiliary_data = aux_data
        
        # Build and sign transaction
        transaction = builder.build_and_sign([self.signing_key], self.service_address)
        
        # Submit transaction
        tx_hash = self.chain_context.submit_tx(transaction)
        
        logger.info(f"Token minting transaction submitted!")
        logger.info(f"Transaction hash: {tx_hash}")
        logger.info(f"Minted {initial_amount} NIMO tokens to {self.service_address}")
        
        return str(tx_hash)
    
    def update_policy_file(self, policy_info: Dict[str, Any], mint_tx_hash: str):
        """Update the policy JSON file with deployment information"""
        
        policy_file = Path('nimo_token_policy.json')
        
        # Load existing policy file
        if policy_file.exists():
            with open(policy_file, 'r') as f:
                policy_data = json.load(f)
        else:
            policy_data = {"deployment": {}}
        
        # Update with deployment info
        if "deployment" not in policy_data:
            policy_data["deployment"] = {}
        
        if "testnet" not in policy_data["deployment"]:
            policy_data["deployment"]["testnet"] = {}
        
        if self.network == "mainnet":
            policy_data["deployment"]["mainnet"] = {
                "policy_id": policy_info['policy_id'],
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "tx_hash": mint_tx_hash
            }
        else:
            policy_data["deployment"]["testnet"][self.network] = {
                "policy_id": policy_info['policy_id'],
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "tx_hash": mint_tx_hash
            }
        
        # Save updated policy file
        with open(policy_file, 'w') as f:
            json.dump(policy_data, f, indent=2)
        
        logger.info(f"Updated policy file: {policy_file}")
    
    def deploy(self, initial_mint: int = 1000000) -> Dict[str, Any]:
        """Complete deployment process"""
        
        logger.info(f"Starting NIMO token deployment on {self.network}")
        
        # Check service address balance
        try:
            balance_info = self.chain_context.api.account(str(self.service_address))
            ada_balance = int(balance_info.controlled_amount) / 1000000
            logger.info(f"Service address balance: {ada_balance} ADA")
            
            if ada_balance < 5.0:
                logger.warning("Low ADA balance! Consider funding the service address.")
                if self.network != "mainnet":
                    logger.info("Get test ADA from: https://docs.cardano.org/cardano-testnets/tools/faucet")
                    response = input("Continue anyway? (y/N): ")
                    if response.lower() != 'y':
                        logger.info("Deployment cancelled")
                        return {"error": "Insufficient funds"}
        except Exception as e:
            logger.warning(f"Could not check balance: {e}")
        
        try:
            # 1. Create minting policy
            logger.info("Creating native script minting policy...")
            policy_info = self.create_native_script_policy()
            
            # 2. Mint initial tokens
            logger.info(f"Minting {initial_mint} initial NIMO tokens...")
            mint_tx_hash = self.mint_initial_tokens(policy_info, initial_mint)
            
            # 3. Update policy file
            logger.info("Updating policy configuration...")
            self.update_policy_file(policy_info, mint_tx_hash)
            
            # 4. Create deployment summary
            deployment_info = {
                "success": True,
                "network": self.network,
                "policy_id": policy_info['policy_id'],
                "service_address": str(self.service_address),
                "mint_tx_hash": mint_tx_hash,
                "initial_mint": initial_mint,
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "blockfrost_url": self.config['blockfrost_url']
            }
            
            logger.info("=" * 60)
            logger.info("NIMO TOKEN DEPLOYMENT SUCCESSFUL!")
            logger.info("=" * 60)
            logger.info(f"Network: {self.network}")
            logger.info(f"Policy ID: {policy_info['policy_id']}")
            logger.info(f"Service Address: {self.service_address}")
            logger.info(f"Mint Transaction: {mint_tx_hash}")
            logger.info(f"Initial Mint: {initial_mint} NIMO tokens")
            logger.info("=" * 60)
            
            # Save deployment info
            with open(f'deployment_{self.network}.json', 'w') as f:
                json.dump(deployment_info, f, indent=2)
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {"error": str(e)}


def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy NIMO token on Cardano')
    parser.add_argument('--network', choices=['preview', 'preprod', 'mainnet'], 
                       default='preview', help='Cardano network to deploy to')
    parser.add_argument('--initial-mint', type=int, default=1000000,
                       help='Initial number of NIMO tokens to mint')
    
    args = parser.parse_args()
    
    # Verify required environment variables
    required_env = {
        'preview': 'BLOCKFROST_PROJECT_ID_PREVIEW',
        'preprod': 'BLOCKFROST_PROJECT_ID_PREPROD',
        'mainnet': 'BLOCKFROST_PROJECT_ID_MAINNET'
    }
    
    env_var = required_env[args.network]
    if not os.getenv(env_var):
        logger.error(f"Environment variable {env_var} is required")
        logger.info("Get your Blockfrost project ID from: https://blockfrost.io/")
        return 1
    
    try:
        deployer = NimoTokenDeployer(args.network)
        result = deployer.deploy(args.initial_mint)
        
        if "error" in result:
            logger.error(f"Deployment failed: {result['error']}")
            return 1
        
        logger.info("Deployment completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())