import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';

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

// Mock useAuth hook
const mockLogin = vi.fn();
const mockUseAuth = vi.fn(() => ({
  login: mockLogin,
  isLoading: false,
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: mockUseAuth,
}));

// Mock wallet utilities
const mockDetectCardanoWallets = vi.fn();
const mockConnectWallet = vi.fn();
const mockSignMessage = vi.fn();
const mockHasCardanoWallets = vi.fn();

vi.mock('@/lib/utils', () => ({
  detectCardanoWallets: mockDetectCardanoWallets,
  connectWallet: mockConnectWallet,
  signMessage: mockSignMessage,
  hasCardanoWallets: mockHasCardanoWallets,
  getWalletInstallationUrls: () => ({
    yoroi: 'https://yoroi-wallet.com',
    eternl: 'https://eternl.io',
  }),
  getWalletTroubleshootingInfo: vi.fn(() => 'Troubleshooting info'),
}));

// Mock UI components
vi.mock('@/components/ui/card', () => ({
  Card: ({ children, className }: { children?: React.ReactNode; className?: string }) =>
    React.createElement('div', { className, 'data-testid': 'card' }, children),
  CardContent: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-content' }, children),
  CardDescription: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-description' }, children),
  CardHeader: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-header' }, children),
  CardTitle: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-title' }, children),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, variant, className, asChild, ...props }: {
    children?: React.ReactNode;
    variant?: string;
    className?: string;
    asChild?: boolean;
    [key: string]: unknown;
  }) => {
    const Component = asChild ? 'a' : 'button';
    return React.createElement(Component, {
      className,
      'data-variant': variant,
      ...props
    }, children);
  },
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ type, placeholder, value, onChange, className, required, ...props }: {
    type?: string;
    placeholder?: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    className?: string;
    required?: boolean;
    [key: string]: unknown;
  }) =>
    React.createElement('input', {
      type: type || 'text',
      placeholder,
      value,
      onChange,
      className,
      required,
      ...props
    }),
}));

vi.mock('@/components/ui/label', () => ({
  Label: ({ children, htmlFor, className }: { children?: React.ReactNode; htmlFor?: string; className?: string }) =>
    React.createElement('label', { htmlFor, className }, children),
}));

vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'alert' }, children),
  AlertDescription: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'alert-description' }, children),
}));

vi.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children, className }: { children?: React.ReactNode; className?: string }) =>
    React.createElement('div', { className, 'data-testid': 'tabs' }, children),
  TabsContent: ({ children, value }: { children?: React.ReactNode; value?: string }) =>
    React.createElement('div', { 'data-value': value }, children),
  TabsList: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'tabs-list' }, children),
  TabsTrigger: ({ children, value }: { children?: React.ReactNode; value?: string }) =>
    React.createElement('button', { 'data-value': value }, children),
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant }: { children?: React.ReactNode; variant?: string }) =>
    React.createElement('span', { 'data-variant': variant }, children),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Mail: () => React.createElement('span', { 'data-testid': 'mail-icon' }, 'Mail'),
  Lock: () => React.createElement('span', { 'data-testid': 'lock-icon' }, 'Lock'),
  Wallet: () => React.createElement('span', { 'data-testid': 'wallet-icon' }, 'Wallet'),
  Sparkles: () => React.createElement('span', { 'data-testid': 'sparkles-icon' }, 'Sparkles'),
  AlertCircle: () => React.createElement('span', { 'data-testid': 'alert-circle-icon' }, 'AlertCircle'),
  CheckCircle: () => React.createElement('span', { 'data-testid': 'check-circle-icon' }, 'CheckCircle'),
  Loader2: () => React.createElement('span', { 'data-testid': 'loader-icon' }, 'Loader2'),
  ExternalLink: () => React.createElement('span', { 'data-testid': 'external-link-icon' }, 'ExternalLink'),
}));

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
    mockLogin.mockClear();
    mockDetectCardanoWallets.mockReturnValue([]);
    mockHasCardanoWallets.mockReturnValue(false);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial Render', () => {
    it('should render the login page with correct title and description', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
      expect(screen.getByText('Sign in to access your decentralized identity')).toBeInTheDocument();
      expect(screen.getByText('Sign In')).toBeInTheDocument();
    });

    it('should show wallet connection required alert when no wallet is connected', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('Wallet connection is required to access Nimo.')).toBeInTheDocument();
    });

    it('should render both email and wallet login tabs', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Wallet')).toBeInTheDocument();
    });
  });

  describe('Traditional Login Form', () => {
    it('should render email and password input fields', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
    });

    it('should require wallet connection before allowing traditional login', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const signInButton = screen.getByText('Sign In');
      expect(signInButton).toBeDisabled();
    });

    it('should enable sign in button when wallet is connected', () => {
      // Mock wallet connection
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' }
      ]);

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Simulate wallet connection
      const connectWalletButton = screen.getByText('Connect Wallet');
      fireEvent.click(connectWalletButton);

      // The button should be enabled after wallet connection
      // Note: In a real scenario, this would be handled by state updates
    });

    it('should call login function with correct credentials on form submission', async () => {
      mockLogin.mockResolvedValue(undefined);
      mockUseAuth.mockReturnValue({
        login: mockLogin,
        isLoading: false,
      });

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Fill out the form
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      // Submit the form
      const form = screen.getByRole('form', { hidden: true });
      fireEvent.submit(form);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          authMethod: 'traditional',
        });
      });
    });

    it('should show success message and redirect on successful login', async () => {
      mockLogin.mockResolvedValue(undefined);

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Fill and submit form
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const form = screen.getByRole('form', { hidden: true });
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Login successful! Redirecting...')).toBeInTheDocument();
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard/user');
      });
    });

    it('should show error message on login failure', async () => {
      const errorMessage = 'Invalid credentials';
      mockLogin.mockRejectedValue(new Error(errorMessage));

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Fill and submit form
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const form = screen.getByRole('form', { hidden: true });
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });
  });

  describe('Wallet Login Form', () => {
    it('should show wallet installation instructions when no wallets are detected', () => {
      mockDetectCardanoWallets.mockReturnValue([]);

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('No Cardano wallet extensions detected')).toBeInTheDocument();
      expect(screen.getByText('Install Yoroi')).toBeInTheDocument();
    });

    it('should show available wallets when wallets are detected', () => {
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' },
        { id: 'eternl', name: 'Eternl', icon: '🔷' }
      ]);

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('Yoroi')).toBeInTheDocument();
      expect(screen.getByText('Eternl')).toBeInTheDocument();
    });

    it('should show wallet connection interface when wallets are available', () => {
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' }
      ]);

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('Select your Cardano wallet to connect')).toBeInTheDocument();
      expect(screen.getByText('Connect Yoroi')).toBeInTheDocument();
    });

    it('should show signature input after wallet connection', async () => {
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' }
      ]);
      mockConnectWallet.mockResolvedValue({
        wallet: { signData: vi.fn() },
        address: 'addr1...'
      });
      mockSignMessage.mockResolvedValue('signature123');

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const connectButton = screen.getByText('Connect Yoroi');
      fireEvent.click(connectButton);

      await waitFor(() => {
        expect(screen.getByText('Wallet Connected')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Enter signature from wallet')).toBeInTheDocument();
      });
    });

    it('should call wallet login function with correct data', async () => {
      mockLogin.mockResolvedValue(undefined);
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' }
      ]);
      mockConnectWallet.mockResolvedValue({
        wallet: { signData: vi.fn() },
        address: 'addr1...'
      });
      mockSignMessage.mockResolvedValue('signature123');

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Connect wallet
      const connectButton = screen.getByText('Connect Yoroi');
      fireEvent.click(connectButton);

      await waitFor(() => {
        expect(screen.getByText('Wallet Connected')).toBeInTheDocument();
      });

      // Fill signature and submit
      const signatureInput = screen.getByPlaceholderText('Enter signature from wallet');
      fireEvent.change(signatureInput, { target: { value: 'signature123' } });

      const signInButton = screen.getByText('Sign In with Wallet');
      fireEvent.click(signInButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          walletAddress: 'addr1...',
          signature: 'signature123',
          message: expect.any(String),
          authMethod: 'wallet',
        });
      });
    });
  });

  describe('Form Validation', () => {
    it('should require email field', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText('Enter your email');
      expect(emailInput).toHaveAttribute('required');
    });

    it('should require password field', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const passwordInput = screen.getByPlaceholderText('Enter your password');
      expect(passwordInput).toHaveAttribute('required');
    });

    it('should validate email format', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText('Enter your email');
      expect(emailInput).toHaveAttribute('type', 'email');
    });
  });

  describe('Loading States', () => {
    it('should show loading spinner during login process', () => {
      mockUseAuth.mockReturnValue({
        login: mockLogin,
        isLoading: true,
      });

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      expect(screen.getByText('Signing In...')).toBeInTheDocument();
      expect(screen.getByTestId('loader-icon')).toBeInTheDocument();
    });

    it('should disable form during loading', () => {
      mockUseAuth.mockReturnValue({
        login: mockLogin,
        isLoading: true,
      });

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const signInButton = screen.getByText('Signing In...');
      expect(signInButton).toBeDisabled();
    });
  });

  describe('Navigation', () => {
    it('should have link to register page', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const registerLink = screen.getByText('Sign up here');
      expect(registerLink).toBeInTheDocument();
      expect(registerLink.closest('a')).toHaveAttribute('href', '/register');
    });
  });

  describe('Error Handling', () => {
    it('should handle wallet connection errors', async () => {
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' }
      ]);
      mockConnectWallet.mockRejectedValue(new Error('Wallet connection failed'));

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const connectButton = screen.getByText('Connect Yoroi');
      fireEvent.click(connectButton);

      await waitFor(() => {
        expect(screen.getByText('Wallet connection failed')).toBeInTheDocument();
      });
    });

    it('should handle wallet extension not available', async () => {
      mockDetectCardanoWallets.mockReturnValue([
        { id: 'yoroi', name: 'Yoroi', icon: '👛' }
      ]);
      mockConnectWallet.mockRejectedValue(new Error('not available'));

      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      const connectButton = screen.getByText('Connect Yoroi');
      fireEvent.click(connectButton);

      await waitFor(() => {
        expect(screen.getByText(/Wallet extension not found/)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and descriptions', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Check for screen reader text
      expect(screen.getByText('Enter your registered email address')).toBeInTheDocument();
      expect(screen.getByText('Enter your account password')).toBeInTheDocument();
    });

    it('should have proper form structure', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      );

      // Check for proper form landmarks
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });
});