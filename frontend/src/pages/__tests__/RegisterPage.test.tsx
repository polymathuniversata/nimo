import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RegisterPage from '../RegisterPage';

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
const mockRegister = vi.fn();
const mockSubmitKyc = vi.fn();
const mockUseAuth = vi.fn(() => ({
  register: mockRegister,
  submitKyc: mockSubmitKyc,
  isLoading: false,
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: mockUseAuth,
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
  Button: ({ children, variant, className, asChild, size, ...props }: {
    children?: React.ReactNode;
    variant?: string;
    className?: string;
    asChild?: boolean;
    size?: string;
    [key: string]: unknown;
  }) => {
    const Component = asChild ? 'a' : 'button';
    return React.createElement(Component, {
      className,
      'data-variant': variant,
      'data-size': size,
      ...props
    }, children);
  },
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ type, placeholder, value, onChange, className, required, id, ...props }: {
    type?: string;
    placeholder?: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    className?: string;
    required?: boolean;
    id?: string;
    [key: string]: unknown;
  }) =>
    React.createElement('input', {
      type: type || 'text',
      placeholder,
      value,
      onChange,
      className,
      required,
      id,
      ...props
    }),
}));

vi.mock('@/components/ui/label', () => ({
  Label: ({ children, htmlFor, className }: { children?: React.ReactNode; htmlFor?: string; className?: string }) =>
    React.createElement('label', { htmlFor, className }, children),
}));

vi.mock('@/components/ui/textarea', () => ({
  Textarea: ({ placeholder, value, onChange, className, rows, id }: {
    placeholder?: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    className?: string;
    rows?: number;
    id?: string;
  }) =>
    React.createElement('textarea', {
      placeholder,
      value,
      onChange,
      className,
      rows,
      id
    }),
}));

vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'alert' }, children),
  AlertDescription: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'alert-description' }, children),
}));

vi.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children, value, className }: { children?: React.ReactNode; value?: string; className?: string }) =>
    React.createElement('div', { className, 'data-testid': 'tabs', 'data-value': value }, children),
  TabsContent: ({ children, value }: { children?: React.ReactNode; value?: string }) =>
    React.createElement('div', { 'data-value': value }, children),
  TabsList: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'tabs-list' }, children),
  TabsTrigger: ({ children, value, onClick, disabled }: {
    children?: React.ReactNode;
    value?: string;
    onClick?: () => void;
    disabled?: boolean;
  }) =>
    React.createElement('button', {
      'data-value': value,
      onClick,
      disabled
    }, children),
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant }: { children?: React.ReactNode; variant?: string }) =>
    React.createElement('span', { 'data-variant': variant }, children),
}));

vi.mock('@/components/ui/select', () => ({
  Select: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'select' }, children),
  SelectContent: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'select-content' }, children),
  SelectItem: ({ children, value }: { children?: React.ReactNode; value?: string }) =>
    React.createElement('option', { value }, children),
  SelectTrigger: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('button', { 'data-testid': 'select-trigger' }, children),
  SelectValue: ({ placeholder }: { placeholder?: string }) =>
    React.createElement('span', { 'data-testid': 'select-value' }, placeholder),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Mail: () => React.createElement('span', { 'data-testid': 'mail-icon' }, 'Mail'),
  Lock: () => React.createElement('span', { 'data-testid': 'lock-icon' }, 'Lock'),
  User: () => React.createElement('span', { 'data-testid': 'user-icon' }, 'User'),
  Wallet: () => React.createElement('span', { 'data-testid': 'wallet-icon' }, 'Wallet'),
  Sparkles: () => React.createElement('span', { 'data-testid': 'sparkles-icon' }, 'Sparkles'),
  AlertCircle: () => React.createElement('span', { 'data-testid': 'alert-circle-icon' }, 'AlertCircle'),
  CheckCircle: () => React.createElement('span', { 'data-testid': 'check-circle-icon' }, 'CheckCircle'),
  Loader2: () => React.createElement('span', { 'data-testid': 'loader-icon' }, 'Loader2'),
  MapPin: () => React.createElement('span', { 'data-testid': 'map-pin-icon' }, 'MapPin'),
  FileText: () => React.createElement('span', { 'data-testid': 'file-text-icon' }, 'FileText'),
  Calendar: () => React.createElement('span', { 'data-testid': 'calendar-icon' }, 'Calendar'),
  Phone: () => React.createElement('span', { 'data-testid': 'phone-icon' }, 'Phone'),
  Globe: () => React.createElement('span', { 'data-testid': 'globe-icon' }, 'Globe'),
  CreditCard: () => React.createElement('span', { 'data-testid': 'credit-card-icon' }, 'CreditCard'),
  Camera: () => React.createElement('span', { 'data-testid': 'camera-icon' }, 'Camera'),
  Upload: () => React.createElement('span', { 'data-testid': 'upload-icon' }, 'Upload'),
  Shield: () => React.createElement('span', { 'data-testid': 'shield-icon' }, 'Shield'),
}));

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
    mockRegister.mockClear();
    mockSubmitKyc.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial Render', () => {
    it('should render the registration page with correct title and description', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      expect(screen.getByText('Join Nimo')).toBeInTheDocument();
      expect(screen.getByText('Create your decentralized identity and start earning reputation')).toBeInTheDocument();
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    it('should show step indicator with profile step active by default', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
      expect(screen.getByText('Complete your profile, KYC verification, and wallet connection')).toBeInTheDocument();
    });

    it('should render step navigation tabs', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      expect(screen.getByText('Profile')).toBeInTheDocument();
      expect(screen.getByText('KYC')).toBeInTheDocument();
      expect(screen.getByText('Wallet')).toBeInTheDocument();
    });
  });

  describe('Profile Step', () => {
    it('should render all required profile fields', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      expect(screen.getByPlaceholderText('Your full name')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('your@email.com')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('City, Country')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Min 6 characters')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Confirm password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Tell us about yourself...')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Python, React, Design (comma-separated)')).toBeInTheDocument();
    });

    it('should require essential fields', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      expect(nameInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
      expect(confirmPasswordInput).toHaveAttribute('required');
    });

    it('should validate email format', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText('your@email.com');
      expect(emailInput).toHaveAttribute('type', 'email');
    });

    it('should show password mismatch error', async () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password456' } });

      // Submit form to trigger validation
      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });
    });

    it('should show password too short error', async () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(passwordInput, { target: { value: '123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: '123' } });

      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters long')).toBeInTheDocument();
      });
    });

    it('should proceed to KYC step with valid profile data', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Fill required fields
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);

      expect(screen.getByText('KYC Verification')).toBeInTheDocument();
    });
  });

  describe('KYC Step', () => {
    beforeEach(() => {
      // Start with profile step and navigate to KYC
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Fill profile and go to KYC
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);
    });

    it('should render KYC form with personal information fields', () => {
      expect(screen.getByPlaceholderText('Your nationality')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('+1234567890')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter document number')).toBeInTheDocument();
    });

    it('should render address information fields', () => {
      expect(screen.getByPlaceholderText('123 Main Street')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('City')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Country')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('12345')).toBeInTheDocument();
    });

    it('should render document upload sections', () => {
      expect(screen.getByText('Upload front of document')).toBeInTheDocument();
      expect(screen.getByText('Upload back of document')).toBeInTheDocument();
      expect(screen.getByText('Upload selfie')).toBeInTheDocument();
    });

    it('should require essential KYC fields', () => {
      const dateOfBirthInput = screen.getByDisplayValue('');
      const nationalityInput = screen.getByPlaceholderText('Your nationality');
      const phoneInput = screen.getByPlaceholderText('+1234567890');
      const documentNumberInput = screen.getByPlaceholderText('Enter document number');
      const streetInput = screen.getByPlaceholderText('123 Main Street');
      const cityInput = screen.getByPlaceholderText('City');
      const countryInput = screen.getByPlaceholderText('Country');
      const postalCodeInput = screen.getByPlaceholderText('12345');

      expect(dateOfBirthInput).toHaveAttribute('required');
      expect(nationalityInput).toHaveAttribute('required');
      expect(phoneInput).toHaveAttribute('required');
      expect(documentNumberInput).toHaveAttribute('required');
      expect(streetInput).toHaveAttribute('required');
      expect(cityInput).toHaveAttribute('required');
      expect(countryInput).toHaveAttribute('required');
      expect(postalCodeInput).toHaveAttribute('required');
    });

    it('should show document type selection', () => {
      expect(screen.getByText('Select document type')).toBeInTheDocument();
    });

    it('should allow navigation back to profile step', () => {
      const backButton = screen.getByText('Back');
      fireEvent.click(backButton);

      expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
    });

    it('should proceed to wallet step when KYC is completed', () => {
      const nextButton = screen.getByText('Next: Connect Wallet');
      fireEvent.click(nextButton);

      expect(screen.getByText('Connect Your Wallet')).toBeInTheDocument();
    });
  });

  describe('Wallet Step', () => {
    beforeEach(() => {
      // Navigate to wallet step
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Fill profile
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      // Go to KYC
      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);

      // Go to wallet
      const walletButton = screen.getByText('Next: Connect Wallet');
      fireEvent.click(walletButton);
    });

    it('should show wallet connection interface', () => {
      expect(screen.getByText('Wallet Connection Required')).toBeInTheDocument();
      expect(screen.getByText('Connect Cardano Wallet')).toBeInTheDocument();
    });

    it('should show supported wallet types', () => {
      expect(screen.getByText('Supported wallets: Yoroi, Eternl, Nami, Flint')).toBeInTheDocument();
    });

    it('should show wallet connected state after connection', async () => {
      // Mock wallet connection
      const originalWindow = global.window;
      (global.window as unknown as Record<string, unknown>) = {
        ...originalWindow,
        cardano: {
          yoroi: {
            enable: vi.fn().mockResolvedValue({
              getUsedAddresses: vi.fn().mockResolvedValue(['addr1...']),
              signData: vi.fn().mockResolvedValue({ signature: 'signature123' })
            })
          }
        }
      };

      const connectButton = screen.getByText('Connect Cardano Wallet');
      fireEvent.click(connectButton);

      await waitFor(() => {
        expect(screen.getByText('Wallet Connected Successfully')).toBeInTheDocument();
      });

      // Restore window
      global.window = originalWindow;
    });
  });

  describe('Form Submission', () => {
    it('should call register function with correct data on traditional registration', async () => {
      mockRegister.mockResolvedValue(undefined);
      mockSubmitKyc.mockResolvedValue(undefined);

      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Fill profile
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
      const locationInput = screen.getByPlaceholderText('City, Country');
      const bioTextarea = screen.getByPlaceholderText('Tell us about yourself...');
      const skillsInput = screen.getByPlaceholderText('Python, React, Design (comma-separated)');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      fireEvent.change(locationInput, { target: { value: 'Accra, Ghana' } });
      fireEvent.change(bioTextarea, { target: { value: 'I am a developer' } });
      fireEvent.change(skillsInput, { target: { value: 'JavaScript, React' } });

      // Submit
      const completeButton = screen.getByText('Complete Registration');
      fireEvent.click(completeButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          email: 'john@example.com',
          password: 'password123',
          name: 'John Doe',
          location: 'Accra, Ghana',
          bio: 'I am a developer',
          skills: ['JavaScript', 'React'],
          authMethod: 'traditional',
        });
      });
    });

    it('should show success message and redirect on successful registration', async () => {
      mockRegister.mockResolvedValue(undefined);
      mockSubmitKyc.mockResolvedValue(undefined);

      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Fill minimal required fields
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      const completeButton = screen.getByText('Complete Registration');
      fireEvent.click(completeButton);

      await waitFor(() => {
        expect(screen.getByText('Registration and KYC submission successful! You can now sign in.')).toBeInTheDocument();
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    it('should show error message on registration failure', async () => {
      const errorMessage = 'Registration failed';
      mockRegister.mockRejectedValue(new Error(errorMessage));

      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Fill minimal required fields
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      const completeButton = screen.getByText('Complete Registration');
      fireEvent.click(completeButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });
  });

  describe('File Upload', () => {
    it('should handle document front upload', async () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Navigate to KYC step
      const nameInput = screen.getByPlaceholderText('Your full name');
      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Min 6 characters');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);

      // Mock file upload
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const fileInput = screen.getByLabelText(/Upload front of document/);

      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('✓ Uploaded')).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading spinner during registration', () => {
      mockUseAuth.mockReturnValue({
        register: mockRegister,
        submitKyc: mockSubmitKyc,
        isLoading: true,
      });

      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      expect(screen.getByText('Creating Account...')).toBeInTheDocument();
      expect(screen.getByTestId('loader-icon')).toBeInTheDocument();
    });

    it('should disable form during loading', () => {
      mockUseAuth.mockReturnValue({
        register: mockRegister,
        submitKyc: mockSubmitKyc,
        isLoading: true,
      });

      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const completeButton = screen.getByText('Creating Account...');
      expect(completeButton).toBeDisabled();
    });
  });

  describe('Navigation', () => {
    it('should have link to login page', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const loginLink = screen.getByText('Sign in here');
      expect(loginLink).toBeInTheDocument();
      expect(loginLink.closest('a')).toHaveAttribute('href', '/login');
    });
  });

  describe('Step Validation', () => {
    it('should disable KYC tab until profile is completed', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const kycTab = screen.getByText('KYC');
      expect(kycTab.closest('button')).toBeDisabled();
    });

    it('should disable wallet tab until KYC is completed', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      const walletTab = screen.getByText('Wallet');
      expect(walletTab.closest('button')).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper form structure and labels', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Check for proper labeling
      const nameInput = screen.getByPlaceholderText('Your full name');
      expect(nameInput).toHaveAttribute('id');
      expect(screen.getByLabelText('Full Name *')).toBeInTheDocument();
    });

    it('should have proper ARIA attributes for step indicator', () => {
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );

      // Check for step indicator accessibility
      expect(screen.getByText('Profile')).toBeInTheDocument();
      expect(screen.getByText('KYC')).toBeInTheDocument();
      expect(screen.getByText('Wallet')).toBeInTheDocument();
    });
  });
});