# Cardano Smart Contract Deployment

## Overview

This document covers the deployment of Nimo Platform smart contracts on the Cardano blockchain, including both testing (mock) and production deployment scenarios.

## Current Status ✅

### Mock Deployment (Completed)
- ✅ Identity Contract: `addr1w8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5gmock`
- ✅ Token Policy ID: `d5e6cc5527629f7b4ea896a148ec828199bd3f46f9b5a9b8f8c2d4e6`
- ✅ Governance Contract: `addr_gov_se38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5gmock`
- ✅ Backend Configuration Updated
- ✅ Deployment Files Generated

### Real Deployment (Pending)
- ❌ Blockfrost API Key Required
- ❌ Test ADA Funding Required
- ❌ Production Deployment

## Mock Deployment

The mock deployment provides a complete testing environment without requiring real blockchain transactions.

### What Was Deployed (Mock)

1. **NimoIdentity Contract**
   - Address: `addr1w8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5gmock`
   - Purpose: Manages decentralized identities and contribution verification
   - Features: Identity creation, contribution tracking, MeTTa integration

2. **NimoToken Contract**
   - Policy ID: `d5e6cc5527629f7b4ea896a148ec828199bd3f46f9b5a9b8f8c2d4e6`
   - Initial Supply: 1,000,000 NIMO tokens
   - Decimals: 6
   - Purpose: Native token for the platform rewards and governance

3. **Governance Contract**
   - Address: `addr_gov_se38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5gmock`
   - Purpose: DAO governance and proposal management
   - Features: Proposal creation, voting, execution

### Files Generated

- `contracts/deployments/mock_deployment_preview.json` - Complete deployment metadata
- Updated `backend/.env` with contract addresses and policy IDs
- Updated `contracts/cardano/.env` with deployment results

## Real Deployment Process

### Prerequisites

1. **Blockfrost API Key**
   ```bash
   # Get from https://blockfrost.io/
   # Create project for Cardano Preview testnet
   export BLOCKFROST_PROJECT_ID_PREVIEW=your_project_id_here
   ```

2. **Test ADA Funding**
   ```bash
   # Service address needs ~5 ADA for deployment
   Service Address: addr1vy8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5pg2ya43y
   Faucet: https://docs.cardano.org/cardano-testnets/tools/faucet
   ```

3. **Dependencies**
   ```bash
   cd contracts/cardano
   pip install -r requirements.txt
   ```

### Deployment Steps

1. **Verify Setup**
   ```bash
   python check_deployment_status.py
   ```

2. **Deploy Token Contract**
   ```bash
   python deploy_nimo_token.py --network preview
   ```

3. **Deploy Identity Contract**
   ```bash
   python deploy.py --network preview
   ```

4. **Update Backend Configuration**
   ```bash
   # The deployment scripts will automatically update .env files
   # with real contract addresses and policy IDs
   ```

## Integration Testing

### With Mock Deployment

The backend is already configured to work with the mock deployment data. You can:

1. **Test Token Operations**
   ```python
   from backend.services.cardano_service import CardanoService
   service = CardanoService()
   # Test minting, transfers, etc. with mock data
   ```

2. **Test Identity Operations**
   ```python
   # Test identity creation and contribution verification
   # using mock contract addresses
   ```

3. **Test Governance Features**
   ```python
   # Test proposal creation and voting with mock contracts
   ```

### With Real Deployment

Once you have real contract addresses:

1. **Update Environment Variables**
   ```bash
   # Replace mock values in backend/.env with real ones
   NIMO_TOKEN_POLICY_ID=real_policy_id_here
   NIMO_IDENTITY_CONTRACT_ADDRESS=real_address_here
   ```

2. **Test Real Transactions**
   ```bash
   # Test actual blockchain interactions
   python test_real_deployment.py
   ```

## Contract Specifications

### NimoIdentity Contract

**Purpose**: Decentralized identity and contribution management

**Features**:
- Identity creation and verification
- Contribution tracking with MeTTa integration
- Proof of contribution validation
- Decentralized reputation system

**Integration Points**:
- MeTTa reasoning engine for fraud detection
- IPFS for evidence storage
- Backend API for user management

### NimoToken Contract

**Purpose**: Native platform token for rewards and governance

**Specifications**:
- Name: Nimo Impact Token
- Ticker: NIMO
- Decimals: 6
- Initial Supply: 1,000,000
- Minting: Controlled by contribution verification

**Use Cases**:
- Reward verified contributions
- Governance voting power
- Platform fee payments
- Staking for enhanced features

### Governance Contract

**Purpose**: Decentralized autonomous organization management

**Features**:
- Proposal creation and voting
- Treasury management
- Parameter updates
- Community decision making

## Security Considerations

### For Testing (Mock Deployment)
- Mock data is clearly marked and separated
- No real value transactions
- Safe for development and testing

### For Production
- Use hardware wallets for private keys
- Implement multi-signature for large transactions
- Regular security audits
- Monitor contract interactions
- Emergency pause mechanisms

## Troubleshooting

### Common Issues

1. **Blockfrost Connection**
   ```bash
   # Check API key
   curl -H "project_id: YOUR_PROJECT_ID" https://cardano-preview.blockfrost.io/api/v0/genesis
   ```

2. **Insufficient Funds**
   ```bash
   # Check service address balance
   python check_balance.py
   ```

3. **Deployment Failures**
   ```bash
   # Check logs
   tail -f deployment.log
   ```

### Support

- **Documentation**: See `DEPLOYMENT_GUIDE.md` for detailed instructions
- **Testing**: Use mock deployment for development
- **Production**: Follow security best practices
- **Issues**: Check deployment logs and Blockfrost status

## Next Steps

1. **Complete Real Deployment**
   - Get Blockfrost API key
   - Fund service address
   - Run production deployment

2. **Integration Testing**
   - Test all contract interactions
   - Verify MeTTa integration
   - Validate IPFS storage

3. **Documentation Updates**
   - Update API documentation
   - Create user guides
   - Document contract ABIs

4. **Security Audit**
   - Third-party contract audit
   - Penetration testing
   - Code review

## Files Overview

```
contracts/
├── cardano/
│   ├── mock_deploy.py          # Mock deployment script
│   ├── deploy_nimo_token.py    # Real token deployment
│   ├── deploy.py              # Real identity deployment
│   ├── check_deployment_status.py  # Status checker
│   └── .env                   # Environment configuration
├── deployments/
│   └── mock_deployment_preview.json  # Mock deployment data
└── README.md                  # Contract documentation
```

The mock deployment provides a complete testing foundation, while the real deployment scripts are ready for production use once Blockfrost API access is configured.