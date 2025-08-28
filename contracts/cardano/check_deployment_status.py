#!/usr/bin/env python3
"""
Cardano Deployment Status Checker

This script checks the current status of Cardano deployment setup
and provides guidance on next steps.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

try:
    from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, BlockFrostChainContext, Network
    PYCARDANO_AVAILABLE = True
except ImportError:
    PYCARDANO_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentChecker:
    """Check Cardano deployment readiness"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.contracts_dir = self.project_root / "contracts" / "cardano"

    def check_service_key(self) -> Dict[str, Any]:
        """Check if service key exists and is valid"""
        key_file = self.contracts_dir / "service_key.skey"

        if not key_file.exists():
            return {"status": "missing", "message": "Service key file not found"}

        try:
            with open(key_file, 'r') as f:
                key_data = json.load(f)

            private_key_hex = key_data.get('cborHex')
            if not private_key_hex:
                return {"status": "invalid", "message": "Invalid key file format"}

            # Validate key
            signing_key = PaymentSigningKey.from_primitive(bytes.fromhex(private_key_hex))
            verification_key = PaymentVerificationKey.from_signing_key(signing_key)
            address = Address(verification_key.hash())

            return {
                "status": "ready",
                "address": str(address),
                "key_file": str(key_file)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error loading key: {e}"}

    def check_blockfrost_config(self) -> Dict[str, Any]:
        """Check Blockfrost API configuration"""
        networks = ['preview', 'preprod', 'mainnet']
        results = {}

        for network in networks:
            env_var = f'BLOCKFROST_PROJECT_ID_{network.upper()}'
            project_id = os.getenv(env_var)

            if project_id and project_id != f'your_{network}_project_id_here':
                results[network] = {"configured": True, "project_id": project_id}
            else:
                results[network] = {"configured": False}

        return results

    def check_blockfrost_connection(self, network: str = "preview") -> Dict[str, Any]:
        """Test Blockfrost API connection"""
        if not PYCARDANO_AVAILABLE:
            return {"status": "error", "message": "PyCardano not available"}

        config = self.check_blockfrost_config()
        if not config[network]["configured"]:
            return {"status": "not_configured", "message": "Blockfrost project ID not configured"}

        try:
            project_id = config[network]["project_id"]
            cardano_network = Network.TESTNET if network != 'mainnet' else Network.MAINNET

            base_urls = {
                'preview': 'https://cardano-preview.blockfrost.io/api',
                'preprod': 'https://cardano-preprod.blockfrost.io/api',
                'mainnet': 'https://cardano-mainnet.blockfrost.io/api'
            }

            chain_context = BlockFrostChainContext(
                project_id=project_id,
                network=cardano_network,
                base_url=base_urls[network]
            )

            # Test connection by getting latest block
            latest_slot = chain_context.last_block_slot

            return {
                "status": "connected",
                "latest_slot": latest_slot,
                "network": network
            }

        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {e}"}

    def check_address_balance(self, address: str, network: str = "preview") -> Dict[str, Any]:
        """Check ADA balance of an address"""
        connection = self.check_blockfrost_connection(network)
        if connection["status"] != "connected":
            return {"status": "error", "message": "Blockfrost connection not available"}

        try:
            config = self.check_blockfrost_config()
            project_id = config[network]["project_id"]
            cardano_network = Network.TESTNET if network != 'mainnet' else Network.MAINNET

            base_urls = {
                'preview': 'https://cardano-preview.blockfrost.io/api',
                'preprod': 'https://cardano-preprod.blockfrost.io/api',
                'mainnet': 'https://cardano-mainnet.blockfrost.io/api'
            }

            chain_context = BlockFrostChainContext(
                project_id=project_id,
                network=cardano_network,
                base_url=base_urls[network]
            )

            addr = Address.from_bech32(address)
            utxos = chain_context.utxos(addr)

            total_lovelace = sum(utxo.output.amount.coin for utxo in utxos)
            ada_balance = total_lovelace / 1000000

            return {
                "status": "success",
                "address": address,
                "ada_balance": ada_balance,
                "lovelace_balance": total_lovelace,
                "utxo_count": len(utxos),
                "network": network
            }

        except Exception as e:
            return {"status": "error", "message": f"Balance check failed: {e}"}

    def get_deployment_readiness(self) -> Dict[str, Any]:
        """Get overall deployment readiness status"""
        key_status = self.check_service_key()
        blockfrost_status = self.check_blockfrost_config()

        readiness = {
            "service_key": key_status,
            "blockfrost_config": blockfrost_status,
            "overall_ready": False,
            "next_steps": []
        }

        # Check if service key is ready
        if key_status["status"] != "ready":
            readiness["next_steps"].append("Generate service key: python setup_cardano.py")

        # Check if Blockfrost is configured
        if not any(config["configured"] for config in blockfrost_status.values()):
            readiness["next_steps"].append("Configure Blockfrost API: Get project ID from https://blockfrost.io/")

        # Check if we can connect to Blockfrost
        if any(config["configured"] for config in blockfrost_status.values()):
            connection = self.check_blockfrost_connection()
            if connection["status"] == "connected":
                readiness["blockfrost_connection"] = connection

                # Check service address balance if key is ready
                if key_status["status"] == "ready":
                    balance = self.check_address_balance(key_status["address"])
                    readiness["service_balance"] = balance

                    if balance["status"] == "success" and balance["ada_balance"] < 5:
                        readiness["next_steps"].append(f"Fund service address with test ADA: {key_status['address']}")
                    elif balance["status"] == "success":
                        readiness["overall_ready"] = True
            else:
                readiness["next_steps"].append("Fix Blockfrost connection")

        return readiness

def main():
    """Main function"""
    checker = DeploymentChecker()

    logger.info("Checking Cardano deployment readiness...")
    logger.info("="*60)

    # Check service key
    key_status = checker.check_service_key()
    logger.info(f"Service Key: {key_status['status']}")
    if key_status["status"] == "ready":
        logger.info(f"  Address: {key_status['address']}")

    # Check Blockfrost config
    blockfrost_status = checker.check_blockfrost_config()
    logger.info("Blockfrost Configuration:")
    for network, status in blockfrost_status.items():
        status_icon = "✓" if status["configured"] else "✗"
        logger.info(f"  {network}: {status_icon}")

    # Get overall readiness
    readiness = checker.get_deployment_readiness()

    logger.info("\nNext Steps:")
    if readiness["next_steps"]:
        for i, step in enumerate(readiness["next_steps"], 1):
            logger.info(f"  {i}. {step}")
    else:
        logger.info("  🎉 Ready for deployment!")
        logger.info("  Run: python deploy_nimo_token.py --network preview")

    # Show service balance if available
    if "service_balance" in readiness:
        balance = readiness["service_balance"]
        if balance["status"] == "success":
            logger.info(f"\nService Address Balance: {balance['ada_balance']} ADA")

if __name__ == "__main__":
    main()