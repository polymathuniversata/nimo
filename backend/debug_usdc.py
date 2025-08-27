import os
from dotenv import load_dotenv
load_dotenv()

print('Environment Variables:')
print(f'METTA_ENABLE_USDC_PAYMENTS: {os.getenv("METTA_ENABLE_USDC_PAYMENTS")}')
print(f'METTA_MIN_CONFIDENCE_FOR_USDC: {os.getenv("METTA_MIN_CONFIDENCE_FOR_USDC")}')

from services.usdc_integration import USDCIntegration
usdc = USDCIntegration()
print(f'USDC Integration enabled: {usdc.usdc_enabled}')

# Test with USDC enabled manually
usdc.usdc_enabled = True
calc = usdc.get_reward_calculation(100, 0.9, 'coding')
print(f'With USDC enabled: Pays USDC = {calc["pays_usdc"]}, Amount = ${calc["final_usdc_amount"]:.3f}')