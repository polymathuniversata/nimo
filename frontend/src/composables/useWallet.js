import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ethers } from 'ethers'

// Base network configuration
const BASE_SEPOLIA_CHAIN_ID = '0x14a34' // 84532 in hex
const BASE_MAINNET_CHAIN_ID = '0x2105' // 8453 in hex

const BASE_NETWORKS = {
  [BASE_SEPOLIA_CHAIN_ID]: {
    chainId: BASE_SEPOLIA_CHAIN_ID,
    chainName: 'Base Sepolia',
    nativeCurrency: {
      name: 'Ethereum',
      symbol: 'ETH',
      decimals: 18,
    },
    rpcUrls: ['https://sepolia.base.org'],
    blockExplorerUrls: ['https://sepolia.basescan.org'],
  },
  [BASE_MAINNET_CHAIN_ID]: {
    chainId: BASE_MAINNET_CHAIN_ID,
    chainName: 'Base',
    nativeCurrency: {
      name: 'Ethereum',
      symbol: 'ETH',
      decimals: 18,
    },
    rpcUrls: ['https://mainnet.base.org'],
    blockExplorerUrls: ['https://basescan.org'],
  },
}

// Reactive state
const account = ref(null)
const provider = ref(null)
const signer = ref(null)
const chainId = ref(null)
const isConnecting = ref(false)
const isConnected = computed(() => !!account.value)

// Error handling
const error = ref(null)
const setError = (err) => {
  error.value = err?.message || err
  console.error('Wallet error:', err)
}

// Check if MetaMask is installed
const isMetaMaskInstalled = () => {
  return typeof window !== 'undefined' && window.ethereum && window.ethereum.isMetaMask
}

// Connect to MetaMask wallet
const connectWallet = async () => {
  if (!isMetaMaskInstalled()) {
    setError('MetaMask is not installed. Please install MetaMask to continue.')
    return false
  }

  try {
    isConnecting.value = true
    error.value = null

    // Request account access
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts',
    })

    if (accounts.length === 0) {
      setError('No accounts found. Please make sure MetaMask is unlocked.')
      return false
    }

    // Set up provider and signer
    provider.value = new ethers.BrowserProvider(window.ethereum)
    signer.value = await provider.value.getSigner()
    account.value = accounts[0]

    // Get network info
    const network = await provider.value.getNetwork()
    chainId.value = '0x' + network.chainId.toString(16)

    // Switch to Base network if not already connected
    await switchToBaseNetwork()

    return true
  } catch (err) {
    setError(err)
    return false
  } finally {
    isConnecting.value = false
  }
}

// Switch to Base network
const switchToBaseNetwork = async (useMainnet = false) => {
  if (!window.ethereum) return false

  const targetChainId = useMainnet ? BASE_MAINNET_CHAIN_ID : BASE_SEPOLIA_CHAIN_ID
  const targetNetwork = BASE_NETWORKS[targetChainId]

  try {
    // Try to switch to the network
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: targetChainId }],
    })

    chainId.value = targetChainId
    return true
  } catch (switchError) {
    // Network not added to MetaMask, so add it
    if (switchError.code === 4902) {
      try {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [targetNetwork],
        })

        chainId.value = targetChainId
        return true
      } catch (addError) {
        setError(`Failed to add Base network: ${addError.message}`)
        return false
      }
    } else {
      setError(`Failed to switch to Base network: ${switchError.message}`)
      return false
    }
  }
}

// Disconnect wallet
const disconnectWallet = () => {
  account.value = null
  provider.value = null
  signer.value = null
  chainId.value = null
  error.value = null
}

// Format address for display
const formatAddress = (address) => {
  if (!address) return ''
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

// Get ETH balance
const getBalance = async () => {
  if (!provider.value || !account.value) return '0'

  try {
    const balance = await provider.value.getBalance(account.value)
    return ethers.formatEther(balance)
  } catch (err) {
    setError(err)
    return '0'
  }
}

// Check if we're on the correct network
const isOnCorrectNetwork = computed(() => {
  return chainId.value === BASE_SEPOLIA_CHAIN_ID || chainId.value === BASE_MAINNET_CHAIN_ID
})

// Listen for account and network changes
const setupEventListeners = () => {
  if (!window.ethereum) return

  window.ethereum.on('accountsChanged', (accounts) => {
    if (accounts.length === 0) {
      disconnectWallet()
    } else {
      account.value = accounts[0]
    }
  })

  window.ethereum.on('chainChanged', (newChainId) => {
    chainId.value = newChainId
    window.location.reload() // Reload on network change for simplicity
  })
}

// Remove event listeners
const removeEventListeners = () => {
  if (!window.ethereum) return

  window.ethereum.removeAllListeners('accountsChanged')
  window.ethereum.removeAllListeners('chainChanged')
}

// Auto-connect if previously connected
const autoConnect = async () => {
  if (!isMetaMaskInstalled()) return

  try {
    const accounts = await window.ethereum.request({
      method: 'eth_accounts',
    })

    if (accounts.length > 0) {
      await connectWallet()
    }
  } catch (err) {
    console.warn('Auto-connect failed:', err)
  }
}

// Composable hook
export const useWallet = () => {
  onMounted(() => {
    setupEventListeners()
    autoConnect()
  })

  onUnmounted(() => {
    removeEventListeners()
  })

  return {
    // State
    account: computed(() => account.value),
    provider: computed(() => provider.value),
    signer: computed(() => signer.value),
    chainId: computed(() => chainId.value),
    isConnected,
    isConnecting: computed(() => isConnecting.value),
    isOnCorrectNetwork,
    error: computed(() => error.value),

    // Methods
    connectWallet,
    disconnectWallet,
    switchToBaseNetwork,
    formatAddress,
    getBalance,
    isMetaMaskInstalled,

    // Utilities
    BASE_SEPOLIA_CHAIN_ID,
    BASE_MAINNET_CHAIN_ID,
    BASE_NETWORKS,
  }
}