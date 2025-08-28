import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  wallet_address?: string;
  did?: string;
  identity_verified?: boolean;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: {
    email?: string;
    password?: string;
    auth_method?: 'traditional' | 'wallet';
    wallet_address?: string;
    signature?: string;
    message?: string;
  }) => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    name: string;
    auth_method?: 'traditional' | 'wallet';
    wallet_address?: string;
    signature?: string;
    message?: string;
  }) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export { AuthContext, type AuthContextType };

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is already authenticated on app start
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      if (apiClient.isAuthenticated()) {
        // Try to get user data to verify token is still valid
        const userData = await apiClient.getCurrentUser();
        setUser(userData);
      }
    } catch (err) {
      // Token is invalid, clear it
      apiClient.logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: {
    email?: string;
    password?: string;
    auth_method?: 'traditional' | 'wallet';
    wallet_address?: string;
    signature?: string;
    message?: string;
  }) => {
    try {
      setIsLoading(true);
      setError(null);

      const authData = await apiClient.login(credentials);
      setUser(authData.user);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: {
    email: string;
    password: string;
    name: string;
    auth_method?: 'traditional' | 'wallet';
    wallet_address?: string;
    signature?: string;
    message?: string;
  }) => {
    try {
      setIsLoading(true);
      setError(null);

      const newUser = await apiClient.register(userData);
      setUser(newUser);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
    setError(null);
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    error,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};