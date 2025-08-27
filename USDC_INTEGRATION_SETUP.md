# Nimo USDC Integration Setup Guide

## Overview
This guide walks through setting up the complete MeTTa → USDC automated reward system on Base Sepolia testnet.

## Architecture
```
User Contribution → MeTTa Reasoning → NIMO Tokens → USDC Rewards (if high confidence)
                                    ↓
                            Blockchain Recording (Base Sepolia)
```

## Prerequisites

### 1. Base Sepolia Testnet Setup
- Get Base Sepolia ETH from: https://bridge.base.org/deposit
- Add Base Sepolia to MetaMask:
  - Network: Base Sepolia
  - RPC: https://sepolia.base.org
  - Chain ID: 84532
  - Currency: ETH
  - Block Explorer: https://sepolia.basescan.org

### 2. Service Account Configuration
```bash
# Generate a new private key for the service account
# NEVER use your personal wallet private key

# Option 1: Using OpenSSL
openssl rand -hex 32

# Option 2: Using Python
python3 -c "import secrets; print('0x' + secrets.token_hex(32))"
```

## Configuration Steps

### 1. Environment Variables
Update `backend/.env`:
```env
# Base Network Configuration
BLOCKCHAIN_NETWORK=base-sepolia
WEB3_PROVIDER_URL=https://sepolia.base.org
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

# Service Account (REPLACE WITH REAL PRIVATE KEY)
BLOCKCHAIN_SERVICE_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Contract Addresses (will be populated after deployment)
NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA=
NIMO_TOKEN_CONTRACT_BASE_SEPOLIA=
USDC_CONTRACT_BASE_SEPOLIA=0x036CbD53842c5426634e7929541eC2318f3dCF7e

# MeTTa Integration with Blockchain
METTA_ENABLE_BLOCKCHAIN_REWARDS=True
METTA_ENABLE_USDC_PAYMENTS=True
METTA_MIN_CONFIDENCE_FOR_USDC=0.8
```

### 2. Fund Service Account
```bash
# Send Base Sepolia ETH to your service account address for gas fees
# Minimum 0.01 ETH recommended

# Get some Base Sepolia USDC for testing rewards
# You can use the Base Sepolia faucet or bridge testnet USDC
```

### 3. Deploy Smart Contracts
```bash
# Using Python deployment script
cd contracts
python3 deploy_to_base.py

# This will update your .env file with deployed contract addresses
```

### 4. Test Integration
```bash
cd backend
python3 test_usdc_integration.py
```

## Smart Contract Addresses

### Base Sepolia Testnet
- **USDC**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- **Nimo Identity**: (deployed via script)
- **Nimo Token**: (deployed via script)

### Base Mainnet (For Production)
- **USDC**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

## API Endpoints

### New USDC Integration Endpoints

#### 1. Check Integration Status
```bash
GET /api/usdc/status
Authorization: Bearer <jwt_token>
```

#### 2. Check USDC Balance
```bash
GET /api/usdc/balance/0x742d35Cc6634C0532925a3b8D6AC14
Authorization: Bearer <jwt_token>
```

#### 3. Calculate Reward Preview
```bash
POST /api/usdc/calculate-reward
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "nimo_amount": 100,
  "confidence": 0.85,
  "contribution_type": "coding"
}
```

#### 4. Preview Complete Reward (MeTTa + USDC)
```bash
POST /api/usdc/contribution-reward-preview
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "contribution_id": "contrib123",
  "contribution_data": {
    "category": "coding",
    "title": "Smart Contract Development",
    "evidence": [{"type": "github", "url": "https://github.com/example/repo"}]
  }
}
```

## Reward Calculation Logic

### NIMO Token Base Amounts (per contribution type)
```python
base_amounts = {
    'coding': 75,
    'education': 60, 
    'volunteer': 50,
    'activism': 65,
    'leadership': 70,
    'entrepreneurship': 80,
    'environmental': 70,
    'community': 60
}
```

### USDC Conversion Rate
- **1 NIMO token = $0.01 USDC** (configurable)

### Confidence-Based Multipliers
- **High Confidence (≥0.8)**: 1.0x - 1.5x multiplier
- **Medium Confidence (0.6-0.8)**: 0.4x - 1.0x multiplier  
- **Low Confidence (<0.6)**: No USDC reward

### Example Rewards
```
Coding Contribution (75 NIMO, 0.9 confidence):
- NIMO Tokens: 75
- Base USDC: $0.75
- Confidence Multiplier: 1.1x
- Final USDC Reward: $0.825
- Total Value: ~$1.575
```

## Security Considerations

### 1. Private Key Management
- ✅ Use a dedicated service account
- ✅ Store private key in environment variables only
- ✅ Never commit private keys to version control
- ✅ Use hardware wallets for production mainnet

### 2. Smart Contract Security
- ✅ Use OpenZeppelin contracts
- ✅ Implement role-based access control
- ✅ Pause functionality for emergencies
- ✅ Multi-signature for admin operations (production)

### 3. MeTTa Reasoning Security
- ✅ Input sanitization for MeTTa queries
- ✅ Rate limiting on verification endpoints
- ✅ Fraud detection algorithms
- ✅ Evidence validation

## Monitoring and Maintenance

### 1. Service Health Monitoring
```bash
# Check API health
curl http://localhost:5000/api/health

# Check USDC integration status
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/usdc/status
```

### 2. Account Balance Monitoring
- Monitor service account ETH balance (for gas)
- Monitor service account USDC balance (for rewards)
- Set up alerts for low balances

### 3. Transaction Monitoring
- Monitor failed transactions
- Track gas costs and optimization
- Monitor USDC reward distribution

## Troubleshooting

### Common Issues

#### 1. "Service account not configured"
- Check `BLOCKCHAIN_SERVICE_PRIVATE_KEY` is set in `.env`
- Ensure private key starts with `0x`
- Verify private key is valid (64 hex characters after 0x)

#### 2. "Insufficient balance" 
- Send more Base Sepolia ETH to service account
- Get Base Sepolia USDC for rewards

#### 3. "Network connection failed"
- Check Base Sepolia RPC is accessible
- Verify network configuration
- Try alternative RPC endpoints

#### 4. "Contract not found"
- Deploy smart contracts using deployment script
- Verify contract addresses in `.env`
- Check contracts on Base Sepolia explorer

### Debug Commands
```bash
# Test MeTTa reasoning
python3 -c "from services.metta_integration import MeTTaIntegration; m=MeTTaIntegration(); print(m.validate_contribution('test', {'category': 'coding'}))"

# Test USDC integration
python3 test_usdc_integration.py

# Check service account balance
python3 -c "from services.usdc_integration import USDCIntegration; u=USDCIntegration(); print(u.get_service_account_info())"
```

## Production Deployment

### 1. Environment Setup
- Use Base Mainnet instead of Sepolia
- Configure production RPC endpoints
- Set up proper monitoring and alerting

### 2. Smart Contract Deployment
- Deploy to Base Mainnet
- Use multi-signature for admin functions
- Set up contract verification on Basescan

### 3. Security Hardening
- Use hardware wallets for production keys
- Implement rate limiting and DDoS protection
- Set up proper logging and monitoring
- Regular security audits

## Support and Resources

- **Base Network Docs**: https://docs.base.org/
- **Base Sepolia Faucet**: https://coinbase.com/faucets/base-ethereum-sepolia-faucet
- **Base Sepolia Explorer**: https://sepolia.basescan.org/
- **USDC on Base**: https://www.centre.io/usdc-multichain/base

## Test Results (Last Run)
```
🏆 Overall: 5/6 tests passed
✅ Network Connection
❌ Service Account (needs configuration)
✅ Reward Calculations
✅ MeTTa Integration
✅ Gas Estimation
✅ Blockchain Integration
```

## Next Steps
1. Configure service account private key
2. Fund service account with ETH and USDC
3. Deploy smart contracts
4. Run full integration test
5. Connect frontend to new USDC endpoints