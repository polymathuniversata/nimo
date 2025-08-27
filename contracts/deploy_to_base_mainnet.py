#!/usr/bin/env python3
"""
Deploy NimoIdentity to Base Mainnet with USDC Integration

This script deploys only NimoIdentity contract to Base mainnet
and integrates with existing USDC contract for token rewards.
"""

import os
import json
import sys
from pathlib import Path
from web3 import Web3
from eth_account import Account
import time
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()

class BaseMainnetDeployer:
    def __init__(self):
        """Initialize deployer for Base mainnet"""
        self.network = 'base-mainnet'
        self.rpc_url = 'https://mainnet.base.org'
        self.chain_id = 8453
        self.explorer_url = 'https://basescan.org'

        # USDC on Base mainnet
        self.usdc_address = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'

        # Initialize Web3
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.web3.is_connected():
            raise Exception("Failed to connect to Base mainnet")

        # Load deployer account
        private_key = os.getenv('BLOCKCHAIN_SERVICE_PRIVATE_KEY')
        if not private_key or private_key == 'your_service_private_key_here':
            raise Exception("Please set BLOCKCHAIN_SERVICE_PRIVATE_KEY in .env file")

        self.account = Account.from_key(private_key)
        print(f"Deploying from account: {self.account.address}")

        # Check account balance
        balance = self.web3.eth.get_balance(self.account.address)
        balance_eth = self.web3.from_wei(balance, 'ether')
        print(f"Account balance: {balance_eth} ETH")

        if balance_eth < 0.1:  # Need at least 0.1 ETH for mainnet deployment
            raise Exception(f"Insufficient balance. Need at least 0.1 ETH, have {balance_eth} ETH")

        # Load contract artifacts
        self.contracts_dir = Path(__file__).parent
        self.load_contract_artifacts()

    def load_contract_artifacts(self):
        """Load compiled contract artifacts"""
        # Load the actual compiled NimoIdentity contract
        try:
            with open(self.contracts_dir / 'out' / 'NimoIdentity.sol' / 'NimoIdentity.json', 'r') as f:
                artifact = json.load(f)
                self.nimo_identity_artifact = {
                    'abi': artifact['abi'],
                    'bytecode': artifact['bytecode']['object']
                }
        except FileNotFoundError:
            raise Exception("Compiled contract not found. Please run 'forge build' first")

    def estimate_gas_price(self):
        """Get optimal gas price for Base mainnet"""
        try:
            gas_price = self.web3.eth.gas_price
            # Base mainnet gas prices are higher than testnet
            return min(int(gas_price * 1.2), self.web3.to_wei(10, 'gwei'))
        except Exception:
            # Fallback to 5 gwei for Base mainnet
            return self.web3.to_wei(5, 'gwei')

    def deploy_identity_contract(self):
        """Deploy NimoIdentity contract"""
        print("
🚀 Deploying NimoIdentity to Base Mainnet..."        print(f"🌐 Network: {self.network}")
        print(f"🌐 RPC URL: {self.rpc_url}")
        print(f"🌐 Chain ID: {self.chain_id}")
        print(f"👤 Deployer: {self.account.address}")
        print(f"💰 USDC Address: {self.usdc_address}")

        # Create contract instance
        contract = self.web3.eth.contract(
            abi=self.nimo_identity_artifact['abi'],
            bytecode=self.nimo_identity_artifact['bytecode']
        )

        try:
            # Build constructor transaction
            constructor_txn = contract.constructor().build_transaction({
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.estimate_gas_price(),
                'chainId': self.chain_id
            })

            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas(constructor_txn)
            constructor_txn['gas'] = int(gas_estimate * 1.3)  # 30% buffer for mainnet

            print(f"  💰 Estimated gas: {gas_estimate:,}")
            print(f"  💰 Gas price: {self.web3.from_wei(constructor_txn['gasPrice'], 'gwei'):.2f} gwei")
            print(f"  💰 Estimated cost: {self.web3.from_wei(gas_estimate * constructor_txn['gasPrice'], 'ether'):.4f} ETH")

            # Confirm deployment
            confirm = input("  ⚠️  Deploy to mainnet? This will cost real ETH! (y/N): ")
            if confirm.lower() != 'y':
                print("  ❌ Deployment cancelled")
                return None

            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(constructor_txn, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            print(f"  📄 Transaction hash: {tx_hash.hex()}")
            print(f"  🔗 Explorer: {self.explorer_url}/tx/{tx_hash.hex()}")

            # Wait for confirmation
            print("  ⏳ Waiting for confirmation...")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)  # 10 min timeout

            if receipt.status == 1:
                contract_address = receipt.contractAddress
                print(f"  ✅ NimoIdentity deployed successfully!")
                print(f"  📍 Contract address: {contract_address}")
                print(f"  🔗 Explorer: {self.explorer_url}/address/{contract_address}")

                return {
                    'name': 'NimoIdentity',
                    'address': contract_address,
                    'tx_hash': tx_hash.hex(),
                    'block_number': receipt.blockNumber,
                    'gas_used': receipt.gasUsed,
                    'usdc_address': self.usdc_address
                }
            else:
                raise Exception(f"Transaction failed with status {receipt.status}")

        except Exception as e:
            print(f"  ❌ Deployment failed: {e}")
            raise

    def update_env_file(self, deployment_result):
        """Update .env file with deployed contract addresses"""
        print("\n📝 Updating .env file with deployed addresses...")

        env_file = Path(__file__).parent.parent / 'backend' / '.env'

        # Set mainnet addresses
        set_key(env_file, 'NIMO_IDENTITY_CONTRACT_BASE_MAINNET', deployment_result['address'])
        set_key(env_file, 'USDC_CONTRACT_BASE_MAINNET', self.usdc_address)

        print(f"  ✅ Set NIMO_IDENTITY_CONTRACT_BASE_MAINNET={deployment_result['address']}")
        print(f"  ✅ Set USDC_CONTRACT_BASE_MAINNET={self.usdc_address}")

    def save_deployment_info(self, deployment_result):
        """Save deployment information to file"""
        deployment_info = {
            'network': self.network,
            'chain_id': self.chain_id,
            'deployer': self.account.address,
            'timestamp': int(time.time()),
            'contracts': [deployment_result],
            'explorer_base_url': self.explorer_url,
            'usdc_integration': True
        }

        deployments_dir = Path(__file__).parent / 'deployments'
        deployments_dir.mkdir(exist_ok=True)

        deployment_file = deployments_dir / f'base-mainnet-{int(time.time())}.json'

        with open(deployment_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)

        print(f"📄 Deployment info saved to: {deployment_file}")

    def verify_deployment(self, deployment_result):
        """Verify deployed contract is working"""
        print("\n🔍 Verifying deployment...")

        try:
            contract = self.web3.eth.contract(
                address=deployment_result['address'],
                abi=self.nimo_identity_artifact['abi']
            )

            # Test basic functions
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            chain_id = contract.functions.getChainId().call()

            print(f"  ✅ Contract name: {name}")
            print(f"  ✅ Contract symbol: {symbol}")
            print(f"  ✅ Chain ID: {chain_id}")

            return True

        except Exception as e:
            print(f"  ❌ Verification failed: {e}")
            return False

def main():
    """Main deployment function"""
    try:
        print("🚨 BASE MAINNET DEPLOYMENT 🚨")
        print("This will deploy to Ethereum mainnet with real ETH costs!")
        print("Make sure you have:")
        print("  - Sufficient ETH balance (>0.1 ETH recommended)")
        print("  - Private key with mainnet funds")
        print("  - Compiled contracts (run 'forge build' first)")
        print()

        # Create deployer instance
        deployer = BaseMainnetDeployer()

        # Deploy contract
        deployment_result = deployer.deploy_identity_contract()

        if deployment_result:
            # Update environment file
            deployer.update_env_file(deployment_result)

            # Save deployment info
            deployer.save_deployment_info(deployment_result)

            # Verify deployment
            if deployer.verify_deployment(deployment_result):
                print("\n🎉 Mainnet deployment completed successfully!")
                print("\n📋 Summary:")
                print(f"  NimoIdentity: {deployment_result['address']}")
                print(f"  USDC Integration: {deployer.usdc_address}")
                print(f"\n🔗 Block Explorer: {deployer.explorer_url}")
                print("\n🔧 Next steps:")
                print("  1. Update frontend configuration with mainnet addresses")
                print("  2. Test identity creation on mainnet")
                print("  3. Monitor contract activity")
            else:
                print("\n⚠️  Deployment completed but verification failed")
        else:
            print("\n❌ Deployment was cancelled or failed")

    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\contracts\deploy_to_base_mainnet.py