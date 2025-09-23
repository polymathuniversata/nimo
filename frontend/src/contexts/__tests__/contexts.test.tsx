import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TokenProvider, useTokens } from '@/contexts/TokenContext'
import { ContributionsProvider, useContributions } from '@/contexts/ContributionsContext'
import { WalletProvider, useWallet } from '@/contexts/WalletContext'

// Test component for TokenContext
function TokenTestComponent() {
  const { state } = useTokens()
  return (
    <div data-testid="token-context">
      <p>Loading: {state.loading.toString()}</p>
      <p>Error: {state.error || 'none'}</p>
      <p>NIMO Tokens: {state.balance.nimoTokens}</p>
    </div>
  )
}

// Test component for ContributionsContext
function ContributionsTestComponent() {
  const { state } = useContributions()
  return (
    <div data-testid="contributions-context">
      <p>Loading: {state.loading.toString()}</p>
      <p>Contributions: {state.contributions.length}</p>
    </div>
  )
}

// Test component for WalletContext
function WalletTestComponent() {
  const { state } = useWallet()
  const isConnected = state.wallet !== null && state.connectedWallet !== null

  return (
    <div data-testid="wallet-context">
      <p>Connected: {isConnected.toString()}</p>
      <p>Wallet Address: {state.wallet?.address || 'none'}</p>
    </div>
  )
}

describe('Context Providers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('TokenProvider renders children without crashing', () => {
    render(
      <TokenProvider>
        <TokenTestComponent />
      </TokenProvider>
    )

    expect(screen.getByTestId('token-context')).toBeInTheDocument()
  })

  it('ContributionsProvider renders children without crashing', () => {
    render(
      <ContributionsProvider>
        <ContributionsTestComponent />
      </ContributionsProvider>
    )

    expect(screen.getByTestId('contributions-context')).toBeInTheDocument()
  })

  it('WalletProvider renders children without crashing', () => {
    render(
      <WalletProvider>
        <WalletTestComponent />
      </WalletProvider>
    )

    expect(screen.getByTestId('wallet-context')).toBeInTheDocument()
  })

  it('TokenProvider initializes with correct default state', () => {
    render(
      <TokenProvider>
        <TokenTestComponent />
      </TokenProvider>
    )

    expect(screen.getByText('Loading: false')).toBeInTheDocument()
    expect(screen.getByText('Error: none')).toBeInTheDocument()
    expect(screen.getByText('NIMO Tokens: 0')).toBeInTheDocument()
  })

  it('ContributionsProvider initializes with correct default state', () => {
    render(
      <ContributionsProvider>
        <ContributionsTestComponent />
      </ContributionsProvider>
    )

    expect(screen.getByText('Loading: false')).toBeInTheDocument()
    expect(screen.getByText('Contributions: 0')).toBeInTheDocument()
  })

  it('WalletProvider initializes with correct default state', () => {
    render(
      <WalletProvider>
        <WalletTestComponent />
      </WalletProvider>
    )

    expect(screen.getByText('Connected: false')).toBeInTheDocument()
    expect(screen.getByText('Wallet Address: none')).toBeInTheDocument()
  })
})

describe('Context Hooks', () => {
  it('useTokens hook throws error when used outside provider', () => {
    expect(() => {
      render(<TokenTestComponent />)
    }).toThrow('useTokens must be used within a TokenProvider')
  })

  it('useContributions hook throws error when used outside provider', () => {
    expect(() => {
      render(<ContributionsTestComponent />)
    }).toThrow('useContributions must be used within a ContributionsProvider')
  })

  it('useWallet hook throws error when used outside provider', () => {
    expect(() => {
      render(<WalletTestComponent />)
    }).toThrow('useWallet must be used within a WalletProvider')
  })
})
