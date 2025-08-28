#!/usr/bin/env python3
"""
Check if addresses are contracts or EOAs
"""

from web3 import Web3

def check_addresses():
    web3 = Web3(Web3.HTTPProvider('https://sepolia.base.org'))

    if not web3.is_connected():
        print("❌ Cannot connect to Base Sepolia")
        return

    addresses = [
        "0x56186c1e64ca8043DEF78d06Aff222212ea5df71",  # Listed as Identity contract
        "0x53Eba1e079F885482238EE8bf01C4A9f09DE458f"   # Listed as Token contract
    ]

    for addr in addresses:
        print(f"\n🔍 Checking: {addr}")
        code = web3.eth.get_code(addr)
        print(f"   Code length: {len(code)} bytes")

        if len(code) > 2:
            print("   ✅ CONTRACT FOUND")
        else:
            print("   ❌ NO CONTRACT (EOA or empty)")
            balance = web3.eth.get_balance(addr)
            eth_balance = web3.from_wei(balance, 'ether')
            print(".6f")

            # Check transaction count
            tx_count = web3.eth.get_transaction_count(addr)
            print(f"   📊 Transaction count: {tx_count}")

if __name__ == "__main__":
    check_addresses()