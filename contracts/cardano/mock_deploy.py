#!/usr/bin/env python3
"""
Mock Cardano Contract Deployment for Testing

This script simulates the deployment process for testing purposes.
It generates mock contract addresses, policy IDs, and transaction hashes
without actually interacting with the Cardano blockchain.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class MockCardanoDeployer:
    """Mock deployer for testing Cardano contract deployment"""

    def __init__(self, network: str = "preview"):
        self.network = network
        self.contracts_dir = Path(__file__).parent
        self.deployments_dir = self.contracts_dir / ".." / "deployments"
        self.deployments_dir.mkdir(exist_ok=True)

        # Mock data
        self.mock_policy_id = "d5e6cc5527629f7b4ea896a148ec828199bd3f46f9b5a9b8f8c2d4e6"
        self.mock_contract_address = "addr1w8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5gmock"
        self.mock_tx_hash = "a1b2c3d4e5f678901234567890123456789012345678901234567890"

    def deploy_identity_contract(self) -> Dict[str, Any]:
        """Mock deployment of identity contract"""
        print("🚀 Deploying NimoIdentity Contract (MOCK)...")

        contract_info = {
            "contract_type": "identity",
            "network": self.network,
            "address": self.mock_contract_address,
            "policy_id": self.mock_policy_id,
            "deployment_tx": self.mock_tx_hash,
            "deployed_at": datetime.utcnow().isoformat(),
            "status": "deployed",
            "mock": True
        }

        print(f"✅ Identity contract deployed at: {self.mock_contract_address}")
        print(f"📋 Policy ID: {self.mock_policy_id}")

        return contract_info

    def deploy_token_contract(self) -> Dict[str, Any]:
        """Mock deployment of token contract"""
        print("🚀 Deploying NimoToken Contract (MOCK)...")

        # Mock token metadata
        token_metadata = {
            "name": "Nimo Impact Token",
            "ticker": "NIMO",
            "description": "Decentralized Youth Identity & Proof of Contribution Network Token",
            "decimals": 6,
            "url": "https://nimo-platform.com"
        }

        contract_info = {
            "contract_type": "token",
            "network": self.network,
            "policy_id": self.mock_policy_id,
            "initial_supply": 1000000,
            "decimals": 6,
            "metadata": token_metadata,
            "deployment_tx": self.mock_tx_hash,
            "deployed_at": datetime.utcnow().isoformat(),
            "status": "deployed",
            "mock": True
        }

        print(f"✅ Token contract deployed with policy: {self.mock_policy_id}")
        print(f"💰 Initial supply: 1,000,000 NIMO")

        return contract_info

    def deploy_governance_contract(self) -> Dict[str, Any]:
        """Mock deployment of governance contract"""
        print("🚀 Deploying Governance Contract (MOCK)...")

        contract_info = {
            "contract_type": "governance",
            "network": self.network,
            "address": f"addr_gov_{self.mock_contract_address[8:]}",
            "policy_id": f"gov_{self.mock_policy_id}",
            "deployment_tx": f"gov_{self.mock_tx_hash}",
            "deployed_at": datetime.utcnow().isoformat(),
            "status": "deployed",
            "mock": True
        }

        print(f"✅ Governance contract deployed at: {contract_info['address']}")

        return contract_info

    def save_deployment_info(self, contracts: Dict[str, Any]) -> None:
        """Save deployment information to file"""
        deployment_file = self.deployments_dir / f"mock_deployment_{self.network}.json"

        deployment_data = {
            "network": self.network,
            "deployment_type": "mock",
            "timestamp": datetime.utcnow().isoformat(),
            "contracts": contracts,
            "note": "This is a mock deployment for testing purposes. No real blockchain transactions were made."
        }

        with open(deployment_file, 'w') as f:
            json.dump(deployment_data, f, indent=2)

        print(f"💾 Deployment info saved to: {deployment_file}")

    def update_env_file(self, contracts: Dict[str, Any]) -> None:
        """Update environment files with deployment information"""
        # Update backend .env
        backend_env = Path(__file__).parent.parent.parent / "backend" / ".env"
        if backend_env.exists():
            with open(backend_env, 'a') as f:
                f.write(f"\n# Mock Cardano Deployment ({self.network})\n")
                f.write(f"NIMO_TOKEN_POLICY_ID={contracts['token']['policy_id']}\n")
                f.write(f"NIMO_IDENTITY_CONTRACT_ADDRESS={contracts['identity']['address']}\n")
                f.write(f"CARDANO_NETWORK={self.network}\n")
            print(f"🔧 Updated backend .env file")

        # Update contracts .env
        contracts_env = self.contracts_dir / ".env"
        with open(contracts_env, 'a') as f:
            f.write(f"\n# Mock Deployment Results ({self.network})\n")
            f.write(f"MOCK_POLICY_ID={contracts['token']['policy_id']}\n")
            f.write(f"MOCK_IDENTITY_ADDRESS={contracts['identity']['address']}\n")
            f.write(f"MOCK_DEPLOYMENT_TX={contracts['token']['deployment_tx']}\n")
        print(f"🔧 Updated contracts .env file")

    def run_deployment(self) -> Dict[str, Any]:
        """Run the complete mock deployment process"""
        print("🎭 Starting Mock Cardano Contract Deployment")
        print("=" * 50)
        print(f"Network: {self.network}")
        print("Note: This is a simulation for testing purposes")
        print("=" * 50)

        contracts = {}

        try:
            # Deploy contracts
            contracts['identity'] = self.deploy_identity_contract()
            print()

            contracts['token'] = self.deploy_token_contract()
            print()

            contracts['governance'] = self.deploy_governance_contract()
            print()

            # Save deployment info
            self.save_deployment_info(contracts)

            # Update environment files
            self.update_env_file(contracts)

            print()
            print("=" * 50)
            print("🎉 MOCK DEPLOYMENT SUCCESSFUL!")
            print("=" * 50)
            print(f"Network: {self.network}")
            print(f"Identity Contract: {contracts['identity']['address']}")
            print(f"Token Policy ID: {contracts['token']['policy_id']}")
            print(f"Governance Contract: {contracts['governance']['address']}")
            print(f"Initial Supply: {contracts['token']['initial_supply']} NIMO")
            print("=" * 50)

            return contracts

        except Exception as e:
            print(f"❌ Mock deployment failed: {e}")
            return {}

def main():
    """Main deployment function"""
    network = sys.argv[1] if len(sys.argv) > 1 else "preview"

    if network not in ["preview", "preprod", "mainnet"]:
        print(f"❌ Invalid network: {network}")
        print("Valid networks: preview, preprod, mainnet")
        sys.exit(1)

    deployer = MockCardanoDeployer(network)
    result = deployer.run_deployment()

    if result:
        print("\n✅ Mock deployment completed successfully!")
        print("📝 Next steps:")
        print("   1. Review the deployment files in contracts/deployments/")
        print("   2. Update your backend configuration")
        print("   3. Test the integration with mock data")
        print("   4. For real deployment, get Blockfrost API key and run:")
        print(f"      python deploy_nimo_token.py --network {network}")
    else:
        print("\n❌ Mock deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()