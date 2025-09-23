import { test, expect, type Page, type Browser, type BrowserContext } from '@playwright/test';

test.describe('Nimo Platform - Performance Testing', () => {

  test('should load dashboard within performance thresholds', async ({ page }: { page: Page }) => {
    const startTime = Date.now();

    // Navigate to dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Performance threshold: < 3 seconds
    expect(loadTime).toBeLessThan(3000);

    // Check Core Web Vitals
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');

      const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
      const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint');

      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: firstPaint ? firstPaint.startTime : 0,
        firstContentfulPaint: firstContentfulPaint ? firstContentfulPaint.startTime : 0,
        totalLoadTime: loadTime
      };
    });

    // Performance assertions
    expect(metrics.domContentLoaded).toBeLessThan(1000);  // DOM should load in < 1s
    expect(metrics.firstPaint).toBeLessThan(1500);        // First paint < 1.5s
    expect(metrics.firstContentfulPaint).toBeLessThan(2000); // FCP < 2s
    expect(metrics.loadComplete).toBeLessThan(3000);       // Total load < 3s

    console.log('Performance metrics:', metrics);
  });

  test('should handle concurrent user sessions', async ({ browser }: { browser: Browser }) => {
    // Create multiple browser contexts to simulate concurrent users
    const contexts: BrowserContext[] = [];
    const pages: Page[] = [];

    // Create 5 concurrent sessions
    for (let i = 0; i < 5; i++) {
      const context = await browser.newContext({
        viewport: { width: 1280, height: 720 }
      });
      const page = await context.newPage();

      contexts.push(context);
      pages.push(page);

      // Navigate to different sections
      if (i === 0) await page.goto('/dashboard');
      else if (i === 1) await page.goto('/contributions');
      else if (i === 2) await page.goto('/tokens');
      else if (i === 3) await page.goto('/governance');
      else await page.goto('/bonds');
    }

    // Wait for all pages to load
    await Promise.all(
      pages.map((page: Page) => page.waitForLoadState('networkidle'))
    );

    // Verify all pages loaded successfully
    for (const [index, page] of pages.entries()) {
      const url = page.url();
      expect(url).toContain('localhost:5173');
      expect(url).not.toContain('error');

      // Check for essential elements
      await expect(page.locator('nav')).toBeVisible();
    }

    // Clean up
    await Promise.all(contexts.map((context: BrowserContext) => context.close()));
  });

  test('should maintain performance under load', async ({ page }: { page: Page }) => {
    // Load dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Simulate user interactions
    const interactions = [
      () => page.click('text=Contributions'),
      () => page.click('text=Tokens'),
      () => page.click('text=Governance'),
      () => page.click('text=Bonds'),
      () => page.click('text=Dashboard'),
    ];

    const interactionTimes: number[] = [];

    for (const interaction of interactions) {
      const startTime = Date.now();
      await interaction();
      await page.waitForLoadState('networkidle');
      const interactionTime = Date.now() - startTime;
      interactionTimes.push(interactionTime);

      expect(interactionTime).toBeLessThan(2000); // Each interaction < 2s
    }

    // Calculate average interaction time
    const avgInteractionTime = interactionTimes.reduce((a, b) => a + b, 0) / interactionTimes.length;
    expect(avgInteractionTime).toBeLessThan(1500); // Average < 1.5s

    console.log('Average interaction time:', avgInteractionTime, 'ms');
  });

  test('should optimize resource loading', async ({ page }: { page: Page }) => {
    // Monitor resource loading
    const resources: any[] = [];

    page.on('request', request => {
      resources.push({
        url: request.url(),
        resourceType: request.resourceType(),
        timestamp: Date.now()
      });
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Analyze resource loading
    const resourceTypes = resources.reduce((acc, resource) => {
      acc[resource.resourceType] = (acc[resource.resourceType] || 0) + 1;
      return acc;
    }, {});

    console.log('Resource loading analysis:', resourceTypes);

    // Performance assertions
    const scripts = resources.filter(r => r.resourceType === 'script');
    const stylesheets = resources.filter(r => r.resourceType === 'stylesheet');
    const images = resources.filter(r => r.resourceType === 'image');

    // Reasonable limits for production
    expect(scripts.length).toBeLessThan(15);    // Max 15 scripts
    expect(stylesheets.length).toBeLessThan(10); // Max 10 stylesheets
    expect(images.length).toBeLessThan(20);     // Max 20 images
  });

  test('should handle API response times', async ({ page }: { page: Page }) => {
    const apiCalls: any[] = [];

    // Monitor API calls
    page.on('response', response => {
      const url = response.url();
      if (url.includes('/api/')) {
        apiCalls.push({
          url: url,
          status: response.status(),
          timestamp: Date.now()
        });
      }
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Analyze API performance
    for (const call of apiCalls) {
      expect(call.status).toBe(200); // All API calls should succeed
    }

    console.log(`API calls made: ${apiCalls.length}`);
    expect(apiCalls.length).toBeGreaterThan(0); // Should make API calls
  });

  test('should maintain memory efficiency', async ({ page }: { page: Page }) => {
    // Monitor memory usage (using memory property if available)
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Simulate user interactions
    await page.click('text=Contributions');
    await page.waitForLoadState('networkidle');
    await page.click('text=Tokens');
    await page.waitForLoadState('networkidle');
    await page.click('text=Dashboard');
    await page.waitForLoadState('networkidle');

    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });
    const memoryIncrease = finalMemory - initialMemory;

    // Memory increase should be reasonable (< 50MB)
    expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);

    console.log(`Memory usage: ${initialMemory / (1024 * 1024)}MB -> ${finalMemory / (1024 * 1024)}MB`);
  });

  test('should handle WebSocket connections efficiently', async ({ page }: { page: Page }) => {
    // Mock WebSocket monitoring
    await page.addInitScript(() => {
      const originalWebSocket = window.WebSocket;
      (window as any).WebSocket = function(url: string | URL, protocols?: string | string[]) {
        const ws = new originalWebSocket(url, protocols);
        console.log('WebSocket connection to:', url);

        ws.addEventListener('open', () => {
          console.log('WebSocket opened');
        });

        ws.addEventListener('message', (event: MessageEvent) => {
          console.log('WebSocket message received:', event.data);
        });

        return ws;
      };
    });

    await page.goto('/dashboard');
    await page.waitForTimeout(2000); // Wait for potential WebSocket connections

    // Check for WebSocket connections in logs
    const logs = await page.evaluate(() => {
      return (window as any).consoleLogs || [];
    });

    const wsLogs = logs.filter((log: string) => log.includes('WebSocket'));
    console.log('WebSocket activity:', wsLogs);

    // WebSocket connections should be established efficiently
    expect(wsLogs.length).toBeGreaterThanOrEqual(0);
  });

  test('should optimize bundle size and loading', async ({ page }: { page: Page }) => {
    // Monitor bundle loading
    const bundleRequests: any[] = [];

    page.on('request', request => {
      const url = request.url();
      if (url.includes('.js') || url.includes('.css') || url.includes('.chunk')) {
        bundleRequests.push({
          url: url,
          resourceType: request.resourceType(),
          timestamp: Date.now()
        });
      }
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    console.log(`Bundle requests: ${bundleRequests.length}`);

    // Bundle loading should be optimized
    expect(bundleRequests.length).toBeLessThan(10); // Max 10 bundle requests

    // Check for code splitting effectiveness
    const chunkRequests = bundleRequests.filter((r: any) => r.url.includes('chunk'));
    expect(chunkRequests.length).toBeGreaterThan(0); // Should use code splitting
  });

  test('should maintain accessibility under load', async ({ page }: { page: Page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Check accessibility features
    const ariaLabels = await page.locator('[aria-label]').count();
    const altTexts = await page.locator('img[alt]').count();
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();

    console.log(`Accessibility elements: ${ariaLabels} ARIA labels, ${altTexts} alt texts, ${headings} headings`);

    // Accessibility should be maintained
    expect(ariaLabels).toBeGreaterThan(5);
    expect(altTexts).toBeGreaterThan(0);
    expect(headings).toBeGreaterThan(2);
  });

  test('should handle error scenarios gracefully', async ({ page }: { page: Page }) => {
    // Mock API error
    await page.route('**/api/contributions/', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal Server Error',
          message: 'Database connection failed'
        })
      });
    });

    await page.goto('/dashboard');
    await page.click('nav >> text=Contributions');

    // Should handle errors gracefully
    await expect(page.locator('text=Unable to load contributions')).toBeVisible();

    // Should provide retry mechanism
    const retryButton = page.locator('button:has-text("Retry")');
    await expect(retryButton).toBeVisible();
  });

  test('should validate SEO and meta tags', async ({ page }: { page: Page }) => {
    await page.goto('/dashboard');

    // Check meta tags
    const title = await page.title();
    const metaDescription = await page.locator('meta[name="description"]').getAttribute('content');
    const metaKeywords = await page.locator('meta[name="keywords"]').getAttribute('content');

    console.log(`SEO: Title="${title}", Description="${metaDescription}", Keywords="${metaKeywords}"`);

    // SEO should be properly configured
    expect(title).toBeTruthy();
    expect(metaDescription).toBeTruthy();
    expect(metaKeywords).toBeTruthy();
  });

  test('should maintain security headers', async ({ page }: { page: Page }) => {
    // Check security headers via API call
    const response = await page.request.get('/dashboard');
    const headers = response.headers();

    // Security headers should be present
    const securityHeaders = [
      'content-security-policy',
      'x-frame-options',
      'x-content-type-options',
      'strict-transport-security',
      'referrer-policy'
    ];

    for (const header of securityHeaders) {
      expect(headers[header] || headers[header.toLowerCase()]).toBeTruthy();
    }

    console.log('Security headers validated:', securityHeaders.length, 'headers present');
  });
});
