# Wallet Integration Guide

## Overview

This guide explains the backend wallet integration for the Nimo platform. The wallet integration allows users to connect their Ethereum wallets to their accounts, enabling Web3 functionality such as identity verification, token transactions, and blockchain interactions.

## Backend Implementation

### User Model Changes

The `User` model has been updated to include a `wallet_address` field:

```python
wallet_address = db.Column(db.String(42), unique=True)  # Ethereum address
```

This field stores the user's Ethereum address in checksum format.

### API Endpoints

#### Check Wallet Status

**Endpoint:** `GET /api/user/me/wallet`

**Authentication:** Required (JWT token)

**Response (Wallet Connected):**
```json
{
  "has_wallet": true,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "message": "Wallet connected successfully"
}
```

**Response (No Wallet):**
```json
{
  "has_wallet": false,
  "message": "No wallet connected. Please connect your wallet to proceed.",
  "action_required": "connect_wallet"
}
```

#### Set/Update Wallet Address

**Endpoint:** `POST /api/user/me/wallet`

**Authentication:** Required (JWT token)

**Request Body:**
```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Wallet address updated successfully",
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

**Response (Error):**
```json
{
  "error": "Invalid Ethereum address format"
}
```

## Integration Workflow

### 1. Check Wallet on App Load

When the application loads or when accessing wallet-dependent features:

1. Call `GET /api/user/me/wallet`
2. If `has_wallet` is `false`, prompt the user to connect their wallet
3. If `has_wallet` is `true`, proceed with wallet-dependent functionality

### 2. Wallet Connection Flow

1. **Frontend Detection:** Use Web3 libraries (e.g., ethers.js, web3.js) to detect available wallets
2. **User Selection:** Present wallet options (MetaMask, WalletConnect, Coinbase Wallet, etc.)
3. **Connection:** Request user to connect their wallet
4. **Address Retrieval:** Get the connected wallet address
5. **Backend Update:** Send the address to `POST /api/user/me/wallet`
6. **Verification:** Optionally verify the address ownership through signature

### 3. Address Validation

The backend performs basic validation:
- Must start with `0x`
- Must be exactly 42 characters long
- Should be a valid Ethereum address format

For enhanced security, consider:
- Checksum validation using ethers.js `getAddress()`
- Signature verification to prove address ownership

## Frontend Integration Steps

### Step 1: Install Web3 Dependencies

```bash
npm install ethers web3 @walletconnect/web3-provider @coinbase/wallet-sdk
```

### Step 2: Create Wallet Store/Service

Create a wallet management service that:

1. Detects available wallets
2. Handles connection logic
3. Manages connection state
4. Integrates with the backend API

### Step 3: Implement Connection UI

Create UI components for:

1. Wallet selection modal
2. Connection status display
3. Error handling for connection failures
4. Disconnect functionality

### Step 4: Backend Integration

```javascript
// Example wallet connection function
async function connectWallet(walletType) {
  try {
    let provider;
    
    switch(walletType) {
      case 'metamask':
        if (!window.ethereum) throw new Error('MetaMask not installed');
        provider = new ethers.providers.Web3Provider(window.ethereum);
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        break;
        
      case 'walletconnect':
        // WalletConnect implementation
        break;
        
      case 'coinbase':
        // Coinbase Wallet implementation
        break;
    }
    
    const signer = provider.getSigner();
    const address = await signer.getAddress();
    
    // Update backend
    const response = await fetch('/api/user/me/wallet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ wallet_address: address })
    });
    
    if (response.ok) {
      // Update local state
      setWalletConnected(true);
      setWalletAddress(address);
    }
    
  } catch (error) {
    console.error('Wallet connection failed:', error);
    // Handle error in UI
  }
}
```

### Step 5: Check Wallet Status

```javascript
// Check wallet status on app load
async function checkWalletStatus() {
  try {
    const response = await fetch('/api/user/me/wallet', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.has_wallet) {
      setWalletConnected(true);
      setWalletAddress(data.wallet_address);
    } else {
      // Show wallet connection prompt
      showWalletPrompt(data.message);
    }
  } catch (error) {
    console.error('Failed to check wallet status:', error);
  }
}
```

## Security Considerations

### Address Ownership Verification

To ensure the user actually owns the wallet address:

1. **Signature Challenge:** Generate a random message
2. **User Signing:** Ask user to sign the message with their wallet
3. **Verification:** Verify the signature matches the address
4. **Backend Validation:** Send signature to backend for verification

### Example Implementation

```javascript
async function verifyAddressOwnership(address) {
  const message = `Verify ownership of ${address} for Nimo platform at ${Date.now()}`;
  
  try {
    const signature = await signer.signMessage(message);
    
    // Send to backend for verification
    const response = await fetch('/api/user/verify-wallet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        address,
        message,
        signature
      })
    });
    
    return response.ok;
  } catch (error) {
    return false;
  }
}
```

## Integration with Existing Features

### Identity Verification

The wallet address can be used for:
- DID verification (`did:eth:address`)
- ENS name resolution
- Identity trust scoring

### Token Transactions

Wallet connection enables:
- USDC balance checking
- Token transfers
- Reward claiming

### Smart Contract Interactions

With wallet connected:
- Bond creation and management
- Contribution verification
- Reputation token awards

## Testing

### Unit Tests

Test the backend endpoints:
- Wallet status retrieval
- Address validation
- Database updates

### Integration Tests

Test the full flow:
- Wallet connection
- Backend synchronization
- Identity verification
- Token operations

### Manual Testing

Test with different wallets:
- MetaMask
- WalletConnect
- Coinbase Wallet
- Hardware wallets (Ledger, Trezor)

## Troubleshooting

### Common Issues

1. **Address Format Errors:** Ensure addresses are in correct format
2. **Network Mismatches:** Verify user is on correct network (Base Sepolia/Mainnet)
3. **Connection Timeouts:** Handle network delays gracefully
4. **Signature Rejections:** Provide clear error messages for user rejections

### Error Handling

Implement comprehensive error handling:
- Network errors
- User rejections
- Invalid addresses
- Backend failures

## Future Enhancements

1. **Multi-Wallet Support:** Allow users to connect multiple wallets
2. **Wallet Switching:** Enable switching between connected wallets
3. **Transaction History:** Track and display wallet transaction history
4. **Gas Optimization:** Implement gas estimation and optimization
5. **Batch Transactions:** Support for multiple transaction batching

## Conclusion

This wallet integration provides a solid foundation for Web3 functionality in the Nimo platform. The backend handles wallet address storage and validation, while the frontend manages the connection process. Following this guide ensures secure and user-friendly wallet integration.