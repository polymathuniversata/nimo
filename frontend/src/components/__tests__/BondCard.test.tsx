import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BondCard, ImpactBond } from '../BondCard'
import { TokenProvider } from '../../contexts/TokenContext'

// Mock the useTokens hook
vi.mock('../../contexts/TokenContext', () => ({
  TokenProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useTokens: () => ({
    formatADA: vi.fn((amount) => `${amount} ADA`),
    balance: 1000,
    refreshBalance: vi.fn()
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

const mockBond: ImpactBond = {
  id: 'bond-1',
  title: 'Clean Water Initiative',
  description: 'Providing clean water access to rural communities in Kenya through sustainable infrastructure development.',
  category: 'environment',
  targetAmount: 50000,
  raisedAmount: 25000,
  minInvestment: 100,
  expectedReturn: 8,
  duration: 24,
  riskLevel: 'medium',
  location: {
    country: 'Kenya',
    region: 'Rift Valley',
    city: 'Nakuru'
  },
  beneficiaries: 5000,
  expectedImpact: 'Clean water access for 5,000 people, reducing waterborne diseases by 70%',
  status: 'active',
  creatorId: 'user-1',
  creatorName: 'Alice Johnson',
  createdAt: '2024-01-15T10:00:00Z',
  endDate: '2024-12-31T23:59:59Z',
  tags: ['water', 'infrastructure', 'health', 'sustainability', 'community'],
  milestones: [
    {
      id: 'milestone-1',
      title: 'Site Assessment',
      description: 'Complete geological and community needs assessment',
      targetDate: '2024-02-15T23:59:59Z',
      completed: true,
      completedDate: '2024-02-10T10:00:00Z'
    },
    {
      id: 'milestone-2',
      title: 'Well Construction',
      description: 'Construct 5 community water wells',
      targetDate: '2024-08-15T23:59:59Z',
      completed: false
    }
  ]
}

const mockFundedBond: ImpactBond = {
  ...mockBond,
  status: 'funded',
  raisedAmount: 50000
}

const mockCompletedBond: ImpactBond = {
  ...mockBond,
  status: 'completed',
  raisedAmount: 50000
}

const renderBondCard = (bond: ImpactBond) => {
  return render(
    <TokenProvider>
      <BondCard
        bond={bond}
        onInvest={vi.fn()}
        onViewDetails={vi.fn()}
      />
    </TokenProvider>
  )
}

describe('BondCard', () => {
  it('renders bond information correctly', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('Clean Water Initiative')).toBeInTheDocument()
    expect(screen.getByText('Providing clean water access to rural communities in Kenya through sustainable infrastructure development.')).toBeInTheDocument()
    expect(screen.getByText('MEDIUM RISK')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('displays correct location information', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('Nakuru, Kenya')).toBeInTheDocument()
    expect(screen.getByText('24 months')).toBeInTheDocument()
  })

  it('shows funding progress for active bonds', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('Funding Progress')).toBeInTheDocument()
    expect(screen.getByText('25000 ADA / 50000 ADA')).toBeInTheDocument()
    expect(screen.getByText('50% funded')).toBeInTheDocument()
  })

  it('calculates days remaining correctly', () => {
    renderBondCard(mockBond)

    const daysLeft = Math.ceil((new Date(mockBond.endDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    expect(screen.getByText(`${daysLeft} days left`)).toBeInTheDocument()
  })

  it('hides progress bar when showProgress is false', () => {
    render(
      <TokenProvider>
        <BondCard
          bond={mockBond}
          onInvest={vi.fn()}
          onViewDetails={vi.fn()}
          showProgress={false}
        />
      </TokenProvider>
    )

    expect(screen.queryByText('Funding Progress')).not.toBeInTheDocument()
  })

  it('displays correct status colors and text', () => {
    // Test active status
    const { rerender } = renderBondCard(mockBond)
    expect(document.querySelector('.bg-green-500')).toBeInTheDocument()

    // Test funded status
    rerender(
      <TokenProvider>
        <BondCard
          bond={mockFundedBond}
          onInvest={vi.fn()}
          onViewDetails={vi.fn()}
        />
      </TokenProvider>
    )
    expect(document.querySelector('.bg-blue-500')).toBeInTheDocument()
    expect(screen.getByText('Fully Funded')).toBeInTheDocument()

    // Test completed status
    rerender(
      <TokenProvider>
        <BondCard
          bond={mockCompletedBond}
          onInvest={vi.fn()}
          onViewDetails={vi.fn()}
        />
      </TokenProvider>
    )
    expect(document.querySelector('.bg-purple-500')).toBeInTheDocument()
    expect(screen.getByText('Completed')).toBeInTheDocument()
  })

  it('shows correct risk level styling', () => {
    renderBondCard(mockBond)

    const riskBadge = screen.getByText('MEDIUM RISK')
    expect(riskBadge).toHaveClass('text-yellow-600', 'bg-yellow-50', 'border-yellow-200')
  })

  it('displays statistics correctly', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('5000')).toBeInTheDocument()
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument()
    expect(screen.getByText('8%')).toBeInTheDocument()
    expect(screen.getByText('Expected Return')).toBeInTheDocument()
  })

  it('shows expected impact with icon', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('Clean water access for 5,000 people, reducing waterborne diseases by 70%')).toBeInTheDocument()
  })

  it('displays tags with limit of 4 plus "more" indicator', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('water')).toBeInTheDocument()
    expect(screen.getByText('infrastructure')).toBeInTheDocument()
    expect(screen.getByText('health')).toBeInTheDocument()
    expect(screen.getByText('sustainability')).toBeInTheDocument()
    expect(screen.getByText('+1 more')).toBeInTheDocument()
    expect(screen.queryByText('community')).not.toBeInTheDocument()
  })

  it('displays all tags when 4 or fewer', () => {
    const bondWithFewTags = {
      ...mockBond,
      tags: ['water', 'infrastructure', 'health']
    }

    render(
      <TokenProvider>
        <BondCard
          bond={bondWithFewTags}
          onInvest={vi.fn()}
          onViewDetails={vi.fn()}
        />
      </TokenProvider>
    )

    expect(screen.getByText('water')).toBeInTheDocument()
    expect(screen.getByText('infrastructure')).toBeInTheDocument()
    expect(screen.getByText('health')).toBeInTheDocument()
    expect(screen.queryByText('+1 more')).not.toBeInTheDocument()
  })

  it('calls onInvest when invest button is clicked', () => {
    const onInvest = vi.fn()
    render(
      <TokenProvider>
        <BondCard
          bond={mockBond}
          onInvest={onInvest}
          onViewDetails={vi.fn()}
        />
      </TokenProvider>
    )

    const investButton = screen.getByRole('button', { name: /invest/i })
    fireEvent.click(investButton)

    expect(onInvest).toHaveBeenCalledWith('bond-1')
  })

  it('disables invest button when bond is fully funded', () => {
    render(
      <TokenProvider>
        <BondCard
          bond={mockFundedBond}
          onInvest={vi.fn()}
          onViewDetails={vi.fn()}
        />
      </TokenProvider>
    )

    const investButton = screen.getByRole('button', { name: /invest/i })
    expect(investButton).toBeDisabled()
  })

  it('calls onViewDetails when details button is clicked', () => {
    const onViewDetails = vi.fn()
    render(
      <TokenProvider>
        <BondCard
          bond={mockBond}
          onInvest={vi.fn()}
          onViewDetails={onViewDetails}
        />
      </TokenProvider>
    )

    const detailsButton = screen.getByRole('button', { name: /details/i })
    fireEvent.click(detailsButton)

    expect(onViewDetails).toHaveBeenCalledWith('bond-1')
  })

  it('displays creator information correctly', () => {
    renderBondCard(mockBond)

    expect(screen.getByText('By Alice Johnson')).toBeInTheDocument()
    expect(screen.getByText('1/15/2024')).toBeInTheDocument()
  })

  it('shows bond image when provided', () => {
    const bondWithImage = {
      ...mockBond,
      images: ['/images/water-project.jpg']
    }

    render(
      <TokenProvider>
        <BondCard
          bond={bondWithImage}
          onInvest={vi.fn()}
          onViewDetails={vi.fn()}
        />
      </TokenProvider>
    )

    const image = document.querySelector('img[alt="Clean Water Initiative"]')
    expect(image).toHaveAttribute('src', '/images/water-project.jpg')
  })

  it('applies hover effects correctly', () => {
    renderBondCard(mockBond)

    const card = document.querySelector('.hover\\:shadow-lg')
    expect(card).toBeInTheDocument()
  })
})
