import { useState, useEffect, useCallback } from 'react';
import { web3Service, WalletConnection, SignatureData, CURRENT_NETWORK } from '@/lib/web3';
import { useToast } from '@/hooks/use-toast';

export interface WalletState {
  isConnected: boolean;
  address: string | null;
  chainId: string | null;
  networkName: string | null;
  isLoading: boolean;
  error: string | null;
}

export const useWallet = () => {
  const { toast } = useToast();
  const [state, setState] = useState<WalletState>({
    isConnected: false,
    address: null,
    chainId: null,
    networkName: null,
    isLoading: false,
    error: null,
  });

  const updateState = (updates: Partial<WalletState>) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  const setError = (error: string | null) => {
    updateState({ error, isLoading: false });
  };

  const clearError = () => {
    updateState({ error: null });
  };

  /**
   * Connect wallet
   */
  const connectWallet = useCallback(async (): Promise<WalletConnection | null> => {
    if (!web3Service.isMetaMaskInstalled()) {
      const errorMsg = 'MetaMask is not installed. Please install MetaMask to continue.';
      setError(errorMsg);
      toast({
        title: "MetaMask Not Found",
        description: errorMsg,
        variant: "destructive",
      });
      return null;
    }

    updateState({ isLoading: true, error: null });

    try {
      const connection = await web3Service.connectWallet();
      
      // Get network info
      const networkInfo = await web3Service.getNetworkInfo();
      
      updateState({
        isConnected: true,
        address: connection.address,
        chainId: connection.chainId,
        networkName: networkInfo?.name || 'Unknown',
        isLoading: false,
        error: null,
      });

      toast({
        title: "Wallet Connected",
        description: `Connected to ${connection.address.slice(0, 6)}...${connection.address.slice(-4)}`,
      });

      return connection;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to connect wallet';
      setError(errorMessage);
      toast({
        title: "Connection Failed",
        description: errorMessage,
        variant: "destructive",
      });
      return null;
    }
  }, [toast]);

  /**
   * Disconnect wallet
   */
  const disconnectWallet = useCallback(() => {
    web3Service.disconnect();
    updateState({
      isConnected: false,
      address: null,
      chainId: null,
      networkName: null,
      isLoading: false,
      error: null,
    });

    toast({
      title: "Wallet Disconnected",
      description: "Your wallet has been disconnected.",
    });
  }, [toast]);

  /**
   * Sign authentication message
   */
  const signMessage = useCallback(async (): Promise<SignatureData | null> => {
    if (!state.address) {
      setError('No wallet connected');
      return null;
    }

    updateState({ isLoading: true, error: null });

    try {
      const signatureData = await web3Service.signAuthMessage(state.address);
      updateState({ isLoading: false });
      return signatureData;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to sign message';
      setError(errorMessage);
      toast({
        title: "Signing Failed",
        description: errorMessage,
        variant: "destructive",
      });
      return null;
    }
  }, [state.address, toast]);

  /**
   * Switch to Base network
   */
  const switchToBaseNetwork = useCallback(async (): Promise<boolean> => {
    updateState({ isLoading: true, error: null });

    try {
      await web3Service.switchToBaseNetwork();
      
      // Update network info
      const networkInfo = await web3Service.getNetworkInfo();
      updateState({
        chainId: networkInfo?.chainId || null,
        networkName: networkInfo?.name || null,
        isLoading: false,
      });

      toast({
        title: "Network Switched",
        description: `Switched to ${networkInfo?.name || 'Base Network'}`,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to switch network';
      setError(errorMessage);
      toast({
        title: "Network Switch Failed",
        description: errorMessage,
        variant: "destructive",
      });
      return false;
    }
  }, [toast]);

  /**
   * Check if on correct network
   */
  const isOnCorrectNetwork = useCallback((): boolean => {
    return state.chainId === CURRENT_NETWORK.chainId;
  }, [state.chainId]);

  /**
   * Check initial wallet connection
   */
  const checkConnection = useCallback(async () => {
    if (!web3Service.isMetaMaskInstalled()) return;

    updateState({ isLoading: true });

    try {
      const isConnected = await web3Service.isWalletConnected();
      
      if (isConnected) {
        const address = await web3Service.getCurrentAddress();
        const networkInfo = await web3Service.getNetworkInfo();
        
        updateState({
          isConnected: !!address,
          address,
          chainId: networkInfo?.chainId || null,
          networkName: networkInfo?.name || null,
          isLoading: false,
        });
      } else {
        updateState({ isLoading: false });
      }
    } catch (error) {
      console.error('Failed to check wallet connection:', error);
      updateState({ isLoading: false });
    }
  }, []);

  /**
   * Setup event listeners
   */
  useEffect(() => {
    const cleanup = [];

    // Listen for account changes
    const removeAccountsListener = web3Service.onAccountsChanged(async (accounts) => {
      if (accounts.length === 0) {
        // Disconnected
        disconnectWallet();
      } else {
        // Account changed
        const newAddress = accounts[0];
        const networkInfo = await web3Service.getNetworkInfo();
        
        updateState({
          isConnected: true,
          address: newAddress,
          chainId: networkInfo?.chainId || null,
          networkName: networkInfo?.name || null,
        });

        toast({
          title: "Account Changed",
          description: `Switched to ${newAddress.slice(0, 6)}...${newAddress.slice(-4)}`,
        });
      }
    });

    // Listen for network changes
    const removeChainListener = web3Service.onChainChanged(async (chainId) => {
      const networkInfo = await web3Service.getNetworkInfo();
      
      updateState({
        chainId,
        networkName: networkInfo?.name || 'Unknown',
      });

      if (chainId !== CURRENT_NETWORK.chainId) {
        toast({
          title: "Network Changed",
          description: `Switched to ${networkInfo?.name || 'Unknown Network'}. Please switch to Base network.`,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Network Changed",
          description: `Switched to ${networkInfo?.name || 'Base Network'}`,
        });
      }
    });

    cleanup.push(removeAccountsListener, removeChainListener);

    // Initial connection check
    checkConnection();

    // Cleanup on unmount
    return () => {
      cleanup.forEach(fn => fn());
    };
  }, [disconnectWallet, checkConnection, toast]);

  return {
    // State
    isConnected: state.isConnected,
    address: state.address,
    chainId: state.chainId,
    networkName: state.networkName,
    isLoading: state.isLoading,
    error: state.error,
    
    // Actions
    connectWallet,
    disconnectWallet,
    signMessage,
    switchToBaseNetwork,
    clearError,
    
    // Utils
    isOnCorrectNetwork,
    isMetaMaskInstalled: web3Service.isMetaMaskInstalled(),
  };
};