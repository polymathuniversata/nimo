import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { TokenBalance } from '../TokenBalance'
import { TokenProvider } from '../../contexts/TokenContext'
import { WalletProvider } from '../../contexts/WalletContext'

// Mock the token and wallet contexts
vi.mock('../../contexts/TokenContext', () => ({
  TokenProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useTokens: () => ({
    state: {
      balance: {
        adaBalance: 1500.50,
        nimoTokens: 25000,
        availableTokens: 20000,
        stakedTokens: 5000
      },
      transactions: [
        {
          id: 'tx1',
          type: 'reward',
          description: 'Contribution verification reward',
          amount: 150,
          timestamp: '2024-01-20T10:00:00Z'
        },
        {
          id: 'tx2',
          type: 'transfer',
          description: 'Token transfer to user123',
          amount: -50,
          timestamp: '2024-01-19T15:30:00Z'
        },
        {
          id: 'tx3',
          type: 'stake',
          description: 'Staking reward',
          amount: 25,
          timestamp: '2024-01-18T09:15:00Z'
        }
      ],
      loading: false,
      error: null
    },
    refreshData: vi.fn(),
    formatADA: vi.fn((amount) => `${amount.toFixed(2)} ADA`)
  })
}))

vi.mock('../../contexts/WalletContext', () => ({
  WalletProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useWallet: () => ({
    state: {
      wallet: {
        walletName: 'Nami Wallet',
        network: 'Preview'
      },
      connected: true
    }
  })
}))

// Mock react-router-dom's useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn()
  }
})

const renderTokenBalance = (props = {}) => {
  return render(
    <TokenProvider>
      <WalletProvider>
        <TokenBalance {...props} />
      </WalletProvider>
    </TokenProvider>
  )
}

describe('TokenBalance', () => {
  it('renders balance overview correctly', () => {
    renderTokenBalance()

    expect(screen.getByText('Token Balance')).toBeInTheDocument()
    expect(screen.getByText('Nami Wallet • Preview')).toBeInTheDocument()
  })

  it('displays total balance correctly', () => {
    renderTokenBalance()

    expect(screen.getByText('1,500.50 ADA')).toBeInTheDocument()
  })

  it('shows masked balance when visibility is toggled off', () => {
    renderTokenBalance()

    const visibilityButton = screen.getByRole('button', { name: /eye/i })
    fireEvent.click(visibilityButton)

    expect(screen.getByText('••••••')).toBeInTheDocument()
  })

  it('displays portfolio change indicator', () => {
    renderTokenBalance()

    expect(screen.getByText('+12.5% this month')).toBeInTheDocument()
    const trendingUpIcon = document.querySelector('.text-green-500')
    expect(trendingUpIcon).toBeInTheDocument()
  })

  it('shows NIMO tokens breakdown', () => {
    renderTokenBalance()

    expect(screen.getByText('NIMO Tokens')).toBeInTheDocument()
    expect(screen.getByText('25K')).toBeInTheDocument()
    expect(screen.getByText('Available: 20K')).toBeInTheDocument()
  })

  it('shows ADA balance breakdown', () => {
    renderTokenBalance()

    expect(screen.getByText('ADA Balance')).toBeInTheDocument()
    expect(screen.getByText('1,500.50 ADA')).toBeInTheDocument()
    expect(screen.getByText('Staked: 5K')).toBeInTheDocument()
  })

  it('displays staking progress when tokens are staked', () => {
    renderTokenBalance()

    expect(screen.getByText('Staking Progress')).toBeInTheDocument()
    expect(screen.getByText('20% staked')).toBeInTheDocument()
  })

  it('shows recent transactions', () => {
    renderTokenBalance()

    expect(screen.getByText('Recent Transactions')).toBeInTheDocument()
    expect(screen.getByText('Contribution verification reward')).toBeInTheDocument()
    expect(screen.getByText('Token transfer to user123')).toBeInTheDocument()
    expect(screen.getByText('Staking reward')).toBeInTheDocument()
  })

  it('displays transaction amounts with correct colors', () => {
    renderTokenBalance()

    expect(screen.getByText('+150')).toHaveClass('text-green-600')
    expect(screen.getByText('-50')).toHaveClass('text-red-600')
  })

  it('shows transaction type badges', () => {
    renderTokenBalance()

    expect(screen.getByText('reward')).toBeInTheDocument()
    expect(screen.getByText('transfer')).toBeInTheDocument()
    expect(screen.getByText('stake')).toBeInTheDocument()
  })

  it('shows transaction timestamps', () => {
    renderTokenBalance()

    expect(screen.getByText('1/20/2024, 10:00:00 AM')).toBeInTheDocument()
    expect(screen.getByText('1/19/2024, 3:30:00 PM')).toBeInTheDocument()
  })

  it('limits transactions to maxTransactions prop', () => {
    renderTokenBalance({ maxTransactions: 2 })

    expect(screen.getByText('Contribution verification reward')).toBeInTheDocument()
    expect(screen.getByText('Token transfer to user123')).toBeInTheDocument()
    expect(screen.queryByText('Staking reward')).not.toBeInTheDocument()
  })

  it('shows "View All" button when onViewAll is provided', () => {
    const onViewAll = vi.fn()
    renderTokenBalance({ onViewAll })

    const viewAllButton = screen.getByRole('button', { name: /view all/i })
    expect(viewAllButton).toBeInTheDocument()
  })

  it('calls onViewAll when View All button is clicked', () => {
    const onViewAll = vi.fn()
    renderTokenBalance({ onViewAll })

    const viewAllButton = screen.getByRole('button', { name: /view all/i })
    fireEvent.click(viewAllButton)

    expect(onViewAll).toHaveBeenCalledTimes(1)
  })

  it('calls refresh handler when refresh button is clicked', async () => {
    const refreshData = vi.fn()
    const { useTokens } = await import('../../contexts/TokenContext')
    vi.mocked(useTokens).mockReturnValue({
      state: {
        balance: {
          adaBalance: 1500.50,
          nimoTokens: 25000,
          availableTokens: 20000,
          stakedTokens: 5000
        },
        transactions: [],
        loading: false,
        error: null
      },
      refreshData,
      formatADA: vi.fn()
    })

    renderTokenBalance()

    const refreshButton = screen.getByRole('button', { name: /refresh/i })
    fireEvent.click(refreshButton)

    await waitFor(() => {
      expect(refreshData).toHaveBeenCalledTimes(1)
    })
  })

  it('shows loading state when refreshing', () => {
    const { useTokens } = vi.hoisted(() => ({
      useTokens: vi.fn()
    }))

    vi.mocked(useTokens).mockReturnValue({
      state: {
        balance: {
          adaBalance: 1500.50,
          nimoTokens: 25000,
          availableTokens: 20000,
          stakedTokens: 5000
        },
        transactions: [],
        loading: true,
        error: null
      },
      refreshData: vi.fn(),
      formatADA: vi.fn()
    })

    renderTokenBalance()

    const refreshButton = screen.getByRole('button', { name: /refresh/i })
    expect(refreshButton).toBeDisabled()
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('hides transactions when showTransactions is false', () => {
    renderTokenBalance({ showTransactions: false })

    expect(screen.queryByText('Recent Transactions')).not.toBeInTheDocument()
  })

  it('shows quick actions when showDetailedView is true', () => {
    renderTokenBalance({ showDetailedView: true })

    expect(screen.getByText('Quick Actions')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send tokens/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /stake tokens/i })).toBeInTheDocument()
  })

  it('hides quick actions when showDetailedView is false', () => {
    renderTokenBalance({ showDetailedView: false })

    expect(screen.queryByText('Quick Actions')).not.toBeInTheDocument()
  })

  it('shows error message when there is an error', () => {
    const { useTokens } = vi.hoisted(() => ({
      useTokens: vi.fn()
    }))

    vi.mocked(useTokens).mockReturnValue({
      state: {
        balance: {
          adaBalance: 1500.50,
          nimoTokens: 25000,
          availableTokens: 20000,
          stakedTokens: 5000
        },
        transactions: [],
        loading: false,
        error: 'Failed to load balance'
      },
      refreshData: vi.fn(),
      formatADA: vi.fn()
    })

    renderTokenBalance()

    expect(screen.getByText('Failed to load balance')).toBeInTheDocument()
  })

  it('shows empty state when no transactions', () => {
    const { useTokens } = vi.hoisted(() => ({
      useTokens: vi.fn()
    }))

    vi.mocked(useTokens).mockReturnValue({
      state: {
        balance: {
          adaBalance: 1500.50,
          nimoTokens: 25000,
          availableTokens: 20000,
          stakedTokens: 5000
        },
        transactions: [],
        loading: false,
        error: null
      },
      refreshData: vi.fn(),
      formatADA: vi.fn()
    })

    renderTokenBalance()

    expect(screen.getByText('No transactions yet')).toBeInTheDocument()
    expect(screen.getByText('Start contributing to earn rewards!')).toBeInTheDocument()
  })

  it('formats large numbers correctly', () => {
    const { useTokens } = vi.hoisted(() => ({
      useTokens: vi.fn()
    }))

    vi.mocked(useTokens).mockReturnValue({
      state: {
        balance: {
          adaBalance: 1500.50,
          nimoTokens: 2500000,
          availableTokens: 2000000,
          stakedTokens: 500000
        },
        transactions: [],
        loading: false,
        error: null
      },
      refreshData: vi.fn(),
      formatADA: vi.fn((amount) => `${amount.toFixed(2)} ADA`)
    })

    renderTokenBalance()

    expect(screen.getByText('2.5M')).toBeInTheDocument()
  })
})
