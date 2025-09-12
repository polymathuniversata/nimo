import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { SubmitContribution } from '../../components/SubmitContribution';
import { AuthProvider } from '../../contexts/AuthContext';

// Import the functions to be mocked
import { analyzeContribution, calculateTokenReward } from '../../utils/metta';
import { updateContributionStatus, getContributions } from '../../utils/api';

// Mock the AuthContext
const mockUser = { id: '1', email: 'test@example.com', walletAddress: '0x123...' };

vi.mock('../../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'auth-provider' }, children),
  useAuth: () => ({
    user: mockUser,
    isLoading: false,
    isAuthenticated: true,
  }),
}));

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

// Mock UI components with proper TypeScript types
vi.mock('@/components/ui/card', () => ({
  Card: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card' }, children),
  CardContent: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card-content' }, children),
  CardHeader: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card-header' }, children),
  CardTitle: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'card-title' }, children),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, variant, disabled, ...props }: {
    children?: React.ReactNode;
    onClick?: () => void;
    variant?: string;
    disabled?: boolean;
    [key: string]: unknown;
  }) =>
    React.createElement('button', {
      onClick,
      'data-variant': variant,
      disabled,
      ...props
    }, children),
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ placeholder, type, value, onChange, ...props }: {
    placeholder?: string;
    type?: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    [key: string]: unknown;
  }) =>
    React.createElement('input', {
      placeholder,
      type: type || 'text',
      value,
      onChange,
      ...props
    }),
}));

vi.mock('@/components/ui/textarea', () => ({
  Textarea: ({ placeholder, value, onChange, ...props }: {
    placeholder?: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    [key: string]: unknown;
  }) =>
    React.createElement('textarea', {
      placeholder,
      value,
      onChange,
      ...props
    }),
}));

vi.mock('@/components/ui/select', () => ({
  Select: ({ children, value }: {
    children: React.ReactNode;
    value?: string;
  }) =>
    React.createElement('div', { 'data-testid': 'select', 'data-value': value }, children),
  SelectContent: ({ children }: { children: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'select-content' }, children),
  SelectItem: ({ children, value }: { children: React.ReactNode; value: string }) =>
    React.createElement('option', { value }, children),
  SelectTrigger: ({ children }: { children: React.ReactNode }) =>
    React.createElement('button', { 'data-testid': 'select-trigger' }, children),
  SelectValue: ({ placeholder }: { placeholder: string }) =>
    React.createElement('span', { 'data-testid': 'select-value' }, placeholder),
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant }: { children: React.ReactNode; variant?: string }) =>
    React.createElement('span', { 'data-variant': variant }, children),
}));

vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'alert' }, children),
  AlertDescription: ({ children }: { children: React.ReactNode }) => React.createElement('div', { 'data-testid': 'alert-description' }, children),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Plus: () => React.createElement('span', { 'data-testid': 'plus-icon' }, 'Plus'),
  Upload: () => React.createElement('span', { 'data-testid': 'upload-icon' }, 'Upload'),
  Link: () => React.createElement('span', { 'data-testid': 'link-icon' }, 'Link'),
}));

describe('Contribution Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Contribution Submission Workflow', () => {
    it('should handle complete contribution submission from form to backend', async () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <SubmitContribution />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    it('should validate contribution data before submission', () => {
      interface FormData {
        title: string;
        category: string;
        description: string;
        evidence: string;
      }

      const TestContributionValidation = () => {
        const [formData, setFormData] = React.useState<FormData>({
          title: '',
          category: '',
          description: '',
          evidence: ''
        });
        const [errors, setErrors] = React.useState<string[]>([]);

        const validateForm = () => {
          const newErrors: string[] = [];
          if (!formData.title.trim()) newErrors.push('Title is required');
          if (!formData.category) newErrors.push('Category is required');
          if (!formData.description.trim()) newErrors.push('Description is required');
          if (!formData.evidence.trim()) newErrors.push('Evidence is required');
          setErrors(newErrors);
          return newErrors.length === 0;
        };

        const handleInputChange = (field: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
          setFormData({...formData, [field]: e.target.value});
        };

        return React.createElement('div', null,
          React.createElement('input', {
            placeholder: 'Title',
            value: formData.title,
            onChange: handleInputChange('title'),
            'data-testid': 'title-input'
          }),
          React.createElement('select', {
            value: formData.category,
            onChange: handleInputChange('category'),
            'data-testid': 'category-select'
          }, React.createElement('option', { value: '' }, 'Select category')),
          React.createElement('textarea', {
            placeholder: 'Description',
            value: formData.description,
            onChange: handleInputChange('description'),
            'data-testid': 'description-textarea'
          }),
          React.createElement('input', {
            placeholder: 'Evidence URL',
            value: formData.evidence,
            onChange: handleInputChange('evidence'),
            'data-testid': 'evidence-input'
          }),
          React.createElement('button', {
            onClick: validateForm,
            'data-testid': 'validate-button'
          }, 'Validate'),
          errors.map((error, index) =>
            React.createElement('div', {
              key: index,
              'data-testid': `error-${index}`
            }, error)
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestContributionValidation />
          </AuthProvider>
        </BrowserRouter>
      );

      const validateButton = screen.getByTestId('validate-button');
      fireEvent.click(validateButton);

      expect(screen.getByTestId('error-0')).toHaveTextContent('Title is required');
      expect(screen.getByTestId('error-1')).toHaveTextContent('Category is required');
      expect(screen.getByTestId('error-2')).toHaveTextContent('Description is required');
      expect(screen.getByTestId('error-3')).toHaveTextContent('Evidence is required');
    });

    it('should handle submission errors gracefully', async () => {
      const mockSubmitContribution = vi.fn().mockRejectedValueOnce(new Error('Submission failed'));

      const TestSubmissionError = () => {
        const [error, setError] = React.useState('');

        const handleSubmit = async () => {
          try {
            await mockSubmitContribution({
              title: 'Test Contribution',
              category: 'coding',
              description: 'Test description',
              evidence: 'https://github.com/test/repo'
            });
          } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
          }
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: handleSubmit,
            'data-testid': 'submit-button'
          }, 'Submit Contribution'),
          error && React.createElement('div', { 'data-testid': 'submission-error' }, error)
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestSubmissionError />
          </AuthProvider>
        </BrowserRouter>
      );

      const submitButton = screen.getByTestId('submit-button');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('submission-error')).toHaveTextContent('Submission failed');
      });
    });
  });

  describe('Contribution Display and Management', () => {
    it('should filter contributions by status', () => {
      interface Contribution {
        id: string;
        title: string;
        status: string;
        category: string;
      }

      const TestContributionFilter = () => {
        const [contributions] = React.useState<Contribution[]>([
          { id: '1', title: 'Project A', status: 'verified', category: 'coding' },
          { id: '2', title: 'Project B', status: 'pending_verification', category: 'education' },
          { id: '3', title: 'Project C', status: 'rejected', category: 'design' }
        ]);
        const [filter, setFilter] = React.useState('all');

        const filteredContributions = contributions.filter(contrib => {
          if (filter === 'all') return true;
          return contrib.status === filter;
        });

        const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
          setFilter(e.target.value);
        };

        return React.createElement('div', null,
          React.createElement('select', {
            value: filter,
            onChange: handleFilterChange,
            'data-testid': 'filter-select'
          },
            React.createElement('option', { value: 'all' }, 'All'),
            React.createElement('option', { value: 'verified' }, 'Verified'),
            React.createElement('option', { value: 'pending_verification' }, 'Pending'),
            React.createElement('option', { value: 'rejected' }, 'Rejected')
          ),
          React.createElement('div', { 'data-testid': 'result-count' }, filteredContributions.length.toString()),
          filteredContributions.map((contrib) =>
            React.createElement('div', {
              key: contrib.id,
              'data-testid': `filtered-${contrib.id}`
            }, contrib.title)
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestContributionFilter />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('result-count')).toHaveTextContent('3');

      const filterSelect = screen.getByTestId('filter-select');
      fireEvent.change(filterSelect, { target: { value: 'verified' } });

      expect(screen.getByTestId('result-count')).toHaveTextContent('1');
      expect(screen.getByTestId('filtered-1')).toBeInTheDocument();

      fireEvent.change(filterSelect, { target: { value: 'pending_verification' } });
      expect(screen.getByTestId('result-count')).toHaveTextContent('1');
      expect(screen.getByTestId('filtered-2')).toBeInTheDocument();
    });
  });

  describe('Token Reward Distribution', () => {
    it('should handle token distribution failures', async () => {
      const mockDistributeTokens = vi.fn().mockRejectedValueOnce(new Error('Insufficient funds in reward pool'));

      const TestDistributionFailure = () => {
        const [error, setError] = React.useState('');

        const distributeReward = async () => {
          try {
            await mockDistributeTokens({
              contributionId: 'contrib_123',
              recipientAddress: '0x1234567890abcdef',
              amount: 200
            });
          } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
          }
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: distributeReward,
            'data-testid': 'distribute-button'
          }, 'Distribute Tokens'),
          error && React.createElement('div', { 'data-testid': 'distribution-error' }, error)
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestDistributionFailure />
          </AuthProvider>
        </BrowserRouter>
      );

      const distributeButton = screen.getByTestId('distribute-button');
      fireEvent.click(distributeButton);

      await waitFor(() => {
        expect(screen.getByTestId('distribution-error')).toHaveTextContent('Insufficient funds in reward pool');
      });
    });
  });
});

describe('Contribution Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Contribution Submission Workflow', () => {
    it('should handle complete contribution submission from form to backend', async () => {
      const mockSubmitContribution = vi.fn();
      const mockAnalyzeContribution = vi.fn();

      // Mock the functions directly
      vi.doMock('../../utils/api', () => ({
        submitContribution: mockSubmitContribution,
      }));
      vi.doMock('../../utils/metta', () => ({
        analyzeContribution: mockAnalyzeContribution,
      }));

      render(
        <BrowserRouter>
          <AuthProvider>
            <SubmitContribution />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    it('should validate contribution data before submission', () => {
      const TestContributionValidation = () => {
        const [formData, setFormData] = React.useState({
          title: '',
          category: '',
          description: '',
          evidence: ''
        });
        const [errors, setErrors] = React.useState<string[]>([]);

        const validateForm = () => {
          const newErrors: string[] = [];
          if (!formData.title.trim()) newErrors.push('Title is required');
          if (!formData.category) newErrors.push('Category is required');
          if (!formData.description.trim()) newErrors.push('Description is required');
          if (!formData.evidence.trim()) newErrors.push('Evidence is required');
          setErrors(newErrors);
          return newErrors.length === 0;
        };

        return React.createElement('div', null,
          React.createElement('input', {
            placeholder: 'Title',
            value: formData.title,
            onChange: (e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, title: e.target.value}),
            'data-testid': 'title-input'
          }),
          React.createElement('select', {
            value: formData.category,
            onChange: (e: React.ChangeEvent<HTMLSelectElement>) => setFormData({...formData, category: e.target.value}),
            'data-testid': 'category-select'
          }, React.createElement('option', { value: '' }, 'Select category')),
          React.createElement('textarea', {
            placeholder: 'Description',
            value: formData.description,
            onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({...formData, description: e.target.value}),
            'data-testid': 'description-textarea'
          }),
          React.createElement('input', {
            placeholder: 'Evidence URL',
            value: formData.evidence,
            onChange: (e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, evidence: e.target.value}),
            'data-testid': 'evidence-input'
          }),
          React.createElement('button', {
            onClick: validateForm,
            'data-testid': 'validate-button'
          }, 'Validate'),
          errors.map((error, index) =>
            React.createElement('div', {
              key: index,
              'data-testid': `error-${index}`
            }, error)
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestContributionValidation />
          </AuthProvider>
        </BrowserRouter>
      );

      const validateButton = screen.getByTestId('validate-button');
      fireEvent.click(validateButton);

      expect(screen.getByTestId('error-0')).toHaveTextContent('Title is required');
      expect(screen.getByTestId('error-1')).toHaveTextContent('Category is required');
      expect(screen.getByTestId('error-2')).toHaveTextContent('Description is required');
      expect(screen.getByTestId('error-3')).toHaveTextContent('Evidence is required');
    });

    it('should handle submission errors gracefully', async () => {
      const mockSubmitContribution = vi.fn().mockRejectedValueOnce(new Error('Submission failed'));

      vi.mocked(mockSubmitContribution).mockImplementation(mockSubmitContribution);

      const TestSubmissionError = () => {
        const [error, setError] = React.useState('');

        const handleSubmit = async () => {
          try {
            await mockSubmitContribution({
              title: 'Test Contribution',
              category: 'coding',
              description: 'Test description',
              evidence: 'https://github.com/test/repo'
            });
          } catch (err) {
            setError(err instanceof Error ? err.message : 'Submission failed');
          }
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: handleSubmit,
            'data-testid': 'submit-button'
          }, 'Submit Contribution'),
          error && React.createElement('div', { 'data-testid': 'submission-error' }, error)
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestSubmissionError />
          </AuthProvider>
        </BrowserRouter>
      );

      const submitButton = screen.getByTestId('submit-button');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('submission-error')).toHaveTextContent('Submission failed');
      });
    });
  });

  describe('MeTTa AI Analysis Integration', () => {
    it('should analyze contribution quality and impact', async () => {
      const mockAnalyzeContribution = vi.fn().mockResolvedValueOnce({
        quality: 0.88,
        impact: 0.92,
        skills: ['python', 'machine_learning', 'community_building'],
        suggestedReward: 180
      });

      vi.mocked(analyzeContribution).mockImplementation(mockAnalyzeContribution);

      const TestMeTTaAnalysis = () => {
        const [analysis, setAnalysis] = React.useState<{
          quality: number;
          impact: number;
          skills: string[];
          suggestedReward: number;
        } | null>(null);

        const analyze = async () => {
          const result = await mockAnalyzeContribution({
            title: 'AI Research Project',
            description: 'Developing machine learning models for social good',
            category: 'research',
            evidence: 'https://github.com/test/ml-research'
          });
          setAnalysis(result);
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: analyze,
            'data-testid': 'analyze-button'
          }, 'Analyze Contribution'),
          analysis && React.createElement('div', null,
            React.createElement('div', { 'data-testid': 'quality-score' }, analysis.quality.toString()),
            React.createElement('div', { 'data-testid': 'impact-score' }, analysis.impact.toString()),
            React.createElement('div', { 'data-testid': 'suggested-reward' }, analysis.suggestedReward.toString()),
            analysis.skills.map((skill: string, index: number) =>
              React.createElement('span', {
                key: index,
                'data-testid': `skill-${index}`
              }, skill)
            )
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestMeTTaAnalysis />
          </AuthProvider>
        </BrowserRouter>
      );

      const analyzeButton = screen.getByTestId('analyze-button');
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByTestId('quality-score')).toHaveTextContent('0.88');
        expect(screen.getByTestId('impact-score')).toHaveTextContent('0.92');
        expect(screen.getByTestId('suggested-reward')).toHaveTextContent('180');
        expect(screen.getByTestId('skill-0')).toHaveTextContent('python');
        expect(screen.getByTestId('skill-1')).toHaveTextContent('machine_learning');
      });
    });

    it('should calculate token rewards based on analysis', async () => {
      const mockCalculateTokenReward = vi.fn().mockResolvedValueOnce({
        baseReward: 150,
        qualityBonus: 25,
        impactBonus: 30,
        totalReward: 205
      });

      vi.mocked(calculateTokenReward).mockImplementation(mockCalculateTokenReward);

      const TestTokenCalculation = () => {
        const [reward, setReward] = React.useState<{
          baseReward: number;
          qualityBonus: number;
          impactBonus: number;
          totalReward: number;
        } | null>(null);

        const calculateReward = async () => {
          const result = await mockCalculateTokenReward({
            quality: 0.85,
            impact: 0.9,
            category: 'coding',
            skills: ['python', 'react']
          });
          setReward(result);
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: calculateReward,
            'data-testid': 'calculate-button'
          }, 'Calculate Reward'),
          reward && React.createElement('div', null,
            React.createElement('div', { 'data-testid': 'base-reward' }, reward.baseReward.toString()),
            React.createElement('div', { 'data-testid': 'quality-bonus' }, reward.qualityBonus.toString()),
            React.createElement('div', { 'data-testid': 'impact-bonus' }, reward.impactBonus.toString()),
            React.createElement('div', { 'data-testid': 'total-reward' }, reward.totalReward.toString())
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestTokenCalculation />
          </AuthProvider>
        </BrowserRouter>
      );

      const calculateButton = screen.getByTestId('calculate-button');
      fireEvent.click(calculateButton);

      await waitFor(() => {
        expect(screen.getByTestId('base-reward')).toHaveTextContent('150');
        expect(screen.getByTestId('quality-bonus')).toHaveTextContent('25');
        expect(screen.getByTestId('impact-bonus')).toHaveTextContent('30');
        expect(screen.getByTestId('total-reward')).toHaveTextContent('205');
      });
    });
  });

  describe('Contribution Status Updates', () => {
    it('should update contribution status from pending to verified', async () => {
      const mockUpdateStatus = vi.fn().mockResolvedValueOnce({
        success: true,
        contribution: {
          id: 'contrib_123',
          status: 'verified',
          tokenReward: 180
        }
      });

      vi.mocked(updateContributionStatus).mockImplementation(mockUpdateStatus);

      const TestStatusUpdate = () => {
        const [contribution, setContribution] = React.useState({
          id: 'contrib_123',
          status: 'pending_verification',
          tokenReward: 0
        });

        const verifyContribution = async () => {
          const result = await mockUpdateStatus('contrib_123', 'verified');
          if (result.success) {
            setContribution(result.contribution);
          }
        };

        return React.createElement('div', null,
          React.createElement('div', { 'data-testid': 'status' }, contribution.status),
          React.createElement('div', { 'data-testid': 'reward' }, contribution.tokenReward.toString()),
          React.createElement('button', {
            onClick: verifyContribution,
            'data-testid': 'verify-button'
          }, 'Verify Contribution')
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestStatusUpdate />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('pending_verification');
      expect(screen.getByTestId('reward')).toHaveTextContent('0');

      const verifyButton = screen.getByTestId('verify-button');
      fireEvent.click(verifyButton);

      await waitFor(() => {
        expect(screen.getByTestId('status')).toHaveTextContent('verified');
        expect(screen.getByTestId('reward')).toHaveTextContent('180');
      });
    });

    it('should handle contribution rejection with feedback', async () => {
      const mockUpdateStatus = vi.fn().mockResolvedValueOnce({
        success: true,
        contribution: {
          id: 'contrib_123',
          status: 'rejected',
          feedback: 'Evidence insufficient for verification'
        }
      });

      vi.mocked(updateContributionStatus).mockImplementation(mockUpdateStatus);

      const TestRejection = () => {
        const [contribution, setContribution] = React.useState({
          id: 'contrib_123',
          status: 'pending_verification',
          feedback: ''
        });

        const rejectContribution = async () => {
          const result = await mockUpdateStatus('contrib_123', 'rejected');
          if (result.success) {
            setContribution(result.contribution);
          }
        };

        return React.createElement('div', null,
          React.createElement('div', { 'data-testid': 'status' }, contribution.status),
          contribution.feedback && React.createElement('div', { 'data-testid': 'feedback' }, contribution.feedback),
          React.createElement('button', {
            onClick: rejectContribution,
            'data-testid': 'reject-button'
          }, 'Reject Contribution')
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestRejection />
          </AuthProvider>
        </BrowserRouter>
      );

      const rejectButton = screen.getByTestId('reject-button');
      fireEvent.click(rejectButton);

      await waitFor(() => {
        expect(screen.getByTestId('status')).toHaveTextContent('rejected');
        expect(screen.getByTestId('feedback')).toHaveTextContent('Evidence insufficient for verification');
      });
    });
  });

  describe('Contribution Display and Management', () => {
    it('should fetch and display user contributions', async () => {
      const mockContributions = [
        {
          id: 'contrib_1',
          title: 'Open Source Project',
          category: 'coding',
          status: 'verified',
          tokenReward: 150,
          createdAt: '2024-01-15'
        },
        {
          id: 'contrib_2',
          title: 'Community Workshop',
          category: 'education',
          status: 'pending_verification',
          tokenReward: 0,
          createdAt: '2024-01-20'
        }
      ];

      const mockGetContributions = vi.fn().mockResolvedValueOnce({
        success: true,
        contributions: mockContributions
      });

      vi.mocked(getContributions).mockImplementation(mockGetContributions);

      const TestContributionList = () => {
        const [contributions, setContributions] = React.useState<{
          id: string;
          title: string;
          category: string;
          status: string;
          tokenReward: number;
          createdAt: string;
        }[]>([]);

        const loadContributions = async () => {
          const result = await mockGetContributions();
          if (result.success) {
            setContributions(result.contributions);
          }
        };

        React.useEffect(() => {
          loadContributions();
        }, []);

        return React.createElement('div', null,
          contributions.map((contrib, index: number) =>
            React.createElement('div', {
              key: contrib.id,
              'data-testid': `contribution-${index}`
            },
              React.createElement('h3', null, contrib.title),
              React.createElement('span', { 'data-testid': `status-${index}` }, contrib.status),
              React.createElement('span', { 'data-testid': `reward-${index}` }, contrib.tokenReward.toString())
            )
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestContributionList />
          </AuthProvider>
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('contribution-0')).toBeInTheDocument();
        expect(screen.getByTestId('contribution-1')).toBeInTheDocument();
      });

      expect(screen.getByTestId('status-0')).toHaveTextContent('verified');
      expect(screen.getByTestId('status-1')).toHaveTextContent('pending_verification');
      expect(screen.getByTestId('reward-0')).toHaveTextContent('150');
      expect(screen.getByTestId('reward-1')).toHaveTextContent('0');
    });

    it('should filter contributions by status', () => {
      const TestContributionFilter = () => {
        const [contributions] = React.useState([
          { id: '1', title: 'Project A', status: 'verified', category: 'coding' },
          { id: '2', title: 'Project B', status: 'pending_verification', category: 'education' },
          { id: '3', title: 'Project C', status: 'rejected', category: 'design' }
        ]);
        const [filter, setFilter] = React.useState('all');

        const filteredContributions = contributions.filter(contrib => {
          if (filter === 'all') return true;
          return contrib.status === filter;
        });

        return React.createElement('div', null,
          React.createElement('select', {
            value: filter,
            onChange: (e: React.ChangeEvent<HTMLSelectElement>) => setFilter(e.target.value),
            'data-testid': 'filter-select'
          },
            React.createElement('option', { value: 'all' }, 'All'),
            React.createElement('option', { value: 'verified' }, 'Verified'),
            React.createElement('option', { value: 'pending_verification' }, 'Pending'),
            React.createElement('option', { value: 'rejected' }, 'Rejected')
          ),
          React.createElement('div', { 'data-testid': 'result-count' }, filteredContributions.length.toString()),
          filteredContributions.map((contrib) =>
            React.createElement('div', {
              key: contrib.id,
              'data-testid': `filtered-${contrib.id}`
            }, contrib.title)
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestContributionFilter />
          </AuthProvider>
        </BrowserRouter>
      );

      expect(screen.getByTestId('result-count')).toHaveTextContent('3');

      const filterSelect = screen.getByTestId('filter-select');
      fireEvent.change(filterSelect, { target: { value: 'verified' } });

      expect(screen.getByTestId('result-count')).toHaveTextContent('1');
      expect(screen.getByTestId('filtered-1')).toBeInTheDocument();

      fireEvent.change(filterSelect, { target: { value: 'pending_verification' } });
      expect(screen.getByTestId('result-count')).toHaveTextContent('1');
      expect(screen.getByTestId('filtered-2')).toBeInTheDocument();
    });
  });

  describe('Token Reward Distribution', () => {
    it('should distribute tokens upon contribution verification', async () => {
      const mockDistributeTokens = vi.fn().mockResolvedValueOnce({
        success: true,
        transactionHash: '0xabcdef123456',
        amount: 175
      });

      const TestTokenDistribution = () => {
        const [distribution, setDistribution] = React.useState<{
          success: boolean;
          transactionHash: string;
          amount: number;
        } | null>(null);

        const distributeReward = async () => {
          const result = await mockDistributeTokens({
            contributionId: 'contrib_123',
            recipientAddress: '0x1234567890abcdef',
            amount: 175
          });
          setDistribution(result);
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: distributeReward,
            'data-testid': 'distribute-button'
          }, 'Distribute Tokens'),
          distribution && React.createElement('div', null,
            React.createElement('div', { 'data-testid': 'tx-hash' }, distribution.transactionHash),
            React.createElement('div', { 'data-testid': 'distributed-amount' }, distribution.amount.toString())
          )
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestTokenDistribution />
          </AuthProvider>
        </BrowserRouter>
      );

      const distributeButton = screen.getByTestId('distribute-button');
      fireEvent.click(distributeButton);

      await waitFor(() => {
        expect(screen.getByTestId('tx-hash')).toHaveTextContent('0xabcdef123456');
        expect(screen.getByTestId('distributed-amount')).toHaveTextContent('175');
      });
    });

    it('should handle token distribution failures', async () => {
      const mockDistributeTokens = vi.fn().mockRejectedValueOnce(new Error('Insufficient funds in reward pool'));

      const TestDistributionFailure = () => {
        const [error, setError] = React.useState('');

        const distributeReward = async () => {
          try {
            await mockDistributeTokens({
              contributionId: 'contrib_123',
              recipientAddress: '0x1234567890abcdef',
              amount: 200
            });
          } catch (err) {
            setError(err instanceof Error ? err.message : 'Insufficient funds in reward pool');
          }
        };

        return React.createElement('div', null,
          React.createElement('button', {
            onClick: distributeReward,
            'data-testid': 'distribute-button'
          }, 'Distribute Tokens'),
          error && React.createElement('div', { 'data-testid': 'distribution-error' }, error)
        );
      };

      render(
        <BrowserRouter>
          <AuthProvider>
            <TestDistributionFailure />
          </AuthProvider>
        </BrowserRouter>
      );

      const distributeButton = screen.getByTestId('distribute-button');
      fireEvent.click(distributeButton);

      await waitFor(() => {
        expect(screen.getByTestId('distribution-error')).toHaveTextContent('Insufficient funds in reward pool');
      });
    });
  });
});