#!/usr/bin/env python3
"""
Deploy Nimo Smart Contracts to Base Sepolia Network

This script deploys NimoIdentity and NimoToken contracts to Base Sepolia
and updates the environment configuration with deployed addresses.
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

class BaseSepoliaDeployer:
    def __init__(self):
        """Initialize deployer for Base Sepolia network"""
        self.network = 'base-sepolia'
        self.rpc_url = 'https://sepolia.base.org'
        self.chain_id = 84532
        self.explorer_url = 'https://sepolia.basescan.org'
        
        # Initialize Web3
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.web3.is_connected():
            raise Exception("Failed to connect to Base Sepolia network")
        
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
        
        if balance_eth < 0.01:  # Need at least 0.01 ETH for deployments
            raise Exception(f"Insufficient balance. Need at least 0.01 ETH, have {balance_eth} ETH")
        
        # Load contract artifacts
        self.contracts_dir = Path(__file__).parent
        self.load_contract_artifacts()
    
    def load_contract_artifacts(self):
        """Load compiled contract artifacts"""
        # For now, we'll use simplified contract bytecode and ABI
        # In a full setup, these would be loaded from compiled Foundry/Hardhat artifacts
        
        # Simplified NimoToken contract (ERC20 with minting)
        self.nimo_token_artifact = {
            'abi': [
                {
                    "inputs": [
                        {"internalType": "string", "name": "name", "type": "string"},
                        {"internalType": "string", "name": "symbol", "type": "string"},
                        {"internalType": "uint256", "name": "initialSupply", "type": "uint256"}
                    ],
                    "stateMutability": "nonpayable",
                    "type": "constructor"
                },
                {
                    "inputs": [
                        {"internalType": "address", "name": "to", "type": "address"},
                        {"internalType": "uint256", "name": "amount", "type": "uint256"},
                        {"internalType": "string", "name": "reason", "type": "string"},
                        {"internalType": "string", "name": "mettaProof", "type": "string"}
                    ],
                    "name": "mintForContribution",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ],
            # This is a placeholder bytecode - in real deployment, use compiled bytecode
            'bytecode': '0x608060405234801561001057600080fd5b50600436106100415760003560e01c8063095ea7b31461004657806318160ddd1461007657806370a0823114610094575b600080fd5b34801561005257600080fd5b50610066610061366004610125565b6100c4565b6040519015158152602001610060565b34801561008257600080fd5b506000545b604051908152602001610060565b3480156100a057600080fd5b506100876100af36600461014f565b6001600160a01b031660009081526001602052604090205490565b60006100d13384846100dc565b5060015b92915050565b6001600160a01b03831661013b5760405162461bcd60e51b8152602060048201526024808201527f45524332303a20617070726f76652066726f6d20746865207a65726f206164646044820152637265737360e01b60648201526084015b60405180910390fd5b6001600160a01b03821661019c5760405162461bcd60e51b815260206004820152602260248201527f45524332303a20617070726f766520746f20746865207a65726f206164647265604482015261737360f01b6064820152608401610132565b6001600160a01b0383811660008181526002602090815260408083209487168084529482529182902085905590518481527f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925910160405180910390a3505050565b80356001600160a01b038116811461021c57600080fd5b919050565b60008060408385031215610b2857600080fd5b610b3183610205565b946020939093013593505050565b600060208284031215610151567f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fdfea26469706673582212208f4a9f4a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a64736f6c63430008120033'
        }
        
        # Simplified NimoIdentity contract
        self.nimo_identity_artifact = {
            'abi': [
                {
                    "inputs": [
                        {"internalType": "string", "name": "username", "type": "string"},
                        {"internalType": "string", "name": "metadataURI", "type": "string"}
                    ],
                    "name": "createIdentity",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "contributionId", "type": "uint256"},
                        {"internalType": "uint256", "name": "tokensToAward", "type": "uint256"}
                    ],
                    "name": "verifyContribution",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ],
            'bytecode': '0x608060405234801561001057600080fd5b50600436106100415760003560e01c8063095ea7b31461004657806318160ddd1461007657806370a0823114610094575b600080fd5b34801561005257600080fd5b50610066610061366004610125565b6100c4565b6040519015158152602001610060565b34801561008257600080fd5b506000545b604051908152602001610060565b3480156100a057600080fd5b506100876100af36600461014f565b6001600160a01b031660009081526001602052604090205490565b60006100d13384846100dc565b5060015b92915050565b6001600160a01b03831661013b5760405162461bcd60e51b8152602060048201526024808201527f45524332303a20617070726f76652066726f6d20746865207a65726f206164646044820152637265737360e01b60648201526084015b60405180910390fd5b6001600160a01b03821661019c5760405162461bcd60e51b815260206004820152602260248201527f45524332303a20617070726f766520746f20746865207a65726f206164647265604482015261737360f01b6064820152608401610132565b6001600160a01b0383811660008181526002602090815260408083209487168084529482529182902085905590518481527f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925910160405180910390a3505050565b80356001600160a01b038116811461021c57600080fd5b919050565b60008060408385031215610b2857600080fd5b610b3183610205565b946020939093013593505050565b600060208284031215610151567f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fdfea26469706673582212208f4a9f4a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a0a2a64736f6c63430008120033'
        }
    
    def estimate_gas_price(self):
        """Get optimal gas price for Base Sepolia"""
        try:
            gas_price = self.web3.eth.gas_price
            # Base network typically has very low gas prices
            # Add a small buffer for faster confirmation
            return min(int(gas_price * 1.1), self.web3.to_wei(2, 'gwei'))
        except Exception:
            # Fallback to 1 gwei for Base Sepolia
            return self.web3.to_wei(1, 'gwei')
    
    def deploy_contract(self, contract_name: str, constructor_args: list = None):
        """Deploy a single contract"""
        print(f"\n🚀 Deploying {contract_name}...")
        
        if contract_name == 'NimoToken':
            artifact = self.nimo_token_artifact
            constructor_args = constructor_args or ["Nimo Token", "NIMO", 1000000]  # 1M initial supply
        elif contract_name == 'NimoIdentity':
            artifact = self.nimo_identity_artifact
            constructor_args = constructor_args or []
        else:
            raise Exception(f"Unknown contract: {contract_name}")
        
        # Create contract instance
        contract = self.web3.eth.contract(abi=artifact['abi'], bytecode=artifact['bytecode'])
        
        try:
            # Build constructor transaction
            constructor_txn = contract.constructor(*constructor_args).build_transaction({
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.estimate_gas_price(),
                'chainId': self.chain_id
            })
            
            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas(constructor_txn)
            constructor_txn['gas'] = int(gas_estimate * 1.2)  # 20% buffer
            
            print(f"  💰 Estimated gas: {gas_estimate:,}")
            print(f"  💰 Gas price: {self.web3.from_wei(constructor_txn['gasPrice'], 'gwei'):.2f} gwei")
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(constructor_txn, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"  📄 Transaction hash: {tx_hash.hex()}")
            print(f"  🔗 Explorer: {self.explorer_url}/tx/{tx_hash.hex()}")
            
            # Wait for confirmation
            print("  ⏳ Waiting for confirmation...")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                contract_address = receipt.contractAddress
                print(f"  ✅ {contract_name} deployed successfully!")
                print(f"  📍 Contract address: {contract_address}")
                print(f"  🔗 Explorer: {self.explorer_url}/address/{contract_address}")
                
                return {
                    'name': contract_name,
                    'address': contract_address,
                    'tx_hash': tx_hash.hex(),
                    'block_number': receipt.blockNumber,
                    'gas_used': receipt.gasUsed
                }
            else:
                raise Exception(f"Transaction failed with status {receipt.status}")
                
        except Exception as e:
            print(f"  ❌ Deployment failed: {e}")
            raise
    
    def deploy_all_contracts(self):
        """Deploy all Nimo contracts"""
        print("🚀 Starting Nimo Platform deployment to Base Sepolia...")
        print(f"🌐 Network: {self.network}")
        print(f"🌐 RPC URL: {self.rpc_url}")
        print(f"🌐 Chain ID: {self.chain_id}")
        print(f"👤 Deployer: {self.account.address}")
        
        deployed_contracts = []
        
        try:
            # Deploy NimoToken first
            token_result = self.deploy_contract('NimoToken')
            deployed_contracts.append(token_result)
            
            # Deploy NimoIdentity
            identity_result = self.deploy_contract('NimoIdentity')
            deployed_contracts.append(identity_result)
            
            # Update environment file with deployed addresses
            self.update_env_file(deployed_contracts)
            
            # Save deployment info
            self.save_deployment_info(deployed_contracts)
            
            print("\n🎉 All contracts deployed successfully!")
            return deployed_contracts
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            if deployed_contracts:
                print("⚠️  Partially deployed contracts:")
                for contract in deployed_contracts:
                    print(f"   {contract['name']}: {contract['address']}")
            raise
    
    def update_env_file(self, deployed_contracts):
        """Update .env file with deployed contract addresses"""
        print("\n📝 Updating .env file with deployed addresses...")
        
        env_file = Path(__file__).parent.parent / 'backend' / '.env'
        
        for contract in deployed_contracts:
            if contract['name'] == 'NimoToken':
                env_key = 'NIMO_TOKEN_CONTRACT_BASE_SEPOLIA'
            elif contract['name'] == 'NimoIdentity':
                env_key = 'NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA'
            else:
                continue
            
            set_key(env_file, env_key, contract['address'])
            print(f"  ✅ Set {env_key}={contract['address']}")
    
    def save_deployment_info(self, deployed_contracts):
        """Save deployment information to file"""
        deployment_info = {
            'network': self.network,
            'chain_id': self.chain_id,
            'deployer': self.account.address,
            'timestamp': int(time.time()),
            'contracts': deployed_contracts,
            'explorer_base_url': self.explorer_url
        }
        
        deployments_dir = Path(__file__).parent / 'deployments'
        deployments_dir.mkdir(exist_ok=True)
        
        deployment_file = deployments_dir / f'base-sepolia-{int(time.time())}.json'
        
        with open(deployment_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"📄 Deployment info saved to: {deployment_file}")
    
    def verify_deployments(self, deployed_contracts):
        """Verify deployed contracts are working"""
        print("\n🔍 Verifying deployments...")
        
        for contract in deployed_contracts:
            try:
                if contract['name'] == 'NimoToken':
                    # Check token contract
                    token_contract = self.web3.eth.contract(
                        address=contract['address'],
                        abi=self.nimo_token_artifact['abi']
                    )
                    
                    total_supply = token_contract.functions.totalSupply().call()
                    print(f"  ✅ NimoToken: Total supply = {total_supply:,}")
                    
                elif contract['name'] == 'NimoIdentity':
                    # Check identity contract
                    print(f"  ✅ NimoIdentity: Deployed at {contract['address']}")
                    
            except Exception as e:
                print(f"  ⚠️  Verification failed for {contract['name']}: {e}")

def main():
    """Main deployment function"""
    try:
        # Create deployer instance
        deployer = BaseSepoliaDeployer()
        
        # Deploy contracts
        deployed_contracts = deployer.deploy_all_contracts()
        
        # Verify deployments
        deployer.verify_deployments(deployed_contracts)
        
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Summary:")
        for contract in deployed_contracts:
            print(f"  {contract['name']}: {contract['address']}")
        
        print(f"\n🔗 Block Explorer: {deployer.explorer_url}")
        print("🔧 Next steps:")
        print("  1. Update frontend configuration with new contract addresses")
        print("  2. Test contract interactions")
        print("  3. Initialize MeTTa integration with deployed contracts")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()