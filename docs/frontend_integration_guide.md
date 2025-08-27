# Frontend Integration Guide - Nimo Platform

## Overview

This guide provides everything needed for frontend developers to integrate with the Nimo Platform's backend API and blockchain contracts. The platform enables decentralized youth identity management and proof of contribution verification using MeTTa AI reasoning.

**Tech Stack:**
- Backend: Flask API with JWT authentication
- Blockchain: Solidity contracts on Base Sepolia
- AI: MeTTa reasoning for contribution verification
- Frontend: **React 19.1.1 + Vite + Tailwind CSS** (already configured)

---

## 1. API Endpoints Documentation

### Base URL
```
http://localhost:5000/api  (development)
https://api.nimo-platform.com/api  (production)
```

### Authentication

#### Register User
```javascript
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "location": "New York, USA",
  "bio": "Software developer passionate about open source",
  "skills": ["JavaScript", "Python", "React"]
}
```

**Response:**
```javascript
{
  "message": "User registered successfully"
}
```

#### Login
```javascript
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```javascript
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "location": "New York, USA",
    "bio": "Software developer...",
    "skills": ["JavaScript", "Python", "React"],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Contributions

#### Get Contributions
```javascript
GET /contributions/
Authorization: Bearer <access_token>
Query params: page, per_page, verified, type, impact, search, sort_by, sort_order
```

**Response:**
```javascript
{
  "contributions": [
    {
      "id": 1,
      "title": "Open Source Contribution",
      "description": "Contributed to React project",
      "contribution_type": "coding",
      "impact_level": "moderate",
      "evidence": {
        "url": "https://github.com/user/repo/pull/123",
        "type": "url"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "verifications": []
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 50,
    "has_next": true,
    "next_num": 2
  }
}
```

#### Create Contribution
```javascript
POST /contributions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Open Source Contribution",
  "description": "Contributed bug fixes to React project",
  "type": "coding",
  "impact": "moderate",
  "evidence": {
    "url": "https://github.com/user/repo/pull/123",
    "type": "url"
  }
}
```

**Response:**
```javascript
{
  "id": 1,
  "title": "Open Source Contribution",
  "description": "Contributed bug fixes to React project",
  "contribution_type": "coding",
  "impact_level": "moderate",
  "evidence": {
    "url": "https://github.com/user/repo/pull/123",
    "type": "url"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Verify Contribution
```javascript
POST /contributions/{id}/verify
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "organization": "Nimo Platform",
  "verifier_name": "AI Verifier",
  "comments": "Verified via MeTTa reasoning"
}
```

#### Get Contribution Explanation
```javascript
GET /contributions/{id}/explain
Authorization: Bearer <access_token>
```

**Response:**
```javascript
{
  "contribution": {
    "id": 1,
    "title": "Open Source Contribution",
    "type": "coding",
    "impact_level": "moderate"
  },
  "verification_history": [
    {
      "verifier": "AI Verifier",
      "organization": "Nimo Platform",
      "date": "2024-01-15T11:00:00Z",
      "comments": "Verified via MeTTa reasoning",
      "proof": "0x1234..."
    }
  ],
  "reasoning_factors": {
    "evidence_quality": "high",
    "skill_match": "verified",
    "impact_assessment": "moderate"
  }
}
```

### Token Management

#### Get Token Balance
```javascript
GET /tokens/balance
Authorization: Bearer <access_token>
```

**Response:**
```javascript
{
  "balance": 150,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Token Transactions
```javascript
GET /tokens/transactions
Authorization: Bearer <access_token>
```

**Response:**
```javascript
{
  "transactions": [
    {
      "id": 1,
      "amount": 50,
      "description": "Contribution verification reward",
      "type": "credit",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Transfer Tokens
```javascript
POST /tokens/transfer
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "recipient_id": 2,
  "amount": 25
}
```

### User Management

#### Get Current User
```javascript
GET /users/me
Authorization: Bearer <access_token>
```

#### Update User Profile
```javascript
PUT /users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "location": "New Location",
  "bio": "Updated bio",
  "skills": ["JavaScript", "Vue.js", "Node.js"]
}
```

---

## 2. Contract ABIs & Addresses

### Network Configuration
```javascript
const NETWORK_CONFIG = {
  chainId: 84531, // Base Sepolia
  chainName: 'Base Sepolia',
  rpcUrls: ['https://goerli.base.org'],
  nativeCurrency: {
    name: 'Ethereum',
    symbol: 'ETH',
    decimals: 18
  },
  blockExplorerUrls: ['https://sepolia.basescan.org']
};
```

### Contract Addresses
```javascript
const CONTRACT_ADDRESSES = {
  NIMO_IDENTITY: '0x...', // Deployed address
  NIMO_TOKEN: '0x...'     // Deployed address
};
```

### NimoIdentity ABI
```javascript
const NIMO_IDENTITY_ABI = [
  "constructor()",
  "function identities(uint256) view returns (string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt)",
  "function contributions(uint256) view returns (uint256 identityId, string contributionType, string description, string evidenceURI, bool verified, address verifier, uint256 tokensAwarded, uint256 timestamp, string mettaHash)",
  "function usernameToTokenId(string) view returns (uint256)",
  "function addressToTokenId(address) view returns (uint256)",
  "function getIdentity(uint256 tokenId) view returns (tuple(string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt))",
  "function getContribution(uint256 contributionId) view returns (tuple(uint256 identityId, string contributionType, string description, string evidenceURI, bool verified, address verifier, uint256 tokensAwarded, uint256 timestamp, string mettaHash))",
  "function balanceOf(address owner) view returns (uint256)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function createIdentity(string username, string metadataURI)",
  "function addContribution(string contributionType, string description, string evidenceURI, string mettaHash)",
  "function verifyContribution(uint256 contributionId, uint256 tokensToAward)",
  "event IdentityCreated(uint256 indexed tokenId, string username, address owner)",
  "event ContributionAdded(uint256 indexed contributionId, uint256 indexed identityId, string contributionType)",
  "event ContributionVerified(uint256 indexed contributionId, address verifier, uint256 tokensAwarded)"
];
```

### NimoToken ABI
```javascript
const NIMO_TOKEN_ABI = [
  "constructor(string name, string symbol, uint256 initialSupply)",
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address account) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function transferFrom(address from, address to, uint256 amount) returns (bool)",
  "function mintForContribution(address to, uint256 amount, string reason, string mettaProof)",
  "function burnForOpportunity(address from, uint256 amount, string reason)",
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "event TokensDistributed(address indexed recipient, uint256 amount, string reason)"
];
```

---

# Frontend Integration Guide - Nimo Platform (React.js)

## Overview

This guide provides everything needed for frontend developers to integrate with the Nimo Platform's backend API and blockchain contracts. The platform enables decentralized youth identity management and proof of contribution verification using MeTTa AI reasoning.

**Tech Stack:**
- Backend: Flask API with JWT authentication
- Blockchain: Solidity contracts on Base Sepolia
- AI: MeTTa reasoning for contribution verification
- Frontend: **React 19.1.1 + Vite + Tailwind CSS** (already configured)

---

## 1. API Endpoints Documentation

### Base URL
```
http://localhost:5000/api  (development)
https://api.nimo-platform.com/api  (production)
```

### Authentication

#### Register User
```javascript
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "location": "New York, USA",
  "bio": "Software developer passionate about open source",
  "skills": ["JavaScript", "Python", "React"]
}
```

**Response:**
```javascript
{
  "message": "User registered successfully"
}
```

#### Login
```javascript
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```javascript
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "location": "New York, USA",
    "bio": "Software developer...",
    "skills": ["JavaScript", "Python", "React"],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Contributions

#### Get Contributions
```javascript
GET /contributions/
Authorization: Bearer <access_token>
Query params: page, per_page, verified, type, impact, search, sort_by, sort_order
```

**Response:**
```javascript
{
  "contributions": [
    {
      "id": 1,
      "title": "Open Source Contribution",
      "description": "Contributed to React project",
      "contribution_type": "coding",
      "impact_level": "moderate",
      "evidence": {
        "url": "https://github.com/user/repo/pull/123",
        "type": "url"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "verifications": []
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 50,
    "has_next": true,
    "next_num": 2
  }
}
```

#### Create Contribution
```javascript
POST /contributions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Open Source Contribution",
  "description": "Contributed bug fixes to React project",
  "type": "coding",
  "impact": "moderate",
  "evidence": {
    "url": "https://github.com/user/repo/pull/123",
    "type": "url"
  }
}
```

**Response:**
```javascript
{
  "id": 1,
  "title": "Open Source Contribution",
  "description": "Contributed bug fixes to React project",
  "contribution_type": "coding",
  "impact_level": "moderate",
  "evidence": {
    "url": "https://github.com/user/repo/pull/123",
    "type": "url"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Verify Contribution
```javascript
POST /contributions/{id}/verify
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "organization": "Nimo Platform",
  "verifier_name": "AI Verifier",
  "comments": "Verified via MeTTa reasoning"
}
```

#### Get Contribution Explanation
```javascript
GET /contributions/{id}/explain
Authorization: Bearer <access_token>
```

**Response:**
```javascript
{
  "contribution": {
    "id": 1,
    "title": "Open Source Contribution",
    "type": "coding",
    "impact_level": "moderate"
  },
  "verification_history": [
    {
      "verifier": "AI Verifier",
      "organization": "Nimo Platform",
      "date": "2024-01-15T11:00:00Z",
      "comments": "Verified via MeTTa reasoning",
      "proof": "0x1234..."
    }
  ],
  "reasoning_factors": {
    "evidence_quality": "high",
    "skill_match": "verified",
    "impact_assessment": "moderate"
  }
}
```

### Token Management

#### Get Token Balance
```javascript
GET /tokens/balance
Authorization: Bearer <access_token>
```

**Response:**
```javascript
{
  "balance": 150,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Token Transactions
```javascript
GET /tokens/transactions
Authorization: Bearer <access_token>
```

**Response:**
```javascript
{
  "transactions": [
    {
      "id": 1,
      "amount": 50,
      "description": "Contribution verification reward",
      "type": "credit",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Transfer Tokens
```javascript
POST /tokens/transfer
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "recipient_id": 2,
  "amount": 25
}
```

### User Management

#### Get Current User
```javascript
GET /users/me
Authorization: Bearer <access_token>
```

#### Update User Profile
```javascript
PUT /users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "location": "New Location",
  "bio": "Updated bio",
  "skills": ["JavaScript", "Vue.js", "Node.js"]
}
```

---

## 2. Contract ABIs & Addresses

### Network Configuration
```javascript
const NETWORK_CONFIG = {
  chainId: 84531, // Base Sepolia
  chainName: 'Base Sepolia',
  rpcUrls: ['https://goerli.base.org'],
  nativeCurrency: {
    name: 'Ethereum',
    symbol: 'ETH',
    decimals: 18
  },
  blockExplorerUrls: ['https://sepolia.basescan.org']
};
```

### Contract Addresses
```javascript
const CONTRACT_ADDRESSES = {
  NIMO_IDENTITY: '0x...', // Deployed address
  NIMO_TOKEN: '0x...'     // Deployed address
};
```

### NimoIdentity ABI
```javascript
const NIMO_IDENTITY_ABI = [
  "constructor()",
  "function identities(uint256) view returns (string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt)",
  "function contributions(uint256) view returns (uint256 identityId, string contributionType, string description, string evidenceURI, bool verified, address verifier, uint256 tokensAwarded, uint256 timestamp, string mettaHash)",
  "function usernameToTokenId(string) view returns (uint256)",
  "function addressToTokenId(address) view returns (uint256)",
  "function getIdentity(uint256 tokenId) view returns (tuple(string username, string metadataURI, uint256 reputationScore, uint256 tokenBalance, bool isActive, uint256 createdAt))",
  "function getContribution(uint256 contributionId) view returns (tuple(uint256 identityId, string contributionType, string description, string evidenceURI, bool verified, address verifier, uint256 tokensAwarded, uint256 timestamp, string mettaHash))",
  "function balanceOf(address owner) view returns (uint256)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function createIdentity(string username, string metadataURI)",
  "function addContribution(string contributionType, string description, string evidenceURI, string mettaHash)",
  "function verifyContribution(uint256 contributionId, uint256 tokensToAward)",
  "event IdentityCreated(uint256 indexed tokenId, string username, address owner)",
  "event ContributionAdded(uint256 indexed contributionId, uint256 indexed identityId, string contributionType)",
  "event ContributionVerified(uint256 indexed contributionId, address verifier, uint256 tokensAwarded)"
];
```

### NimoToken ABI
```javascript
const NIMO_TOKEN_ABI = [
  "constructor(string name, string symbol, uint256 initialSupply)",
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address account) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function transferFrom(address from, address to, uint256 amount) returns (bool)",
  "function mintForContribution(address to, uint256 amount, string reason, string mettaProof)",
  "function burnForOpportunity(address from, uint256 amount, string reason)",
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "event TokensDistributed(address indexed recipient, uint256 amount, string reason)"
];
```

---

## 3. React.js Implementation Guide

### Setup Web3 Connection

#### Install Dependencies (Already Done)
```bash
cd frontend
npm install ethers viem wagmi @web3modal/wagmi @walletconnect/web3-provider
```

#### Web3 Configuration
```javascript
// src/hooks/useWeb3.js
import { createPublicClient, createWalletClient, custom, http } from 'viem';
import { baseSepolia } from 'viem/chains';
import { useState, useEffect } from 'react';

export const useWeb3 = () => {
  const [publicClient, setPublicClient] = useState(null);
  const [walletClient, setWalletClient] = useState(null);
  const [account, setAccount] = useState(null);

  useEffect(() => {
    const initPublicClient = createPublicClient({
      chain: baseSepolia,
      transport: http('https://goerli.base.org')
    });
    setPublicClient(initPublicClient);
  }, []);

  const connectWallet = async () => {
    if (!window.ethereum) throw new Error('No wallet found');

    const client = createWalletClient({
      chain: baseSepolia,
      transport: custom(window.ethereum)
    });

    const [address] = await client.getAddresses();
    setWalletClient(client);
    setAccount(address);

    return address;
  };

  return {
    publicClient,
    walletClient,
    account,
    connectWallet
  };
};
```

### API Service Setup

#### Axios Configuration
```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production'
    ? 'https://api.nimo-platform.com/api'
    : 'http://localhost:5000/api',
  timeout: 10000
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### API Service Methods
```javascript
// src/services/auth.js
import api from './api.js';

export const authService = {
  async login(credentials) {
    const response = await api.post('/auth/login', credentials);
    const { access_token, user } = response.data;
    localStorage.setItem('access_token', access_token);
    return { token: access_token, user };
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
  }
};

// src/services/contributions.js
export const contributionService = {
  async getContributions(params = {}) {
    const response = await api.get('/contributions/', { params });
    return response.data;
  },

  async createContribution(contributionData) {
    const response = await api.post('/contributions/', contributionData);
    return response.data;
  },

  async verifyContribution(id, verificationData) {
    const response = await api.post(`/contributions/${id}/verify`, verificationData);
    return response.data;
  },

  async getContributionExplanation(id) {
    const response = await api.get(`/contributions/${id}/explain`);
    return response.data;
  }
};

// src/services/tokens.js
export const tokenService = {
  async getBalance() {
    const response = await api.get('/tokens/balance');
    return response.data;
  },

  async getTransactions() {
    const response = await api.get('/tokens/transactions');
    return response.data;
  },

  async transferTokens(recipientId, amount) {
    const response = await api.post('/tokens/transfer', {
      recipient_id: recipientId,
      amount
    });
    return response.data;
  }
};
```

### Blockchain Service Setup

#### Contract Interactions
```javascript
// src/services/blockchain.js
import { useWeb3 } from '@/hooks/useWeb3';
import { CONTRACT_ADDRESSES, NIMO_IDENTITY_ABI, NIMO_TOKEN_ABI } from '@/constants/contracts';

export const blockchainService = {
  async getUserIdentity(userAddress) {
    const { publicClient } = useWeb3();

    try {
      const identityId = await publicClient.readContract({
        address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
        abi: NIMO_IDENTITY_ABI,
        functionName: 'addressToTokenId',
        args: [userAddress]
      });

      if (identityId === 0n) return null;

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
    } catch (error) {
      console.error('Error fetching identity:', error);
      return null;
    }
  },

  async createIdentity(username, metadataURI) {
    const { walletClient, account } = useWeb3();

    const hash = await walletClient.writeContract({
      address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
      abi: NIMO_IDENTITY_ABI,
      functionName: 'createIdentity',
      args: [username, metadataURI],
      account
    });

    return hash;
  },

  async addContribution(type, description, evidenceURI, mettaHash) {
    const { walletClient, account } = useWeb3();

    const hash = await walletClient.writeContract({
      address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
      abi: NIMO_IDENTITY_ABI,
      functionName: 'addContribution',
      args: [type, description, evidenceURI, mettaHash],
      account
    });

    return hash;
  },

  async getTokenBalance(userAddress) {
    const { publicClient } = useWeb3();

    const balance = await publicClient.readContract({
      address: CONTRACT_ADDRESSES.NIMO_TOKEN,
      abi: NIMO_TOKEN_ABI,
      functionName: 'balanceOf',
      args: [userAddress]
    });

    return balance;
  }
};
```

### React Components Implementation

#### Authentication Store (Context API)
```javascript
// src/contexts/UserContext.jsx
import { createContext, useContext, useState } from 'react';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [wallet, setWallet] = useState({ connected: false, address: null });

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('access_token', authToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setWallet({ connected: false, address: null });
    localStorage.removeItem('access_token');
  };

  const connectWallet = (address) => {
    setWallet({ connected: true, address });
  };

  return (
    <UserContext.Provider value={{
      user,
      token,
      wallet,
      login,
      logout,
      connectWallet
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
```

#### Contribution Component
```jsx
// src/components/ContributionCard.jsx
import { useState } from 'react';
import { contributionService } from '../services/contributions';
import { useUser } from '../contexts/UserContext';

const ContributionCard = ({ contribution, onVerified, onExplained }) => {
  const [verifying, setVerifying] = useState(false);
  const { user } = useUser();

  const getTypeColor = (type) => {
    const colors = {
      coding: 'bg-blue-100 text-blue-800',
      education: 'bg-green-100 text-green-800',
      volunteer: 'bg-orange-100 text-orange-800',
      activism: 'bg-red-100 text-red-800',
      leadership: 'bg-purple-100 text-purple-800',
      entrepreneurship: 'bg-teal-100 text-teal-800',
      environmental: 'bg-green-100 text-green-800',
      community: 'bg-indigo-100 text-indigo-800',
      other: 'bg-gray-100 text-gray-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getImpactColor = (impact) => {
    const colors = {
      minimal: 'bg-gray-100 text-gray-800',
      moderate: 'bg-yellow-100 text-yellow-800',
      significant: 'bg-orange-100 text-orange-800',
      transformative: 'bg-red-100 text-red-800'
    };
    return colors[impact] || 'bg-gray-100 text-gray-800';
  };

  const verifyContribution = async () => {
    setVerifying(true);
    try {
      await contributionService.verifyContribution(contribution.id, {
        organization: 'Nimo Platform',
        verifier_name: user?.name || 'Community Verifier',
        comments: 'Verified by community member'
      });
      onVerified && onVerified();
    } catch (error) {
      console.error('Verification failed:', error);
    } finally {
      setVerifying(false);
    }
  };

  const showExplanation = async () => {
    try {
      const explanation = await contributionService.getContributionExplanation(contribution.id);
      onExplained && onExplained(explanation);
    } catch (error) {
      console.error('Failed to get explanation:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {contribution.title}
        </h3>
        <p className="text-gray-600 mb-3">{contribution.description}</p>

        <div className="flex flex-wrap gap-2 mb-3">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(contribution.contribution_type)}`}>
            {contribution.contribution_type}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(contribution.impact_level)}`}>
            {contribution.impact_level}
          </span>
        </div>

        {contribution.evidence && (
          <div className="mb-4">
            <p className="text-sm text-gray-500 mb-1">Evidence:</p>
            <a
              href={contribution.evidence.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {contribution.evidence.url}
            </a>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        {!contribution.verifications?.length && (
          <button
            onClick={verifyContribution}
            disabled={verifying}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {verifying ? 'Verifying...' : 'Verify'}
          </button>
        )}
        <button
          onClick={showExplanation}
          className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
        >
          Explain
        </button>
      </div>
    </div>
  );
};

export default ContributionCard;
```

#### Token Balance Component
```jsx
// src/components/TokenBalance.jsx
import { useState, useEffect } from 'react';
import { tokenService } from '../services/tokens';

const TokenBalance = () => {
  const [balance, setBalance] = useState(0);
  const [updatedAt, setUpdatedAt] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    setLoading(true);
    try {
      const data = await tokenService.getBalance();
      setBalance(data.balance);
      setUpdatedAt(data.updated_at);
    } catch (error) {
      console.error('Failed to load token balance:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="animate-pulse bg-gray-200 h-24 rounded"></div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Token Balance</h3>
        <div className="text-3xl font-bold text-blue-600">{balance} NIMO</div>
        {updatedAt && (
          <p className="text-sm text-gray-500 mt-1">
            Updated: {formatDate(updatedAt)}
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => {/* Show transactions */}}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          View Transactions
        </button>
        <button
          onClick={() => {/* Show transfer dialog */}}
          className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
        >
          Transfer
        </button>
      </div>
    </div>
  );
};

export default TokenBalance;
```

### Event Listening Setup

#### Blockchain Events Listener
```javascript
// src/hooks/useBlockchainEvents.js
import { useEffect, useRef } from 'react';
import { useWeb3 } from './useWeb3';
import { CONTRACT_ADDRESSES, NIMO_IDENTITY_ABI, NIMO_TOKEN_ABI } from '../constants/contracts';

export const useBlockchainEvents = (callback) => {
  const { publicClient } = useWeb3();
  const unwatchRef = useRef(null);

  const listenToIdentityEvents = () => {
    if (!publicClient) return;

    unwatchRef.current = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
      abi: NIMO_IDENTITY_ABI,
      eventName: 'IdentityCreated',
      onLogs: (logs) => {
        logs.forEach(log => {
          callback({
            type: 'identity_created',
            tokenId: log.args.tokenId,
            username: log.args.username,
            owner: log.args.owner,
            blockNumber: log.blockNumber,
            transactionHash: log.transactionHash
          });
        });
      }
    });
  };

  const listenToContributionEvents = () => {
    if (!publicClient) return;

    unwatchRef.current = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.NIMO_IDENTITY,
      abi: NIMO_IDENTITY_ABI,
      eventName: 'ContributionVerified',
      onLogs: (logs) => {
        logs.forEach(log => {
          callback({
            type: 'contribution_verified',
            contributionId: log.args.contributionId,
            verifier: log.args.verifier,
            tokensAwarded: log.args.tokensAwarded,
            blockNumber: log.blockNumber,
            transactionHash: log.transactionHash
          });
        });
      }
    });
  };

  const listenToTokenEvents = () => {
    if (!publicClient) return;

    unwatchRef.current = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESSES.NIMO_TOKEN,
      abi: NIMO_TOKEN_ABI,
      eventName: 'Transfer',
      onLogs: (logs) => {
        logs.forEach(log => {
          callback({
            type: 'token_transfer',
            from: log.args.from,
            to: log.args.to,
            value: log.args.value,
            blockNumber: log.blockNumber,
            transactionHash: log.transactionHash
          });
        });
      }
    });
  };

  useEffect(() => {
    listenToIdentityEvents();
    listenToContributionEvents();
    listenToTokenEvents();

    return () => {
      if (unwatchRef.current) {
        unwatchRef.current();
      }
    };
  }, [publicClient, callback]);

  return {
    listenToIdentityEvents,
    listenToContributionEvents,
    listenToTokenEvents
  };
};
```

### Error Handling & Loading States

#### Global Error Handler
```javascript
// src/hooks/useErrorHandler.js
import { useState } from 'react';

export const useErrorHandler = () => {
  const [error, setError] = useState(null);

  const handleApiError = (error) => {
    let message = 'An unexpected error occurred';

    if (error.response) {
      message = error.response.data?.error || `Server error: ${error.response.status}`;
    } else if (error.request) {
      message = 'Network error - please check your connection';
    } else {
      message = error.message || 'An unexpected error occurred';
    }

    setError(message);
    console.error('API Error:', error);

    // Auto-clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const handleBlockchainError = (error) => {
    let message = 'Blockchain transaction failed';

    if (error.message.includes('User denied transaction')) {
      message = 'Transaction was cancelled by user';
    } else if (error.message.includes('insufficient funds')) {
      message = 'Insufficient funds to complete transaction';
    } else if (error.message.includes('Username already exists')) {
      message = 'This username is already taken';
    }

    setError(message);
    console.error('Blockchain Error:', error);

    // Auto-clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const clearError = () => setError(null);

  return {
    error,
    handleApiError,
    handleBlockchainError,
    clearError
  };
};
```

---

## 4. Authentication Flows

### Login Flow
```jsx
// src/components/AuthModal.jsx
import { useState } from 'react';
import { authService } from '../services/auth';
import { useUser } from '../contexts/UserContext';
import { useErrorHandler } from '../hooks/useErrorHandler';

const AuthModal = ({ isOpen, onClose, activeTab, setActiveTab, onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    name: '',
    location: '',
    bio: '',
    skills: []
  });

  const { login } = useUser();
  const { error, handleApiError } = useErrorHandler();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await authService.login(credentials);
      login(result.user, result.token);
      onLogin(result.user);
      onClose();
    } catch (error) {
      handleApiError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authService.register(registerData);
      // After successful registration, switch to login
      setActiveTab('login');
      setCredentials({
        email: registerData.email,
        password: registerData.password
      });
    } catch (error) {
      handleApiError(error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">
            {activeTab === 'login' ? 'Login' : 'Register'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <div className="flex mb-6">
          <button
            onClick={() => setActiveTab('login')}
            className={`flex-1 py-2 px-4 rounded-l ${
              activeTab === 'login'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setActiveTab('register')}
            className={`flex-1 py-2 px-4 rounded-r ${
              activeTab === 'register'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {activeTab === 'login' ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={credentials.email}
                onChange={(e) => setCredentials({...credentials, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                value={registerData.name}
                onChange={(e) => setRegisterData({...registerData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={registerData.email}
                onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location (Optional)
              </label>
              <input
                type="text"
                value={registerData.location}
                onChange={(e) => setRegisterData({...registerData, location: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Registering...' : 'Register'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default AuthModal;
```

### Protected Route Guard
```javascript
// src/components/ProtectedRoute.jsx
import { useUser } from '../contexts/UserContext';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const { user } = useUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

---

## 5. Contribution Submission Process

### Create Contribution Flow
```jsx
// src/components/ContributionForm.jsx
import { useState } from 'react';
import { contributionService } from '../services/contributions';
import { useErrorHandler } from '../hooks/useErrorHandler';

const ContributionForm = ({ onSubmitted }) => {
  const [submitting, setSubmitting] = useState(false);
  const [contribution, setContribution] = useState({
    title: '',
    description: '',
    type: '',
    impact: '',
    evidence: {
      url: '',
      type: 'url'
    }
  });

  const { error, handleApiError } = useErrorHandler();

  const contributionTypes = [
    'coding',
    'education',
    'volunteer',
    'activism',
    'leadership',
    'entrepreneurship',
    'environmental',
    'community',
    'other'
  ];

  const impactLevels = [
    'minimal',
    'moderate',
    'significant',
    'transformative'
  ];

  const isValidUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (contribution.evidence.url && !isValidUrl(contribution.evidence.url)) {
      handleApiError({ message: 'Please enter a valid URL for evidence' });
      return;
    }

    setSubmitting(true);

    try {
      const result = await contributionService.createContribution(contribution);
      onSubmitted && onSubmitted(result);
      // Reset form
      setContribution({
        title: '',
        description: '',
        type: '',
        impact: '',
        evidence: {
          url: '',
          type: 'url'
        }
      });
    } catch (error) {
      handleApiError(error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">
        Submit Contribution
      </h3>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            value={contribution.title}
            onChange={(e) => setContribution({...contribution, title: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            minLength={3}
            maxLength={200}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={contribution.description}
            onChange={(e) => setContribution({...contribution, description: e.target.value})}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={2000}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contribution Type *
            </label>
            <select
              value={contribution.type}
              onChange={(e) => setContribution({...contribution, type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select type</option>
              {contributionTypes.map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Impact Level *
            </label>
            <select
              value={contribution.impact}
              onChange={(e) => setContribution({...contribution, impact: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select impact</option>
              {impactLevels.map(level => (
                <option key={level} value={level}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Evidence URL
          </label>
          <input
            type="url"
            value={contribution.evidence.url}
            onChange={(e) => setContribution({
              ...contribution,
              evidence: { ...contribution.evidence, url: e.target.value }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://github.com/user/repo/pull/123"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Submitting...' : 'Submit Contribution'}
        </button>
      </form>
    </div>
  );
};

export default ContributionForm;
```

---

## 6. Token Balance & Transaction Monitoring

### Real-time Token Balance Updates
```javascript
// src/hooks/useTokenBalance.js
import { useState, useEffect } from 'react';
import { tokenService } from '../services/tokens';
import { useBlockchainEvents } from './useBlockchainEvents';

export const useTokenBalance = (userAddress) => {
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(false);

  const loadBalance = async () => {
    setLoading(true);
    try {
      const data = await tokenService.getBalance();
      setBalance(data.balance);
    } catch (error) {
      console.error('Failed to load balance:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockchainEvent = (event) => {
    if (event.type === 'token_transfer') {
      // Check if this affects the user's balance
      if (event.to === userAddress || event.from === userAddress) {
        loadBalance(); // Refresh balance
      }
    }
  };

  useBlockchainEvents(handleBlockchainEvent);

  useEffect(() => {
    loadBalance();
  }, [userAddress]);

  return {
    balance,
    loading,
    refresh: loadBalance
  };
};
```

### Transaction History Component
```jsx
// src/components/TransactionHistory.jsx
import { useState, useEffect } from 'react';
import { tokenService } from '../services/tokens';

const TransactionHistory = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const data = await tokenService.getTransactions();
      setTransactions(data.transactions);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="animate-pulse bg-gray-200 h-64 rounded"></div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">
        Transaction History
      </h3>

      {transactions.length === 0 ? (
        <p className="text-gray-500 text-center py-8">
          No transactions found
        </p>
      ) : (
        <div className="space-y-4">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  transaction.type === 'credit'
                    ? 'bg-green-100 text-green-600'
                    : 'bg-red-100 text-red-600'
                }`}>
                  {transaction.type === 'credit' ? '↓' : '↑'}
                </div>
                <div>
                  <p className="font-medium text-gray-900">
                    {transaction.description}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatDate(transaction.created_at)}
                  </p>
                </div>
              </div>

              <div className={`font-semibold ${
                transaction.type === 'credit'
                  ? 'text-green-600'
                  : 'text-red-600'
              }`}>
                {transaction.type === 'credit' ? '+' : '-'}{transaction.amount} NIMO
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TransactionHistory;
```

---

## 7. Integration Checklist

### Backend Integration
- [ ] Set up Axios instance with base URL and interceptors
- [ ] Implement authentication service (login, register, logout)
- [ ] Create contribution service (CRUD operations)
- [ ] Set up token service (balance, transactions, transfers)
- [ ] Add error handling for API calls
- [ ] Implement loading states for async operations

### Blockchain Integration
- [ ] Configure Web3 providers (viem, ethers)
- [ ] Set up contract ABIs and addresses
- [ ] Implement contract read functions
- [ ] Add contract write functions with gas estimation
- [ ] Set up event listeners for real-time updates
- [ ] Add error handling for blockchain operations

### UI Components
- [ ] Create login/register forms
- [ ] Build contribution list and detail views
- [ ] Implement contribution creation form
- [ ] Add token balance display
- [ ] Create transaction history view
- [ ] Set up loading states and error messages

### State Management
- [ ] Set up React Context API for authentication
- [ ] Add contribution state management
- [ ] Implement token balance state
- [ ] Add global error handling

### Routing & Guards
- [ ] Set up protected routes with React Router
- [ ] Add authentication guards
- [ ] Implement route-based loading

### Testing
- [ ] Test API integration
- [ ] Test blockchain connectivity
- [ ] Verify authentication flows
- [ ] Test contribution workflows
- [ ] Validate token operations

---

## 8. Deployment & Production Considerations

### Environment Variables
```javascript
// .env
VITE_API_BASE_URL=https://api.nimo-platform.com/api
VITE_CONTRACT_ADDRESS_IDENTITY=0x...
VITE_CONTRACT_ADDRESS_TOKEN=0x...
VITE_NETWORK_RPC=https://goerli.base.org
VITE_NETWORK_CHAIN_ID=84531
```

### Build Configuration
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version)
  }
});
```

### Production Optimizations
- Enable gzip compression
- Implement code splitting
- Add service worker for caching
- Set up error monitoring (Sentry)
- Configure analytics

---

## 9. Common Issues & Solutions

### CORS Issues
```javascript
// Backend Flask-CORS setup
from flask_cors import CORS
CORS(app, origins=["http://localhost:5173", "https://nimo-platform.com"])
```

### Web3 Connection Issues
```javascript
// Check if wallet is connected
const isWalletConnected = async () => {
  if (!window.ethereum) return false;
  try {
    const accounts = await window.ethereum.request({ method: 'eth_accounts' });
    return accounts.length > 0;
  } catch {
    return false;
  }
};
```

### Token Expiration Handling
```javascript
// Automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      // Attempt to refresh token
      const newToken = await refreshToken();
      if (newToken) {
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return api(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

---

*This guide provides everything needed for frontend developers to integrate with the Nimo Platform. Follow the checklist above and refer to the code examples for implementation details.*

**Last Updated:** August 27, 2025  
**Version:** 2.0.0  
**Authors:** Backend Team, Frontend Team  
**Framework:** React 19.1.1 + Vite + Tailwind CSS

---

## 7. Integration Checklist

### Backend Integration
- [ ] Set up Axios instance with base URL and interceptors
- [ ] Implement authentication service (login, register, logout)
- [ ] Create contribution service (CRUD operations)
- [ ] Set up token service (balance, transactions, transfers)
- [ ] Add error handling for API calls
- [ ] Implement loading states for async operations

### Blockchain Integration
- [ ] Configure Web3 providers (viem, ethers)
- [ ] Set up contract ABIs and addresses
- [ ] Implement contract read functions
- [ ] Add contract write functions with gas estimation
- [ ] Set up event listeners for real-time updates
- [ ] Add error handling for blockchain operations

### UI Components
- [ ] Create login/register forms
- [ ] Build contribution list and detail views
- [ ] Implement contribution creation form
- [ ] Add token balance display
- [ ] Create transaction history view
- [ ] Set up loading states and error messages

### State Management
- [ ] Set up React Context API for authentication
- [ ] Add contribution state management
- [ ] Implement token balance state
- [ ] Add global error handling

### Routing & Guards
- [ ] Set up protected routes
- [ ] Add authentication guards
- [ ] Implement route-based loading

### Testing
- [ ] Test API integration
- [ ] Test blockchain connectivity
- [ ] Verify authentication flows
- [ ] Test contribution workflows
- [ ] Validate token operations

---

## 8. Deployment & Production Considerations

### Environment Variables
```javascript
// .env
VITE_API_BASE_URL=https://api.nimo-platform.com/api
VITE_CONTRACT_ADDRESS_IDENTITY=0x...
VITE_CONTRACT_ADDRESS_TOKEN=0x...
VITE_NETWORK_RPC=https://goerli.base.org
VITE_NETWORK_CHAIN_ID=84531
```

### Build Configuration
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version)
  }
});
```

### Production Optimizations
- Enable gzip compression
- Implement code splitting
- Add service worker for caching
- Set up error monitoring (Sentry)
- Configure analytics

---

## 9. Common Issues & Solutions

### CORS Issues
```javascript
// Backend Flask-CORS setup
from flask_cors import CORS
CORS(app, origins=["http://localhost:5173", "https://nimo-platform.com"])
```

### Web3 Connection Issues
```javascript
// Check if wallet is connected
const isWalletConnected = async () => {
  if (!window.ethereum) return false;
  try {
    const accounts = await window.ethereum.request({ method: 'eth_accounts' });
    return accounts.length > 0;
  } catch {
    return false;
  }
};
```

### Token Expiration Handling
```javascript
// Automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      // Attempt to refresh token
      const newToken = await refreshToken();
      if (newToken) {
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return api(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

---

*This guide provides everything needed for frontend developers to integrate with the Nimo Platform. Follow the checklist above and refer to the code examples for implementation details.*

**Last Updated:** December 2024  
**Version:** 2.1.0  
**Authors:** Backend Team, Frontend Team  
**Framework:** React 19.1.1 + Vite + Tailwind CSS</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\docs\frontend_integration_guide.md