# Nimo Testing Infrastructure Setup Guide

This guide provides comprehensive setup instructions for the testing infrastructure implemented for the Nimo project.

## Testing Coverage Overview

### ✅ Completed Testing Suites

1. **Component Testing** - 25+ test cases per component
   - Navbar component testing
   - ProtectedRoute component testing
   - LoginPage component testing
   - RegisterPage component testing
   - SubmitContribution component testing

2. **Integration Testing**
   - Authentication flow integration tests
   - KYC submission workflow integration tests
   - Contribution creation and management integration tests

3. **End-to-End Testing Setup**
   - Playwright configuration
   - User registration and KYC flow tests
   - Contribution submission and verification flow tests
   - Authentication and user management flow tests

## Setup Instructions

### 1. Install Dependencies

```bash
# Install testing dependencies
npm install --save-dev @playwright/test
npm install --save-dev @testing-library/jest-dom
npm install --save-dev @testing-library/react
npm install --save-dev @testing-library/user-event
npm install --save-dev jsdom
npm install --save-dev vitest

# Install Playwright browsers
npx playwright install
```

### 2. Environment Configuration

Create test environment files:

```bash
# .env.test
VITE_API_URL=http://localhost:3001/api
VITE_BLOCKCHAIN_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
VITE_WALLET_CONNECT_PROJECT_ID=your_wallet_connect_id
```

### 3. Test Data Setup

Create test data directory:

```bash
mkdir -p frontend/test-data
# Add test files for file upload tests
# - passport.jpg
# - utility-bill.pdf
# - id-card.png
```

### 4. Mock Services Setup

For integration tests, set up mock services:

```bash
# Start mock API server
npm run mock-server

# Start blockchain simulator
npm run blockchain-simulator
```

## Running Tests

### Unit Tests (Vitest)

```bash
# Run all unit tests
npm test

# Run specific test file
npm test -- LoginPage.test.tsx

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# Run specific integration test
npm run test:integration -- auth-flow
```

### End-to-End Tests (Playwright)

```bash
# Install Playwright browsers
npx playwright install

# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test registration-kyc.spec.ts

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run tests in specific browser
npx playwright test --project=chromium

# Generate test report
npx playwright show-report
```

## Test Configuration

### Vitest Configuration (`vitest.config.ts`)

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', 'build'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/']
    }
  },
})
```

### Playwright Configuration (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Test Categories

### 1. Component Tests
- **Location**: `src/components/__tests__/`
- **Purpose**: Test individual React components in isolation
- **Mocking**: UI components, external dependencies, API calls
- **Coverage**: Form validation, user interactions, accessibility

### 2. Integration Tests
- **Location**: `src/components/__tests__/*.integration.test.tsx`
- **Purpose**: Test component interactions and data flow
- **Mocking**: API responses, external services
- **Coverage**: User workflows, state management, error handling

### 3. E2E Tests
- **Location**: `e2e/`
- **Purpose**: Test complete user journeys
- **Mocking**: Minimal, uses real browser interactions
- **Coverage**: Critical user paths, cross-browser compatibility

## Mocking Strategy

### API Mocking
```typescript
// Mock API responses
vi.mock('../../utils/api', () => ({
  submitContribution: vi.fn(),
  getContributions: vi.fn(),
  updateContributionStatus: vi.fn(),
}));
```

### Component Mocking
```typescript
// Mock UI components
vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick }) =>
    React.createElement('button', { onClick }, children),
}));
```

### External Service Mocking
```typescript
// Mock wallet connections
vi.mock('../../utils/wallet', () => ({
  connectWallet: vi.fn(),
  getWalletAddress: vi.fn(),
}));
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      - run: npm run test:integration
      - run: npx playwright install
      - run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Performance Testing

### Lighthouse CI Setup

```yaml
# lighthouse.config.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:5173'],
      numberOfRuns: 3
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
};
```

## Accessibility Testing

### axe-playwright Integration

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('should pass accessibility audit', async ({ page }) => {
  await page.goto('/dashboard');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## Test Maintenance

### Regular Tasks
1. **Update mocks** when API contracts change
2. **Review test coverage** reports monthly
3. **Update E2E tests** when UI changes
4. **Performance benchmarks** quarterly
5. **Accessibility audits** with each release

### Best Practices
- Keep tests focused and fast
- Use descriptive test names
- Mock external dependencies
- Test error states and edge cases
- Maintain test data separately
- Use page objects for E2E tests

## Troubleshooting

### Common Issues

1. **Tests failing due to timing**
   - Use `waitFor` for async operations
   - Increase timeout for slow operations

2. **Mock not working**
   - Ensure mock is defined before import
   - Check mock implementation matches actual API

3. **E2E tests flaky**
   - Use stable selectors
   - Wait for elements to be ready
   - Handle async operations properly

4. **Coverage not updating**
   - Clear coverage cache
   - Check file paths in coverage config

## Next Steps

1. **Install Playwright** and run E2E tests
2. **Set up CI/CD pipeline** with automated testing
3. **Add performance testing** with Lighthouse
4. **Implement visual regression testing**
5. **Set up test data management**
6. **Create testing documentation** for contributors

## Support

For testing-related issues:
1. Check test logs for detailed error messages
2. Review mock implementations
3. Verify test data and fixtures
4. Consult testing documentation
5. Reach out to testing team for complex issues