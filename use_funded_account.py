#!/usr/bin/env python3
"""
Update deployment to use funded a                print("✅ Updated contracts/.env with private key")
                print("✅ Updated backend/.env with private key")
                print("✅ Ready for deployment!")count
"""

import os
import json
from pathlib import Path
from dotenv import set_key

def update_deployment_for_funded_account():
    """Update deployment configuration to use the funded account"""

    funded_address = "0x56186c1e64ca8043DEF78d06Aff222212ea5df71"
    funded_balance = "0.021169 ETH"

    print("🎉 FOUND FUNDED ACCOUNT!")
    print("=" * 50)
    print(f"Address: {funded_address}")
    print(f"Balance: {funded_balance}")
    print("✅ Sufficient for deployment (need only ~0.01 ETH)")

    print("\n🔑 Private Key Required")
    print("This address needs a private key to deploy contracts.")
    print("\nOptions:")
    print("1. If you have MetaMask/Coinbase Wallet connected to this address")
    print("2. If you have the private key from previous deployments")
    print("3. If this is from a hardware wallet")

    choice = input("\nDo you have the private key for this address? (y/n): ").lower()

    if choice == 'y':
        private_key = input("Enter the private key (without 0x prefix): ").strip()
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key

        # Validate private key matches address
        from eth_account import Account
        try:
            account = Account.from_key(private_key)
            if account.address.lower() == funded_address.lower():
                print(f"✅ Valid private key for address {funded_address}")

                # Update deployment setup
                deployment_info = {
                    "network": "base-sepolia",
                    "account_address": funded_address,
                    "private_key_set": True,
                    "balance": funded_balance,
                    "next_steps": [
                        "Deploy contracts using funded account",
                        "Update .env with deployed contract addresses"
                    ]
                }

                with open("deployment_setup.json", "w") as f:
                    json.dump(deployment_info, f, indent=2)

                # Update env files
                set_key(Path("contracts/.env"), "PRIVATE_KEY", private_key)
                set_key(Path("backend/.env"), "BLOCKCHAIN_SERVICE_PRIVATE_KEY", private_key)

                print("✅ Updated contracts/.env with private key")
                print("✅ Updated backend/.env with private key")
                print("✅ Ready for deployment!")
                return True
            else:
                print(f"❌ Private key doesn't match address {funded_address}")
                return False

        except Exception as e:
            print(f"❌ Invalid private key: {e}")
            return False

    else:
        print("\n🔧 How to get the private key:")
        print("\n1. MetaMask/Coinbase Wallet:")
        print("   - Open your wallet")
        print("   - Go to Account Details")
        print("   - Export Private Key")
        print("   - Copy the key (starts with 0x)")

        print("\n2. If you used this for previous deployments:")
        print("   - Check your deployment records")
        print("   - Look in old .env files")
        print("   - Check deployment scripts")

        print("\n3. Alternative: Use a different address")
        print("   - Generate new account with setup_deployment.py")
        print("   - Use faucet to fund it")

        return False

def show_deployment_command():
    """Show the deployment command"""

    print("\n🚀 DEPLOYMENT COMMAND:")
    print("=" * 40)
    print("cd contracts")
    print("forge script script/Deploy.s.sol --rpc-url base-sepolia --broadcast --verify")
    print("\nThis will:")
    print("• Deploy NimoToken contract")
    print("• Deploy NimoIdentity contract")
    print("• Set up roles and permissions")
    print("• Save deployment addresses")

def main():
    """Main function"""

    print("🚀 Nimo Platform - Use Funded Account for Deployment")
    print("=" * 60)

    success = update_deployment_for_funded_account()

    if success:
        show_deployment_command()
        print("\n📋 AFTER DEPLOYMENT:")
        print("• Update backend/.env with new contract addresses")
        print("• Test backend integration")
        print("• Run end-to-end tests")
    else:
        print("\n❌ Could not configure funded account")
        print("💡 Try: python setup_deployment.py (for new account)")
        print("   Then use faucet to fund it")

if __name__ == "__main__":
    main()