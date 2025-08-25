import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ethers } from 'ethers'

export const useWalletStore = defineStore('wallet', () => {
  // State
  const account = ref(null)
  const provider = ref(null)
  const signer = ref(null)
  const chainId = ref(null)
  const isConnecting = ref(false)
  const balance = ref('0')
  const error = ref(null)

  // Base network configuration
  const BASE_SEPOLIA_CHAIN_ID = '0x14a34' // 84532 in hex
  const BASE_MAINNET_CHAIN_ID = '0x2105' // 8453 in hex

  const BASE_NETWORKS = {
    [BASE_SEPOLIA_CHAIN_ID]: {
      chainId: BASE_SEPOLIA_CHAIN_ID,
      chainName: 'Base Sepolia',
      nativeCurrency: { name: 'Ethereum', symbol: 'ETH', decimals: 18 },
      rpcUrls: ['https://sepolia.base.org'],
      blockExplorerUrls: ['https://sepolia.basescan.org'],
    },
    [BASE_MAINNET_CHAIN_ID]: {
      chainId: BASE_MAINNET_CHAIN_ID,
      chainName: 'Base',
      nativeCurrency: { name: 'Ethereum', symbol: 'ETH', decimals: 18 },
      rpcUrls: ['https://mainnet.base.org'],
      blockExplorerUrls: ['https://basescan.org'],
    },
  }

  // Getters
  const isConnected = computed(() => !!account.value)
  const isOnCorrectNetwork = computed(() => {
    return chainId.value === BASE_SEPOLIA_CHAIN_ID || chainId.value === BASE_MAINNET_CHAIN_ID
  })
  const formattedAddress = computed(() => {
    if (!account.value) return ''
    return `${account.value.slice(0, 6)}...${account.value.slice(-4)}`
  })
  const networkName = computed(() => {
    const network = BASE_NETWORKS[chainId.value]
    return network ? network.chainName : 'Unknown Network'
  })

  // Actions
  const setError = (err) => {
    error.value = err?.message || err
    console.error('Wallet store error:', err)
  }

  const clearError = () => {
    error.value = null
  }

  const isMetaMaskInstalled = () => {
    return typeof window !== 'undefined' && window.ethereum && window.ethereum.isMetaMask
  }

  const connectWallet = async () => {
    if (!isMetaMaskInstalled()) {
      setError('MetaMask is not installed. Please install MetaMask to continue.')
      return false
    }

    try {
      isConnecting.value = true
      clearError()

      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      })

      if (accounts.length === 0) {
        setError('No accounts found. Please make sure MetaMask is unlocked.')
        return false
      }

      provider.value = new ethers.BrowserProvider(window.ethereum)
      signer.value = await provider.value.getSigner()
      account.value = accounts[0]

      const network = await provider.value.getNetwork()
      chainId.value = '0x' + network.chainId.toString(16)

      await updateBalance()
      await switchToBaseNetwork()

      return true
    } catch (err) {
      setError(err)
      return false
    } finally {
      isConnecting.value = false
    }
  }

  const disconnectWallet = () => {
    account.value = null
    provider.value = null
    signer.value = null
    chainId.value = null
    balance.value = '0'
    clearError()
  }

  const switchToBaseNetwork = async (useMainnet = false) => {
    if (!window.ethereum) return false

    const targetChainId = useMainnet ? BASE_MAINNET_CHAIN_ID : BASE_SEPOLIA_CHAIN_ID
    const targetNetwork = BASE_NETWORKS[targetChainId]

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: targetChainId }],
      })

      chainId.value = targetChainId
      return true
    } catch (switchError) {
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

  const updateBalance = async () => {
    if (!provider.value || !account.value) {
      balance.value = '0'
      return
    }

    try {
      const balanceWei = await provider.value.getBalance(account.value)
      balance.value = ethers.formatEther(balanceWei)
    } catch (err) {
      setError(err)
      balance.value = '0'
    }
  }

  const sendTransaction = async (to, value, data = '0x') => {
    if (!signer.value) {
      setError('No signer available. Please connect your wallet.')
      return null
    }

    try {
      const transaction = {
        to,
        value: ethers.parseEther(value.toString()),
        data,
      }

      const tx = await signer.value.sendTransaction(transaction)
      return tx
    } catch (err) {
      setError(err)
      return null
    }
  }

  const signMessage = async (message) => {
    if (!signer.value) {
      setError('No signer available. Please connect your wallet.')
      return null
    }

    try {
      const signature = await signer.value.signMessage(message)
      return signature
    } catch (err) {
      setError(err)
      return null
    }
  }

  // Initialize event listeners
  const setupEventListeners = () => {
    if (!window.ethereum) return

    window.ethereum.on('accountsChanged', async (accounts) => {
      if (accounts.length === 0) {
        disconnectWallet()
      } else {
        account.value = accounts[0]
        await updateBalance()
      }
    })

    window.ethereum.on('chainChanged', async (newChainId) => {
      chainId.value = newChainId
      await updateBalance()
    })
  }

  const removeEventListeners = () => {
    if (!window.ethereum) return

    window.ethereum.removeAllListeners('accountsChanged')
    window.ethereum.removeAllListeners('chainChanged')
  }

  const autoConnect = async () => {
    if (!isMetaMaskInstalled()) return

    try {
      const accounts = await window.ethereum.request({ method: 'eth_accounts' })
      if (accounts.length > 0) {
        await connectWallet()
      }
    } catch (err) {
      console.warn('Auto-connect failed:', err)
    }
  }

  return {
    // State
    account,
    provider,
    signer,
    chainId,
    isConnecting,
    balance,
    error,

    // Getters
    isConnected,
    isOnCorrectNetwork,
    formattedAddress,
    networkName,

    // Actions
    connectWallet,
    disconnectWallet,
    switchToBaseNetwork,
    updateBalance,
    sendTransaction,
    signMessage,
    setupEventListeners,
    removeEventListeners,
    autoConnect,
    isMetaMaskInstalled,
    setError,
    clearError,

    // Constants
    BASE_SEPOLIA_CHAIN_ID,
    BASE_MAINNET_CHAIN_ID,
    BASE_NETWORKS,
  }
})