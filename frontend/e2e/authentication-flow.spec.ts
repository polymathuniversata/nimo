import { test, expect, type Page, type Browser } from '@playwright/test';

test.describe('Authentication and User Management Flow', () => {
  test('should complete traditional login flow', async ({ page }: { page: Page }) => {
    await page.goto('/login');

    // Fill login form
    await page.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page.fill('[placeholder="Enter your password"]', 'SecurePass123!');

    // Submit login
    await page.click('button:has-text("Sign In")');

    // Verify successful login
    await page.waitForURL('/dashboard');
    await expect(page.locator('text=Welcome back, John')).toBeVisible();

    // Verify navigation elements are present
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Profile')).toBeVisible();
  });

  test('should handle wallet-based authentication', async ({ page }: { page: Page }) => {
    // Mock MetaMask
    await page.addScriptTag({
      content: `
        window.ethereum = {
          request: async ({ method, params }) => {
            if (method === 'eth_requestAccounts') {
              return ['0x742d35Cc6634C0532925a3b844Bc454e4438f44e'];
            }
            if (method === 'personal_sign') {
              return '0x1234567890abcdef...';
            }
            return null;
          },
          isMetaMask: true,
          selectedAddress: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        };
      `
    });

    await page.goto('/login');

    // Click wallet login option
    await page.click('button:has-text("Connect Wallet")');

    // Approve wallet connection (mocked)
    await page.waitForSelector('text=Wallet Connected');

    // Verify wallet address is displayed
    await expect(page.locator('text=0x742d...f44e')).toBeVisible();

    // Complete authentication
    await page.click('button:has-text("Continue")');

    // Verify successful login
    await page.waitForURL('/dashboard');
    await expect(page.locator('text=Wallet authenticated successfully')).toBeVisible();
  });

  test('should handle login errors gracefully', async ({ page }: { page: Page }) => {
    await page.goto('/login');

    // Attempt login with wrong credentials
    await page.fill('[placeholder="Enter your email"]', 'wrong@example.com');
    await page.fill('[placeholder="Enter your password"]', 'wrongpassword');
    await page.click('button:has-text("Sign In")');

    // Verify error message
    await expect(page.locator('text=Invalid email or password')).toBeVisible();

    // Verify still on login page
    await expect(page.url()).toContain('/login');
  });

  test('should handle password reset flow', async ({ page }: { page: Page }) => {
    await page.goto('/login');

    // Click forgot password
    await page.click('text=Forgot your password?');

    // Fill reset form
    await page.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page.click('button:has-text("Send Reset Link")');

    // Verify success message
    await expect(page.locator('text=Password reset link sent')).toBeVisible();

    // Mock receiving reset email and clicking link
    await page.goto('/reset-password?token=mock-reset-token');

    // Fill new password
    await page.fill('[placeholder="New password"]', 'NewSecurePass123!');
    await page.fill('[placeholder="Confirm new password"]', 'NewSecurePass123!');
    await page.click('button:has-text("Reset Password")');

    // Verify success
    await expect(page.locator('text=Password reset successfully')).toBeVisible();

    // Should be redirected to login
    await page.waitForURL('/login');
  });

  test('should maintain session across page refreshes', async ({ page }: { page: Page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page.fill('[placeholder="Enter your password"]', 'SecurePass123!');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('/dashboard');

    // Refresh page
    await page.reload();

    // Verify still logged in
    await expect(page.locator('text=Welcome back, John')).toBeVisible();
    await expect(page.url()).toContain('/dashboard');
  });

  test('should handle logout correctly', async ({ page }: { page: Page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page.fill('[placeholder="Enter your password"]', 'SecurePass123!');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('/dashboard');

    // Click logout
    await page.click('button:has-text("Logout")');

    // Confirm logout
    await page.click('button:has-text("Yes, Logout")');

    // Verify redirected to login
    await page.waitForURL('/login');
    await expect(page.locator('text=You have been logged out')).toBeVisible();

    // Try to access protected page
    await page.goto('/dashboard');

    // Should be redirected back to login
    await page.waitForURL('/login');
  });

  test('should handle session timeout', async ({ page }: { page: Page }) => {
    // Mock session timeout
    await page.addScriptTag({
      content: `
        // Simulate session expiry after 5 seconds
        setTimeout(() => {
          localStorage.removeItem('auth_token');
          window.location.reload();
        }, 5000);
      `
    });

    // Login
    await page.goto('/login');
    await page.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page.fill('[placeholder="Enter your password"]', 'SecurePass123!');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('/dashboard');

    // Wait for session timeout
    await page.waitForTimeout(6000);

    // Verify redirected to login due to expired session
    await expect(page.url()).toContain('/login');
    await expect(page.locator('text=Session expired')).toBeVisible();
  });

  test('should handle concurrent sessions', async ({ browser }: { browser: Browser }) => {
    // Create two browser contexts (simulating two devices)
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();

    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // Login on first device
    await page1.goto('/login');
    await page1.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page1.fill('[placeholder="Enter your password"]', 'SecurePass123!');
    await page1.click('button:has-text("Sign In")');
    await page1.waitForURL('/dashboard');

    // Login on second device
    await page2.goto('/login');
    await page2.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page2.fill('[placeholder="Enter your password"]', 'SecurePass123!');
    await page2.click('button:has-text("Sign In")');
    await page2.waitForURL('/dashboard');

    // Verify both sessions are active
    await expect(page1.locator('text=Welcome back, John')).toBeVisible();
    await expect(page2.locator('text=Welcome back, John')).toBeVisible();

    // Logout from first device
    await page1.click('button:has-text("Logout")');
    await page1.click('button:has-text("Yes, Logout")');

    // Verify first device is logged out
    await page1.waitForURL('/login');

    // Verify second device is still logged in
    await expect(page2.locator('text=Welcome back, John')).toBeVisible();

    await context1.close();
    await context2.close();
  });
});