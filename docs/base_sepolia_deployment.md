# Base Sepolia Deployment Guide

## Overview

This guide covers the complete deployment process for Nimo Platform smart contracts on Base Sepolia testnet. Base Sepolia is the official testnet for Base (Coinbase's L2), providing a safe environment for testing before mainnet deployment.

**Network:** Base Sepolia  
**Chain ID:** 84532  
**RPC URL:** https://sepolia.base.org  
**Block Explorer:** https://sepolia.basescan.org  
**Faucet:** https://faucet.quicknode.com/base/sepolia  

---

## Prerequisites

### 1. Environment Setup

```bash
# Install Foundry (if not already installed)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Verify installation
forge --version
cast --version
anvil --version
```

### 2. Required Environment Variables

Create a `.env` file in the `contracts/` directory:

```env
# Deployment Configuration
PRIVATE_KEY=0x...  # Private key for deployment account (without 0x prefix)

# API Keys for Verification
BASESCAN_API_KEY=...  # Get from https://basescan.org/apis
ALCHEMY_API_KEY=...   # Get from https://alchemy.com (optional, for backup RPC)

# Network Configuration (already configured in foundry.toml)
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

# Optional: For production deployment
ETHERSCAN_API_KEY=...  # For Ethereum mainnet verification
```

### 3. Test Ether (SepoliaETH)

Get test ETH for Base Sepolia:
1. Visit https://faucet.quicknode.com/base/sepolia
2. Enter your deployment wallet address
3. Request test ETH
4. Wait for confirmation

**Note:** You need at least 0.01 ETH for contract deployment and initial transactions.

---

## Pre-Deployment Checklist

### 1. Contract Compilation

```bash
cd contracts/

# Clean previous builds
forge clean

# Install dependencies
forge install

# Compile contracts
forge build

# Verify compilation succeeded
ls out/
```

Expected output should include:
- `NimoIdentity.sol/NimoIdentity.json`
- `NimoToken.sol/NimoToken.json`

### 2. Run Tests

```bash
# Run all tests
forge test -vv

# Run tests for specific contracts
forge test --match-contract NimoIdentityTest -vv
forge test --match-contract NimoTokenTest -vv

# Generate coverage report
forge coverage
```

### 3. Gas Estimation

```bash
# Estimate deployment gas costs
forge test --gas-report

# Simulate deployment (dry run)
forge script script/Deploy.s.sol --rpc-url base-sepolia --sender 0x...
```

---

## Deployment Process

### Step 1: Deploy Contracts

```bash
# Deploy to Base Sepolia testnet
forge script script/Deploy.s.sol \
    --rpc-url base-sepolia \
    --broadcast \
    --verify \
    --delay 30 \
    -vvvv

# Alternative: Deploy without immediate verification
forge script script/Deploy.s.sol \
    --rpc-url base-sepolia \
    --broadcast \
    -vvvv
```

**Expected Output:**
```
== Logs ==
  Deploying contracts to Base network...
  Deployer address: 0x742d35cc6634c0532925a3b8c17f4ac70af45f5d
  Deployer balance: 50000000000000000 (0.05 ETH)
  Deploying NimoToken...
  NimoToken deployed to: 0x1234...5678
  Deploying NimoIdentity...
  NimoIdentity deployed to: 0x9876...5432
  Setting up contract integrations...
  Granted MINTER_ROLE to NimoIdentity contract
  Granted VERIFIER_ROLE to deployer
  Granted METTA_AGENT_ROLE to deployer
  Granted BURNER_ROLE to NimoIdentity contract

=== DEPLOYMENT SUMMARY ===
Network: Base
Chain ID: 84532
Block Number: 15234567
Deployer: 0x742d35cc6634c0532925a3b8c17f4ac70af45f5d
NimoIdentity: 0x9876...5432
NimoToken: 0x1234...5678
Token Name: NimoToken
Token Symbol: NIMO
Token Total Supply: 1000000000000000000000000
Identity Contract Name: NimoIdentity
Identity Contract Symbol: NIMO
===========================

Deployment addresses written to: deployments/base-sepolia.json
```

### Step 2: Verify Deployment

```bash
# Check deployment file
cat deployments/base-sepolia.json

# Verify contract addresses on BaseScan
open https://sepolia.basescan.org/address/0x...  # NimoIdentity
open https://sepolia.basescan.org/address/0x...  # NimoToken
```

### Step 3: Manual Verification (if automatic failed)

```bash
# Verify NimoToken
forge verify-contract \
    --chain base-sepolia \
    0x1234...5678 \
    src/NimoToken.sol:NimoToken \
    --constructor-args $(cast abi-encode "constructor(string,string,uint256)" "NimoToken" "NIMO" 1000000000000000000000000)

# Verify NimoIdentity
forge verify-contract \
    --chain base-sepolia \
    0x9876...5432 \
    src/NimoIdentity.sol:NimoIdentity
```

---

## Post-Deployment Configuration

### 1. Update Frontend Configuration

Update contract addresses in frontend environment:

```javascript
// frontend/.env.local
NEXT_PUBLIC_CONTRACT_NIMO_IDENTITY=0x9876...5432
NEXT_PUBLIC_CONTRACT_NIMO_TOKEN=0x1234...5678
NEXT_PUBLIC_CHAIN_ID=84532
NEXT_PUBLIC_RPC_URL=https://sepolia.base.org
```

### 2. Update Backend Configuration

Update contract addresses in backend config:

```python
# backend/config.py
BLOCKCHAIN_NETWORK = 'base-sepolia'
CONTRACT_ADDRESS_IDENTITY = '0x9876...5432'
CONTRACT_ADDRESS_TOKEN = '0x1234...5678'
PROVIDER_URL = 'https://sepolia.base.org'
```

### 3. Role Management Setup

```bash
# Add additional verifiers (if needed)
cast send 0x9876...5432 \
    "grantRole(bytes32,address)" \
    0x0c34e6b28e6d63c0eca7a6b32b3b2c40b9e5ba4e5c5cd9f37e8cc2b2b8b8b8b8 \
    0xVERIFIER_ADDRESS \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY

# Add MeTTa agent addresses
cast send 0x9876...5432 \
    "grantRole(bytes32,address)" \
    0x...... \
    0xMETTA_AGENT_ADDRESS \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY
```

---

## Testing Deployed Contracts

### 1. Basic Contract Interaction Tests

```bash
# Check token details
cast call 0x1234...5678 "name()" --rpc-url base-sepolia
cast call 0x1234...5678 "symbol()" --rpc-url base-sepolia
cast call 0x1234...5678 "totalSupply()" --rpc-url base-sepolia

# Check identity contract
cast call 0x9876...5432 "name()" --rpc-url base-sepolia
cast call 0x9876...5432 "symbol()" --rpc-url base-sepolia

# Check roles
cast call 0x9876...5432 \
    "hasRole(bytes32,address)" \
    0x0000000000000000000000000000000000000000000000000000000000000000 \
    0x742d35cc6634c0532925a3b8c17f4ac70af45f5d \
    --rpc-url base-sepolia
```

### 2. Create Test Identity

```bash
# Create an identity
cast send 0x9876...5432 \
    "createIdentity(string,string)" \
    "testuser" \
    "ipfs://QmTest123..." \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY

# Check if identity was created
cast call 0x9876...5432 \
    "usernameToTokenId(string)" \
    "testuser" \
    --rpc-url base-sepolia
```

### 3. Add Test Contribution

```bash
# Add a contribution
cast send 0x9876...5432 \
    "addContribution(string,string,string,string)" \
    "development" \
    "Test smart contract deployment" \
    "https://github.com/test/repo" \
    "metta_hash_123" \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY
```

### 4. Test Token Operations

```bash
# Check deployer token balance
cast call 0x1234...5678 \
    "balanceOf(address)" \
    0x742d35cc6634c0532925a3b8c17f4ac70af45f5d \
    --rpc-url base-sepolia

# Mint tokens for contribution (as verifier)
cast send 0x1234...5678 \
    "mintForContribution(address,uint256,string,string)" \
    0xRECIPIENT_ADDRESS \
    1000000000000000000 \
    "Test contribution reward" \
    "metta_proof_123" \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY
```

---

## Contract Verification Status

### Verification Commands for Each Contract

```bash
# NimoToken Verification
forge verify-contract \
    --chain base-sepolia \
    --compiler-version v0.8.19+commit.7dd6d404 \
    0x1234...5678 \
    src/NimoToken.sol:NimoToken \
    --constructor-args 0x0000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000d3c21bcecceda1000000000000000000000000000000000000000000000000000000000000000000000a4e696d6f546f6b656e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044e494d4f00000000000000000000000000000000000000000000000000000000

# NimoIdentity Verification
forge verify-contract \
    --chain base-sepolia \
    --compiler-version v0.8.19+commit.7dd6d404 \
    0x9876...5432 \
    src/NimoIdentity.sol:NimoIdentity
```

### Expected Verification Results

✅ **NimoToken Contract**
- Source Code: Verified
- ABI: Available
- Contract Creation: Block #15234567
- Optimization: Enabled (200 runs)

✅ **NimoIdentity Contract**
- Source Code: Verified
- ABI: Available
- Contract Creation: Block #15234568
- Optimization: Enabled (200 runs)

---

## Monitoring & Maintenance

### 1. Block Explorer Monitoring

Monitor contracts on BaseScan:
- **NimoToken:** https://sepolia.basescan.org/token/0x1234...5678
- **NimoIdentity:** https://sepolia.basescan.org/address/0x9876...5432

### 2. Event Monitoring

Set up event monitoring for key contract events:

```javascript
// Example monitoring script
const events = [
  'IdentityCreated',
  'ContributionAdded',
  'ContributionVerified',
  'TokensDistributed',
  'ImpactBondCreated',
  'BondInvestment'
];

// Monitor events in real-time
events.forEach(eventName => {
  contract.on(eventName, (...args) => {
    console.log(`Event: ${eventName}`, args);
    // Log to monitoring service
  });
});
```

### 3. Gas Optimization

Monitor gas usage and optimize if necessary:

```bash
# Analyze gas usage patterns
forge test --gas-report

# Optimize critical functions
# Focus on: createIdentity, addContribution, verifyContribution
```

---

## Troubleshooting

### Common Deployment Issues

**1. Insufficient Funds Error**
```
Error: insufficient funds for gas * price + value
```
**Solution:** Get more SepoliaETH from faucet or reduce gas price

**2. Verification Failed**
```
Error: Failed to verify contract
```
**Solution:** 
- Check constructor arguments encoding
- Ensure exact compiler version match
- Try manual verification with BaseScan UI

**3. RPC Connection Issues**
```
Error: could not connect to RPC
```
**Solutions:**
- Check internet connection
- Try alternative RPC: https://base-sepolia.public.blastapi.io
- Use Alchemy RPC with API key

**4. Nonce Issues**
```
Error: nonce too low
```
**Solution:** 
- Check account nonce: `cast nonce ADDRESS --rpc-url base-sepolia`
- Wait for pending transactions to confirm
- Use `--skip-simulation` flag if needed

### Emergency Procedures

**Contract Pause (if needed):**
```bash
# Pause token transfers
cast send 0x1234...5678 "pause()" \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY

# Unpause token transfers
cast send 0x1234...5678 "unpause()" \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY
```

**Role Revocation:**
```bash
# Revoke verifier role
cast send 0x9876...5432 \
    "revokeRole(bytes32,address)" \
    0x0c34e6b28e6d63c0eca7a6b32b3b2c40b9e5ba4e5c5cd9f37e8cc2b2b8b8b8b8 \
    0xBAD_VERIFIER_ADDRESS \
    --rpc-url base-sepolia \
    --private-key $PRIVATE_KEY
```

---

## Mainnet Preparation

### Pre-Mainnet Checklist

- [ ] Thorough testing on Base Sepolia completed
- [ ] Security audit completed and issues resolved
- [ ] Gas optimization analysis completed
- [ ] Frontend integration tested end-to-end
- [ ] Emergency procedures documented and tested
- [ ] Multi-signature setup for admin roles
- [ ] Contract verification process validated
- [ ] Monitoring and alerting systems ready

### Mainnet Deployment Changes

```toml
# foundry.toml - Update RPC endpoints
[rpc_endpoints]
base = "https://mainnet.base.org"

# Environment variables
BASE_RPC_URL=https://mainnet.base.org
BASESCAN_API_KEY=...  # Production API key
```

### Production Security Considerations

1. **Multi-Signature Wallets:** Use Gnosis Safe for admin operations
2. **Timelocks:** Implement timelock for critical operations
3. **Role Distribution:** Distribute roles among trusted parties
4. **Monitoring:** Set up 24/7 monitoring and alerting
5. **Backup Plans:** Have emergency response procedures

---

## Integration with Backend Services

### MeTTa Service Integration

```python
# backend/services/blockchain_service.py
class BlockchainService:
    def __init__(self):
        self.contract_identity = "0x9876...5432"
        self.contract_token = "0x1234...5678"
        self.rpc_url = "https://sepolia.base.org"
        
    async def verify_contribution_on_chain(self, contribution_id, tokens_awarded):
        # Implementation for on-chain verification
        pass
```

### API Endpoint Updates

Update API endpoints to include contract addresses:

```python
# backend/routes/blockchain.py
@blockchain_bp.route('/contracts', methods=['GET'])
def get_contract_addresses():
    return jsonify({
        "identity": current_app.config['CONTRACT_ADDRESS_IDENTITY'],
        "token": current_app.config['CONTRACT_ADDRESS_TOKEN'],
        "network": "base-sepolia",
        "chainId": 84532,
        "rpcUrl": "https://sepolia.base.org"
    })
```

---

## Cost Analysis

### Deployment Costs (Base Sepolia)

| Operation | Gas Used | Cost (ETH) | USD Estimate* |
|-----------|----------|------------|---------------|
| NimoToken Deployment | ~1,200,000 | ~0.0024 | ~$6.00 |
| NimoIdentity Deployment | ~2,800,000 | ~0.0056 | ~$14.00 |
| Role Setup (4 operations) | ~200,000 | ~0.0004 | ~$1.00 |
| **Total Deployment** | **~4,200,000** | **~0.0084** | **~$21.00** |

*USD estimates based on ETH at $2500 and gas price of 2 gwei

### Ongoing Operation Costs

| User Action | Gas Used | Cost (ETH) | USD Estimate* |
|-------------|----------|------------|---------------|
| Create Identity | ~150,000 | ~0.0003 | ~$0.75 |
| Add Contribution | ~100,000 | ~0.0002 | ~$0.50 |
| Verify Contribution | ~120,000 | ~0.00024 | ~$0.60 |
| Token Transfer | ~50,000 | ~0.0001 | ~$0.25 |
| Create Impact Bond | ~200,000 | ~0.0004 | ~$1.00 |
| Invest in Bond | ~80,000 | ~0.00016 | ~$0.40 |

---

## Documentation Updates

After successful deployment, update the following documents:
1. **API Documentation** - Add actual contract addresses
2. **Frontend Integration Guide** - Update with deployed addresses
3. **User Guide** - Update with Base Sepolia network details
4. **Architecture Documentation** - Include deployment diagram

---

## Conclusion

This deployment guide provides a comprehensive process for deploying Nimo Platform smart contracts to Base Sepolia testnet. The deployment process includes:

✅ **Completed:**
- Contract compilation and testing
- Deployment script with role configuration
- Automatic contract verification
- Integration with frontend and backend systems

🔄 **Next Steps:**
1. Execute deployment on Base Sepolia
2. Update all configuration files with actual addresses
3. Conduct end-to-end testing
4. Prepare for mainnet deployment

---

*Last Updated: January 26, 2025*  
*Author: John (Backend Developer)*  
*Status: Ready for deployment execution*