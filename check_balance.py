#!/usr/bin/env python3
"""
Check account balance and explore funding options
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_balance():
    """Check account balance on Base Sepolia"""

    # Load deployment info
    if os.path.exists("deployment_setup.json"):
        with open("deployment_setup.json", "r") as f:
            deployment_info = json.load(f)
        account_address = deployment_info.get("account_address")
    else:
        print("❌ No deployment setup found. Run setup_deployment.py first.")
        return

    print("🔍 Checking Account Balance on Base Sepolia")
    print("=" * 50)
    print(f"Account: {account_address}")
    print(f"Network: Base Sepolia (Testnet)")
    print(f"RPC: https://sepolia.base.org")

    try:
        # Connect to Base Sepolia
        web3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))

        if not web3.is_connected():
            print("❌ Cannot connect to Base Sepolia")
            return

        # Get balance
        balance_wei = web3.eth.get_balance(account_address)
        balance_eth = web3.from_wei(balance_wei, 'ether')

        print(f"Balance (ETH): {balance_eth:.6f}")
        print(f"Balance (Wei): {balance_wei}")

        if balance_eth >= 0.01:
            print("✅ Sufficient balance for deployment!")
            return True
        else:
            print("❌ Insufficient balance for deployment")
            print("   Need: ~0.01 ETH")
            print(f"   Have: {balance_eth:.6f}")
            return False

    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return False

def show_funding_options():
    """Show alternative funding options"""

    print("\n💰 Alternative Funding Options (No Mainnet ETH Required)")
    print("=" * 60)

    options = [
        {
            "name": "Alchemy Faucet",
            "url": "https://sepoliafaucet.com",
            "description": "Free Sepolia ETH, may have queue",
            "requirements": "None"
        },
        {
            "name": "Infura Faucet",
            "url": "https://www.infura.io/faucet/sepolia",
            "description": "Infura's Sepolia faucet",
            "requirements": "Infura account"
        },
        {
            "name": "QuickNode Faucet",
            "url": "https://faucet.quicknode.com/drip",
            "description": "QuickNode's faucet (may require API key)",
            "requirements": "QuickNode account"
        },
        {
            "name": "PoW Faucet",
            "url": "https://sepolia-faucet.pk910.de",
            "description": "Proof-of-work faucet (mine ETH)",
            "requirements": "Complete captcha/mining"
        },
        {
            "name": "Chainstack Faucet",
            "url": "https://faucet.chainstack.com/sepolia-testnet-faucet",
            "description": "Chainstack's faucet",
            "requirements": "None"
        }
    ]

    for i, option in enumerate(options, 1):
        print(f"\n{i}. {option['name']}")
        print(f"   URL: {option['url']}")
        print(f"   Description: {option['description']}")
        print(f"   Requirements: {option['requirements']}")

    print("\n🔧 Additional Options:")
    print("• Use a different wallet with existing Sepolia ETH")
    print("• Ask in Discord communities (Base, Ethereum)")
    print("• Use testnet bridges if you have ETH on other testnets")

def check_existing_accounts():
    """Check if there are other accounts with balance"""

    print("\n🔍 Checking for Existing Accounts")
    print("=" * 40)

    # Check if there are any other private keys or accounts in env files
    env_files = ["backend/.env", "contracts/.env", ".env"]

    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"\nChecking {env_file}:")
            with open(env_file, "r") as f:
                content = f.read()
                # Look for any ethereum addresses
                import re
                addresses = re.findall(r'0x[a-fA-F0-9]{40}', content)
                for addr in addresses:
                    print(f"  Found address: {addr}")

def main():
    """Main function"""

    print("🚀 Nimo Platform - Balance Check & Funding Options")
    print("=" * 60)

    # Check current balance
    has_balance = check_balance()

    if not has_balance:
        show_funding_options()

    check_existing_accounts()

    print("\n📋 Summary:")
    if has_balance:
        print("✅ Ready for deployment!")
        print("   Run: cd contracts && forge script script/Deploy.s.sol --rpc-url base-sepolia --broadcast --verify")
    else:
        print("❌ Need to fund account first")
        print("   Use one of the faucet options above")
        print("   Then run deployment command")

if __name__ == "__main__":
    main()