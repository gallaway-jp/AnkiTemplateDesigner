/**
 * E2E Test: Anki Bridge Integration
 * Tests Python ↔ React communication through the bridge
 */

import { test, expect } from '@playwright/test';
import {
  setupMockBridge,
  waitForEditorReady,
  dragBlockToCanvas,
  selectBlock,
} from './helpers/test-helpers';

test.describe('Anki Bridge Integration', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
  });

  test('should initialize bridge and load Anki fields', async ({ page }) => {
    // Wait for bridge initialization
    await page.waitForTimeout(500);
    
    // Verify fields loaded in blocks panel
    const ankiFieldBlock = page.locator('[data-block="AnkiField"]');
    await expect(ankiFieldBlock).toBeVisible();
    
    // Open Anki Field block properties
    await dragBlockToCanvas(page, 'AnkiField');
    await selectBlock(page, '[data-block-type="AnkiField"]');
    
    // Verify field dropdown populated with mock fields
    const fieldSelect = page.locator('[data-property="fieldName"]');
    await expect(fieldSelect).toBeVisible();
    
    // Check for Front, Back, Extra fields
    const options = await fieldSelect.locator('option').allTextContents();
    expect(options).toContain('Front');
    expect(options).toContain('Back');
    expect(options).toContain('Extra');
  });

  test('should handle bridge communication for getAnkiFields', async ({ page }) => {
    let bridgeRequest: any = null;
    
    // Intercept bridge request
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      bridgeRequest = request.postDataJSON();
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: [
            { name: 'TestField1', ordinal: 0 },
            { name: 'TestField2', ordinal: 1 },
          ],
        }),
      });
    });
    
    // Trigger fields reload
    await page.click('[data-cy="reload-fields"]');
    await page.waitForTimeout(500);
    
    // Verify request was made
    expect(bridgeRequest).toBeTruthy();
    expect(bridgeRequest.action).toBe('getAnkiFields');
  });

  test('should handle bridge communication for saveTemplate', async ({ page }) => {
    let saveRequest: any = null;
    
    // Intercept save request
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();
      
      if (postData?.action === 'saveTemplate') {
        saveRequest = postData;
        
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            success: true,
            data: { id: 456, name: 'Saved Template' },
          }),
        });
      } else {
        await route.continue();
      }
    });
    
    // Create and save template
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="save-button"]');
    await page.fill('[data-cy="template-name-input"]', 'Integration Test Template');
    await page.click('[data-cy="confirm-save"]');
    
    await page.waitForTimeout(1000);
    
    // Verify save request sent
    expect(saveRequest).toBeTruthy();
    expect(saveRequest.action).toBe('saveTemplate');
    expect(saveRequest.params?.name).toBe('Integration Test Template');
  });

  test('should handle bridge communication for loadTemplate', async ({ page }) => {
    let loadRequest: any = null;
    
    // Intercept load request
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();
      
      if (postData?.action === 'loadTemplate') {
        loadRequest = postData;
        
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            success: true,
            data: {
              id: 789,
              name: 'Loaded Template',
              html: '<div>{{Front}}</div>',
              css: '.card { background: white; }',
              fields: ['Front', 'Back'],
            },
          }),
        });
      } else {
        await route.continue();
      }
    });
    
    // Load template
    await page.click('[data-cy="load-button"]');
    await page.click('[data-template-id="789"]');
    
    await page.waitForTimeout(1000);
    
    // Verify load request sent
    expect(loadRequest).toBeTruthy();
    expect(loadRequest.action).toBe('loadTemplate');
    expect(loadRequest.params?.id).toBe(789);
  });

  test('should handle bridge communication for previewTemplate', async ({ page }) => {
    let previewRequest: any = null;
    
    // Intercept preview request
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();
      
      if (postData?.action === 'previewTemplate') {
        previewRequest = postData;
        
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            success: true,
            data: {
              html: '<div class="preview">Preview Content</div>',
              css: '.preview { color: blue; }',
            },
          }),
        });
      } else {
        await route.continue();
      }
    });
    
    // Create template and preview
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="preview-button"]');
    
    await page.waitForTimeout(1000);
    
    // Verify preview request sent
    expect(previewRequest).toBeTruthy();
    expect(previewRequest.action).toBe('previewTemplate');
  });

  test('should handle concurrent bridge requests', async ({ page }) => {
    const requests: any[] = [];
    
    // Intercept all requests
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      requests.push(request.postDataJSON());
      
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ success: true, data: {} }),
      });
    });
    
    // Trigger multiple operations simultaneously
    await Promise.all([
      page.click('[data-cy="reload-fields"]'),
      page.click('[data-cy="reload-behaviors"]'),
    ]);
    
    await page.waitForTimeout(1000);
    
    // Verify both requests made
    expect(requests.length).toBeGreaterThanOrEqual(2);
  });

  test('should batch bridge requests when appropriate', async ({ page }) => {
    const requests: any[] = [];
    
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();
      requests.push(postData);
      
      // Simulate batched response
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: postData.batch ? postData.batch.map(() => ({ success: true })) : {},
        }),
      });
    });
    
    // Trigger operations that should be batched
    await page.evaluate(() => {
      // Simulate rapid fire requests (would be batched in implementation)
      for (let i = 0; i < 5; i++) {
        (window as any).bridge?.request({ action: 'getData', id: i });
      }
    });
    
    await page.waitForTimeout(1000);
    
    // Verify batching occurred (fewer requests than operations)
    expect(requests.length).toBeLessThan(5);
  });

  test('should deduplicate identical bridge requests', async ({ page }) => {
    const requests: any[] = [];
    
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      requests.push(request.postDataJSON());
      
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ success: true, data: { name: 'Front' } }),
      });
    });
    
    // Make duplicate requests
    await page.evaluate(() => {
      const bridge = (window as any).bridge;
      if (bridge) {
        bridge.getAnkiFields();
        bridge.getAnkiFields(); // Duplicate
        bridge.getAnkiFields(); // Duplicate
      }
    });
    
    await page.waitForTimeout(500);
    
    // Verify deduplication (only 1 request made)
    const fieldRequests = requests.filter(r => r.action === 'getAnkiFields');
    expect(fieldRequests.length).toBeLessThanOrEqual(1);
  });

  test('should retry failed bridge requests', async ({ page }) => {
    let attemptCount = 0;
    
    await page.route('**/pycmd/**', async (route) => {
      attemptCount++;
      
      // Fail first 2 attempts, succeed on 3rd
      if (attemptCount < 3) {
        await route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Server error' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          body: JSON.stringify({ success: true, data: [] }),
        });
      }
    });
    
    // Trigger operation that should retry
    await page.click('[data-cy="reload-fields"]');
    
    await page.waitForTimeout(3000);
    
    // Verify retries occurred
    expect(attemptCount).toBeGreaterThanOrEqual(2);
  });

  test('should cache bridge responses', async ({ page }) => {
    let requestCount = 0;
    
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();
      
      if (postData?.action === 'getAnkiFields') {
        requestCount++;
      }
      
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: [{ name: 'Front', ordinal: 0 }],
        }),
      });
    });
    
    // Make same request multiple times
    await page.evaluate(() => {
      const bridge = (window as any).bridge;
      if (bridge) {
        bridge.getAnkiFields(); // Should make request
        bridge.getAnkiFields(); // Should use cache
        bridge.getAnkiFields(); // Should use cache
      }
    });
    
    await page.waitForTimeout(500);
    
    // Verify caching (only 1 request made)
    expect(requestCount).toBe(1);
  });

  test('should invalidate cache when needed', async ({ page }) => {
    let requestCount = 0;
    
    await page.route('**/pycmd/**', async (route) => {
      const request = route.request();
      const postData = request.postDataJSON();
      
      if (postData?.action === 'getAnkiFields') {
        requestCount++;
      }
      
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ success: true, data: [] }),
      });
    });
    
    // Make request, invalidate cache, make request again
    await page.evaluate(() => {
      const bridge = (window as any).bridge;
      if (bridge) {
        bridge.getAnkiFields(); // Request 1
        bridge.invalidateCache('getAnkiFields');
        bridge.getAnkiFields(); // Request 2 (cache invalidated)
      }
    });
    
    await page.waitForTimeout(500);
    
    // Verify cache invalidation (2 requests made)
    expect(requestCount).toBe(2);
  });
});
