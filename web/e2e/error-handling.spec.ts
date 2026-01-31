/**
 * E2E Test: Error Handling
 * Tests error scenarios, timeouts, and edge cases
 */

import { test, expect } from '@playwright/test';
import {
  setupMockBridge,
  waitForEditorReady,
  dragBlockToCanvas,
} from './helpers/test-helpers';

test.describe('Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should handle bridge initialization failure', async ({ page }) => {
    // Don't setup mock bridge - let it fail
    await page.waitForTimeout(1000);
    
    // Verify error message displayed
    await expect(page.locator('[data-cy="bridge-error"]')).toBeVisible();
    
    // Verify error message content
    const errorText = await page.locator('[data-cy="bridge-error"]').textContent();
    expect(errorText).toContain('bridge');
  });

  test('should handle network timeout', async ({ page }) => {
    // Setup route that never resolves
    await page.route('**/pycmd/**', async (route) => {
      // Don't fulfill - simulate timeout
      await new Promise(resolve => setTimeout(resolve, 35000)); // Longer than timeout
      await route.abort('timedout');
    });
    
    await page.goto('/');
    
    // Attempt operation
    await page.click('[data-cy="reload-fields"]').catch(() => {});
    
    await page.waitForTimeout(2000);
    
    // Verify timeout error displayed
    await expect(page.locator('[data-cy="toast-error"]')).toBeVisible();
  });

  test('should handle 500 server error', async ({ page }) => {
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal server error' }),
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Verify error handling
    await expect(page.locator('[data-cy="error-message"]')).toBeVisible();
  });

  test('should handle 404 not found', async ({ page }) => {
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 404,
        body: JSON.stringify({ error: 'Not found' }),
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Verify appropriate error message
    const error = page.locator('[data-cy="error-message"]');
    await expect(error).toBeVisible();
  });

  test('should handle invalid JSON response', async ({ page }) => {
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 200,
        body: 'Invalid JSON{{{',
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Verify parse error handled
    await expect(page.locator('[data-cy="parse-error"]')).toBeVisible();
  });

  test('should handle missing required fields in response', async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
    
    // Override to return incomplete data
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: null, // Missing expected data
        }),
      });
    });
    
    await page.click('[data-cy="reload-fields"]');
    await page.waitForTimeout(500);
    
    // Verify error toast
    await expect(page.locator('[data-cy="toast-error"]')).toBeVisible();
  });

  test('should handle network disconnect', async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
    
    // Simulate network failure
    await page.route('**/pycmd/**', async (route) => {
      await route.abort('failed');
    });
    
    // Attempt operation
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="save-button"]');
    await page.fill('[data-cy="template-name-input"]', 'Test');
    await page.click('[data-cy="confirm-save"]');
    
    await page.waitForTimeout(1000);
    
    // Verify network error message
    await expect(page.locator('[data-cy="network-error"]')).toBeVisible();
  });

  test('should handle partial response corruption', async ({ page }) => {
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: {
            fields: [
              { name: 'Front', ordinal: 0 },
              { name: 'Back' }, // Missing ordinal
              null, // Invalid field
            ],
          },
        }),
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Verify graceful handling of corrupted data
    // Should filter out invalid entries
    await page.click('[data-cy="blocks-panel"]');
    const validFields = await page.locator('[data-field-name]').count();
    expect(validFields).toBeGreaterThan(0);
  });

  test('should handle save conflict', async ({ page }) => {
    let saveCount = 0;
    
    await page.route('**/pycmd/**', async (route) => {
      const postData = route.request().postDataJSON();
      
      if (postData?.action === 'saveTemplate') {
        saveCount++;
        
        if (saveCount === 1) {
          // First save succeeds
          await route.fulfill({
            status: 200,
            body: JSON.stringify({ success: true, data: { id: 1 } }),
          });
        } else {
          // Second save conflicts
          await route.fulfill({
            status: 409,
            body: JSON.stringify({
              error: 'Conflict',
              message: 'Template was modified by another user',
            }),
          });
        }
      } else {
        await route.continue();
      }
    });
    
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
    
    // Save once
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="save-button"]');
    await page.fill('[data-cy="template-name-input"]', 'Test');
    await page.click('[data-cy="confirm-save"]');
    await page.waitForTimeout(500);
    
    // Save again (conflict)
    await page.click('[data-cy="save-button"]');
    await page.click('[data-cy="confirm-save"]');
    await page.waitForTimeout(500);
    
    // Verify conflict dialog
    await expect(page.locator('[data-cy="conflict-dialog"]')).toBeVisible();
  });

  test('should handle quota exceeded error', async ({ page }) => {
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 413,
        body: JSON.stringify({
          error: 'Payload too large',
          message: 'Template size exceeds limit',
        }),
      });
    });
    
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
    
    // Try to save large template
    for (let i = 0; i < 50; i++) {
      await dragBlockToCanvas(page, 'TextBlock');
    }
    
    await page.click('[data-cy="save-button"]');
    await page.fill('[data-cy="template-name-input"]', 'Large Template');
    await page.click('[data-cy="confirm-save"]');
    
    await page.waitForTimeout(1000);
    
    // Verify quota error message
    const errorToast = page.locator('[data-cy="toast-error"]');
    await expect(errorToast).toBeVisible();
    const errorText = await errorToast.textContent();
    expect(errorText).toMatch(/size|limit|large/i);
  });

  test('should recover from transient errors', async ({ page }) => {
    let attemptCount = 0;
    
    await page.route('**/pycmd/**', async (route) => {
      attemptCount++;
      
      // Fail first 2 attempts
      if (attemptCount <= 2) {
        await route.fulfill({
          status: 503,
          body: JSON.stringify({ error: 'Service unavailable' }),
        });
      } else {
        // Succeed on 3rd attempt
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            success: true,
            data: [{ name: 'Front', ordinal: 0 }],
          }),
        });
      }
    });
    
    await page.goto('/');
    await page.waitForTimeout(5000); // Wait for retries
    
    // Verify eventual success
    const errorCount = await page.locator('[data-cy="error-message"]').count();
    expect(errorCount).toBe(0);
  });

  test('should handle permission denied error', async ({ page }) => {
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 403,
        body: JSON.stringify({
          error: 'Permission denied',
          message: 'Insufficient permissions',
        }),
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Verify permission error displayed
    const error = page.locator('[data-cy="permission-error"]');
    await expect(error).toBeVisible();
  });

  test('should handle browser offline mode', async ({ page, context }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
    
    // Go offline
    await context.setOffline(true);
    
    // Attempt operation
    await page.click('[data-cy="reload-fields"]');
    await page.waitForTimeout(1000);
    
    // Verify offline indicator
    await expect(page.locator('[data-cy="offline-indicator"]')).toBeVisible();
    
    // Go back online
    await context.setOffline(false);
    await page.waitForTimeout(500);
    
    // Verify online indicator
    await expect(page.locator('[data-cy="offline-indicator"]')).not.toBeVisible();
  });
});
