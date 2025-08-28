#!/usr/bin/env python3
"""
Cardano Setup Script for Nimo Platform

This script helps set up the Cardano environment for the Nimo Platform,
including generating service keys, configuring Blockfrost API, and preparing
for token deployment.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from pycardano import PaymentSigningKey, PaymentVerificationKey, Address
    PYCARDANO_AVAILABLE = True
except ImportError:
    PYCARDANO_AVAILABLE = False
    print("Warning: PyCardano not installed. Install with: pip install pycardano")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CardanoSetup:
    """Helper class for Cardano environment setup"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_dir = self.project_root / "backend"
        self.contracts_dir = self.project_root / "contracts" / "cardano"

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        missing_deps = []

        if not PYCARDANO_AVAILABLE:
            missing_deps.append("pycardano")

        try:
            import blockfrost
        except ImportError:
            missing_deps.append("blockfrost-python")

        if missing_deps:
            logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
            logger.info("Install with: pip install pycardano blockfrost-python")
            return False

        logger.info("All dependencies are available")
        return True

    def generate_service_key(self) -> Dict[str, Any]:
        """Generate a new Cardano service key pair"""
        if not PYCARDANO_AVAILABLE:
            return {"error": "PyCardano not available"}

        logger.info("Generating new Cardano service key pair...")

        # Generate new key pair
        signing_key = PaymentSigningKey.generate()
        verification_key = PaymentVerificationKey.from_signing_key(signing_key)
        address = Address(verification_key.hash())

        # Prepare key data
        key_data = {
            "type": "PaymentSigningKeyShelley_ed25519",
            "description": "Nimo Platform Service Key",
            "cborHex": signing_key.to_primitive().hex()
        }

        # Save to file
        key_file = self.contracts_dir / "service_key.skey"
        with open(key_file, 'w') as f:
            json.dump(key_data, f, indent=2)

        logger.info(f"Service key saved to: {key_file}")
        logger.info(f"Service address: {address}")

        return {
            "success": True,
            "address": str(address),
            "key_file": str(key_file),
            "private_key_hex": signing_key.to_primitive().hex()
        }

    def setup_blockfrost_config(self) -> Dict[str, Any]:
        """Guide user through Blockfrost API setup"""
        logger.info("\n" + "="*60)
        logger.info("BLOCKFROST API CONFIGURATION")
        logger.info("="*60)
        logger.info("1. Go to https://blockfrost.io/")
        logger.info("2. Create a free account")
        logger.info("3. Create a new project for Cardano Preview testnet")
        logger.info("4. Copy your Project ID")
        logger.info("5. Add it to your environment variables")
        logger.info("")
        logger.info("Example environment variables to add:")
        logger.info("BLOCKFROST_PROJECT_ID_PREVIEW=your_project_id_here")
        logger.info("")

        # Check if already configured
        project_id = os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW')
        if project_id:
            logger.info(f"✓ Blockfrost project ID already configured: {project_id[:10]}...")
            return {"configured": True, "project_id": project_id}
        else:
            logger.warning("⚠ Blockfrost project ID not configured")
            return {"configured": False}

    def update_env_files(self, key_info: Optional[Dict[str, Any]] = None) -> bool:
        """Update environment files with Cardano configuration"""
        try:
            # Update backend .env
            backend_env = self.backend_dir / ".env"
            if backend_env.exists():
                with open(backend_env, 'r') as f:
                    content = f.read()

                # Add Cardano config if not present
                if 'CARDANO_NETWORK' not in content:
                    cardano_config = """
# Cardano Blockchain Configuration
CARDANO_NETWORK=preview
BLOCKFROST_PROJECT_ID_PREVIEW=your_preview_project_id_here
BLOCKFROST_PROJECT_ID_PREPROD=your_preprod_project_id_here
BLOCKFROST_PROJECT_ID_MAINNET=your_mainnet_project_id_here
CARDANO_SERVICE_PRIVATE_KEY=your_cardano_private_key_hex_here
CARDANO_SERVICE_KEY_FILE=service_key.skey
NIMO_TOKEN_POLICY_ID=
NIMO_TOKEN_ASSET_NAME=NIMO
ADA_TO_NIMO_RATE=100
"""
                    with open(backend_env, 'a') as f:
                        f.write(cardano_config)
                    logger.info("✓ Updated backend/.env with Cardano configuration")

            # Update contracts .env
            contracts_env = self.contracts_dir / ".env"
            if not contracts_env.exists():
                contracts_config = """# Cardano Contract Deployment Configuration
BLOCKFROST_PROJECT_ID_PREVIEW=your_preview_project_id_here
BLOCKFROST_PROJECT_ID_PREPROD=your_preprod_project_id_here
BLOCKFROST_PROJECT_ID_MAINNET=your_mainnet_project_id_here
CARDANO_SERVICE_PRIVATE_KEY=your_cardano_private_key_hex_here
CARDANO_SERVICE_KEY_FILE=service_key.skey
CARDANO_NETWORK=preview
"""
                with open(contracts_env, 'w') as f:
                    f.write(contracts_config)
                logger.info("✓ Created contracts/cardano/.env with Cardano configuration")

            # Update private key if provided
            if key_info and key_info.get('private_key_hex'):
                self._update_env_var('CARDANO_SERVICE_PRIVATE_KEY', key_info['private_key_hex'])

            return True

        except Exception as e:
            logger.error(f"Error updating environment files: {e}")
            return False

    def _update_env_var(self, var_name: str, value: str):
        """Update environment variable in files"""
        # This is a simple implementation - in production you might want more sophisticated env management
        logger.info(f"Set {var_name} in your environment (value: {value[:10]}...)")

    def get_faucet_instructions(self) -> None:
        """Display faucet instructions"""
        logger.info("\n" + "="*60)
        logger.info("GET TEST ADA FROM FAUCET")
        logger.info("="*60)
        logger.info("1. Go to: https://docs.cardano.org/cardano-testnets/tools/faucet")
        logger.info("2. Select 'Preview' testnet")
        logger.info("3. Enter your service address:")
        logger.info("4. Click 'Receive test ada'")
        logger.info("5. Wait a few minutes for the transaction to confirm")
        logger.info("")
        logger.info("Note: Test ADA has no monetary value and is only for testing")

    def run_setup(self) -> Dict[str, Any]:
        """Run the complete setup process"""
        logger.info("Starting Cardano setup for Nimo Platform...")

        results = {
            "dependencies_ok": False,
            "key_generated": False,
            "blockfrost_configured": False,
            "env_updated": False
        }

        # 1. Check dependencies
        results["dependencies_ok"] = self.check_dependencies()
        if not results["dependencies_ok"]:
            return results

        # 2. Generate service key
        if PYCARDANO_AVAILABLE:
            key_result = self.generate_service_key()
            if key_result.get("success"):
                results["key_generated"] = True
                results["service_address"] = key_result["address"]
                logger.info(f"✓ Generated service key: {key_result['address']}")

        # 3. Check Blockfrost configuration
        blockfrost_result = self.setup_blockfrost_config()
        results["blockfrost_configured"] = blockfrost_result.get("configured", False)

        # 4. Update environment files
        results["env_updated"] = self.update_env_files(key_result if results["key_generated"] else None)

        # 5. Show faucet instructions
        if results["key_generated"]:
            self.get_faucet_instructions()

        # Summary
        logger.info("\n" + "="*60)
        logger.info("CARDANO SETUP SUMMARY")
        logger.info("="*60)
        logger.info(f"Dependencies: {'✓' if results['dependencies_ok'] else '✗'}")
        logger.info(f"Service Key: {'✓' if results['key_generated'] else '✗'}")
        logger.info(f"Blockfrost: {'✓' if results['blockfrost_configured'] else '✗'}")
        logger.info(f"Environment: {'✓' if results['env_updated'] else '✗'}")

        if results["service_address"]:
            logger.info(f"Service Address: {results['service_address']}")

        next_steps = []
        if not results["blockfrost_configured"]:
            next_steps.append("1. Get Blockfrost API key from https://blockfrost.io/")
        if results["key_generated"] and not results["blockfrost_configured"]:
            next_steps.append("2. Fund service address with test ADA from faucet")
        if all(results.values()):
            next_steps.append("Ready to deploy NIMO token!")

        if next_steps:
            logger.info("\nNext steps:")
            for step in next_steps:
                logger.info(f"  {step}")

        return results

def main():
    """Main setup function"""
    setup = CardanoSetup()
    results = setup.run_setup()

    if all(results.values()):
        logger.info("\n🎉 Cardano setup completed successfully!")
        return 0
    else:
        logger.warning("\n⚠️  Some setup steps are incomplete. Please complete them before deployment.")
        return 1

if __name__ == "__main__":
    exit(main())