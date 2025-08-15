import { test, expect } from '@playwright/test';

test.describe('MindCanvas E2E Tests', () => {
  test('should load the homepage and show login option', async ({ page }) => {
    await page.goto('/');

    // Should redirect to login
    await expect(page).toHaveURL('/login');

    // Should show login form
    await expect(page.locator('h2')).toContainText('Sign in to MindCanvas');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login');

    // Click register link
    await page.click('text=create a new account');

    // Should be on register page
    await expect(page).toHaveURL('/register');
    await expect(page.locator('h2')).toContainText('Create your MindCanvas account');
  });

  test('should show validation errors for invalid login', async ({ page }) => {
    await page.goto('/login');

    // Try to submit empty form
    await page.click('button[type="submit"]');

    // HTML5 validation should prevent submission
    await expect(page.locator('input[name="email"]:invalid')).toBeVisible();
  });

  test('should toggle dark mode', async ({ page }) => {
    await page.goto('/login');

    // Click dark mode toggle
    await page.click('button[aria-label="Toggle dark mode"]');

    // Should add dark class to html
    await expect(page.locator('html')).toHaveClass(/dark/);

    // Click again to toggle back
    await page.click('button[aria-label="Toggle dark mode"]');

    // Should remove dark class
    await expect(page.locator('html')).not.toHaveClass(/dark/);
  });

  test('should register a new user and redirect to dashboard', async ({ page }) => {
    await page.goto('/register');

    // Fill registration form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.fill('input[name="confirmPassword"]', 'testpassword123');

    // Mock successful registration
    await page.route('**/auth/register', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-token',
          token_type: 'bearer',
          user: {
            id: 1,
            email: 'test@example.com',
            full_name: 'Test User',
            is_active: true,
            is_admin: false,
            created_at: new Date().toISOString()
          }
        })
      });
    });

    // Mock current user endpoint
    await page.route('**/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          is_admin: false,
          created_at: new Date().toISOString()
        })
      });
    });

    // Submit form
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
  });

  test('should perform search when authenticated', async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-token');
    });

    // Mock API endpoints
    await page.route('**/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          is_admin: false,
          created_at: new Date().toISOString()
        })
      });
    });

    await page.route('**/search/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          query: 'artificial intelligence',
          results: [
            {
              title: 'AI Overview',
              url: 'https://example.com/ai',
              content: 'Artificial intelligence overview content',
              score: 0.95
            }
          ],
          total_results: 1,
          metadata: { source: 'test' }
        })
      });
    });

    await page.goto('/search');

    // Fill search form
    await page.fill('input[type="text"]', 'artificial intelligence');
    await page.click('button[type="submit"]');

    // Should show results
    await expect(page.locator('text=Search Results')).toBeVisible();
    await expect(page.locator('text=AI Overview')).toBeVisible();
  });

  test('should generate image when authenticated', async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-token');
    });

    // Mock API endpoints
    await page.route('**/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          is_admin: false,
          created_at: new Date().toISOString()
        })
      });
    });

    await page.route('**/image/generate', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          prompt: 'a beautiful sunset',
          image_data: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
          metadata: { width: 512, height: 512, steps: 20 }
        })
      });
    });

    await page.goto('/image');

    // Fill image generation form
    await page.fill('textarea[id="prompt"]', 'a beautiful sunset');
    await page.click('button[type="submit"]');

    // Should show generated image
    await expect(page.locator('text=Generated Image')).toBeVisible();
    await expect(page.locator('img[alt="a beautiful sunset"]')).toBeVisible();
  });
});