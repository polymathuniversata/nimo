import React, { createContext, useEffect, useState } from 'react';
import type { User, AuthState, LoginCredentials, RegisterData, KycData, KycStatus } from '../types/auth';
import { secureStorage } from '../lib/secureStorage';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  walletConnected: boolean;
  walletAddress?: string;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  connectWallet: (walletAddress: string) => Promise<void>;
  disconnectWallet: () => void;
  refreshUser: () => Promise<void>;
  updateKycStatus: (status: User['kycStatus']) => void;
  submitKyc: (kycData: KycData) => Promise<void>;
  getKycStatus: () => Promise<KycStatus>;
  checkEligibility: () => Promise<{ eligible: boolean; reason: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export { AuthContext };

// API base URL - should match your backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    walletConnected: false,
  });

  // Check for existing session on mount
  useEffect(() => {
    // Do not perform network auth checks in test environments or when explicitly skipped
    if (import.meta.env.VITE_SKIP_AUTH === 'true' || process.env.NODE_ENV === 'test') {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    const checkAuth = async () => {
      try {
        const token = secureStorage.getToken();
        if (token) {
          // Verify token with backend
          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const userData = await response.json();
            // Map backend fields to frontend interface
            const mappedUser: User = {
              id: userData.id?.toString() || '',
              email: userData.email || '',
              name: userData.name || '',
              walletAddress: userData.wallet_address,
              authMethod: userData.auth_method || 'traditional',
              isKycVerified: userData.kyc_status === 'approved',
              kycStatus: userData.kyc_status || 'not_started',
              reputationScore: 0, // TODO: Add to backend
              tokenBalance: userData.token_balance || 0,
              createdAt: userData.created_at || '',
              skills: userData.skills || [],
              location: userData.location,
              bio: userData.bio,
            };
            setAuthState({
              user: mappedUser,
              isAuthenticated: true,
              isLoading: false,
              walletConnected: !!mappedUser.walletAddress,
              walletAddress: mappedUser.walletAddress,
            });
          } else {
            // Token invalid, remove it
            secureStorage.removeToken();
            setAuthState(prev => ({ ...prev, isLoading: false }));
          }
        } else {
          setAuthState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setAuthState(prev => ({ ...prev, isLoading: false }));
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Login failed');
      }

      const data = await response.json();

      // Store token
      secureStorage.setToken(data.access_token);

      // Map backend user data to frontend interface
      const mappedUser: User = {
        id: data.user.id?.toString() || '',
        email: data.user.email || '',
        name: data.user.name || '',
        walletAddress: data.user.wallet_address,
        authMethod: data.user.auth_method || 'traditional',
        isKycVerified: data.user.kyc_status === 'approved',
        kycStatus: data.user.kyc_status || 'not_started',
        reputationScore: 0, // TODO: Add to backend
        tokenBalance: data.user.token_balance || 0,
        createdAt: data.user.created_at || '',
        skills: data.user.skills || [],
        location: data.user.location,
        bio: data.user.bio,
      };

      // Update state
      setAuthState({
        user: mappedUser,
        isAuthenticated: true,
        isLoading: false,
        walletConnected: !!mappedUser.walletAddress,
        walletAddress: mappedUser.walletAddress,
      });
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Registration failed');
      }

      const result = await response.json();

      // For wallet registration, user might need to complete additional steps
      if (data.authMethod === 'wallet') {
        setAuthState(prev => ({ ...prev, isLoading: false }));
        return result;
      }

      // For traditional registration, automatically log them in
      if (result.message === 'User registered successfully') {
        // Try to login immediately after registration
        await login({
          email: data.email,
          password: data.password,
          authMethod: 'traditional',
        });
      }
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const logout = () => {
    secureStorage.removeToken();
    setAuthState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      walletConnected: false,
    });
  };

  const connectWallet = async (walletAddress: string) => {
    setAuthState(prev => ({
      ...prev,
      walletConnected: true,
      walletAddress,
    }));
  };

  const disconnectWallet = () => {
    setAuthState(prev => ({
      ...prev,
      walletConnected: false,
      walletAddress: undefined,
    }));
  };

  const refreshUser = async () => {
    try {
      const token = secureStorage.getToken();
      if (token && authState.isAuthenticated) {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const userData = await response.json();
          // Map backend fields to frontend interface
          const mappedUser: User = {
            id: userData.id?.toString() || '',
            email: userData.email || '',
            name: userData.name || '',
            walletAddress: userData.wallet_address,
            authMethod: userData.auth_method || 'traditional',
            isKycVerified: userData.kyc_status === 'approved',
            kycStatus: userData.kyc_status || 'not_started',
            reputationScore: 0, // TODO: Add to backend
            tokenBalance: userData.token_balance || 0,
            createdAt: userData.created_at || '',
            skills: userData.skills || [],
            location: userData.location,
            bio: userData.bio,
          };
          setAuthState(prev => ({
            ...prev,
            user: mappedUser,
            walletConnected: !!mappedUser.walletAddress,
            walletAddress: mappedUser.walletAddress,
          }));
        }
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const updateKycStatus = (status: User['kycStatus']) => {
    if (authState.user) {
      setAuthState(prev => ({
        ...prev,
        user: {
          ...prev.user!,
          kycStatus: status,
          isKycVerified: status === 'approved',
        },
      }));
    }
  };

  const submitKyc = async (kycData: KycData) => {
    const token = secureStorage.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/kyc/submit`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(kycData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'KYC submission failed');
    }

    const result = await response.json();

    // Update local user state
    if (authState.user) {
      setAuthState(prev => ({
        ...prev,
        user: {
          ...prev.user!,
          kycStatus: 'in_review',
          isKycVerified: false,
        },
      }));
    }

    return result;
  };

  const getKycStatus = async (): Promise<KycStatus> => {
    const token = secureStorage.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/kyc/status`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get KYC status');
    }

    return await response.json();
  };

  const checkEligibility = async (): Promise<{ eligible: boolean; reason: string }> => {
    const token = secureStorage.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/kyc/eligibility`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to check eligibility');
    }

    return await response.json();
  };

  const contextValue: AuthContextType = {
    user: authState.user,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    walletConnected: authState.walletConnected,
    walletAddress: authState.walletAddress,
    login,
    register,
    logout,
    connectWallet,
    disconnectWallet,
    refreshUser,
    updateKycStatus,
    submitKyc,
    getKycStatus,
    checkEligibility,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}