#!/usr/bin/env python3
"""
Check contract deployer/owner addresses on Base Sepolia
"""

import os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_contract_deployer():
    """Check who deployed the contracts and their current balance"""

    # Initialize Web3 connection to Base Sepolia
    rpc_url = 'https://sepolia.base.org'
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    if not web3.is_connected():
        print("❌ Failed to connect to Base Sepolia")
        return

    print("✅ Connected to Base Sepolia")
    print(f"🔗 RPC URL: {rpc_url}")
    print(f"🆔 Chain ID: {web3.eth.chain_id}")

    # Contract addresses from .env
    nimo_identity_address = os.getenv('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA')
    nimo_token_address = os.getenv('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA')

    print(f"\n📋 Contract Addresses:")
    print(f"  NimoIdentity: {nimo_identity_address}")
    print(f"  NimoToken: {nimo_token_address}")

    # Check contract deployment transaction
    for contract_name, address in [("NimoIdentity", nimo_identity_address), ("NimoToken", nimo_token_address)]:
        if address:
            try:
                # Get contract code
                code = web3.eth.get_code(address)
                if code == b'':
                    print(f"❌ {contract_name}: No contract found at {address}")
                    continue

                print(f"\n✅ {contract_name} contract found at {address}")

                # Try to get owner (common pattern)
                try:
                    # Create contract instance (minimal ABI for owner function)
                    abi = [{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]
                    contract = web3.eth.contract(address=address, abi=abi)
                    owner = contract.functions.owner().call()
                    print(f"  👤 Owner: {owner}")

                    # Check owner balance
                    balance = web3.eth.get_balance(owner)
                    balance_eth = web3.from_wei(balance, 'ether')
                    print(f"  💰 Owner Balance: {balance_eth:.6f} ETH")

                    if balance_eth < 0.001:
                        print(f"  ⚠️  LOW BALANCE: Owner needs more ETH for transactions")
                    else:
                        print(f"  ✅ Sufficient balance for transactions")

                except Exception as e:
                    print(f"  ⚠️  Could not get owner info: {e}")

            except Exception as e:
                print(f"❌ Error checking {contract_name}: {e}")

if __name__ == "__main__":
    check_contract_deployer()