# Blockfrost API Setup Guide

## Quick Setup Steps

1. **Get Blockfrost API Key**:
   - Visit: https://blockfrost.io
   - Create account (free)
   - Go to Dashboard → Add new project
   - Select "Cardano Preview Testnet"
   - Copy your project ID

2. **Set Environment Variable**:
   ```bash
   # For Preview testnet (recommended for testing)
   export BLOCKFROST_PROJECT_ID_PREVIEW="preview_your_key_here"
   
   # Optional: For Preprod testnet  
   export BLOCKFROST_PROJECT_ID_PREPROD="preprod_your_key_here"
   
   # Optional: For Mainnet (production)
   export BLOCKFROST_PROJECT_ID_MAINNET="mainnet_your_key_here"
   ```

3. **Test Connection**:
   ```bash
   cd backend
   python test_cardano_connection.py
   ```

## Blockfrost Plans

- **Free Tier**: 100,000 requests/month (perfect for testing)
- **Paid Plans**: Higher limits for production

## Alternative: Use Demo Key (Limited)

For initial testing, you can use Blockfrost's demo project ID:
```bash
export BLOCKFROST_PROJECT_ID_PREVIEW="preview123demo456"
```

**Note**: Demo keys have severe rate limits and may not work for all operations.

## Network Endpoints

- **Preview**: https://cardano-preview.blockfrost.io/api
- **Preprod**: https://cardano-preprod.blockfrost.io/api  
- **Mainnet**: https://cardano-mainnet.blockfrost.io/api

## Next Steps

Once you have API keys:
1. Set the environment variables
2. Run the integration tests
3. Fund a test wallet with ADA from the faucet
4. Deploy NIMO token policy