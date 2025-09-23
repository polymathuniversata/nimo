import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '../../pages/LoginPage'
import { AuthProvider } from '../../contexts/AuthContext'

// Mock the authentication hook
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    isLoading: false,
    user: null,
    isAuthenticated: false
  })
}))

// Mock wallet utilities
vi.mock('../../lib/utils', () => ({
  detectCardanoWallets: vi.fn(),
  connectWallet: vi.fn(),
  signMessage: vi.fn(),
  getWalletInstallationUrls: vi.fn(),
  getWalletTroubleshootingInfo: vi.fn()
}))

// Mock react-router-dom's useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

// Mock window.open for wallet installation
const mockWindowOpen = vi.fn()
Object.defineProperty(window, 'open', {
  value: mockWindowOpen,
  writable: true
})

const renderLoginPage = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </BrowserRouter>
  )
}

describe('Authentication Flow Integration Tests', () => {
  const mockWallets = [
    { id: 'nami', name: 'Nami', icon: '🦊' },
    { id: 'eternl', name: 'Eternl', icon: '🔗' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock wallet detection
    const { detectCardanoWallets } = require('../../lib/utils')
    vi.mocked(detectCardanoWallets).mockReturnValue(mockWallets)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders login page with wallet connection requirement', async () => {
    renderLoginPage()

    expect(screen.getByText('Welcome Back')).toBeInTheDocument()
    expect(screen.getByText('🔐 Wallet Connection Required')).toBeInTheDocument()
    expect(screen.getByText('Select your Cardano wallet to connect')).toBeInTheDocument()
  })

  it('displays available wallets when detected', () => {
    renderLoginPage()

    expect(screen.getByText('Nami')).toBeInTheDocument()
    expect(screen.getByText('Eternl')).toBeInTheDocument()
  })

  it('allows switching between traditional and wallet login tabs', () => {
    renderLoginPage()

    // Default tab should be traditional
    expect(screen.getByRole('tab', { name: /email/i })).toHaveAttribute('aria-selected', 'true')

    // Switch to wallet tab
    const walletTab = screen.getByRole('tab', { name: /wallet/i })
    fireEvent.click(walletTab)

    expect(walletTab).toHaveAttribute('aria-selected', 'true')
  })

  it('shows wallet installation instructions when no wallets detected', () => {
    const { detectCardanoWallets } = require('../../lib/utils')
    vi.mocked(detectCardanoWallets).mockReturnValue([])

    const { getWalletInstallationUrls } = require('../../lib/utils')
    vi.mocked(getWalletInstallationUrls).mockReturnValue({
      nami: 'https://chrome.google.com/webstore/detail/nami/lpfcbjknijpeeillifnddfaldlindpkp',
      eternl: 'https://chrome.google.com/webstore/detail/eternl/kmhcihpebfmpgmihbkipmjlmmioameka'
    })

    renderLoginPage()

    expect(screen.getByText('No Cardano wallet extensions detected')).toBeInTheDocument()
    expect(screen.getByText('Install Nami')).toBeInTheDocument()
    expect(screen.getByText('Install Eternl')).toBeInTheDocument()
  })

  it('connects wallet successfully and shows connection status', async () => {
    const { connectWallet, signMessage } = require('../../lib/utils')

    vi.mocked(connectWallet).mockResolvedValue({
      wallet: { name: 'Nami' },
      address: 'addr1_test1234567890abcdef'
    })

    vi.mocked(signMessage).mockResolvedValue('mock_signature_123')

    renderLoginPage()

    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('Wallet Connected')).toBeInTheDocument()
      expect(screen.getByText('addr1_te...bcdef')).toBeInTheDocument()
    })
  })

  it('handles wallet connection errors gracefully', async () => {
    const { connectWallet } = require('../../lib/utils')
    vi.mocked(connectWallet).mockRejectedValue(new Error('Wallet connection rejected'))

    renderLoginPage()

    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('Wallet connection was rejected. Please try again and approve the connection.')).toBeInTheDocument()
    })
  })

  it('validates traditional login form fields', async () => {
    renderLoginPage()

    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: 'Sign In' })

    // Submit without wallet connection should show error
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Please connect your Cardano wallet to sign in')).toBeInTheDocument()
    })
  })

  it('submits traditional login with wallet connection', async () => {
    const { connectWallet, signMessage } = require('../../lib/utils')
    const { useAuth } = require('../../hooks/useAuth')

    const mockLogin = vi.fn().mockResolvedValue({ success: true })
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: null,
      isAuthenticated: false
    })

    vi.mocked(connectWallet).mockResolvedValue({
      wallet: { name: 'Nami' },
      address: 'addr1_test1234567890abcdef'
    })

    vi.mocked(signMessage).mockResolvedValue('mock_signature_123')

    renderLoginPage()

    // Connect wallet first
    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('Wallet Connected')).toBeInTheDocument()
    })

    // Fill and submit form
    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: 'Sign In' })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        authMethod: 'traditional'
      })
    })
  })

  it('submits wallet login with signature', async () => {
    const { connectWallet, signMessage } = require('../../lib/utils')
    const { useAuth } = require('../../hooks/useAuth')

    const mockLogin = vi.fn().mockResolvedValue({ success: true })
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: null,
      isAuthenticated: false
    })

    vi.mocked(connectWallet).mockResolvedValue({
      wallet: { name: 'Nami' },
      address: 'addr1_test1234567890abcdef'
    })

    vi.mocked(signMessage).mockResolvedValue('mock_signature_123')

    renderLoginPage()

    // Connect wallet
    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('Wallet Connected')).toBeInTheDocument()
    })

    // Switch to wallet tab
    const walletTab = screen.getByRole('tab', { name: /wallet/i })
    fireEvent.click(walletTab)

    // Fill signature
    const signatureInput = screen.getByPlaceholderText('Enter signature from wallet')
    fireEvent.change(signatureInput, { target: { value: 'mock_signature_123' } })

    // Submit wallet login
    const walletSubmitButton = screen.getByRole('button', { name: 'Sign In with Wallet' })
    fireEvent.click(walletSubmitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        walletAddress: 'addr1_test1234567890abcdef',
        signature: 'mock_signature_123',
        message: expect.any(String),
        authMethod: 'wallet'
      })
    })
  })

  it('shows success message and redirects on successful login', async () => {
    const { useAuth } = require('../../hooks/useAuth')

    const mockLogin = vi.fn().mockResolvedValue({ success: true })
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: null,
      isAuthenticated: false
    })

    renderLoginPage()

    // Mock wallet connection
    const { connectWallet } = require('../../lib/utils')
    vi.mocked(connectWallet).mockResolvedValue({
      wallet: { name: 'Nami' },
      address: 'addr1_test1234567890abcdef'
    })

    // Connect wallet
    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('Wallet Connected')).toBeInTheDocument()
    })

    // Fill and submit form
    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: 'Sign In' })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Login successful! Redirecting...')).toBeInTheDocument()
    })

    // Should navigate after delay
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard/user')
    }, { timeout: 2000 })
  })

  it('handles login errors and displays error messages', async () => {
    const { useAuth } = require('../../hooks/useAuth')

    const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      user: null,
      isAuthenticated: false
    })

    renderLoginPage()

    // Mock wallet connection
    const { connectWallet } = require('../../lib/utils')
    vi.mocked(connectWallet).mockResolvedValue({
      wallet: { name: 'Nami' },
      address: 'addr1_test1234567890abcdef'
    })

    // Connect wallet
    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('Wallet Connected')).toBeInTheDocument()
    })

    // Fill and submit form
    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: 'Sign In' })

    fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })
  })

  it('navigates back to home when back button is clicked', () => {
    renderLoginPage()

    const backButton = screen.getByRole('button', { name: /back to home/i })
    fireEvent.click(backButton)

    expect(mockNavigate).toHaveBeenCalledWith('/')
  })

  it('disables submit buttons during loading', async () => {
    const { useAuth } = require('../../hooks/useAuth')

    const mockLogin = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isLoading: true,
      user: null,
      isAuthenticated: false
    })

    renderLoginPage()

    const submitButton = screen.getByRole('button', { name: 'Sign In' })
    expect(submitButton).toBeDisabled()
    expect(screen.getByText('Signing In...')).toBeInTheDocument()
  })

  it('opens wallet installation links in new tab', () => {
    const { detectCardanoWallets } = require('../../lib/utils')
    vi.mocked(detectCardanoWallets).mockReturnValue([])

    const { getWalletInstallationUrls } = require('../../lib/utils')
    vi.mocked(getWalletInstallationUrls).mockReturnValue({
      nami: 'https://chrome.google.com/webstore/detail/nami/lpfcbjknijpeeillifnddfaldlindpkp'
    })

    renderLoginPage()

    const installButton = screen.getByRole('button', { name: /install nami/i })
    fireEvent.click(installButton)

    expect(mockWindowOpen).toHaveBeenCalledWith(
      'https://chrome.google.com/webstore/detail/nami/lpfcbjknijpeeillifnddfaldlindpkp',
      '_blank'
    )
  })

  it('shows wallet troubleshooting information for connection issues', async () => {
    const { connectWallet } = require('../../lib/utils')
    const { getWalletTroubleshootingInfo } = require('../../lib/utils')

    vi.mocked(connectWallet).mockRejectedValue(new Error('No addresses found'))
    vi.mocked(getWalletTroubleshootingInfo).mockReturnValue('Make sure your wallet has addresses')

    renderLoginPage()

    const connectButton = screen.getByRole('button', { name: /connect nami/i })
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(screen.getByText('No addresses found')).toBeInTheDocument()
      expect(screen.getByText('Make sure your wallet has addresses')).toBeInTheDocument()
    })
  })
})
