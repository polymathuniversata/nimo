#!/bin/bash
# Simple deployment script for Polygon Mumbai
# Run this when network connectivity is restored

echo "🚀 Deploying Nimo Contracts to Polygon Mumbai"
echo "============================================"

# Set the private key
export BLOCKCHAIN_SERVICE_PRIVATE_KEY="13e571df7b98faa41a12010b5bd2ed00a2f1faae54f4a8c3496d101910fe7b26"

echo "Deployment Account: 0x4CE536b148BF86Ce30E2A28E610e3B2df973d9Af"
echo "Network: Polygon Mumbai"
echo ""

# Try different RPC endpoints
echo "Trying deployment with multiple RPC endpoints..."
echo ""

# Try Alchemy endpoint
echo "Attempt 1: Alchemy RPC"
forge script script/Deploy.s.sol --rpc-url https://polygon-mumbai.g.alchemy.com/v2/demo --broadcast --verify -vvvv

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    exit 0
fi

echo ""
echo "Attempt 2: MaticVigil RPC"
forge script script/Deploy.s.sol --rpc-url https://rpc-mumbai.maticvigil.com --broadcast --verify -vvvv

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    exit 0
fi

echo ""
echo "Attempt 3: Chainstack RPC"
forge script script/Deploy.s.sol --rpc-url https://matic-mumbai.chainstacklabs.com --broadcast --verify -vvvv

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    exit 0
fi

echo ""
echo "❌ All deployment attempts failed"
echo "   This might be due to:"
echo "   - Network connectivity issues"
echo "   - Insufficient MATIC balance"
echo "   - RPC endpoint problems"
echo ""
echo "💡 Try again later or check your MATIC balance"</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\contracts\deploy.sh