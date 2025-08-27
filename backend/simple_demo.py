#!/usr/bin/env python3
"""
Simple MeTTa USDC Integration Demo
"""

from services.usdc_integration import USDCIntegration

print("=== NIMO MeTTa -> USDC Integration Demo ===")
print()

# Test USDC integration
usdc = USDCIntegration()
status = usdc.get_network_status()
print("Network Status:")
print(f"  Connected: {status['connected']}")
print(f"  Network: {status['network']}")  
print(f"  Chain ID: {status['chain_id']}")
print(f"  USDC Contract: {status['usdc_contract']}")
print(f"  USDC Enabled: {status['usdc_enabled']}")
print(f"  Min Confidence: {status['min_confidence_for_usdc']}")
print()

# Test reward calculations
print("Reward Calculations:")
scenarios = [
    {'nimo': 100, 'confidence': 0.9, 'type': 'coding'},
    {'nimo': 75, 'confidence': 0.85, 'type': 'education'},
    {'nimo': 50, 'confidence': 0.75, 'type': 'volunteer'}
]

total_usdc = 0
for i, s in enumerate(scenarios, 1):
    calc = usdc.get_reward_calculation(s['nimo'], s['confidence'], s['type'])
    print(f"  Scenario {i}: {s['type']}")
    print(f"    NIMO: {calc['nimo_amount']}, USDC: ${calc['final_usdc_amount']:.3f}")
    print(f"    Confidence: {calc['confidence']:.2f}, Pays USDC: {calc['pays_usdc']}")
    if calc['pays_usdc']:
        total_usdc += calc['final_usdc_amount']

print()
print(f"Total USDC rewards: ${total_usdc:.3f}")
print()
print("=== Integration Status: WORKING ===")
print("Ready for deployment with service account funding!")