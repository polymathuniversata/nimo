import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

// Test user data
export const testUsers = {
  admin: {
    id: '1',
    email: 'admin@nimo.com',
    role: 'admin',
    profile: {
      firstName: 'Admin',
      lastName: 'User',
      avatar: 'https://example.com/avatar.jpg'
    }
  },
  contributor: {
    id: '2',
    email: 'contributor@nimo.com',
    role: 'contributor',
    profile: {
      firstName: 'John',
      lastName: 'Contributor',
      avatar: 'https://example.com/avatar2.jpg'
    }
  },
  youth: {
    id: '3',
    email: 'youth@nimo.com',
    role: 'youth',
    profile: {
      firstName: 'Jane',
      lastName: 'Youth',
      dateOfBirth: '2005-01-01'
    }
  }
}

// Test contribution data
export const testContributions = {
  pending: {
    id: '1',
    title: 'Community Garden Project',
    description: 'Started a community garden in the neighborhood',
    category: 'Community Service',
    status: 'pending',
    evidenceUrls: ['https://example.com/photo1.jpg'],
    aiAnalysis: {
      score: 85,
      feedback: 'Great initiative with strong community impact'
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  approved: {
    id: '2',
    title: 'Coding Workshop',
    description: 'Organized a coding workshop for local youth',
    category: 'Education',
    status: 'approved',
    tokens: 150,
    evidenceUrls: ['https://example.com/photo2.jpg'],
    aiAnalysis: {
      score: 92,
      feedback: 'Excellent educational impact and execution'
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z'
  },
  rejected: {
    id: '3',
    title: 'Social Media Campaign',
    description: 'Created social media posts',
    category: 'Digital Marketing',
    status: 'rejected',
    rejectionReason: 'Insufficient evidence of impact',
    evidenceUrls: ['https://example.com/photo3.jpg'],
    aiAnalysis: {
      score: 45,
      feedback: 'Evidence does not clearly demonstrate contribution value'
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-03T00:00:00Z'
  }
}

// Mock API responses
export const mockApiResponses = {
  login: {
    success: {
      user: testUsers.admin,
      token: 'fake-jwt-token',
      refreshToken: 'fake-refresh-token'
    },
    error: {
      error: 'Invalid credentials'
    }
  },
  register: {
    success: {
      user: testUsers.youth,
      message: 'Registration successful. Please check your email.'
    },
    error: {
      error: 'Email already exists'
    }
  },
  contributions: {
    success: [testContributions.pending, testContributions.approved],
    error: {
      error: 'Failed to fetch contributions'
    }
  },
  submitContribution: {
    success: {
      ...testContributions.pending,
      id: 'new-contribution-id'
    },
    error: {
      error: 'Validation failed'
    }
  }
}

// Create a custom render function that includes providers
const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0
      },
      mutations: {
        retry: false
      }
    }
  })

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string
  queryClient?: QueryClient
}

export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const { route = '/', queryClient = createQueryClient(), ...renderOptions } = options

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient
  }
}

// Custom user event setup with default options
export const setupUserEvent = () => {
  return userEvent.setup({
    delay: null, // Disable delays for faster tests
    pointerEventsCheck: 0 // Disable pointer events check
  })
}

// Mock implementations
export const mockImplementations = {
  // Auth hooks
  useAuth: vi.fn(() => ({
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    isAuthenticated: false,
    isLoading: false
  })),

  // Navigation
  useNavigate: vi.fn(),
  useLocation: vi.fn(() => ({
    pathname: '/',
    search: '',
    hash: '',
    state: null
  })),

  // Wallet utilities
  connectWallet: vi.fn(),
  getWalletAddress: vi.fn(),
  signMessage: vi.fn(),

  // File upload
  uploadFile: vi.fn(),
  validateFile: vi.fn(),

  // API utilities
  apiRequest: vi.fn(),
  submitContribution: vi.fn(),
  getContributions: vi.fn(),
  updateContributionStatus: vi.fn()
}

// Test data generators
export const generateTestData = {
  user: (overrides = {}) => ({
    id: 'test-user-id',
    email: 'test@example.com',
    role: 'contributor',
    profile: {
      firstName: 'Test',
      lastName: 'User'
    },
    ...overrides
  }),

  contribution: (overrides = {}) => ({
    id: 'test-contribution-id',
    title: 'Test Contribution',
    description: 'Test description',
    category: 'Community Service',
    status: 'pending',
    evidenceUrls: [],
    createdAt: new Date().toISOString(),
    ...overrides
  }),

  kycDocument: (overrides = {}) => ({
    id: 'test-doc-id',
    type: 'passport',
    status: 'pending',
    url: 'https://example.com/doc.jpg',
    uploadedAt: new Date().toISOString(),
    ...overrides
  })
}

// Form validation helpers
export const formValidation = {
  // Simulate form submission with validation
  submitForm: async (form: HTMLFormElement, user = setupUserEvent()) => {
    await user.click(form.querySelector('button[type="submit"]')!)
  },

  // Fill form fields
  fillForm: async (formData: Record<string, string>, user = setupUserEvent()) => {
    for (const [name, value] of Object.entries(formData)) {
      const input = document.querySelector(`[name="${name}"]`) as HTMLInputElement
      if (input) {
        await user.clear(input)
        await user.type(input, value)
      }
    }
  },

  // Check validation errors
  getValidationErrors: () => {
    return Array.from(document.querySelectorAll('[data-testid*="error"]'))
      .map(el => el.textContent)
      .filter(Boolean)
  }
}

// Accessibility helpers
export const accessibility = {
  // Check if element has proper ARIA attributes
  hasAriaAttributes: (element: HTMLElement, required: string[]) => {
    return required.every(attr => element.hasAttribute(attr))
  },

  // Check keyboard navigation
  isKeyboardNavigable: (element: HTMLElement) => {
    const tabIndex = element.getAttribute('tabindex')
    return !element.hasAttribute('disabled') &&
           (tabIndex === null || parseInt(tabIndex) >= 0)
  }
}

// Performance testing helpers
export const performance = {
  // Measure render time
  measureRenderTime: async (component: React.ComponentType, props = {}) => {
    const start = performance.now()
    renderWithProviders(React.createElement(component, props))
    const end = performance.now()
    return end - start
  },

  // Mock slow operations
  delay: (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
}

// Export everything as a single object for convenience
export const testUtils = {
  renderWithProviders,
  setupUserEvent,
  testUsers,
  testContributions,
  mockApiResponses,
  mockImplementations,
  generateTestData,
  formValidation,
  accessibility,
  performance
}