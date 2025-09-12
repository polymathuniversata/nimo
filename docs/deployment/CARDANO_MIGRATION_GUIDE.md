# Nimo Platform - Cardano Migration Guide

## Migration Summary

The Nimo Platform has been **successfully migrated** from Ethereum/Base/Polygon USDC to **Cardano blockchain** with native ADA and NIMO tokens.

## Key Changes

### ✅ **Completed Migration Components**

1. **Backend Service Layer**
   - `CardanoService` replaces `BlockchainService` for Web3/Ethereum
   - Blockfrost API integration for Cardano network access
   - PyCardano for transaction building and signing
   - Support for Preview, Preprod, and Mainnet networks

2. **API Endpoints**
   - `/api/cardano/*` routes replace `/api/usdc/*` routes
   - Native ADA transfers instead of USDC transfers
   - NIMO token minting and transfers
   - Cardano address balance checking
   - Transaction status monitoring

3. **Token System**
   - **NIMO tokens**: Cardano native assets (not ERC20)
   - **ADA rewards**: Direct ADA transfers for high-confidence contributions
   - **Conversion rate**: 1 ADA = 100 NIMO tokens (configurable)

4. **Smart Contracts**
   - Plutus smart contracts replace Solidity contracts
   - Native token minting policy for NIMO tokens
   - Contribution validation through Plutus validators

5. **Configuration Updates**
   - Cardano network selection (preview/preprod/mainnet)
   - Blockfrost API key management
   - Service wallet configuration

## Setup Instructions

### 1. Install Cardano Dependencies

```bash
cd backend
pip install -r requirements_cardano.txt
```

### 2. Get Blockfrost API Keys

1. Visit [Blockfrost.io](https://blockfrost.io)
2. Create account and get API keys for your target networks
3. Set environment variables:

```bash
export BLOCKFROST_PROJECT_ID_PREVIEW="preview_api_key_here"
export BLOCKFROST_PROJECT_ID_PREPROD="preprod_api_key_here"
export BLOCKFROST_PROJECT_ID_MAINNET="mainnet_api_key_here"
```

### 3. Configure Cardano Network

```bash
# Use Cardano Preview testnet (default)
export CARDANO_NETWORK="preview"

# Or use Preprod testnet
export CARDANO_NETWORK="preprod"

# Or use Mainnet (production)
export CARDANO_NETWORK="mainnet"
```

### 4. Set Up Service Wallet

Generate a Cardano wallet for platform operations:

```bash
cd contracts/cardano
python deploy_nimo_token.py --network preview
```

This will:
- Generate a service wallet if none exists
- Display the wallet address for funding
- Create the NIMO token minting policy

### 5. Fund Service Wallet (Testnet)

For **testnet networks** (preview/preprod):

1. Go to [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnets/tools/faucet)
2. Enter your service wallet address
3. Request test ADA (arrives within minutes)
4. Verify funding: `/api/cardano/status`

### 6. Deploy NIMO Token Policy

```bash
cd contracts/cardano
python deploy_nimo_token.py --network preview --initial-mint 1000000
```

This creates:
- NIMO token minting policy
- Initial token supply
- Policy configuration file

## API Usage Examples

### Check Cardano Integration Status

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5000/api/cardano/status
```

### Get Address Balance

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5000/api/cardano/balance/addr_test1qp...
```

### Calculate Contribution Rewards

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"nimo_amount": 100, "confidence": 0.85, "contribution_type": "coding"}' \
  http://localhost:5000/api/cardano/calculate-reward
```

### Preview Complete Reward

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"contribution_id": "contrib123", "contribution_data": {"category": "coding"}}' \
  http://localhost:5000/api/cardano/contribution-reward-preview
```

### Mint NIMO Tokens

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"recipient_address": "addr_test1qp...", "amount": 50, "reason": "Verified contribution", "metta_proof": "hash123"}' \
  http://localhost:5000/api/cardano/mint-nimo
```

### Send ADA Rewards

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"amount": "0.5", "recipient_address": "addr_test1qp...", "reason": "High-confidence contribution"}' \
  http://localhost:5000/api/cardano/send-ada
```

### Get Testnet Faucet Information

```bash
curl http://localhost:5000/api/cardano/faucet-info
```

## Migration Benefits

### 🌟 **Advantages of Cardano**

1. **Lower Transaction Costs**
   - Typical transaction: ~0.17 ADA (~$0.08)
   - No gas price volatility
   - Predictable fees

2. **Sustainability**
   - Proof-of-Stake consensus
   - ~99.95% lower energy consumption than Bitcoin
   - Carbon-neutral blockchain

3. **Native Multi-Asset Support**
   - No smart contract needed for tokens
   - Built-in metadata standards
   - Native token features

4. **Reliability**
   - High uptime and network stability
   - Formal verification for critical components
   - Peer-reviewed research foundation

5. **Developer Experience**
   - Rich metadata support
   - Comprehensive APIs (Blockfrost)
   - Strong typing with Haskell/Plutus

## Network Information

### Testnet Networks

- **Preview**: Latest features, frequent updates
- **Preprod**: Pre-production testing, stable
- **Mainnet**: Production network

### Faucet Access

- **Preview/Preprod**: [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnets/tools/faucet)
- **Mainnet**: Purchase ADA from exchanges

### Block Explorers

- **Preview**: [Cardanoscan Preview](https://preview.cardanoscan.io/)
- **Preprod**: [Cardanoscan Preprod](https://preprod.cardanoscan.io/)
- **Mainnet**: [Cardanoscan](https://cardanoscan.io/)

## Environment Variables Reference

```bash
# Network Selection
CARDANO_NETWORK="preview"  # preview, preprod, mainnet

# Blockfrost API Keys
BLOCKFROST_PROJECT_ID_PREVIEW="preview_your_key_here"
BLOCKFROST_PROJECT_ID_PREPROD="preprod_your_key_here"
BLOCKFROST_PROJECT_ID_MAINNET="mainnet_your_key_here"

# Service Wallet
CARDANO_SERVICE_PRIVATE_KEY="ed25519_private_key_hex"
CARDANO_SERVICE_KEY_FILE="service_key.skey"

# Token Configuration  
NIMO_TOKEN_POLICY_ID="policy_id_from_deployment"
NIMO_TOKEN_ASSET_NAME="NIMO"
ADA_TO_NIMO_RATE="100"  # 1 ADA = 100 NIMO
```

## Troubleshooting

### Common Issues

1. **"PyCardano not available"**
   ```bash
   pip install pycardano blockfrost-python
   ```

2. **"Blockfrost project ID not configured"**
   ```bash
   export BLOCKFROST_PROJECT_ID_PREVIEW="your_key_here"
   ```

3. **"Service account not configured"**
   - Generate wallet with deployment script
   - Fund wallet with test ADA
   - Set private key in environment

4. **"Insufficient funds"**
   - Check wallet balance: `/api/cardano/status`
   - Get test ADA from faucet
   - Verify network configuration

### Support Resources

- [Cardano Developer Portal](https://developers.cardano.org/)
- [PyCardano Documentation](https://pycardano.readthedocs.io/)
- [Blockfrost API Docs](https://docs.blockfrost.io/)
- [Cardano Community Discord](https://discord.gg/cardano)

## Production Deployment

### Security Checklist

- [ ] Use hardware wallets for mainnet service keys
- [ ] Implement proper key rotation procedures
- [ ] Audit all Plutus smart contracts
- [ ] Set up monitoring and alerting
- [ ] Configure backup and recovery procedures
- [ ] Test disaster recovery scenarios

### Performance Optimization

- [ ] Implement caching for frequent queries
- [ ] Use connection pooling for Blockfrost API
- [ ] Monitor transaction confirmation times
- [ ] Implement retry logic for failed transactions
- [ ] Set up metrics and monitoring dashboards

---

## 🎉 **Migration Complete!**

The Nimo Platform is now successfully running on Cardano blockchain with native ADA and NIMO tokens, providing a more sustainable, cost-effective, and feature-rich foundation for the decentralized reputation platform.