import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, AuthContext } from '../AuthContext';

// Mock secureStorage
vi.mock('../../lib/secureStorage', () => ({
  secureStorage: {
    getToken: vi.fn(),
    setToken: vi.fn(),
    removeToken: vi.fn(),
    isStorageAvailable: vi.fn(),
  },
}));

import { secureStorage } from '../../lib/secureStorage';

const mockedSecureStorage = vi.mocked(secureStorage);

// Create a useAuth hook for testing
const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Mock fetch
const fetchMock = vi.fn();
global.fetch = fetchMock;

// Test component that uses auth context
const TestComponent = () => {
  const { user, login, logout, isAuthenticated, isLoading } = useAuth();

  return (
    <div>
      <div data-testid="user">{user ? JSON.stringify(user) : 'No user'}</div>
      <div data-testid="isAuthenticated">{isAuthenticated.toString()}</div>
      <div data-testid="isLoading">{isLoading.toString()}</div>
      <button onClick={() => login({ email: 'test@example.com', password: 'password', authMethod: 'traditional' })}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset secureStorage mocks
    mockedSecureStorage.getToken.mockReturnValue(null);
    mockedSecureStorage.setToken.mockReturnValue();
    mockedSecureStorage.removeToken.mockReturnValue();
    mockedSecureStorage.isStorageAvailable.mockReturnValue(true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with no user when no token exists', () => {
    mockedSecureStorage.getToken.mockReturnValue(null);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('No user');
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
  });

  it('should initialize with user when token exists', async () => {
    const mockToken = 'mock-jwt-token';
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };

    mockedSecureStorage.getToken.mockReturnValue(mockToken);
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        walletAddress: undefined,
        authMethod: 'traditional',
        isKycVerified: false,
        kycStatus: 'not_started',
        reputationScore: 0,
        tokenBalance: 0,
        createdAt: '',
        skills: [],
        location: undefined,
        bio: undefined,
      }));
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });
  });

  it('should handle login successfully', async () => {
    const mockToken = 'new-jwt-token';
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ access_token: mockToken, user: mockUser }),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    loginButton.click();

    await waitFor(() => {
      expect(mockedSecureStorage.setToken).toHaveBeenCalledWith(mockToken);
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        walletAddress: undefined,
        authMethod: 'traditional',
        isKycVerified: false,
        kycStatus: 'not_started',
        reputationScore: 0,
        tokenBalance: 0,
        createdAt: '',
        skills: [],
        location: undefined,
        bio: undefined,
      }));
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });
  });

  it('should handle login failure', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ message: 'Invalid credentials' }),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    loginButton.click();

    await waitFor(() => {
      expect(mockedSecureStorage.setToken).not.toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });

  it('should handle logout', async () => {
    const mockToken = 'mock-jwt-token';
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };

    mockedSecureStorage.getToken.mockReturnValue(mockToken);
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    });

    const logoutButton = screen.getByText('Logout');
    logoutButton.click();

    await waitFor(() => {
      expect(mockedSecureStorage.removeToken).toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });

  it('should handle token validation failure on initialization', async () => {
    const mockToken = 'invalid-token';

    mockedSecureStorage.getToken.mockReturnValue(mockToken);
    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ message: 'Invalid token' }),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(mockedSecureStorage.removeToken).toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });

  it('should handle network errors during login', async () => {
    fetchMock.mockRejectedValueOnce(new Error('Network error'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    loginButton.click();

    await waitFor(() => {
      expect(mockedSecureStorage.setToken).not.toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });

  it('should handle storage unavailable', async () => {
    mockedSecureStorage.isStorageAvailable.mockReturnValue(false);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    loginButton.click();

    await waitFor(() => {
      expect(mockedSecureStorage.setToken).not.toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });
});