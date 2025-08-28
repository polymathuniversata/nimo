#!/usr/bin/env python3
"""
Check Contract Address Formats
"""

import os
import re
from dotenv import load_dotenv
load_dotenv()

# Check contract address formats
identity_addr = os.getenv('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA')
token_addr = os.getenv('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA')
usdc_addr = os.getenv('USDC_CONTRACT_BASE_SEPOLIA')

print('🔍 Contract Address Validation:')
print(f'Identity: {identity_addr} (Length: {len(identity_addr or "")})')
print(f'Token: {token_addr} (Length: {len(token_addr or "")})')
print(f'USDC: {usdc_addr} (Length: {len(usdc_addr or "")})')

# Validate hex format
def is_valid_address(addr):
    if not addr:
        return False
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', addr))

print(f'\nValidation Results:')
print(f'✅ Identity valid: {is_valid_address(identity_addr)}')
print(f'✅ Token valid: {is_valid_address(token_addr)}')
print(f'✅ USDC valid: {is_valid_address(usdc_addr)}')

# Check if addresses are the same as in config
print(f'\nComparing with config.py defaults:')
print(f'Identity match: {identity_addr == "0x56186c1e64ca8043DEF78d06Aff222212ea5df71"}')
print(f'Token match: {token_addr == "0x53Eba1e079F885482238EE8bf01C4A9f09DE458f"}')
print(f'USDC match: {usdc_addr == "0x036CbD53842c5426634e7929541eC2318f3dCF7e"}')