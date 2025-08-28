#!/usr/bin/env python3
"""
Check balance of existing addresses and provide funding guide
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_existing_addresses():
    """Check balance of addresses found in env files"""

    addresses = [
        "0x56186c1e64ca8043DEF78d06Aff222212ea5df71",  # From .env files
        "0x53Eba1e079F885482238EE8bf01C4A9f09DE458f",  # From .env files
        "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # USDC on Sepolia
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478",  # Anvil default
    ]

    print("🔍 Checking Existing Addresses for Balance")
    print("=" * 50)

    try:
        web3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))

        if not web3.is_connected():
            print("❌ Cannot connect to Base Sepolia")
            return

        for address in addresses:
            balance_wei = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')

            print(f"\nAddress: {address}")
            print(f"Balance: {balance_eth:.6f} ETH")

            if balance_eth > 0:
                print("✅ HAS BALANCE!")
                return address
            else:
                print("❌ No balance")

    except Exception as e:
        print(f"❌ Error: {e}")

    return None

def comprehensive_funding_guide():
    """Provide comprehensive funding options"""

    print("\n💰 COMPREHENSIVE FUNDING GUIDE")
    print("=" * 60)
    print("🚫 AVOID faucets that require mainnet ETH!")
    print("✅ USE these working options:\n")

    # Working faucets (no mainnet ETH required)
    faucets = [
        {
            "name": "Sepolia Faucet (pk910)",
            "url": "https://sepolia-faucet.pk910.de/",
            "description": "Proof-of-work faucet - just solve captcha",
            "amount": "0.5 ETH",
            "wait_time": "None",
            "requirements": "Complete captcha"
        },
        {
            "name": "Chainstack Faucet",
            "url": "https://faucet.chainstack.com/sepolia-testnet-faucet",
            "description": "Direct faucet - no requirements",
            "amount": "0.1 ETH",
            "wait_time": "None",
            "requirements": "None"
        },
        {
            "name": "Alchemy Sepolia Faucet",
            "url": "https://sepoliafaucet.com/",
            "description": "Alchemy's official faucet",
            "amount": "0.5 ETH",
            "wait_time": "Queue system",
            "requirements": "May need to wait in queue"
        },
        {
            "name": "Infura Sepolia Faucet",
            "url": "https://www.infura.io/faucet/sepolia",
            "description": "Infura's faucet",
            "amount": "0.5 ETH",
            "wait_time": "None",
            "requirements": "Infura account (free)"
        },
        {
            "name": "QuickNode Alternative",
            "url": "https://faucet.quicknode.com/",
            "description": "QuickNode's alternative faucet",
            "amount": "0.1 ETH",
            "wait_time": "None",
            "requirements": "May need API key"
        }
    ]

    for i, faucet in enumerate(faucets, 1):
        print(f"{i}. {faucet['name']}")
        print(f"   URL: {faucet['url']}")
        print(f"   Amount: {faucet['amount']}")
        print(f"   Wait Time: {faucet['wait_time']}")
        print(f"   Requirements: {faucet['requirements']}\n")

    print("🎯 RECOMMENDED APPROACH:")
    print("1. Try Chainstack Faucet first (fastest)")
    print("2. If that doesn't work, use pk910 PoW faucet")
    print("3. Use your address: 0x36Ae6475851858fffBBa2f7a746bc98766d4792D")
    print("4. Request 0.1 ETH (more than enough for deployment)")

    print("\n🔧 ALTERNATIVE APPROACHES:")
    print("• Use MetaMask mobile app faucet (if you have MetaMask)")
    print("• Join Base Discord and ask for testnet ETH")
    print("• Use a different wallet that already has Sepolia ETH")

def main():
    """Main function"""

    print("🚀 Nimo Platform - Funding Status Check")
    print("=" * 60)

    # Check existing addresses
    funded_address = check_existing_addresses()

    if funded_address:
        print(f"\n🎉 FOUND FUNDED ADDRESS: {funded_address}")
        print("You can use this address for deployment!")
        return

    # Show funding options
    comprehensive_funding_guide()

    print("\n📋 NEXT STEPS:")
    print("1. Pick a faucet from the list above")
    print("2. Use address: 0x36Ae6475851858fffBBa2f7a746bc98766d4792D")
    print("3. Request at least 0.01 ETH")
    print("4. Wait for confirmation (1-2 minutes)")
    print("5. Run: python check_balance.py (to verify)")
    print("6. Deploy: cd contracts && forge script script/Deploy.s.sol --rpc-url base-sepolia --broadcast --verify")

if __name__ == "__main__":
    main()