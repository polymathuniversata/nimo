import { test, expect } from '@playwright/test';

test.describe('User Registration and KYC Flow', () => {
  test('should complete full user registration journey', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');

    // Fill out profile information
    await page.fill('[placeholder="Enter your full name"]', 'John Doe');
    await page.fill('[placeholder="Enter your email"]', 'john.doe@example.com');
    await page.fill('[placeholder="Create a password"]', 'SecurePass123!');
    await page.fill('[placeholder="Confirm your password"]', 'SecurePass123!');

    // Move to next step
    await page.click('button:has-text("Next")');

    // KYC Step - Upload documents
    await page.setInputFiles('input[type="file"]', [
      './test-files/passport.jpg',
      './test-files/utility-bill.pdf'
    ]);

    // Fill KYC information
    await page.fill('[placeholder="Enter your address"]', '123 Main St, City, State 12345');
    await page.selectOption('select[name="country"]', 'US');
    await page.fill('[placeholder="MM/DD/YYYY"]', '01/15/1990');

    // Accept terms and conditions
    await page.check('input[name="acceptTerms"]');
    await page.check('input[name="acceptPrivacy"]');

    // Submit KYC
    await page.click('button:has-text("Submit for Verification")');

    // Verify success message
    await expect(page.locator('text=KYC submitted successfully')).toBeVisible();

    // Check that user is redirected to dashboard
    await page.waitForURL('/dashboard');
    await expect(page.locator('text=Welcome to Nimo')).toBeVisible();
  });

  test('should handle wallet connection during registration', async ({ page }) => {
    // Mock wallet connection
    await page.addScriptTag({
      content: `
        window.ethereum = {
          request: async ({ method }) => {
            if (method === 'eth_requestAccounts') {
              return ['0x1234567890abcdef1234567890abcdef12345678'];
            }
            return null;
          },
          isMetaMask: true
        };
      `
    });

    await page.goto('/register');

    // Skip to wallet step
    await page.click('button:has-text("Next")');
    await page.click('button:has-text("Next")');

    // Connect wallet
    await page.click('button:has-text("Connect Wallet")');

    // Verify wallet address is displayed
    await expect(page.locator('text=0x1234...5678')).toBeVisible();

    // Complete registration
    await page.click('button:has-text("Complete Registration")');

    // Verify success
    await expect(page.locator('text=Registration completed')).toBeVisible();
  });

  test('should validate required fields in registration', async ({ page }) => {
    await page.goto('/register');

    // Try to submit without filling required fields
    await page.click('button:has-text("Next")');

    // Check for validation errors
    await expect(page.locator('text=Name is required')).toBeVisible();
    await expect(page.locator('text=Email is required')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();
  });

  test('should handle KYC rejection and resubmission', async ({ page }) => {
    // Navigate to KYC status page (assuming user is logged in)
    await page.goto('/kyc-status');

    // Mock KYC rejection status
    await page.addScriptTag({
      content: `
        window.mockKYCStatus = 'rejected';
        window.mockRejectionReason = 'Document quality insufficient';
      `
    });

    // Verify rejection status is displayed
    await expect(page.locator('text=KYC Rejected')).toBeVisible();
    await expect(page.locator('text=Document quality insufficient')).toBeVisible();

    // Click resubmit button
    await page.click('button:has-text("Resubmit Documents")');

    // Verify redirected to KYC upload page
    await page.waitForURL('/kyc-upload');

    // Upload new documents
    await page.setInputFiles('input[type="file"]', [
      './test-files/passport-high-quality.jpg',
      './test-files/utility-bill-clear.pdf'
    ]);

    // Submit resubmission
    await page.click('button:has-text("Submit for Review")');

    // Verify success message
    await expect(page.locator('text=Documents resubmitted successfully')).toBeVisible();
  });
});