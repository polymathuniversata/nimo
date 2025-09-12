import { test, expect, type Page } from '@playwright/test';

test.describe('Basic Test', () => {
  test('should load the page', async ({ page }: { page: Page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Vite/);
  });
});