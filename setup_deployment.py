#!/usr/bin/env python3
"""
Setup script for Base Sepolia deployment
"""

import os
import json
from pathlib import Path
from eth_account import Account
from dotenv import set_key

def setup_deployment():
    """Setup deployment configuration for Base Sepolia"""

    print("🚀 Nimo Platform - Base Sepolia Deployment Setup")
    print("=" * 60)

    # Get private key from user
    print("\n1. 🔑 Private Key Setup")
    print("   You need a private key for contract deployment and transactions")
    print("   Options:")
    print("   a) Use existing wallet (MetaMask, Coinbase Wallet, etc.)")
    print("   b) Generate new key (for testing only)")

    choice = input("\n   Do you have an existing private key? (y/n): ").lower()

    if choice == 'y':
        private_key = input("   Enter your private key (without 0x prefix): ").strip()
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
    else:
        # Generate new key for testing
        print("   ⚠️  Generating new private key (for testing only!)")
        account = Account.create()
        private_key = account.key.hex()
        print(f"   📝 New private key: {private_key}")
        print(f"   📝 Account address: {account.address}")
        print("   💰 Fund this address with SepoliaETH for deployment")

    # Validate private key
    try:
        account = Account.from_key(private_key)
        print(f"   ✅ Valid private key - Account: {account.address}")
    except Exception as e:
        print(f"   ❌ Invalid private key: {e}")
        return False

    # Update contracts/.env
    contracts_env = Path("contracts/.env")
    if not contracts_env.exists():
        contracts_env.touch()

    set_key(contracts_env, "PRIVATE_KEY", private_key)
    print(f"   ✅ Updated contracts/.env with private key")

    # Update backend/.env
    backend_env = Path("backend/.env")
    set_key(backend_env, "BLOCKCHAIN_SERVICE_PRIVATE_KEY", private_key)
    print(f"   ✅ Updated backend/.env with private key")

    # Display funding information
    print("\n2. 💰 Funding Information")
    print(f"   Account Address: {account.address}")
    print("   Network: Base Sepolia")
    print("   Required: ~0.01 ETH for deployment")
    print("   Faucet: https://faucet.quicknode.com/base/sepolia")
    print("   Block Explorer: https://sepolia.basescan.org")

    # Create deployment info
    deployment_info = {
        "network": "base-sepolia",
        "account_address": account.address,
        "private_key_set": True,
        "next_steps": [
            "Fund account with SepoliaETH",
            "Run deployment script",
            "Update .env with deployed contract addresses"
        ]
    }

    with open("deployment_setup.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("\n3. 📋 Next Steps")
    print("   a) Fund your account with SepoliaETH from the faucet")
    print("   b) Run deployment: cd contracts && forge script script/Deploy.s.sol --rpc-url base-sepolia --broadcast --verify")
    print("   c) Update .env files with deployed contract addresses")

    print(f"\n   📄 Setup saved to: deployment_setup.json")
    print("   🔗 Account to fund: https://sepolia.basescan.org/address/" + account.address)

    return True

if __name__ == "__main__":
    setup_deployment()