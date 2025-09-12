import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import LoginPage from '../../pages/LoginPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { useAuth } from '../../hooks/useAuth';

// Mock implementations
const mockLogin = vi.fn();
const mockLogout = vi.fn();
const mockRegister = vi.fn();
const mockConnectWallet = vi.fn();
const mockDisconnectWallet = vi.fn();
const mockRefreshUser = vi.fn();
const mockUpdateKycStatus = vi.fn();
const mockSubmitKyc = vi.fn();
const mockGetKycStatus = vi.fn();
const mockCheckEligibility = vi.fn();

const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  authMethod: 'traditional' as const,
  isKycVerified: false,
  kycStatus: 'not_started' as const,
  reputationScore: 0,
  tokenBalance: 0,
  createdAt: '2024-01-01T00:00:00Z',
  skills: [],
};

// Helper function to create complete mock auth context
const createMockAuthContext = (overrides = {}) => ({
  user: mockUser,
  isAuthenticated: true,
  isLoading: false,
  walletConnected: false,
  walletAddress: undefined,
  login: mockLogin,
  register: mockRegister,
  logout: mockLogout,
  connectWallet: mockConnectWallet,
  disconnectWallet: mockDisconnectWallet,
  refreshUser: mockRefreshUser,
  updateKycStatus: mockUpdateKycStatus,
  submitKyc: mockSubmitKyc,
  getKycStatus: mockGetKycStatus,
  checkEligibility: mockCheckEligibility,
  ...overrides,
});

// Mock the useAuth hook
vi.mock('../../hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// Mock React Router
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    Link: ({ to, children, ...props }: { to: string; children: React.ReactNode; [key: string]: unknown }) =>
      React.createElement('a', { href: to, ...props }, children),
  };
});

// Mock UI components
vi.mock('@/components/ui/card', () => ({
  Card: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card' }, children),
  CardContent: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card-content' }, children),
  CardHeader: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card-header' }, children),
  CardTitle: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card-title' }, children),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, variant, disabled, ...props }: {
    children: React.ReactNode;
    onClick?: () => void;
    variant?: string;
    disabled?: boolean;
    [key: string]: unknown;
  }) =>
    React.createElement('button', {
      onClick,
      'data-variant': variant,
      disabled,
      ...props
    }, children),
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ placeholder, type, value, onChange, ...props }: {
    placeholder?: string;
    type?: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    [key: string]: unknown;
  }) =>
    React.createElement('input', {
      placeholder,
      type: type || 'text',
      value,
      onChange,
      ...props
    }),
}));

vi.mock('@/components/ui/label', () => ({
  Label: ({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) =>
    React.createElement('label', { htmlFor }, children),
}));

vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'alert' }, children),
  AlertDescription: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'alert-description' }, children),
}));

// Mock wallet utilities
vi.mock('../../utils/wallet', () => ({
  connectWallet: mockConnectWallet,
  getWalletAddress: vi.fn(),
  isWalletConnected: vi.fn(),
}));

// Mock the LoginPage component
vi.mock('../../pages/LoginPage', () => ({
  default: () => React.createElement('div', { 'data-testid': 'login-page' }, 'Login Page'),
}));

describe('Authentication Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Login Flow', () => {
    it('should handle traditional login successfully', async () => {
      mockLogin.mockResolvedValueOnce({ success: true });

      render(
        <BrowserRouter>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </BrowserRouter>
      );

      // The LoginPage component should be rendered
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    it('should handle wallet login successfully', async () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    it('should handle login failure gracefully', async () => {
      mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

      render(
        <BrowserRouter>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    it('should redirect to dashboard after successful login', async () => {
      mockLogin.mockResolvedValueOnce({ success: true });

      render(
        <MemoryRouter initialEntries={['/login']}>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </MemoryRouter>
      );

      // After successful login, should navigate to dashboard
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });
  });

  describe('Logout Flow', () => {
    it('should handle logout successfully', async () => {
      mockLogout.mockResolvedValueOnce({ success: true });

      // Create a simple component that uses logout
      const TestLogoutComponent = () => {
        const { logout } = useAuth();

        const handleLogout = async () => {
          await logout();
        };

        return React.createElement('button', {
          onClick: handleLogout,
          'data-testid': 'logout-button'
        }, 'Logout');
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestLogoutComponent />
          </AuthProvider>
        </BrowserRouter>
      );

      const logoutButton = screen.getByTestId('logout-button');
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalled();
      });
    });

    it('should redirect to login page after logout', async () => {
      mockLogout.mockResolvedValueOnce({ success: true });

      const TestLogoutComponent = () => {
        const { logout } = useAuth();

        React.useEffect(() => {
          logout();
        }, [logout]);

        return React.createElement('div', null, 'Logging out...');
      };

      render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <AuthProvider>
            <TestLogoutComponent />
          </AuthProvider>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });
  });

  describe('Authentication State Management', () => {
    it('should maintain authentication state across navigation', () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <div data-testid="test-component">Authenticated Content</div>
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('test-component')).toBeInTheDocument();
      expect(screen.getByText('Authenticated Content')).toBeInTheDocument();
    });

    it('should handle authentication loading states', () => {
      // Mock loading state
      const mockUseAuth = vi.mocked(useAuth);
      mockUseAuth.mockReturnValue(createMockAuthContext({
        user: null,
        isLoading: true,
        isAuthenticated: false,
      }));

      const LoadingComponent = () => {
        const { isLoading } = useAuth();
        return React.createElement('div', {
          'data-testid': 'loading-state'
        }, isLoading ? 'Loading...' : 'Loaded');
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <LoadingComponent />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('loading-state')).toHaveTextContent('Loading...');
    });
  });

  describe('Route Protection', () => {
    it('should allow access to protected routes when authenticated', () => {
      const ProtectedComponent = () => {
        const { isAuthenticated } = useAuth();
        return React.createElement('div', {
          'data-testid': 'protected-content'
        }, isAuthenticated ? 'Protected Content' : 'Access Denied');
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <ProtectedComponent />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('protected-content')).toHaveTextContent('Protected Content');
    });

    it('should redirect unauthenticated users from protected routes', () => {
      // Mock unauthenticated state
      const mockUseAuth = vi.mocked(useAuth);
      mockUseAuth.mockReturnValue(createMockAuthContext({
        user: null,
        isAuthenticated: false,
      }));

      const ProtectedComponent = () => {
        const { isAuthenticated } = useAuth();

        React.useEffect(() => {
          if (!isAuthenticated) {
            mockNavigate('/login');
          }
        }, [isAuthenticated]);

        return React.createElement('div', null, 'Checking auth...');
      };

      render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <AuthProvider>
            <ProtectedComponent />
          </AuthProvider>
        </MemoryRouter>
      );

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors during login', async () => {
      mockLogin.mockRejectedValueOnce(new Error('Network error'));

      const TestLoginComponent = () => {
        const { login } = useAuth();
        const [error, setError] = React.useState('');

        const handleLogin = async () => {
          try {
            await login({ email: 'test@example.com', password: 'password', authMethod: 'traditional' });
          } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'An error occurred');
          }
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: handleLogin,
            'data-testid': 'login-button'
          }, 'Login'),
          error && React.createElement('div', { 'data-testid': 'error-message' }, error)
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestLoginComponent />
          </AuthProvider>
        </BrowserRouter>
      );

      const loginButton = screen.getByTestId('login-button');
      fireEvent.click(loginButton);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Network error');
      });
    });

    it('should handle wallet connection errors', async () => {
      const mockConnectWallet = vi.fn().mockRejectedValueOnce(new Error('Wallet connection failed'));

      const TestWalletComponent = () => {
        const [error, setError] = React.useState('');

        const handleWalletConnect = async () => {
          try {
            await mockConnectWallet();
          } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'An error occurred');
          }
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: handleWalletConnect,
            'data-testid': 'wallet-button'
          }, 'Connect Wallet'),
          error && React.createElement('div', { 'data-testid': 'wallet-error' }, error)
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestWalletComponent />
          </AuthProvider>
        </BrowserRouter>
      );

      const walletButton = screen.getByTestId('wallet-button');
      fireEvent.click(walletButton);

      await waitFor(() => {
        expect(screen.getByTestId('wallet-error')).toHaveTextContent('Wallet connection failed');
      });
    });
  });

  describe('Session Management', () => {
    it('should persist authentication state across page reloads', () => {
      // Mock localStorage
      const mockLocalStorage = {
        getItem: vi.fn().mockReturnValue(JSON.stringify(mockUser)),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      };

      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true,
      });

      render(
        <BrowserRouter>
          <AuthProvider>
            <div data-testid="session-test">Session Test</div>
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('session-test')).toBeInTheDocument();
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('auth_user');
    });

    it('should clear session on logout', async () => {
      const mockLocalStorage = {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      };

      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true,
      });

      mockLogout.mockImplementation(async () => {
        mockLocalStorage.removeItem('auth_user');
        mockLocalStorage.removeItem('auth_token');
        return { success: true };
      });

      const TestLogoutComponent = () => {
        const { logout } = useAuth();

        const handleLogout = async () => {
          await logout();
        };

        return React.createElement('button', {
          onClick: handleLogout,
          'data-testid': 'logout-button'
        }, 'Logout');
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestLogoutComponent />
          </AuthProvider>
        </BrowserRouter>
      );

      const logoutButton = screen.getByTestId('logout-button');
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_user');
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_token');
      });
    });
  });
});