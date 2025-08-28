#!/usr/bin/env python3
"""
Transfer ETH from funded account to new deployment account
Run this after importing the funded account private key into a wallet
"""

import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def transfer_eth():
    """Transfer ETH from funded account to deployment account"""

    # Configuration
    FUNDED_PRIVATE_KEY = os.getenv('FUNDED_PRIVATE_KEY')  # You'll need to set this
    NEW_DEPLOYMENT_ADDRESS = '0xbcAd701a315f5Ccd17210c9333cFDf465616DFF9'  # New account we generated
    AMOUNT_ETH = 0.02  # Amount to transfer

    if not FUNDED_PRIVATE_KEY:
        print("ERROR: Set FUNDED_PRIVATE_KEY in your .env file first")
        print("Get this from your wallet where the funded account is imported")
        return

    # Connect to Base Sepolia
    web3 = Web3(Web3.HTTPProvider('https://sepolia.base.org'))

    if not web3.is_connected():
        print("ERROR: Cannot connect to Base Sepolia")
        return

    # Get account from private key
    account = Account.from_key(FUNDED_PRIVATE_KEY)
    from_address = account.address

    print(f"Transferring {AMOUNT_ETH} ETH")
    print(f"From: {from_address}")
    print(f"To: {NEW_DEPLOYMENT_ADDRESS}")

    # Check balance
    balance = web3.eth.get_balance(from_address)
    balance_eth = web3.from_wei(balance, 'ether')

    if balance_eth < AMOUNT_ETH:
        print(f"ERROR: Insufficient balance. Have {balance_eth} ETH, need {AMOUNT_ETH} ETH")
        return

    # Build transaction
    amount_wei = web3.to_wei(AMOUNT_ETH, 'ether')
    gas_price = web3.eth.gas_price

    transaction = {
        'to': NEW_DEPLOYMENT_ADDRESS,
        'value': amount_wei,
        'gas': 21000,
        'gasPrice': gas_price,
        'nonce': web3.eth.get_transaction_count(from_address),
        'chainId': 84532  # Base Sepolia chain ID
    }

    # Sign and send transaction
    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, FUNDED_PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaction sent: {web3.to_hex(tx_hash)}")
        print("Waiting for confirmation...")

        # Wait for receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed in block {receipt['blockNumber']}")

        # Check new balance
        new_balance = web3.eth.get_balance(NEW_DEPLOYMENT_ADDRESS)
        new_balance_eth = web3.from_wei(new_balance, 'ether')
        print(f"New deployment account balance: {new_balance_eth} ETH")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    transfer_eth()</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\transfer_eth.py