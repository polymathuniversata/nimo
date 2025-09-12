# Web3 Wallet Integration Improvements
**Enhancing the Frontend Web3 Experience: August 25, 2025**

## Current Implementation

Our current wallet integration provides basic functionality with:
- MetaMask connection
- Base network detection
- Balance display
- Basic transaction handling

However, there are several areas for improvement to provide a better user experience and handle more complex Web3 interactions.

## Planned Enhancements

### 1. Multi-Wallet Support

Currently, our implementation mainly focuses on MetaMask. We should expand to support:

```javascript
// wallet.js store
import { defineStore } from 'pinia'
import { ethers } from 'ethers'
import WalletConnectProvider from '@walletconnect/web3-provider'
import CoinbaseWalletSDK from '@coinbase/wallet-sdk'

export const useWalletStore = defineStore('wallet', () => {
  // ... existing code ...

  // New wallet providers
  const walletConnectProvider = ref(null)
  const coinbaseWalletProvider = ref(null)
  
  // Add support for additional wallets
  const connectWalletConnect = async () => {
    try {
      walletConnectProvider.value = new WalletConnectProvider({
        rpc: {
          84532: BASE_NETWORKS[BASE_SEPOLIA_CHAIN_ID].rpcUrls[0],
          8453: BASE_NETWORKS[BASE_MAINNET_CHAIN_ID].rpcUrls[0],
        },
      })
      
      await walletConnectProvider.value.enable()
      provider.value = new ethers.providers.Web3Provider(walletConnectProvider.value)
      
      // Remaining connection logic similar to connectWallet()
      // ...
    } catch (err) {
      setError(err)
      return false
    }
  }
  
  const connectCoinbaseWallet = async () => {
    try {
      const coinbaseWallet = new CoinbaseWalletSDK({
        appName: "Nimo",
        appLogoUrl: "/logo.png",
      })
      
      coinbaseWalletProvider.value = coinbaseWallet.makeWeb3Provider(
        BASE_NETWORKS[BASE_SEPOLIA_CHAIN_ID].rpcUrls[0], 
        84532
      )
      
      provider.value = new ethers.providers.Web3Provider(coinbaseWalletProvider.value)
      
      // Remaining connection logic
      // ...
    } catch (err) {
      setError(err)
      return false
    }
  }
  
  return {
    // ... existing returns ...
    connectWalletConnect,
    connectCoinbaseWallet,
  }
})
```

### 2. Improved Transaction Management

We should enhance our transaction handling with:

```javascript
// Add to wallet.js store
const pendingTransactions = ref([])
const transactionHistory = ref([])

// Enhanced transaction tracking
const sendTransaction = async (to, value, data = '0x', options = {}) => {
  if (!signer.value) {
    setError('No signer available. Please connect your wallet.')
    return null
  }

  try {
    const transaction = {
      to,
      value: ethers.utils.parseEther(value.toString()),
      data,
      ...options
    }

    // Add gas estimation
    if (!transaction.gasLimit) {
      const estimatedGas = await provider.value.estimateGas(transaction)
      transaction.gasLimit = estimatedGas.mul(12).div(10) // Add 20% buffer
    }

    // Create transaction tracking object
    const txTracker = {
      id: `tx-${Date.now()}`,
      to,
      value,
      status: 'pending',
      hash: null,
      receipt: null,
      createdAt: new Date(),
      confirmations: 0,
      error: null
    }
    
    pendingTransactions.value.push(txTracker)

    // Send transaction
    const tx = await signer.value.sendTransaction(transaction)
    txTracker.hash = tx.hash
    
    // Wait for transaction
    const receipt = await tx.wait()
    txTracker.receipt = receipt
    txTracker.status = 'confirmed'
    txTracker.confirmations = 1
    
    // Move to history
    transactionHistory.value.push({
      ...txTracker,
      completedAt: new Date()
    })
    pendingTransactions.value = pendingTransactions.value.filter(t => t.id !== txTracker.id)
    
    return receipt
  } catch (err) {
    const failedTx = pendingTransactions.value.find(t => t.to === to && t.value === value)
    if (failedTx) {
      failedTx.status = 'failed'
      failedTx.error = err.message
      
      // Move to history
      transactionHistory.value.push({
        ...failedTx,
        completedAt: new Date()
      })
      pendingTransactions.value = pendingTransactions.value.filter(t => t.id !== failedTx.id)
    }
    
    setError(err)
    return null
  }
}
```

### 3. Transaction UI Components

Create reusable transaction UI components:

```vue
<!-- components/web3/TransactionManager.vue -->
<template>
  <div class="transaction-manager">
    <!-- Pending Transactions -->
    <div v-if="pendingTransactions.length > 0" class="pending-transactions">
      <div class="text-subtitle1">Pending Transactions</div>
      
      <q-list separator>
        <q-item v-for="tx in pendingTransactions" :key="tx.id" class="transaction-item">
          <q-item-section avatar>
            <q-spinner color="primary" />
          </q-item-section>
          
          <q-item-section>
            <q-item-label>{{ getTransactionType(tx) }}</q-item-label>
            <q-item-label caption>{{ formatAmount(tx.value) }} ETH</q-item-label>
          </q-item-section>
          
          <q-item-section side>
            <q-btn
              flat
              round
              color="primary"
              icon="open_in_new"
              size="sm"
              :href="getExplorerLink(tx.hash)"
              target="_blank"
              v-if="tx.hash"
            />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
    
    <!-- Transaction History -->
    <div v-if="recentTransactions.length > 0" class="transaction-history">
      <div class="text-subtitle1">Recent Transactions</div>
      
      <q-list separator>
        <q-item 
          v-for="tx in recentTransactions" 
          :key="tx.id" 
          class="transaction-item"
          :class="tx.status"
        >
          <q-item-section avatar>
            <q-icon 
              :name="getStatusIcon(tx.status)" 
              :color="getStatusColor(tx.status)" 
            />
          </q-item-section>
          
          <q-item-section>
            <q-item-label>{{ getTransactionType(tx) }}</q-item-label>
            <q-item-label caption>
              {{ formatAmount(tx.value) }} ETH
              <span class="transaction-time">
                {{ formatTime(tx.completedAt) }}
              </span>
            </q-item-label>
          </q-item-section>
          
          <q-item-section side>
            <q-btn
              flat
              round
              color="primary"
              icon="open_in_new"
              size="sm"
              :href="getExplorerLink(tx.hash)"
              target="_blank"
              v-if="tx.hash"
            />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWalletStore } from 'src/stores/wallet'
import { format } from 'date-fns'

const walletStore = useWalletStore()

const pendingTransactions = computed(() => walletStore.pendingTransactions)
const recentTransactions = computed(() => {
  return walletStore.transactionHistory
    .slice()
    .sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))
    .slice(0, 5)
})

const getStatusIcon = (status) => {
  if (status === 'confirmed') return 'check_circle'
  if (status === 'failed') return 'error'
  return 'pending'
}

const getStatusColor = (status) => {
  if (status === 'confirmed') return 'positive'
  if (status === 'failed') return 'negative'
  return 'grey'
}

const formatAmount = (value) => {
  if (!value) return '0'
  return parseFloat(value).toFixed(4)
}

const formatTime = (date) => {
  if (!date) return ''
  return format(new Date(date), 'h:mm a')
}

const getExplorerLink = (hash) => {
  if (!hash) return ''
  const network = walletStore.BASE_NETWORKS[walletStore.chainId]
  if (!network || !network.blockExplorerUrls || network.blockExplorerUrls.length === 0) {
    return ''
  }
  return `${network.blockExplorerUrls[0]}/tx/${hash}`
}

const getTransactionType = (tx) => {
  // This would be enhanced to detect contract interactions, token transfers, etc.
  return 'Transfer'
}
</script>
```

### 4. Contract Interaction Utilities

Create a reusable contract interaction service:

```javascript
// services/contract.service.js
import { ethers } from 'ethers'
import { useWalletStore } from 'src/stores/wallet'

// Import ABIs
import NimoIdentityABI from 'src/contracts/NimoIdentity.json'
import NimoTokenABI from 'src/contracts/NimoToken.json'

// Contract addresses - these would be pulled from environment variables
const CONTRACT_ADDRESSES = {
  sepolia: {
    NimoIdentity: '0x...',
    NimoToken: '0x...'
  },
  mainnet: {
    NimoIdentity: '0x...',
    NimoToken: '0x...'
  }
}

class ContractService {
  constructor() {
    this.walletStore = useWalletStore()
    this.contracts = {}
  }
  
  getNetworkType() {
    if (this.walletStore.chainId === this.walletStore.BASE_SEPOLIA_CHAIN_ID) {
      return 'sepolia'
    }
    if (this.walletStore.chainId === this.walletStore.BASE_MAINNET_CHAIN_ID) {
      return 'mainnet'
    }
    return null
  }
  
  async getIdentityContract() {
    const networkType = this.getNetworkType()
    
    if (!networkType) {
      throw new Error('Not connected to a supported network')
    }
    
    if (!this.contracts.identity) {
      const address = CONTRACT_ADDRESSES[networkType].NimoIdentity
      this.contracts.identity = new ethers.Contract(
        address,
        NimoIdentityABI,
        this.walletStore.signer || this.walletStore.provider
      )
    }
    
    return this.contracts.identity
  }
  
  async getTokenContract() {
    const networkType = this.getNetworkType()
    
    if (!networkType) {
      throw new Error('Not connected to a supported network')
    }
    
    if (!this.contracts.token) {
      const address = CONTRACT_ADDRESSES[networkType].NimoToken
      this.contracts.token = new ethers.Contract(
        address,
        NimoTokenABI,
        this.walletStore.signer || this.walletStore.provider
      )
    }
    
    return this.contracts.token
  }
  
  async createIdentity(username, metadataURI) {
    try {
      const contract = await this.getIdentityContract()
      
      if (!this.walletStore.signer) {
        throw new Error('No signer available. Please connect your wallet.')
      }
      
      const tx = await contract.connect(this.walletStore.signer).createIdentity(
        username,
        metadataURI
      )
      
      const receipt = await tx.wait()
      return receipt
    } catch (error) {
      console.error('Error creating identity:', error)
      throw error
    }
  }
  
  async getUserIdentity(address) {
    try {
      const contract = await this.getIdentityContract()
      const identity = await contract.identities(address || this.walletStore.account)
      return identity
    } catch (error) {
      console.error('Error getting user identity:', error)
      throw error
    }
  }
  
  async addContribution(contributionType, description, evidenceURI) {
    try {
      const contract = await this.getIdentityContract()
      
      if (!this.walletStore.signer) {
        throw new Error('No signer available. Please connect your wallet.')
      }
      
      const tx = await contract.connect(this.walletStore.signer).addContribution(
        contributionType,
        description,
        evidenceURI,
        '0x' // MeTTa hash placeholder
      )
      
      const receipt = await tx.wait()
      return receipt
    } catch (error) {
      console.error('Error adding contribution:', error)
      throw error
    }
  }
  
  // Additional contract methods would be added here
}

export default new ContractService()
```

### 5. Error Handling & Recovery

Improve error handling for Web3 interactions:

```javascript
// Add to wallet.js store
const handleWeb3Error = (error) => {
  // Extract useful information from Web3 errors
  let errorMessage = 'Unknown error'
  
  if (error.code) {
    // MetaMask error codes
    switch (error.code) {
      case 4001:
        errorMessage = 'Transaction rejected by user'
        break
      case -32602:
        errorMessage = 'Invalid transaction parameters'
        break
      case -32603:
        errorMessage = 'Internal error in the wallet'
        break
      default:
        errorMessage = error.message || 'Transaction failed'
    }
  } else if (error.reason) {
    // Contract reversion errors
    errorMessage = `Contract error: ${error.reason}`
  }
  
  // Handle common scenarios
  if (error.message && error.message.includes('insufficient funds')) {
    errorMessage = 'Insufficient ETH for transaction'
  }
  
  setError(errorMessage)
  
  // Return categorized error for UI handling
  return {
    type: error.code === 4001 ? 'user_rejected' : 'transaction_error',
    message: errorMessage,
    originalError: error
  }
}
```

### 6. Chain ID Management

Improve chain ID management with:

```javascript
// Add to wallet.js store
const SUPPORTED_CHAIN_IDS = [
  BASE_SEPOLIA_CHAIN_ID,
  BASE_MAINNET_CHAIN_ID,
  // Add any other supported networks
]

const isChainSupported = (chainId) => {
  return SUPPORTED_CHAIN_IDS.includes(chainId)
}

// Enhanced network switching
const switchNetwork = async (targetChainId) => {
  if (!SUPPORTED_CHAIN_IDS.includes(targetChainId)) {
    setError('Network not supported')
    return false
  }
  
  try {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: targetChainId }],
    })
    
    chainId.value = targetChainId
    await updateBalance()
    return true
  } catch (switchError) {
    // Handle chain not added to MetaMask
    if (switchError.code === 4902) {
      try {
        const networkConfig = BASE_NETWORKS[targetChainId]
        if (!networkConfig) {
          throw new Error('Network configuration not found')
        }
        
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [networkConfig],
        })
        
        chainId.value = targetChainId
        await updateBalance()
        return true
      } catch (addError) {
        setError(`Failed to add network: ${addError.message}`)
        return false
      }
    } else {
      setError(`Failed to switch network: ${switchError.message}`)
      return false
    }
  }
}
```

### 7. ENS Name Resolution

Add support for ENS name resolution:

```javascript
// Add to wallet.js store
const ensName = ref(null)

const lookupEnsName = async (address) => {
  if (!provider.value || !address) return null
  
  try {
    // Try to resolve ENS name
    const name = await provider.value.lookupAddress(address)
    ensName.value = name
    return name
  } catch (error) {
    console.warn('ENS lookup failed:', error)
    ensName.value = null
    return null
  }
}

// Enhanced connect method
const connectWallet = async () => {
  // ... existing connect code ...
  
  if (account.value) {
    // Try to resolve ENS name after connection
    await lookupEnsName(account.value)
  }
  
  // ... continue with existing code ...
}
```

## Implementation Plan

### 1. Core Wallet Improvements (Week 1)
- [ ] Implement multi-wallet support
- [ ] Enhance transaction management
- [ ] Improve error handling

### 2. Contract Interaction Layer (Week 1)
- [ ] Create contract service
- [ ] Add identity contract integration
- [ ] Add token contract integration

### 3. User Experience Enhancements (Week 2)
- [ ] Implement transaction UI components
- [ ] Add ENS name resolution
- [ ] Create wallet selection modal

### 4. Testing & Documentation (Week 2)
- [ ] Test on multiple browsers and wallets
- [ ] Document wallet integration patterns
- [ ] Create examples for common interactions

## Compatibility Testing

We should test with the following combinations:

- **Browsers**: Chrome, Firefox, Safari, Edge
- **Wallets**: MetaMask, WalletConnect, Coinbase Wallet
- **Devices**: Desktop, Mobile
- **Networks**: Base Sepolia Testnet, Base Mainnet

## Security Considerations

1. **Private Key Handling**: Never request or store private keys
2. **Transaction Verification**: Always confirm transaction parameters before sending
3. **Error Prevention**: Validate all inputs before sending to blockchain
4. **Network Validation**: Always verify the connected network
5. **Signature Requests**: Provide clear descriptions for signature requests

This plan will significantly improve our Web3 wallet integration, providing a better user experience and more robust blockchain interactions.