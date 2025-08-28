#!/usr/bin/env python3
"""
Deploy Nimo contracts to Polygon Mumbai
"""

import os
import json
import subprocess
from pathlib import Path

def deploy_contracts():
    """Deploy contracts to Polygon Mumbai"""

    print("Deploying Nimo Contracts to Polygon Mumbai")
    print("=" * 50)

    # Check if we're in the right directory
    contracts_dir = Path("contracts")
    if not contracts_dir.exists():
        print("Error: contracts directory not found")
        return False

    # Change to contracts directory
    os.chdir(contracts_dir)

    try:
        # Set the private key environment variable
        private_key = "13e571df7b98faa41a12010b5bd2ed00a2f1faae54f4a8c3496d101910fe7b26"
        os.environ["BLOCKCHAIN_SERVICE_PRIVATE_KEY"] = private_key

        print("Deployment Configuration:")
        print(f"   Network: polygon-mumbai")
        print(f"   Account: 0x4CE536b148BF86Ce30E2A28E610e3B2df973d9Af")
        print(f"   RPC: https://polygon-mumbai.g.alchemy.com/v2/demo")

        # Run the deployment
        print("\nRunning deployment...")
        cmd = [
            "forge", "script", "script/Deploy.s.sol",
            "--rpc-url", "polygon-mumbai",
            "--broadcast",
            "--verify",
            "-vvvv"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        print("Deployment Output:")
        print("=" * 30)
        print(result.stdout)

        if result.stderr:
            print("Errors/Warnings:")
            print("=" * 20)
            print(result.stderr)

        if result.returncode == 0:
            print("\nDeployment completed successfully!")

            # Try to extract contract addresses from output
            extract_contract_addresses(result.stdout)
            return True
        else:
            print(f"\nDeployment failed with exit code {result.returncode}")
            return False

    except Exception as e:
        print(f"Error during deployment: {e}")
        return False
    finally:
        # Clean up environment
        if "BLOCKCHAIN_SERVICE_PRIVATE_KEY" in os.environ:
            del os.environ["BLOCKCHAIN_SERVICE_PRIVATE_KEY"]

def extract_contract_addresses(output):
    """Extract deployed contract addresses from deployment output"""

    print("\nExtracting Contract Addresses...")
    print("=" * 40)

    lines = output.split('\n')
    addresses = {}

    for line in lines:
        if 'NimoIdentity deployed to:' in line:
            address = line.split(':')[1].strip()
            addresses['NimoIdentity'] = address
            print(f"NimoIdentity: {address}")
        elif 'NimoToken deployed to:' in line:
            address = line.split(':')[1].strip()
            addresses['NimoToken'] = address
            print(f"NimoToken: {address}")

    if addresses:
        # Save to deployment file
        deployment_file = Path("../deployment_addresses.json")
        with open(deployment_file, 'w') as f:
            json.dump({
                "network": "polygon-mumbai",
                "chain_id": 80001,
                "contracts": addresses
            }, f, indent=2)

        print(f"\nAddresses saved to: {deployment_file}")

        # Update .env files
        update_env_files(addresses)
    else:
        print("Could not extract contract addresses from output")

def update_env_files(addresses):
    """Update .env files with deployed contract addresses"""

    print("\nUpdating Environment Files...")
    print("=" * 35)

    env_files = ["../.env", "../backend/.env"]

    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"Updated {env_file}...")
            # Read current content
            with open(env_file, 'r') as f:
                content = f.read()

            # Update contract addresses
            if 'NimoIdentity' in addresses:
                content = content.replace(
                    'NIMO_IDENTITY_CONTRACT_POLYGON_MUMBAI=0x4CE536b148BF86Ce30E2A28E610e3B2df973d9Af',
                    f'NIMO_IDENTITY_CONTRACT_POLYGON_MUMBAI={addresses["NimoIdentity"]}'
                )

            if 'NimoToken' in addresses:
                content = content.replace(
                    'NIMO_TOKEN_CONTRACT_POLYGON_MUMBAI=0x4CE536b148BF86Ce30E2A28E610e3B2df973d9Af',
                    f'NIMO_TOKEN_CONTRACT_POLYGON_MUMBAI={addresses["NimoToken"]}'
                )

            # Write back
            with open(env_file, 'w') as f:
                f.write(content)

            print(f"Updated {env_file}")
        else:
            print(f"{env_file} not found")

if __name__ == "__main__":
    success = deploy_contracts()

    if success:
        print("\nDeployment completed successfully!")
        print("   Your contracts are now live on Polygon Mumbai!")
        print("   Next: Test the backend integration")
    else:
        print("\nDeployment failed")
        print("   Check the output above for details")
        print("   Make sure you have MATIC in your account")</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\deploy_polygon.py