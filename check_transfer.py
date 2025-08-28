#!/usr/bin/env python3
"""
Verify ETH transfer completion and check deployment account balance
"""

from web3 import Web3

def check_transfer_status():
    """Check if ETH has been transferred to deployment account"""

    funded_account = '0x56186c1e64ca8043DEF78d06Aff222212ea5df71'
    deployment_account = '0xbcAd701a315f5Ccd17210c9333cFDf465616DFF9'

    web3 = Web3(Web3.HTTPProvider('https://sepolia.base.org'))

    if not web3.is_connected():
        print("❌ Cannot connect to Base Sepolia")
        return False

    print("🔍 Checking Transfer Status")
    print("=" * 40)

    # Check funded account balance
    funded_balance = web3.eth.get_balance(funded_account)
    funded_balance_eth = web3.from_wei(funded_balance, 'ether')

    # Check deployment account balance
    deploy_balance = web3.eth.get_balance(deployment_account)
    deploy_balance_eth = web3.from_wei(deploy_balance, 'ether')

    print(f"Funded Account ({funded_account}):")
    print(f"  Balance: {funded_balance_eth} ETH")

    print(f"\nDeployment Account ({deployment_account}):")
    print(f"  Balance: {deploy_balance_eth} ETH")

    # Check if transfer is complete
    if deploy_balance_eth >= 0.015:  # Account for gas fees
        print("\n✅ Transfer Complete! Ready for deployment")
        print(f"   Deployment account has {deploy_balance_eth} ETH")
        return True
    else:
        print("\n⏳ Transfer not yet complete")
        print("   Waiting for ETH in deployment account...")
        return False

if __name__ == "__main__":
    check_transfer_status()</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\check_transfer.py