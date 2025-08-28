#!/usr/bin/env python3
"""
Quick Blockfrost Setup Script

This script helps you quickly configure your Blockfrost API key
after you've obtained it from https://blockfrost.io/
"""

import os
import sys
from pathlib import Path

def setup_blockfrost_key():
    """Set up Blockfrost API key"""
    print("Blockfrost API Key Setup")
    print("=" * 40)
    print()

    # Get project ID from user
    project_id = input("Enter your Blockfrost Preview Project ID: ").strip()

    if not project_id:
        print("❌ No project ID provided")
        return False

    if len(project_id) < 20:
        print("❌ Project ID seems too short. Please check and try again.")
        return False

    # Update environment files
    project_root = Path(__file__).parent.parent.parent
    env_files = [
        project_root / "backend" / ".env",
        project_root / "contracts" / "cardano" / ".env",
        project_root / ".env.cardano"
    ]

    updated_files = []
    for env_file in env_files:
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    content = f.read()

                # Replace placeholder with actual key
                old_line = "BLOCKFROST_PROJECT_ID_PREVIEW=your_preview_project_id_here"
                new_line = f"BLOCKFROST_PROJECT_ID_PREVIEW={project_id}"

                if old_line in content:
                    content = content.replace(old_line, new_line)

                    with open(env_file, 'w') as f:
                        f.write(content)

                    updated_files.append(str(env_file))
                    print(f"✓ Updated {env_file.name}")
                else:
                    print(f"⚠ Placeholder not found in {env_file.name}")

            except Exception as e:
                print(f"❌ Error updating {env_file.name}: {e}")

    # Set environment variable for current session
    os.environ['BLOCKFROST_PROJECT_ID_PREVIEW'] = project_id
    print(f"✓ Set BLOCKFROST_PROJECT_ID_PREVIEW for current session")

    print()
    print("🎉 Blockfrost API key configured successfully!")
    print()
    print("Updated files:")
    for file in updated_files:
        print(f"  - {file}")
    print()
    print("Next steps:")
    print("1. Fund your service address with test ADA from the faucet")
    print("2. Run: python check_deployment_status.py")
    print("3. If ready, deploy: python deploy_nimo_token.py --network preview")

    return True

def main():
    """Main function"""
    try:
        success = setup_blockfrost_key()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())