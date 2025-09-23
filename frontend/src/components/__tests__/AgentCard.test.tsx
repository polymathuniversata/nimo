import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { AgentCard, Agent } from '../AgentCard'
import { AuthProvider } from '../../contexts/AuthContext'

// Mock the useAuth hook
vi.mock('../../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    hasRole: vi.fn(),
    user: null,
    isAuthenticated: false
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

const mockAgent: Agent = {
  id: 'agent-1',
  name: 'Verification Agent',
  description: 'Handles contribution verification and fraud detection',
  category: 'verification',
  healthScore: 95,
  totalDecisions: 150,
  recentDecisions: 25,
  accuracy: 98,
  status: 'active',
  lastActive: '2024-01-20T10:30:00Z',
  capabilities: ['fraud-detection', 'verification', 'analysis', 'reporting']
}

const renderAgentCard = (agent: Agent, isAdmin = false) => {
  // Mock the hasRole function to return isAdmin
  const { useAuth } = vi.hoisted(() => ({
    useAuth: vi.fn()
  }))
  vi.mocked(useAuth).mockReturnValue({
    hasRole: vi.fn().mockReturnValue(isAdmin),
    user: null,
    isAuthenticated: false
  })

  return render(
    <AuthProvider>
      <AgentCard
        agent={agent}
        onOverride={isAdmin ? vi.fn() : undefined}
        onViewDetails={vi.fn()}
      />
    </AuthProvider>
  )
}

describe('AgentCard', () => {
  it('renders agent information correctly', () => {
    renderAgentCard(mockAgent)

    expect(screen.getByText('Verification Agent')).toBeInTheDocument()
    expect(screen.getByText('Handles contribution verification and fraud detection')).toBeInTheDocument()
    expect(screen.getByText('verification')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
    expect(screen.getByText('98%')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
    expect(screen.getByText('95%')).toBeInTheDocument()
  })

  it('displays the correct status indicator', () => {
    renderAgentCard(mockAgent)
    const statusIndicator = document.querySelector('.bg-green-500')
    expect(statusIndicator).toBeInTheDocument()
  })

  it('shows capabilities with limit of 3 plus "more" indicator', () => {
    renderAgentCard(mockAgent)

    expect(screen.getByText('fraud-detection')).toBeInTheDocument()
    expect(screen.getByText('verification')).toBeInTheDocument()
    expect(screen.getByText('analysis')).toBeInTheDocument()
    expect(screen.getByText('+1 more')).toBeInTheDocument()
    expect(screen.queryByText('reporting')).not.toBeInTheDocument()
  })

  it('displays all capabilities when less than or equal to 3', () => {
    const agentWithFewCapabilities = {
      ...mockAgent,
      capabilities: ['fraud-detection', 'verification']
    }
    renderAgentCard(agentWithFewCapabilities)

    expect(screen.getByText('fraud-detection')).toBeInTheDocument()
    expect(screen.getByText('verification')).toBeInTheDocument()
    expect(screen.queryByText('+1 more')).not.toBeInTheDocument()
  })

  it('displays correct category icon', () => {
    renderAgentCard(mockAgent)
    // Award icon should be present for verification category
    const awardIcon = document.querySelector('svg')
    expect(awardIcon).toBeInTheDocument()
  })

  it('shows admin override button when user is admin', () => {
    renderAgentCard(mockAgent, true)

    const overrideButton = screen.getByRole('button', { name: /more/i })
    expect(overrideButton).toBeInTheDocument()
  })

  it('hides admin override button when user is not admin', () => {
    renderAgentCard(mockAgent, false)

    const overrideButton = screen.queryByRole('button', { name: /more/i })
    expect(overrideButton).not.toBeInTheDocument()
  })

  it('calls onOverride when admin override button is clicked', () => {
    const onOverride = vi.fn()
    render(
      <AuthProvider>
        <AgentCard
          agent={mockAgent}
          onOverride={onOverride}
          onViewDetails={vi.fn()}
        />
      </AuthProvider>
    )

    const overrideButton = screen.getByRole('button', { name: /more/i })
    fireEvent.click(overrideButton)

    expect(onOverride).toHaveBeenCalledWith('agent-1')
  })

  it('calls onViewDetails when view details button is clicked', () => {
    const onViewDetails = vi.fn()
    renderAgentCard(mockAgent)

    const viewDetailsButton = screen.getByRole('button', { name: /view details/i })
    fireEvent.click(viewDetailsButton)

    expect(onViewDetails).toHaveBeenCalledWith('agent-1')
  })

  it('displays correct last active date', () => {
    renderAgentCard(mockAgent)

    expect(screen.getByText('Last active: 1/20/2024')).toBeInTheDocument()
  })

  it('shows avatar fallback when no avatar image provided', () => {
    renderAgentCard(mockAgent)

    expect(screen.getByText('VE')).toBeInTheDocument()
  })

  it('shows avatar image when provided', () => {
    const agentWithAvatar = { ...mockAgent, avatar: '/path/to/avatar.jpg' }
    renderAgentCard(agentWithAvatar)

    const avatarImage = document.querySelector('img[alt="Verification Agent"]')
    expect(avatarImage).toHaveAttribute('src', '/path/to/avatar.jpg')
  })

  it('applies hover effects correctly', () => {
    renderAgentCard(mockAgent)

    const card = document.querySelector('.hover\\:shadow-lg')
    expect(card).toBeInTheDocument()
  })
})
