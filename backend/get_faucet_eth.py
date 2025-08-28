#!/usr/bin/env python3
"""
Get Sepolia ETH from faucets for deployment account
"""

import requests
import json
import time
from web3 import Web3

def check_balance():
    """Check current balance of deployment account"""
    web3 = Web3(Web3.HTTPProvider('https://sepolia.base.org'))
    account = '0xbcAd701a315f5Ccd17210c9333cFDf465616DFF9'

    if web3.is_connected():
        balance = web3.eth.get_balance(account)
        balance_eth = web3.from_wei(balance, 'ether')
        print(f"Deployment Account: {account}")
        print(f"Current Balance: {balance_eth} ETH")
        return balance_eth > 0
    return False

def show_faucet_options():
    """Show available faucet options"""
    print("\n💰 Base Sepolia Faucet Options:")
    print("=" * 50)

    faucets = [
        {
            "name": "Alchemy Sepolia Faucet",
            "url": "https://sepoliafaucet.com",
            "description": "Free Sepolia ETH, may have queue",
            "requirements": "None - just request"
        },
        {
            "name": "Infura Sepolia Faucet",
            "url": "https://www.infura.io/faucet/sepolia",
            "description": "Infura's official faucet",
            "requirements": "Infura account recommended"
        },
        {
            "name": "QuickNode Faucet",
            "url": "https://faucet.quicknode.com/drip",
            "description": "QuickNode's faucet",
            "requirements": "QuickNode account"
        },
        {
            "name": "PoW Faucet",
            "url": "https://sepolia-faucet.pk910.de",
            "description": "Proof-of-work faucet",
            "requirements": "Complete captcha/mining"
        },
        {
            "name": "Chainstack Faucet",
            "url": "https://faucet.chainstack.com/sepolia-testnet-faucet",
            "description": "Chainstack's faucet",
            "requirements": "None"
        }
    ]

    for i, faucet in enumerate(faucets, 1):
        print(f"\n{i}. {faucet['name']}")
        print(f"   URL: {faucet['url']}")
        print(f"   Description: {faucet['description']}")
        print(f"   Requirements: {faucet['requirements']}")

    print(f"\n🎯 Target Address: 0xbcAd701a315f5Ccd17210c9333cFDf465616DFF9")
    print("   Request 0.02 ETH or more from any faucet above")

def wait_for_funding():
    """Wait for funding and check balance periodically"""
    print("\n⏳ Waiting for faucet funding...")
    print("   This will check every 30 seconds for 5 minutes")
    print("   Press Ctrl+C to stop")

    for i in range(10):  # 10 checks * 30 seconds = 5 minutes
        if check_balance():
            print("\n✅ Funding received! Ready for deployment.")
            return True

        if i < 9:  # Don't wait after last check
            print(f"   Check {i+1}/10 - No funding yet, waiting 30 seconds...")
            time.sleep(30)

    print("\n⏸️  Still no funding after 5 minutes.")
    print("   Try another faucet or check back later.")
    return False

def main():
    """Main function"""
    print("🚀 Nimo Deployment - Faucet Funding Guide")
    print("=" * 50)

    # Check current balance
    has_balance = check_balance()

    if has_balance:
        print("\n✅ Account already funded! Ready for deployment.")
        return

    # Show faucet options
    show_faucet_options()

    print("\n📋 Instructions:")
    print("1. Copy the target address: 0xbcAd701a315f5Ccd17210c9333cFDf465616DFF9")
    print("2. Visit one of the faucet URLs above")
    print("3. Paste your address and request ETH")
    print("4. Wait for the transaction to confirm (usually 10-30 seconds)")
    print("5. Run this script again to check balance")

    # Ask if they want to wait
    response = input("\nWould you like me to wait and check for funding? (y/n): ")
    if response.lower() == 'y':
        wait_for_funding()

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\get_faucet_eth.py