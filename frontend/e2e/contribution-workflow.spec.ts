import { test, expect } from '@playwright/test';

test.describe('Contribution Submission and Verification Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login user before each test
    await page.goto('/login');
    await page.fill('[placeholder="Enter your email"]', 'test@example.com');
    await page.fill('[placeholder="Enter your password"]', 'password123');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('/dashboard');
  });

  test('should submit contribution and track verification status', async ({ page }) => {
    // Navigate to contribution submission
    await page.goto('/submit-contribution');

    // Fill contribution form
    await page.fill('[placeholder="e.g., KRNL Hackathon Project"]', 'Community Health App');
    await page.click('[data-testid="select-trigger"]');
    await page.click('text=Community Building');

    await page.fill('[placeholder="Describe your contribution, its impact, and how it benefits the community..."]',
      'Developed a mobile app that connects local volunteers with community health initiatives, resulting in 500+ volunteer hours and improved health outcomes for 200+ residents.');

    // Add evidence links
    await page.fill('[placeholder="GitHub repo, website, or documentation URL"]',
      'https://github.com/johndoe/health-app');
    await page.fill('[placeholder="Additional evidence URL"]',
      'https://health-app-demo.vercel.app');

    // Add skills
    await page.click('button:has-text("Add Skill")');
    await page.fill('[placeholder="Enter skill"]', 'React Native');
    await page.click('button:has-text("Add")');

    // Submit contribution
    await page.click('button:has-text("Submit for Verification")');

    // Verify success message
    await expect(page.locator('text=Contribution submitted successfully')).toBeVisible();

    // Check contribution appears in user's dashboard
    await page.goto('/dashboard');
    await expect(page.locator('text=Community Health App')).toBeVisible();
    await expect(page.locator('text=Pending Verification')).toBeVisible();
  });

  test('should display MeTTa AI analysis results', async ({ page }) => {
    await page.goto('/submit-contribution');

    // Fill basic contribution info
    await page.fill('[placeholder="e.g., KRNL Hackathon Project"]', 'AI Research Paper');
    await page.click('[data-testid="select-trigger"]');
    await page.click('text=Research');

    await page.fill('[placeholder="Describe your contribution, its impact, and how it benefits the community..."]',
      'Published research on machine learning applications in environmental monitoring, cited by 50+ researchers.');

    await page.fill('[placeholder="GitHub repo, website, or documentation URL"]',
      'https://arxiv.org/abs/2301.12345');

    // Wait for AI analysis to appear
    await expect(page.locator('text=MeTTa AI Analysis Preview')).toBeVisible();

    // Verify analysis components
    await expect(page.locator('text=Estimated token reward:')).toBeVisible();
    await expect(page.locator('text=Quality Score:')).toBeVisible();
    await expect(page.locator('text=Impact Score:')).toBeVisible();
    await expect(page.locator('text=Skills Match:')).toBeVisible();
  });

  test('should handle contribution verification workflow', async ({ page }) => {
    // Navigate to admin/verifier dashboard (assuming user has verifier role)
    await page.goto('/admin/verifications');

    // Find pending contribution
    await expect(page.locator('text=Community Health App')).toBeVisible();

    // Click to review contribution
    await page.click('text=Community Health App');

    // Verify contribution details are displayed
    await expect(page.locator('text=Developed a mobile app')).toBeVisible();
    await expect(page.locator('text=https://github.com/johndoe/health-app')).toBeVisible();

    // Check evidence links
    const evidenceLinks = page.locator('a[href*="github.com"], a[href*="vercel.app"]');
    await expect(evidenceLinks).toHaveCount(2);

    // Approve contribution
    await page.click('button:has-text("Approve")');

    // Add approval notes
    await page.fill('[placeholder="Add verification notes"]', 'Excellent contribution with clear impact metrics and verifiable evidence.');

    // Confirm approval
    await page.click('button:has-text("Confirm Approval")');

    // Verify success message
    await expect(page.locator('text=Contribution approved successfully')).toBeVisible();
  });

  test('should distribute tokens upon contribution approval', async ({ page }) => {
    // Mock blockchain interaction for token distribution
    await page.addScriptTag({
      content: `
        window.mockTokenDistribution = {
          success: true,
          transactionHash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
          amount: 175,
          recipient: '0x1234567890abcdef1234567890abcdef12345678'
        };
      `
    });

    await page.goto('/admin/verifications');

    // Approve a contribution
    await page.click('text=AI Research Paper');
    await page.click('button:has-text("Approve")');
    await page.click('button:has-text("Confirm Approval")');

    // Verify token distribution
    await expect(page.locator('text=Tokens distributed successfully')).toBeVisible();
    await expect(page.locator('text=175 NIMO')).toBeVisible();
    await expect(page.locator('text=Transaction: 0xabcdef...')).toBeVisible();
  });

  test('should handle contribution rejection with feedback', async ({ page }) => {
    await page.goto('/admin/verifications');

    // Find and click on contribution to review
    await page.click('text=Test Contribution');

    // Reject contribution
    await page.click('button:has-text("Reject")');

    // Fill rejection reason
    await page.fill('[placeholder="Explain rejection reason"]',
      'Evidence links are not accessible. Please provide working URLs or alternative verification methods.');

    // Submit rejection
    await page.click('button:has-text("Submit Rejection")');

    // Verify rejection notification
    await expect(page.locator('text=Contribution rejected')).toBeVisible();

    // Check that contributor receives notification
    await page.goto('/dashboard');
    await expect(page.locator('text=Your contribution was rejected')).toBeVisible();
    await expect(page.locator('text=Evidence links are not accessible')).toBeVisible();
  });

  test('should allow contributors to resubmit after rejection', async ({ page }) => {
    // Navigate to rejected contribution
    await page.goto('/dashboard');
    await page.click('text=Rejected Contribution');

    // Click resubmit button
    await page.click('button:has-text("Resubmit")');

    // Update contribution with better evidence
    await page.fill('[placeholder="GitHub repo, website, or documentation URL"]',
      'https://github.com/johndoe/fixed-contribution');
    await page.fill('[placeholder="Additional evidence URL"]',
      'https://contribution-demo-fixed.vercel.app');

    // Add explanation for resubmission
    await page.fill('[placeholder="Explain what you changed"]',
      'Fixed broken links and added working demo URL');

    // Resubmit
    await page.click('button:has-text("Resubmit for Verification")');

    // Verify resubmission success
    await expect(page.locator('text=Contribution resubmitted successfully')).toBeVisible();

    // Check status changed back to pending
    await page.goto('/dashboard');
    await expect(page.locator('text=Pending Verification')).toBeVisible();
  });
});