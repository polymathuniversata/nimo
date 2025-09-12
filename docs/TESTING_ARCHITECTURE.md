# Nimo Testing Architecture & Best Practices

## Overview

This document outlines the comprehensive testing strategy implemented for the Nimo project, a Decentralized Youth Identity & Proof of Contribution Network. The testing infrastructure covers component testing, integration testing, end-to-end testing, performance testing, and accessibility testing to ensure >80% code coverage and robust application quality.

## Testing Pyramid

```
┌─────────────────┐
│   E2E Tests     │ ← User Journey Validation
│   (Playwright)  │
├─────────────────┤
│ Integration     │ ← Component Interactions
│   Tests         │
├─────────────────┤
│ Component       │ ← Individual Component Logic
│   Tests         │
│   (Vitest + RTL)│
└─────────────────┘
```

## Component Testing Strategy

### Test Structure

Each component test file follows this structure:

```typescript
// ComponentName.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mocks
vi.mock('../../hooks/useAuth');
vi.mock('../../utils/wallet');
vi.mock('../../components/ui/button');

// Test setup
const renderComponent = (props = {}) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <ComponentName {...props} />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('ComponentName', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders component correctly', () => {
      renderComponent();
      expect(screen.getByRole('heading')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('handles user input correctly', async () => {
      const user = userEvent.setup();
      renderComponent();

      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('shows validation errors for invalid input', async () => {
      const user = userEvent.setup();
      renderComponent();

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      renderComponent();
      expect(screen.getByLabelText(/email/i)).toHaveAttribute('aria-describedby');
    });
  });
});
```

### Mocking Patterns

#### API Mocking
```typescript
// utils/api.ts mock
vi.mock('../../utils/api', () => ({
  submitContribution: vi.fn().mockResolvedValue({
    id: '123',
    status: 'pending'
  }),
  getContributions: vi.fn().mockResolvedValue([
    { id: '1', title: 'Test Contribution' }
  ])
}));
```

#### Hook Mocking
```typescript
// hooks/useAuth.ts mock
vi.mock('../../hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({
    user: { id: '1', email: 'test@example.com' },
    login: vi.fn(),
    logout: vi.fn(),
    isAuthenticated: true
  }))
}));
```

#### Component Mocking
```typescript
// UI component mocks
vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled }) =>
    React.createElement('button', { onClick, disabled }, children)
}));
```

## Integration Testing Strategy

### Test Categories

1. **Authentication Flow**
   - Login → Dashboard redirect
   - Registration → Email verification
   - Password reset flow
   - Session management

2. **KYC Flow**
   - Document upload → Validation
   - Status updates → Notifications
   - Rejection handling → Resubmission

3. **Contribution Flow**
   - Form submission → AI analysis
   - Status updates → Token distribution
   - Rejection handling → Appeal process

### Integration Test Example

```typescript
// auth-flow.integration.test.tsx
describe('Authentication Flow', () => {
  it('completes full login flow', async () => {
    // Mock API responses
    mockAuthAPI.login.mockResolvedValue({
      user: testUser,
      token: 'fake-token'
    });

    render(<App />);

    // Navigate to login
    await userEvent.click(screen.getByText(/login/i));

    // Fill login form
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');

    // Submit form
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify redirect and user state
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    expect(mockAuthAPI.login).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });
});
```

## End-to-End Testing Strategy

### Playwright Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: devices['Desktop Chrome'] },
    { name: 'firefox', use: devices['Desktop Firefox'] },
    { name: 'webkit', use: devices['Desktop Safari'] },
  ],
});
```

### E2E Test Structure

```typescript
// e2e/user-registration.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test('completes full registration with KYC', async ({ page }) => {
    // Navigate to registration
    await page.goto('/register');

    // Fill profile information
    await page.fill('[data-testid="first-name"]', 'John');
    await page.fill('[data-testid="last-name"]', 'Doe');
    await page.fill('[data-testid="email"]', 'john.doe@example.com');

    // Navigate to next step
    await page.click('[data-testid="next-step"]');

    // Upload KYC documents
    await page.setInputFiles('[data-testid="passport-upload"]', 'test-data/passport.jpg');
    await page.setInputFiles('[data-testid="utility-bill-upload"]', 'test-data/utility-bill.pdf');

    // Submit registration
    await page.click('[data-testid="submit-registration"]');

    // Verify success
    await expect(page.locator('[data-testid="registration-success"]')).toBeVisible();
  });
});
```

### Page Object Pattern

```typescript
// e2e/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
  }

  async expectLoginSuccess() {
    await expect(this.page.locator('[data-testid="dashboard"]')).toBeVisible();
  }
}
```

## Performance Testing

### Component Performance Tests

```typescript
// ComponentName.performance.test.tsx
import { render } from '@testing-library/react';
import { performance } from 'perf_hooks';

describe('ComponentName Performance', () => {
  it('renders within performance budget', () => {
    const startTime = performance.now();

    render(<ComponentName />);

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    expect(renderTime).toBeLessThan(100); // 100ms budget
  });
});
```

### Lighthouse CI Integration

```javascript
// lighthouse.config.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:5173'],
      numberOfRuns: 3
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.8 }]
      }
    }
  }
};
```

## Accessibility Testing

### axe-playwright Integration

```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage passes accessibility audit', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

### Component Accessibility Tests

```typescript
// ComponentName.accessibility.test.tsx
import { axe } from 'jest-axe';

describe('ComponentName Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<ComponentName />);
    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });
});
```

## Test Data Management

### Test Fixtures

```typescript
// test/fixtures/users.ts
export const testUsers = {
  admin: {
    id: '1',
    email: 'admin@nimo.com',
    role: 'admin',
    profile: {
      firstName: 'Admin',
      lastName: 'User'
    }
  },
  contributor: {
    id: '2',
    email: 'contributor@nimo.com',
    role: 'contributor',
    profile: {
      firstName: 'John',
      lastName: 'Contributor'
    }
  }
};
```

### Mock API Responses

```typescript
// test/mocks/api-responses.ts
export const mockApiResponses = {
  contributions: {
    success: {
      data: [
        {
          id: '1',
          title: 'Test Contribution',
          status: 'approved',
          tokens: 100
        }
      ]
    },
    error: {
      error: 'Failed to fetch contributions'
    }
  }
};
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test -- --coverage

      - name: Run integration tests
        run: npm run test:integration

      - name: Install Playwright
        run: npx playwright install

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Best Practices

### Test Organization
- Group related tests in describe blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests focused and independent

### Mocking Guidelines
- Mock external dependencies
- Use realistic test data
- Avoid mocking implementation details
- Keep mocks simple and focused

### Performance Considerations
- Keep tests fast (< 100ms per test)
- Use parallel execution when possible
- Mock slow operations
- Clean up after tests

### Maintenance
- Update tests when code changes
- Remove obsolete tests
- Keep test data current
- Review test coverage regularly

## Coverage Goals

- **Unit Tests**: >80% statement coverage
- **Integration Tests**: >70% branch coverage
- **E2E Tests**: Critical user paths covered
- **Performance**: <100ms component render time
- **Accessibility**: WCAG 2.1 AA compliance

## Monitoring & Reporting

### Coverage Reporting
```javascript
// vitest.config.ts
export default {
  test: {
    coverage: {
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: ['node_modules/', 'src/test/', '**/*.d.ts'],
      thresholds: {
        global: {
          statements: 80,
          branches: 75,
          functions: 80,
          lines: 80
        }
      }
    }
  }
};
```

### Test Results Dashboard
- Automated test execution
- Coverage trend analysis
- Performance metrics tracking
- Accessibility compliance reports

## Troubleshooting

### Common Issues

1. **Async Test Timeouts**
   ```typescript
   // Use waitFor for async assertions
   await waitFor(() => {
     expect(screen.getByText('Success')).toBeInTheDocument();
   }, { timeout: 3000 });
   ```

2. **Mock Setup Issues**
   ```typescript
   // Clear mocks between tests
   beforeEach(() => {
     vi.clearAllMocks();
   });
   ```

3. **Component Context Issues**
   ```typescript
   // Wrap components with necessary providers
   const renderWithProviders = (component) => {
     return render(
       <AuthProvider>
         <Router>
           {component}
         </Router>
       </AuthProvider>
     );
   };
   ```

## Future Enhancements

1. **Visual Regression Testing**
   - Storybook integration
   - Chromatic for visual diffs
   - Automated screenshot comparison

2. **Load Testing**
   - k6 for API load testing
   - Artillery for scenario-based testing
   - Performance profiling

3. **Contract Testing**
   - API contract validation
   - Consumer-driven contracts
   - Service virtualization

4. **Security Testing**
   - OWASP ZAP integration
   - Dependency vulnerability scanning
   - Static security analysis

This comprehensive testing strategy ensures the Nimo platform maintains high quality, reliability, and user experience across all features and user journeys.