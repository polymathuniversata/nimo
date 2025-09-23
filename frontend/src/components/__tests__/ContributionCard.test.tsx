import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ContributionCard } from '../ContributionCard'

// Mock react-router-dom's useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn()
  }
})

const mockProps = {
  id: 'contribution-1',
  title: 'Solar Panel Installation Project',
  category: 'Sustainability',
  description: 'Installed 50 solar panels at local school, providing clean energy and reducing electricity costs by 70%.',
  status: 'verified' as const,
  impact: 'significant' as const,
  tokenReward: 150,
  evidenceUrl: 'https://example.com/evidence.pdf',
  verifierName: 'Green Energy Corp'
}

const mockPendingContribution = {
  ...mockProps,
  status: 'pending' as const,
  impact: 'moderate' as const,
  tokenReward: 75,
  verifierName: undefined
}

const mockRejectedContribution = {
  ...mockProps,
  status: 'rejected' as const,
  impact: 'low' as const,
  tokenReward: 0,
  verifierName: 'Verification Team'
}

describe('ContributionCard', () => {
  it('renders contribution information correctly', () => {
    render(<ContributionCard {...mockProps} />)

    expect(screen.getByText('Solar Panel Installation Project')).toBeInTheDocument()
    expect(screen.getByText('Sustainability')).toBeInTheDocument()
    expect(screen.getByText('Installed 50 solar panels at local school, providing clean energy and reducing electricity costs by 70%.')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
    expect(screen.getByText('NIMO')).toBeInTheDocument()
  })

  it('displays correct status badge with icon', () => {
    render(<ContributionCard {...mockProps} />)

    expect(screen.getByText('verified')).toBeInTheDocument()
    const statusBadge = screen.getByText('verified').closest('div')
    expect(statusBadge).toHaveClass('text-verification-green', 'bg-verification-green/10')
  })

  it('shows different status configurations', () => {
    // Test verified status
    const { rerender } = render(<ContributionCard {...mockProps} />)
    expect(document.querySelector('.text-verification-green')).toBeInTheDocument()

    // Test pending status
    rerender(<ContributionCard {...mockPendingContribution} />)
    expect(document.querySelector('.text-primary')).toBeInTheDocument()

    // Test rejected status
    rerender(<ContributionCard {...mockRejectedContribution} />)
    expect(document.querySelector('.text-destructive')).toBeInTheDocument()
  })

  it('displays correct impact level styling', () => {
    // Test significant impact
    const { rerender } = render(<ContributionCard {...mockProps} />)
    const impactText = screen.getByText('Significant')
    expect(impactText).toHaveClass('text-token-gold')

    // Test moderate impact
    rerender(<ContributionCard {...mockPendingContribution} />)
    expect(screen.getByText('Moderate')).toHaveClass('text-primary')

    // Test low impact
    rerender(<ContributionCard {...mockRejectedContribution} />)
    expect(screen.getByText('Low')).toHaveClass('text-muted-foreground')
  })

  it('shows verifier name when provided', () => {
    render(<ContributionCard {...mockProps} />)

    expect(screen.getByText('Verified by Green Energy Corp')).toBeInTheDocument()
  })

  it('hides verifier name when not provided', () => {
    render(<ContributionCard {...mockPendingContribution} />)

    expect(screen.queryByText(/Verified by/)).not.toBeInTheDocument()
  })

  it('shows evidence button when evidence URL is provided', () => {
    render(<ContributionCard {...mockProps} />)

    const evidenceButton = screen.getByRole('button', { name: /evidence/i })
    expect(evidenceButton).toBeInTheDocument()
    expect(evidenceButton).toHaveAttribute('href', 'https://example.com/evidence.pdf')
  })

  it('opens evidence link in new tab', () => {
    render(<ContributionCard {...mockProps} />)

    const evidenceLink = screen.getByRole('link', { name: /evidence/i })
    expect(evidenceLink).toHaveAttribute('target', '_blank')
    expect(evidenceLink).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('shows details button always', () => {
    render(<ContributionCard {...mockProps} />)

    const detailsButton = screen.getByRole('button', { name: /details/i })
    expect(detailsButton).toBeInTheDocument()
  })

  it('applies hover effects correctly', () => {
    render(<ContributionCard {...mockProps} />)

    const card = document.querySelector('.hover\\:shadow-glow')
    expect(card).toBeInTheDocument()
  })

  it('displays correct token reward for different statuses', () => {
    // Test verified contribution
    const { rerender } = render(<ContributionCard {...mockProps} />)
    expect(screen.getByText('150')).toBeInTheDocument()

    // Test pending contribution
    rerender(<ContributionCard {...mockPendingContribution} />)
    expect(screen.getByText('75')).toBeInTheDocument()

    // Test rejected contribution
    rerender(<ContributionCard {...mockRejectedContribution} />)
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('has correct card structure', () => {
    render(<ContributionCard {...mockProps} />)

    expect(document.querySelector('article')).toBeInTheDocument() // Card element
    expect(document.querySelector('header')).toBeInTheDocument() // CardHeader
    expect(document.querySelector('div[role="contentinfo"]')).toBeInTheDocument() // CardContent
  })

  it('displays category badge correctly', () => {
    render(<ContributionCard {...mockProps} />)

    const categoryBadge = screen.getByText('Sustainability')
    expect(categoryBadge).toBeInTheDocument()
    expect(categoryBadge.closest('div')).toHaveClass('bg-secondary')
  })
})
