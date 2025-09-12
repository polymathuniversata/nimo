import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SubmitContribution } from '../../components/SubmitContribution';

// Mock UI components
vi.mock('@/components/ui/card', () => ({
  Card: ({ children, className }: { children?: React.ReactNode; className?: string }) =>
    React.createElement('div', { className, 'data-testid': 'card' }, children),
  CardContent: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-content' }, children),
  CardHeader: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-header' }, children),
  CardTitle: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'card-title' }, children),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, variant, className, size, asChild, ...props }: {
    children?: React.ReactNode;
    variant?: string;
    className?: string;
    size?: string;
    asChild?: boolean;
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
  Input: ({ placeholder, className, ...props }: {
    placeholder?: string;
    className?: string;
    [key: string]: unknown;
  }) =>
    React.createElement('input', {
      placeholder,
      className,
      ...props
    }),
}));

vi.mock('@/components/ui/textarea', () => ({
  Textarea: ({ placeholder, className, minH, ...props }: {
    placeholder?: string;
    className?: string;
    minH?: string;
    [key: string]: unknown;
  }) =>
    React.createElement('textarea', {
      placeholder,
      className,
      ...props
    }),
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

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant }: { children?: React.ReactNode; variant?: string }) =>
    React.createElement('span', { 'data-variant': variant }, children),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Plus: () => React.createElement('span', { 'data-testid': 'plus-icon' }, 'Plus'),
  Upload: () => React.createElement('span', { 'data-testid': 'upload-icon' }, 'Upload'),
  Link: () => React.createElement('span', { 'data-testid': 'link-icon' }, 'Link'),
}));

describe('SubmitContribution', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial Render', () => {
    it('should render the contribution submission form', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Submit New Contribution')).toBeInTheDocument();
      expect(screen.getByText('Add your work, activism, or community contribution for verification and token rewards.')).toBeInTheDocument();
    });

    it('should render all form fields', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Title')).toBeInTheDocument();
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('Evidence & Links')).toBeInTheDocument();
      expect(screen.getByText('Skills Used')).toBeInTheDocument();
    });

    it('should render submit button', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Submit for Verification')).toBeInTheDocument();
    });
  });

  describe('Form Fields', () => {
    it('should render title input field', () => {
      render(<SubmitContribution />);

      const titleInput = screen.getByPlaceholderText('e.g., KRNL Hackathon Project');
      expect(titleInput).toBeInTheDocument();
      expect(titleInput).toHaveAttribute('type', 'text');
    });

    it('should render category select field', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Select category')).toBeInTheDocument();
      expect(screen.getByText('Coding')).toBeInTheDocument();
      expect(screen.getByText('Community Building')).toBeInTheDocument();
      expect(screen.getByText('Activism')).toBeInTheDocument();
      expect(screen.getByText('Education')).toBeInTheDocument();
      expect(screen.getByText('Design')).toBeInTheDocument();
      expect(screen.getByText('Research')).toBeInTheDocument();
    });

    it('should render description textarea', () => {
      render(<SubmitContribution />);

      const descriptionTextarea = screen.getByPlaceholderText('Describe your contribution, its impact, and how it benefits the community...');
      expect(descriptionTextarea).toBeInTheDocument();
      expect(descriptionTextarea.tagName).toBe('TEXTAREA');
    });

    it('should render evidence and links inputs', () => {
      render(<SubmitContribution />);

      expect(screen.getByPlaceholderText('GitHub repo, website, or documentation URL')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Additional evidence URL')).toBeInTheDocument();
    });
  });

  describe('Skills Section', () => {
    it('should render skills section with default badges', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Python')).toBeInTheDocument();
      expect(screen.getByText('Community Building')).toBeInTheDocument();
    });

    it('should render add skill button', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Add Skill')).toBeInTheDocument();
      expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
    });
  });

  describe('MeTTa AI Analysis Preview', () => {
    it('should render AI analysis preview section', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('MeTTa AI Analysis Preview')).toBeInTheDocument();
      expect(screen.getByText('Estimated token reward:')).toBeInTheDocument();
      expect(screen.getByText('150-220 NIMO')).toBeInTheDocument();
    });

    it('should show analysis explanation', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Based on category, evidence quality, and skill match. Final reward determined after verification.')).toBeInTheDocument();
    });
  });

  describe('Form Interactions', () => {
    it('should allow typing in title field', () => {
      render(<SubmitContribution />);

      const titleInput = screen.getByPlaceholderText('e.g., KRNL Hackathon Project');
      fireEvent.change(titleInput, { target: { value: 'My Awesome Project' } });

      expect(titleInput).toHaveValue('My Awesome Project');
    });

    it('should allow typing in description field', () => {
      render(<SubmitContribution />);

      const descriptionTextarea = screen.getByPlaceholderText('Describe your contribution, its impact, and how it benefits the community...');
      const testDescription = 'This is a test description for my contribution.';
      fireEvent.change(descriptionTextarea, { target: { value: testDescription } });

      expect(descriptionTextarea).toHaveValue(testDescription);
    });

    it('should allow typing in evidence URL fields', () => {
      render(<SubmitContribution />);

      const mainUrlInput = screen.getByPlaceholderText('GitHub repo, website, or documentation URL');
      const additionalUrlInput = screen.getByPlaceholderText('Additional evidence URL');

      fireEvent.change(mainUrlInput, { target: { value: 'https://github.com/user/repo' } });
      fireEvent.change(additionalUrlInput, { target: { value: 'https://example.com/docs' } });

      expect(mainUrlInput).toHaveValue('https://github.com/user/repo');
      expect(additionalUrlInput).toHaveValue('https://example.com/docs');
    });

    it('should handle category selection', () => {
      render(<SubmitContribution />);

      const selectTrigger = screen.getByTestId('select-trigger');
      fireEvent.click(selectTrigger);

      // The select content should be visible (in a real implementation)
      // For this test, we just verify the structure exists
      expect(screen.getByText('Coding')).toBeInTheDocument();
    });
  });

  describe('Submit Button', () => {
    it('should render submit button with correct styling', () => {
      render(<SubmitContribution />);

      const submitButton = screen.getByText('Submit for Verification');
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveClass('bg-gradient-primary');
    });

    it('should be clickable', () => {
      render(<SubmitContribution />);

      const submitButton = screen.getByText('Submit for Verification');
      expect(submitButton).not.toBeDisabled();

      // Click the button (in a real implementation, this would trigger form submission)
      fireEvent.click(submitButton);
      // No specific assertion here as the component doesn't have submit logic
    });
  });

  describe('Form Validation', () => {
    it('should allow empty form submission', () => {
      render(<SubmitContribution />);

      const submitButton = screen.getByText('Submit for Verification');
      fireEvent.click(submitButton);

      // The component doesn't have built-in validation, so no error should appear
      expect(submitButton).toBeInTheDocument();
    });

    it('should handle form data collection', () => {
      render(<SubmitContribution />);

      // Fill out the form
      const titleInput = screen.getByPlaceholderText('e.g., KRNL Hackathon Project');
      const descriptionTextarea = screen.getByPlaceholderText('Describe your contribution, its impact, and how it benefits the community...');
      const mainUrlInput = screen.getByPlaceholderText('GitHub repo, website, or documentation URL');

      fireEvent.change(titleInput, { target: { value: 'Test Project' } });
      fireEvent.change(descriptionTextarea, { target: { value: 'Test description' } });
      fireEvent.change(mainUrlInput, { target: { value: 'https://github.com/test/repo' } });

      // Verify values are set
      expect(titleInput).toHaveValue('Test Project');
      expect(descriptionTextarea).toHaveValue('Test description');
      expect(mainUrlInput).toHaveValue('https://github.com/test/repo');
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for form fields', () => {
      render(<SubmitContribution />);

      // Check that labels exist for form fields
      expect(screen.getByText('Title')).toBeInTheDocument();
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('Evidence & Links')).toBeInTheDocument();
      expect(screen.getByText('Skills Used')).toBeInTheDocument();
    });

    it('should have descriptive placeholders', () => {
      render(<SubmitContribution />);

      expect(screen.getByPlaceholderText('e.g., KRNL Hackathon Project')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Describe your contribution, its impact, and how it benefits the community...')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('GitHub repo, website, or documentation URL')).toBeInTheDocument();
    });

    it('should have proper button labels', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('Add Skill')).toBeInTheDocument();
      expect(screen.getByText('Submit for Verification')).toBeInTheDocument();
    });
  });

  describe('UI Components', () => {
    it('should render card structure correctly', () => {
      render(<SubmitContribution />);

      expect(screen.getByTestId('card')).toBeInTheDocument();
      expect(screen.getByTestId('card-header')).toBeInTheDocument();
      expect(screen.getByTestId('card-content')).toBeInTheDocument();
    });

    it('should render badges for skills', () => {
      render(<SubmitContribution />);

      const badges = screen.getAllByText(/Python|Community Building/);
      expect(badges).toHaveLength(2);
    });

    it('should render icons correctly', () => {
      render(<SubmitContribution />);

      expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
      expect(screen.getByTestId('upload-icon')).toBeInTheDocument();
      expect(screen.getByTestId('link-icon')).toBeInTheDocument();
    });
  });

  describe('Category Options', () => {
    it('should display all available categories', () => {
      render(<SubmitContribution />);

      const categories = ['Coding', 'Community Building', 'Activism', 'Education', 'Design', 'Research'];
      categories.forEach(category => {
        expect(screen.getByText(category)).toBeInTheDocument();
      });
    });

    it('should have proper category structure', () => {
      render(<SubmitContribution />);

      expect(screen.getByTestId('select')).toBeInTheDocument();
      expect(screen.getByTestId('select-trigger')).toBeInTheDocument();
      expect(screen.getByTestId('select-content')).toBeInTheDocument();
    });
  });

  describe('Evidence Links', () => {
    it('should render multiple evidence input fields', () => {
      render(<SubmitContribution />);

      const evidenceInputs = screen.getAllByPlaceholderText(/GitHub repo|Additional evidence URL/);
      expect(evidenceInputs).toHaveLength(2);
    });

    it('should have upload and link buttons for evidence', () => {
      render(<SubmitContribution />);

      const buttons = screen.getAllByTestId(/upload-icon|link-icon/);
      expect(buttons).toHaveLength(2);
    });
  });

  describe('Token Reward Display', () => {
    it('should display estimated token reward prominently', () => {
      render(<SubmitContribution />);

      expect(screen.getByText('150-220 NIMO')).toBeInTheDocument();
    });

    it('should show token-gold styling class', () => {
      render(<SubmitContribution />);

      const rewardText = screen.getByText('150-220 NIMO');
      expect(rewardText).toHaveClass('text-token-gold');
    });
  });
});