# Cardano Deployment Guide

## Current Status ✅
- ✅ Service key generated: `addr1vy8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5pg2ya43y`
- ✅ Environment files configured
- ✅ Dependencies installed
- ❌ Blockfrost API key needed

## Next Steps

### 1. Get Blockfrost API Key
1. Go to https://blockfrost.io/
2. Create a free account
3. Create a new project:
   - Select "Cardano" as the blockchain
   - Select "Preview" as the network (testnet)
   - Name your project "Nimo Platform Preview"
4. Copy your Project ID (it looks like: `previewXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

### 2. Configure Environment Variables
Add this to your environment or `.env` files:

```bash
# For Linux/Mac
export BLOCKFROST_PROJECT_ID_PREVIEW=your_project_id_here

# For Windows (Command Prompt)
set BLOCKFROST_PROJECT_ID_PREVIEW=your_project_id_here

# For Windows (PowerShell)
$env:BLOCKFROST_PROJECT_ID_PREVIEW="your_project_id_here"
```

Or add to your `.env` files:
```
BLOCKFROST_PROJECT_ID_PREVIEW=your_project_id_here
```

### 3. Fund Service Address with Test ADA
1. Go to: https://docs.cardano.org/cardano-testnets/tools/faucet
2. Select "Preview" testnet
3. Enter this address: `addr1vy8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5pg2ya43y`
4. Click "Receive test ada"
5. Wait 2-3 minutes for confirmation

### 4. Verify Setup
Run the status checker again:
```bash
cd contracts/cardano
python check_deployment_status.py
```

You should see:
- Blockfrost: ✓
- Service balance: > 5 ADA

### 5. Deploy NIMO Token
Once everything is ready:
```bash
cd contracts/cardano
python deploy_nimo_token.py --network preview
```

## What Will Be Deployed

1. **NIMO Token Policy**: A native Cardano token policy
2. **Initial Mint**: 1,000,000 NIMO tokens
3. **Metadata**: CIP-25 compliant token metadata
4. **Policy File**: Updated `nimo_token_policy.json`

## Expected Output
```
============================================================
NIMO TOKEN DEPLOYMENT SUCCESSFUL!
============================================================
Network: preview
Policy ID: [generated_policy_id]
Service Address: addr1vy8nse38pa7zj2sur39c205t4smhqz8t6dwq36ava8rt5pg2ya43y
Mint Transaction: [transaction_hash]
Initial Mint: 1000000 NIMO tokens
============================================================
```

## Integration with Backend

After deployment, update your backend `.env`:
```
NIMO_TOKEN_POLICY_ID=[generated_policy_id]
```

The backend will automatically:
- Use the deployed token for rewards
- Mint new tokens for verified contributions
- Handle ADA transfers for rewards
- Integrate with MeTTa reasoning engine

## Troubleshooting

### Blockfrost Connection Issues
- Verify your project ID is correct
- Check if you're using the right network (Preview testnet)
- Ensure your IP is not blocked

### Insufficient Funds
- Service address needs at least 5 ADA for deployment
- Use the faucet to get more test ADA
- Check transaction fees (typically ~0.17 ADA)

### Token Deployment Fails
- Ensure service address has sufficient ADA
- Check Blockfrost API limits
- Verify network connectivity

## Security Notes

- The generated service key is for testing only
- For production, use a hardware wallet
- Never commit private keys to version control
- Regularly rotate service keys
- Implement proper access controls for minting