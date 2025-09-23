import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AgentCard } from '@/components/AgentCard'
import { BondCard } from '@/components/BondCard'
import { ProposalCard } from '@/components/ProposalCard'
import { TokenBalance } from '@/components/TokenBalance'

describe('AgentCard', () => {
  const mockAgent = {
    id: '1',
    name: 'Verification Agent Alpha',
    description: 'AI agent for contribution verification',
    category: 'verification' as const,
    healthScore: 85,
    totalDecisions: 1250,
    recentDecisions: 45,
    accuracy: 92,
    status: 'active' as const,
    lastActive: new Date().toISOString(),
    capabilities: ['pattern recognition', 'document analysis', 'fraud detection']
  }

  it('renders agent information correctly', () => {
    render(<AgentCard agent={mockAgent} />)

    expect(screen.getByText(mockAgent.name)).toBeInTheDocument()
    expect(screen.getByText(mockAgent.description)).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('1250')).toBeInTheDocument()
  })

  it('displays status indicator', () => {
    render(<AgentCard agent={mockAgent} />)

    const statusIndicator = screen.getByText('ACTIVE')
    expect(statusIndicator).toBeInTheDocument()
  })

  it('shows capabilities badges', () => {
    render(<AgentCard agent={mockAgent} />)

    expect(screen.getByText('pattern recognition')).toBeInTheDocument()
    expect(screen.getByText('document analysis')).toBeInTheDocument()
  })
})

describe('BondCard', () => {
  const mockBond = {
    id: '1',
    title: 'Youth Education Initiative',
    description: 'Providing education access to underserved youth',
    category: 'education' as const,
    targetAmount: 10000,
    raisedAmount: 6500,
    minInvestment: 100,
    expectedReturn: 8.5,
    duration: 12,
    riskLevel: 'medium' as const,
    location: { country: 'Kenya', city: 'Nairobi' },
    beneficiaries: 500,
    expectedImpact: '500 youth receive quality education',
    status: 'active' as const,
    creatorId: 'user1',
    creatorName: 'Education Foundation',
    createdAt: new Date().toISOString(),
    endDate: new Date(Date.now() + 86400000 * 30).toISOString(),
    tags: ['education', 'youth', 'impact'],
    milestones: [] // Add missing required property
  }

  it('renders bond information correctly', () => {
    render(<BondCard bond={mockBond} />)

    expect(screen.getByText(mockBond.title)).toBeInTheDocument()
    expect(screen.getByText(mockBond.description)).toBeInTheDocument()
    expect(screen.getByText('500')).toBeInTheDocument()
    expect(screen.getByText('8.5%')).toBeInTheDocument()
  })

  it('displays funding progress', () => {
    render(<BondCard bond={mockBond} />)

    expect(screen.getByText('Funding Progress')).toBeInTheDocument()
    expect(screen.getByText('65% funded')).toBeInTheDocument()
  })

  it('shows risk level badge', () => {
    render(<BondCard bond={mockBond} />)

    expect(screen.getByText('MEDIUM RISK')).toBeInTheDocument()
  })
})

describe('ProposalCard', () => {
  const mockProposal = {
    id: '1',
    title: 'Improve User Dashboard UX',
    description: 'Enhance the user dashboard with better navigation and mobile responsiveness',
    type: 'improvement' as const,
    status: 'active' as const,
    priority: 'high' as const,
    authorId: 'user1',
    authorName: 'John Doe',
    createdAt: new Date().toISOString(),
    endDate: new Date(Date.now() + 86400000 * 14).toISOString(),
    totalVotes: 45,
    yesVotes: 32,
    noVotes: 8,
    abstainVotes: 5,
    quorum: 20,
    requiredMajority: 60,
    tags: ['ux', 'dashboard', 'improvement'],
    category: 'technical' as const,
    expectedImpact: 'Better user experience for all platform users'
  }

  it('renders proposal information correctly', () => {
    render(<ProposalCard proposal={mockProposal} />)

    expect(screen.getByText(mockProposal.title)).toBeInTheDocument()
    expect(screen.getByText(mockProposal.description)).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('displays voting information', () => {
    render(<ProposalCard proposal={mockProposal} />)

    expect(screen.getByText('45 votes')).toBeInTheDocument()
    expect(screen.getByText('71%')).toBeInTheDocument() // Yes percentage
    expect(screen.getByText('18%')).toBeInTheDocument() // No percentage
  })

  it('shows vote buttons when active', () => {
    render(<ProposalCard proposal={mockProposal} showVoteButtons={true} />)

    expect(screen.getByText('Yes (32)')).toBeInTheDocument()
    expect(screen.getByText('No (8)')).toBeInTheDocument()
  })
})

describe('TokenBalance', () => {
  it('renders balance information', () => {
    render(<TokenBalance />)

    // Should render without crashing
    expect(document.querySelector('[data-testid="token-balance"]')).toBeInTheDocument()
  })

  it('handles refresh functionality', async () => {
    const user = userEvent.setup()
    render(<TokenBalance />)

    // Should handle refresh button click
    const refreshButton = screen.getByRole('button', { name: /refresh/i })
    await user.click(refreshButton)
  })
})
