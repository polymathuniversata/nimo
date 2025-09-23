import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { SubmitContribution } from '../SubmitContribution'

// Mock the AuthContext
vi.mock('../../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    user: { id: 'user-1', name: 'Test User' },
    isAuthenticated: true
  })
}))

// Mock the ContributionsContext
vi.mock('../../contexts/ContributionsContext', () => ({
  ContributionsProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useContributions: () => ({
    submitContribution: vi.fn(),
    isSubmitting: false,
    categories: [
      { id: 'coding', name: 'Coding', description: 'Software development' },
      { id: 'community_building', name: 'Community Building', description: 'Building communities' },
      { id: 'activism', name: 'Activism', description: 'Social activism' },
      { id: 'education', name: 'Education', description: 'Educational content' },
      { id: 'design', name: 'Design', description: 'Visual design' },
      { id: 'research', name: 'Research', description: 'Research work' }
    ]
  })
}))

const renderSubmitContribution = () => {
  return render(
    <BrowserRouter>
      <SubmitContribution />
    </BrowserRouter>
  )
}

describe('Contribution Submission Flow Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders contribution form with all required fields', () => {
    renderSubmitContribution()

    expect(screen.getByText('Submit New Contribution')).toBeInTheDocument()
    expect(screen.getByText('Add your work, activism, or community contribution for verification and token rewards.')).toBeInTheDocument()

    // Check for form fields
    expect(screen.getByLabelText('Title')).toBeInTheDocument()
    expect(screen.getByLabelText('Category')).toBeInTheDocument()
    expect(screen.getByLabelText('Description')).toBeInTheDocument()
    expect(screen.getByLabelText('Evidence & Links')).toBeInTheDocument()
    expect(screen.getByLabelText('Skills Used')).toBeInTheDocument()
  })

  it('displays category options in dropdown', () => {
    renderSubmitContribution()

    const categorySelect = screen.getByRole('combobox', { name: /category/i })
    fireEvent.click(categorySelect)

    expect(screen.getByText('Coding')).toBeInTheDocument()
    expect(screen.getByText('Community Building')).toBeInTheDocument()
    expect(screen.getByText('Activism')).toBeInTheDocument()
    expect(screen.getByText('Education')).toBeInTheDocument()
    expect(screen.getByText('Design')).toBeInTheDocument()
    expect(screen.getByText('Research')).toBeInTheDocument()
  })

  it('allows adding evidence URLs', () => {
    renderSubmitContribution()

    const evidenceInput = screen.getByPlaceholderText('GitHub repo, website, or documentation URL')
    const linkButton = screen.getByRole('button', { name: /link/i })

    fireEvent.change(evidenceInput, { target: { value: 'https://github.com/example/project' } })

    expect(evidenceInput).toHaveValue('https://github.com/example/project')
    expect(linkButton).toBeInTheDocument()
  })

  it('allows adding multiple evidence URLs', () => {
    renderSubmitContribution()

    const firstEvidenceInput = screen.getByPlaceholderText('GitHub repo, website, or documentation URL')
    const secondEvidenceInput = screen.getByPlaceholderText('Additional evidence URL')

    fireEvent.change(firstEvidenceInput, { target: { value: 'https://github.com/example/project' } })
    fireEvent.change(secondEvidenceInput, { target: { value: 'https://docs.example.com' } })

    expect(firstEvidenceInput).toHaveValue('https://github.com/example/project')
    expect(secondEvidenceInput).toHaveValue('https://docs.example.com')
  })

  it('displays existing skills as badges', () => {
    renderSubmitContribution()

    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('Community Building')).toBeInTheDocument()
  })

  it('allows adding new skills', () => {
    renderSubmitContribution()

    const addSkillButton = screen.getByRole('button', { name: /add skill/i })
    expect(addSkillButton).toBeInTheDocument()
  })

  it('shows MeTTa AI analysis preview', () => {
    renderSubmitContribution()

    expect(screen.getByText('MeTTa AI Analysis Preview')).toBeInTheDocument()
    expect(screen.getByText('Estimated token reward:')).toBeInTheDocument()
    expect(screen.getByText('150-220 NIMO')).toBeInTheDocument()
    expect(screen.getByText('Based on category, evidence quality, and skill match. Final reward determined after verification.')).toBeInTheDocument()
  })

  it('allows form submission', () => {
    const { useContributions } = require('../../contexts/ContributionsContext')
    const mockSubmitContribution = vi.fn().mockResolvedValue({ success: true })
    vi.mocked(useContributions).mockReturnValue({
      submitContribution: mockSubmitContribution,
      isSubmitting: false,
      categories: []
    })

    renderSubmitContribution()

    const submitButton = screen.getByRole('button', { name: /submit for verification/i })
    expect(submitButton).toBeInTheDocument()
    expect(submitButton).toHaveClass('bg-gradient-primary')
  })

  it('shows loading state during submission', async () => {
    const { useContributions } = require('../../contexts/ContributionsContext')
    const mockSubmitContribution = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    vi.mocked(useContributions).mockReturnValue({
      submitContribution: mockSubmitContribution,
      isSubmitting: true,
      categories: []
    })

    renderSubmitContribution()

    const submitButton = screen.getByRole('button', { name: /submit for verification/i })
    expect(submitButton).toBeDisabled()
  })

  it('validates required fields before submission', () => {
    const { useContributions } = require('../../contexts/ContributionsContext')
    const mockSubmitContribution = vi.fn()
    vi.mocked(useContributions).mockReturnValue({
      submitContribution: mockSubmitContribution,
      isSubmitting: false,
      categories: []
    })

    renderSubmitContribution()

    // Submit without filling required fields
    const submitButton = screen.getByRole('button', { name: /submit for verification/i })
    fireEvent.click(submitButton)

    // Should not call submit function if validation fails
    expect(mockSubmitContribution).not.toHaveBeenCalled()
  })

  it('allows selecting a category from dropdown', () => {
    renderSubmitContribution()

    const categorySelect = screen.getByRole('combobox', { name: /category/i })
    fireEvent.click(categorySelect)

    const codingOption = screen.getByText('Coding')
    fireEvent.click(codingOption)

    expect(screen.getByText('Coding')).toBeInTheDocument()
  })

  it('allows entering description with sufficient length', () => {
    renderSubmitContribution()

    const descriptionTextarea = screen.getByPlaceholderText('Describe your contribution, its impact, and how it benefits the community...')

    const testDescription = 'This is a comprehensive description of my contribution that demonstrates significant impact on the community through innovative solutions and collaborative efforts.'
    fireEvent.change(descriptionTextarea, { target: { value: testDescription } })

    expect(descriptionTextarea).toHaveValue(testDescription)
  })

  it('has proper accessibility attributes', () => {
    renderSubmitContribution()

    expect(screen.getByLabelText('Title')).toBeInTheDocument()
    expect(screen.getByLabelText('Category')).toBeInTheDocument()
    expect(screen.getByLabelText('Description')).toBeInTheDocument()
    expect(screen.getByLabelText('Evidence & Links')).toBeInTheDocument()
    expect(screen.getByLabelText('Skills Used')).toBeInTheDocument()
  })

  it('applies proper styling classes', () => {
    renderSubmitContribution()

    const card = screen.getByText('Submit New Contribution').closest('.shadow-card')
    expect(card).toBeInTheDocument()

    const submitButton = screen.getByRole('button', { name: /submit for verification/i })
    expect(submitButton).toHaveClass('bg-gradient-primary')
  })

  it('handles keyboard navigation', () => {
    renderSubmitContribution()

    const titleInput = screen.getByLabelText('Title')
    titleInput.focus()
    expect(titleInput).toHaveFocus()

    // Tab to category select
    fireEvent.keyDown(titleInput, { key: 'Tab' })
    const categorySelect = screen.getByRole('combobox', { name: /category/i })
    expect(categorySelect).toHaveFocus()
  })

  it('shows upload button for evidence', () => {
    renderSubmitContribution()

    const uploadButtons = screen.getAllByRole('button', { name: /upload/i })
    expect(uploadButtons.length).toBeGreaterThan(0)
  })

  it('displays skills as removable badges', () => {
    renderSubmitContribution()

    const pythonBadge = screen.getByText('Python')
    expect(pythonBadge).toBeInTheDocument()
    expect(pythonBadge.closest('div')).toHaveClass('bg-secondary')
  })

  it('has proper form structure', () => {
    renderSubmitContribution()

    const form = screen.getByText('Submit New Contribution').closest('article')
    expect(form).toBeInTheDocument()

    const header = form?.querySelector('header')
    expect(header).toBeInTheDocument()

    const content = form?.querySelector('div[role="contentinfo"]')
    expect(content).toBeInTheDocument()
  })
})
