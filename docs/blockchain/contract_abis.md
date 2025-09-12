# Smart Contract ABIs for Frontend Integration

## Overview

This document provides the Application Binary Interfaces (ABIs) for Nimo Platform smart contracts deployed on Base Sepolia network. These ABIs enable the frontend to interact with the blockchain components of the platform.

**Network:** Base Sepolia Testnet  
**Chain ID:** 84531  
**RPC URL:** https://goerli.base.org  

---

## Contract Addresses

```javascript
// Base Sepolia Testnet Addresses
const CONTRACT_ADDRESSES = {
  NIMO_IDENTITY: "0x...", // To be deployed
  NIMO_TOKEN: "0x...",    // To be deployed
};
```

---

## NimoIdentity Contract

The core identity and reputation management contract.

### Contract Address
- **Base Sepolia:** `0x...` (Pending deployment)

### ABI

```javascript
const NIMO_IDENTITY_ABI = [
  // Constructor
  "constructor()",
  
  // View Functions
  "function identities(uint256) view returns (string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt)",
  "function contributions(uint256) view returns (uint256 identityId, string contributionType, string description, string evidenceURI, bool verified, address verifier, uint256 tokensAwarded, uint256 timestamp, string mettaHash)",
  "function impactBonds(uint256) view returns (uint256 bondId, address creator, string title, string description, uint256 targetAmount, uint256 currentAmount, uint256 maturityDate, bool isActive)",
  "function usernameToTokenId(string) view returns (uint256)",
  "function addressToTokenId(address) view returns (uint256)",
  "function getIdentity(uint256 tokenId) view returns (tuple(string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt))",
  "function getContribution(uint256 contributionId) view returns (tuple(uint256 identityId, string contributionType, string description, string evidenceURI, bool verified, address verifier, uint256 tokensAwarded, uint256 timestamp, string mettaHash))",
  "function getIdentityByUsername(string username) view returns (tuple(string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt))",
  "function getBondInvestment(uint256 bondId, address investor) view returns (uint256)",
  "function isMilestoneComplete(uint256 bondId, string milestone) view returns (bool)",
  
  // ERC721 Standard Functions
  "function balanceOf(address owner) view returns (uint256)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function safeTransferFrom(address from, address to, uint256 tokenId)",
  "function transferFrom(address from, address to, uint256 tokenId)",
  "function approve(address to, uint256 tokenId)",
  "function getApproved(uint256 tokenId) view returns (address)",
  "function setApprovalForAll(address operator, bool approved)",
  "function isApprovedForAll(address owner, address operator) view returns (bool)",
  "function safeTransferFrom(address from, address to, uint256 tokenId, bytes data)",
  
  // Access Control Functions
  "function hasRole(bytes32 role, address account) view returns (bool)",
  "function getRoleAdmin(bytes32 role) view returns (bytes32)",
  "function grantRole(bytes32 role, address account)",
  "function revokeRole(bytes32 role, address account)",
  "function renounceRole(bytes32 role, address account)",
  
  // Main Functions
  "function createIdentity(string username, string metadataURI)",
  "function addContribution(string contributionType, string description, string evidenceURI, string mettaHash)",
  "function verifyContribution(uint256 contributionId, uint256 tokensToAward)",
  "function executeMeTTaRule(string rule, uint256 targetIdentityId, uint256 tokensToAward)",
  "function createImpactBond(string title, string description, uint256 targetAmount, uint256 maturityDate, string[] milestones)",
  "function investInBond(uint256 bondId) payable",
  "function completeMilestone(uint256 bondId, string milestone)",
  
  // Constants
  "function VERIFIER_ROLE() view returns (bytes32)",
  "function METTA_AGENT_ROLE() view returns (bytes32)",
  "function DEFAULT_ADMIN_ROLE() view returns (bytes32)",
  
  // Events
  "event IdentityCreated(uint256 indexed tokenId, string username, address owner)",
  "event ContributionAdded(uint256 indexed contributionId, uint256 indexed identityId, string contributionType)",
  "event ContributionVerified(uint256 indexed contributionId, address verifier, uint256 tokensAwarded)",
  "event TokensAwarded(uint256 indexed identityId, uint256 amount, string reason)",
  "event ImpactBondCreated(uint256 indexed bondId, address creator, uint256 targetAmount)",
  "event BondInvestment(uint256 indexed bondId, address investor, uint256 amount)",
  "event MilestoneCompleted(uint256 indexed bondId, string milestone)",
  "event MeTTaRuleExecuted(string rule, string result)"
];
```

### Key Constants

```javascript
// Role identifiers for access control
const ROLES = {
  DEFAULT_ADMIN_ROLE: "0x0000000000000000000000000000000000000000000000000000000000000000",
  VERIFIER_ROLE: "0x0c34e6b28e6d63c0eca7a6b32b3b2c40b9e5ba4e5c5cd9f37e8cc2b2b8b8b8b8", // keccak256("VERIFIER_ROLE")
  METTA_AGENT_ROLE: "0x......" // keccak256("METTA_AGENT_ROLE")
};
```

---

## NimoToken Contract

ERC20 token contract for reputation and governance.

### Contract Address
- **Base Sepolia:** `0x...` (Pending deployment)

### ABI

```javascript
const NIMO_TOKEN_ABI = [
  // Constructor
  "constructor(string name, string symbol, uint256 initialSupply)",
  
  // ERC20 Standard Functions
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address account) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function transferFrom(address from, address to, uint256 amount) returns (bool)",
  
  // Custom Token Functions
  "function mintForContribution(address to, uint256 amount, string reason, string mettaProof)",
  "function burnForOpportunity(address from, uint256 amount, string reason)",
  "function pause()",
  "function unpause()",
  "function paused() view returns (bool)",
  
  // Distribution Tracking
  "function distributions(uint256) view returns (address recipient, uint256 amount, string reason, uint256 timestamp, string mettaProof)",
  "function getDistribution(uint256 distributionId) view returns (tuple(address recipient, uint256 amount, string reason, uint256 timestamp, string mettaProof))",
  "function getTotalDistributions() view returns (uint256)",
  
  // Access Control Functions
  "function hasRole(bytes32 role, address account) view returns (bool)",
  "function getRoleAdmin(bytes32 role) view returns (bytes32)",
  "function grantRole(bytes32 role, address account)",
  "function revokeRole(bytes32 role, address account)",
  "function renounceRole(bytes32 role, address account)",
  
  // Constants
  "function MINTER_ROLE() view returns (bytes32)",
  "function PAUSER_ROLE() view returns (bytes32)",
  "function BURNER_ROLE() view returns (bytes32)",
  "function DEFAULT_ADMIN_ROLE() view returns (bytes32)",
  
  // Events
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "event Approval(address indexed owner, address indexed spender, uint256 value)",
  "event TokensDistributed(address indexed recipient, uint256 amount, string reason)",
  "event TokensBurned(address indexed from, uint256 amount, string reason)",
  "event MeTTaProofAttached(uint256 indexed distributionId, string proof)",
  "event Paused(address account)",
  "event Unpaused(address account)"
];
```

### Key Constants

```javascript
// Role identifiers for token operations
const TOKEN_ROLES = {
  DEFAULT_ADMIN_ROLE: "0x0000000000000000000000000000000000000000000000000000000000000000",
  MINTER_ROLE: "0x9f2df0fed2c77648de5860a4cc508cd0818c85b8b8a1ab4ceeef8d981c8956a6", // keccak256("MINTER_ROLE")
  PAUSER_ROLE: "0x65d7a28e3265b37a6474929f336521b332c1681b933f6cb9f3376673440d862a", // keccak256("PAUSER_ROLE")
  BURNER_ROLE: "0x......" // keccak256("BURNER_ROLE")
};
```

---

## Frontend Integration Examples

### Setup Web3 Connection

```javascript
import { createPublicClient, createWalletClient, custom, http } from 'viem';
import { baseSepolia } from 'viem/chains';

// Public client for reading from contracts
const publicClient = createPublicClient({
  chain: baseSepolia,
  transport: http('https://goerli.base.org')
});

// Wallet client for writing to contracts (requires user wallet)
const walletClient = createWalletClient({
  chain: baseSepolia,
  transport: custom(window.ethereum)
});
```

### Reading Contract Data

```javascript
// Get user's identity
async function getUserIdentity(userAddress) {
  const identityId = await publicClient.readContract({
    address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
    abi: NIMO_IDENTITY_ABI,
    functionName: 'addressToTokenId',
    args: [userAddress]
  });
  
  if (identityId === 0n) {
    return null; // No identity found
  }
  
  const identity = await publicClient.readContract({
    address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
    abi: NIMO_IDENTITY_ABI,
    functionName: 'getIdentity',
    args: [identityId]
  });
  
  return {
    id: identityId,
    username: identity.username,
    metadataURI: identity.metadataURI,
    reputationScore: identity.reputationScore,
    tokenBalance: identity.tokenBalance,
    isActive: identity.isActive,
    createdAt: new Date(Number(identity.createdAt) * 1000)
  };
}

// Get token balance
async function getTokenBalance(userAddress) {
  const balance = await publicClient.readContract({
    address: CONTRACT_ADDRESSES.NIMO_TOKEN,
    abi: NIMO_TOKEN_ABI,
    functionName: 'balanceOf',
    args: [userAddress]
  });
  
  return balance;
}

// Get contribution details
async function getContribution(contributionId) {
  const contribution = await publicClient.readContract({
    address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
    abi: NIMO_IDENTITY_ABI,
    functionName: 'getContribution',
    args: [contributionId]
  });
  
  return {
    id: contributionId,
    identityId: contribution.identityId,
    type: contribution.contributionType,
    description: contribution.description,
    evidenceURI: contribution.evidenceURI,
    verified: contribution.verified,
    verifier: contribution.verifier,
    tokensAwarded: contribution.tokensAwarded,
    timestamp: new Date(Number(contribution.timestamp) * 1000),
    mettaHash: contribution.mettaHash
  };
}
```

### Writing to Contracts

```javascript
// Create new identity
async function createIdentity(username, metadataURI) {
  const account = await walletClient.getAddresses()[0];
  
  const hash = await walletClient.writeContract({
    address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
    abi: NIMO_IDENTITY_ABI,
    functionName: 'createIdentity',
    args: [username, metadataURI],
    account
  });
  
  // Wait for transaction confirmation
  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  return receipt;
}

// Add contribution
async function addContribution(type, description, evidenceURI, mettaHash) {
  const account = await walletClient.getAddresses()[0];
  
  const hash = await walletClient.writeContract({
    address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
    abi: NIMO_IDENTITY_ABI,
    functionName: 'addContribution',
    args: [type, description, evidenceURI, mettaHash],
    account
  });
  
  return await publicClient.waitForTransactionReceipt({ hash });
}

// Invest in impact bond
async function investInBond(bondId, amount) {
  const account = await walletClient.getAddresses()[0];
  
  const hash = await walletClient.writeContract({
    address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
    abi: NIMO_IDENTITY_ABI,
    functionName: 'investInBond',
    args: [bondId],
    value: amount, // Amount in wei
    account
  });
  
  return await publicClient.waitForTransactionReceipt({ hash });
}
```

### Event Listening

```javascript
// Listen for identity creation events
const unwatch = publicClient.watchContractEvent({
  address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
  abi: NIMO_IDENTITY_ABI,
  eventName: 'IdentityCreated',
  onLogs: (logs) => {
    logs.forEach(log => {
      console.log('New identity created:', {
        tokenId: log.args.tokenId,
        username: log.args.username,
        owner: log.args.owner,
        blockNumber: log.blockNumber,
        transactionHash: log.transactionHash
      });
    });
  }
});

// Listen for contribution verifications
publicClient.watchContractEvent({
  address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
  abi: NIMO_IDENTITY_ABI,
  eventName: 'ContributionVerified',
  onLogs: (logs) => {
    logs.forEach(log => {
      console.log('Contribution verified:', {
        contributionId: log.args.contributionId,
        verifier: log.args.verifier,
        tokensAwarded: log.args.tokensAwarded
      });
    });
  }
});

// Listen for token transfers
publicClient.watchContractEvent({
  address: CONTRACT_ADDRESSES.NIMO_TOKEN,
  abi: NIMO_TOKEN_ABI,
  eventName: 'Transfer',
  onLogs: (logs) => {
    logs.forEach(log => {
      console.log('Token transfer:', {
        from: log.args.from,
        to: log.args.to,
        value: log.args.value
      });
    });
  }
});
```

---

## Error Handling

### Common Contract Errors

```javascript
// Error handling for contract interactions
async function safeContractCall(contractCall) {
  try {
    return await contractCall();
  } catch (error) {
    if (error.message.includes('User denied transaction')) {
      throw new Error('Transaction was cancelled by user');
    }
    
    if (error.message.includes('insufficient funds')) {
      throw new Error('Insufficient funds to complete transaction');
    }
    
    if (error.message.includes('Username already exists')) {
      throw new Error('This username is already taken');
    }
    
    if (error.message.includes('No identity found')) {
      throw new Error('You must create an identity first');
    }
    
    if (error.message.includes('Contribution already verified')) {
      throw new Error('This contribution has already been verified');
    }
    
    console.error('Contract error:', error);
    throw new Error('Transaction failed. Please try again.');
  }
}

// Usage example
try {
  const receipt = await safeContractCall(() => 
    createIdentity('john_doe', 'ipfs://QmXxx...')
  );
  console.log('Identity created successfully:', receipt);
} catch (error) {
  console.error('Failed to create identity:', error.message);
}
```

---

## Gas Estimation

```javascript
// Estimate gas for transactions before sending
async function estimateGasForIdentityCreation(username, metadataURI) {
  const account = await walletClient.getAddresses()[0];
  
  try {
    const gas = await publicClient.estimateContractGas({
      address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
      abi: NIMO_IDENTITY_ABI,
      functionName: 'createIdentity',
      args: [username, metadataURI],
      account
    });
    
    return gas;
  } catch (error) {
    console.error('Gas estimation failed:', error);
    return null;
  }
}
```

---

## TypeScript Interfaces

```typescript
// TypeScript interfaces for type safety
interface Identity {
  id: bigint;
  username: string;
  metadataURI: string;
  reputationScore: bigint;
  tokenBalance: bigint;
  isActive: boolean;
  createdAt: Date;
}

interface Contribution {
  id: bigint;
  identityId: bigint;
  type: string;
  description: string;
  evidenceURI: string;
  verified: boolean;
  verifier: `0x${string}`;
  tokensAwarded: bigint;
  timestamp: Date;
  mettaHash: string;
}

interface ImpactBond {
  id: bigint;
  bondId: bigint;
  creator: `0x${string}`;
  title: string;
  description: string;
  targetAmount: bigint;
  currentAmount: bigint;
  maturityDate: Date;
  isActive: boolean;
}

interface TokenDistribution {
  recipient: `0x${string}`;
  amount: bigint;
  reason: string;
  timestamp: Date;
  mettaProof: string;
}
```

---

## Deployment Information

### Contract Deployment Status

| Contract | Status | Base Sepolia Address | Verification Status |
|----------|--------|---------------------|-------------------|
| NimoIdentity | Pending | `0x...` | Pending |
| NimoToken | Pending | `0x...` | Pending |

### Deployment Scripts

Located in `contracts/script/Deploy.s.sol` - Foundry deployment script for both contracts.

### Verification

Once deployed, contracts will be verified on BaseScan for transparency:
- BaseScan Sepolia: https://sepolia.basescan.org/

---

## Integration Checklist for Frontend

- [ ] Add contract addresses to environment variables
- [ ] Import ABIs into Web3 utilities
- [ ] Implement wallet connection flow
- [ ] Add contract read functions for displaying data
- [ ] Add contract write functions for user actions
- [ ] Implement event listeners for real-time updates
- [ ] Add error handling for all contract interactions
- [ ] Add gas estimation for better UX
- [ ] Add loading states for blockchain operations
- [ ] Test on Base Sepolia testnet
- [ ] Prepare for mainnet deployment

---

*Last Updated: January 26, 2025*  
*Author: John (Backend Developer)*  
*Status: Ready for frontend integration pending contract deployment*