#!/usr/bin/env python3
"""
Generate Cardano Service Wallet

This script generates a new Cardano wallet for the Nimo platform service operations.
It creates the necessary key files and provides the wallet address for funding.
"""

import os
import json
import secrets
from pathlib import Path
import hashlib
from typing import Tuple

def generate_cardano_wallet() -> Tuple[str, str]:
    """Generate a new Cardano wallet with signing and verification keys

    Returns:
        Tuple of (address, private_key_hex)
    """
    print("🔑 Generating Cardano Service Wallet...")
    print("=" * 50)

    # Generate a 32-byte private key (256 bits) for Ed25519
    private_key_bytes = secrets.token_bytes(32)

    # Convert to hex format for storage
    private_key_hex = private_key_bytes.hex()

    # For Cardano, we need to create proper key structures
    # This is a simplified version - in production you'd use proper HD wallet derivation
    wallet_data = {
        "type": "PaymentSigningKeyShelley_ed25519",
        "description": "Nimo Platform Service Wallet - Generated for Cardano Testnet",
        "cborHex": private_key_hex
    }

    # Define file paths
    backend_dir = Path(__file__).parent
    key_file = backend_dir / "service_key.skey"
    address_file = backend_dir / "service_address.txt"

    # Save the signing key
    with open(key_file, 'w') as f:
        json.dump(wallet_data, f, indent=2)

    print(f"✅ Signing key saved to: {key_file}")

    # Generate a mock address for demonstration
    # In production, you'd derive this from the verification key using pycardano
    address_hash = hashlib.blake2b(private_key_bytes, digest_size=28).digest()
    mock_address = f"addr_test1{address_hash.hex()}"

    # Save address
    with open(address_file, 'w') as f:
        f.write(f"{mock_address}\n")
        f.write(f"# This is a mock address for demonstration\n")
        f.write(f"# In production, derive from verification key using pycardano\n")

    print(f"✅ Address saved to: {address_file}")
    print(f"📧 Service Address: {mock_address}")

    return mock_address, private_key_hex

def update_env_file(address: str, private_key_hex: str):
    """Update the .env.cardano file with the generated wallet info"""

    env_file = Path(__file__).parent / ".env.cardano"

    if not env_file.exists():
        print("⚠️  .env.cardano file not found, skipping update")
        return

    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()

    # Update the service wallet settings
    updates = [
        (r'CARDANO_SERVICE_PRIVATE_KEY=.*', f'CARDANO_SERVICE_PRIVATE_KEY={private_key_hex}'),
        (r'CARDANO_SERVICE_KEY_FILE=.*', 'CARDANO_SERVICE_KEY_FILE=service_key.skey'),
    ]

    for pattern, replacement in updates:
        import re
        content = re.sub(pattern, replacement, content)

    # Write back
    with open(env_file, 'w') as f:
        f.write(content)

    print("✅ Updated .env.cardano with wallet information")

def generate_faucet_instructions(address: str):
    """Generate instructions for getting test ADA"""

    instructions = f"""
🎯 GET TEST ADA FOR YOUR WALLET

Your service wallet address: {address}

📋 Step-by-Step Instructions:

1. 🌐 Open your browser and go to:
   https://docs.cardano.org/cardano-testnets/tools/faucet

2. 📝 Copy your wallet address:
   {address}

3. 🖱️  Paste the address in the faucet form

4. 💰 Request test ADA (start with 10-20 ADA for testing)

5. ⏳ Wait 1-2 minutes for the transaction to confirm

6. ✅ Verify the funds arrived using the balance check script

💡 Pro Tips:
• Test ADA has NO monetary value - it's only for testing
• Start small - you can always request more later
• Save your address for future funding needs
• The faucet may have daily limits per address

🔍 After funding, run this to check your balance:
python check_address_balance.py {address}
"""

    # Save instructions to file
    instructions_file = Path(__file__).parent / "FAUCET_INSTRUCTIONS.md"
    with open(instructions_file, 'w') as f:
        f.write(instructions)

    print(f"✅ Faucet instructions saved to: {instructions_file}")

def main():
    """Main wallet generation function"""

    print("🚀 Nimo Platform - Cardano Wallet Generator")
    print("=" * 60)

    try:
        # Generate the wallet
        address, private_key = generate_cardano_wallet()

        # Update environment file
        update_env_file(address, private_key)

        # Generate faucet instructions
        generate_faucet_instructions(address)

        print("\n" + "=" * 60)
        print("🎉 WALLET GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📧 Address: {address}")
        print(f"🔐 Private Key: {private_key[:16]}...{private_key[-16:]}")
        print("\n📋 Next Steps:")
        print("1. Follow the faucet instructions above to get test ADA")
        print("2. Run the Cardano connection test: python test_cardano_connection.py")
        print("3. Deploy NIMO token policy when ready")
        print("\n⚠️  SECURITY REMINDER:")
        print("• Never share your private key")
        print("• Keep the service_key.skey file secure")
        print("• Use environment variables in production")
        print("• Consider using hardware security modules for mainnet")

    except Exception as e:
        print(f"❌ Error generating wallet: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())