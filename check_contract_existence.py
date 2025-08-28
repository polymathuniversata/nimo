#!/usr/bin/env python3
"""
Check contract existence on Base networks
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_contract_on_network(rpc_url, contract_address, network_name):
    """Check if contract exists on a specific network"""
    print(f"\n🔍 Checking {network_name}...")
    print(f"   RPC: {rpc_url}")
    print(f"   Address: {contract_address}")

    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not web3.is_connected():
            print(f"   ❌ Cannot connect to {network_name}")
            return False

        # Get contract code
        code = web3.eth.get_code(contract_address)
        code_length = len(code)

        if code_length > 2:  # More than just '0x'
            print(f"   ✅ Contract exists! Code length: {code_length} bytes")

            # Try to get contract info
            try:
                # Load ABI to check contract functions
                abi_path = "contracts/out/NimoIdentity.sol/NimoIdentity_clean.json"
                if os.path.exists(abi_path):
                    with open(abi_path, 'r') as f:
                        abi = json.load(f)
                    contract = web3.eth.contract(address=contract_address, abi=abi)
                    name = contract.functions.name().call()
                    print(f"   📋 Contract name: {name}")
            except Exception as e:
                print(f"   ⚠️  Could not verify contract functions: {e}")

            return True
        else:
            print(f"   ❌ No contract found at this address (code length: {code_length})")
            return False

    except Exception as e:
        print(f"   ❌ Error checking {network_name}: {e}")
        return False

def main():
    """Check contracts on both networks"""
    print("🔍 Contract Existence Check")
    print("=" * 50)

    # Sepolia contracts
    sepolia_identity = os.getenv('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA')
    sepolia_token = os.getenv('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA')
    sepolia_rpc = os.getenv('BASE_SEPOLIA_RPC_URL')

    # Mainnet contracts
    mainnet_identity = os.getenv('NIMO_IDENTITY_CONTRACT_BASE_MAINNET')
    mainnet_token = os.getenv('NIMO_TOKEN_CONTRACT_BASE_MAINNET')
    mainnet_rpc = os.getenv('BASE_MAINNET_RPC_URL')

    # Check Sepolia
    if sepolia_identity and sepolia_rpc:
        check_contract_on_network(sepolia_rpc, sepolia_identity, "Base Sepolia - NimoIdentity")
    if sepolia_token and sepolia_rpc:
        check_contract_on_network(sepolia_rpc, sepolia_token, "Base Sepolia - NimoToken")

    # Check Mainnet
    if mainnet_identity and mainnet_rpc:
        check_contract_on_network(mainnet_rpc, mainnet_identity, "Base Mainnet - NimoIdentity")
    else:
        print("\n❌ No mainnet identity contract address set")

    if mainnet_token and mainnet_rpc:
        check_contract_on_network(mainnet_rpc, mainnet_token, "Base Mainnet - NimoToken")
    else:
        print("\n❌ No mainnet token contract address set")

    print("\n" + "=" * 50)
    print("Summary:")
    print("- If contracts don't exist, you'll need to deploy them")
    print("- Update .env with correct addresses after deployment")

if __name__ == "__main__":
    main()