import { test, expect } from '@playwright/test';

test.describe('Section 6 Frontend Wiring Verification', () => {
  test('Backend offline shows explicit connection error banner, not fake numbers', async ({ page }) => {
    // Navigate to dashboard overview directly
    await page.goto('http://localhost:5173/');

    // Launch dashboard
    const launchBtn = page.getByRole('button', { name: /Open Universal Dashboard|Launch Dashboard/i }).first();
    if (await launchBtn.isVisible()) {
      await launchBtn.click();
    }

    // Expect explicit error banner when backend is offline
    const errorBanner = page.locator('text=Unable to reach AISMM backend');
    await expect(errorBanner).toBeVisible({ timeout: 5000 });
  });
});
