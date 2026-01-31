/**
 * E2E Test Helpers
 * Utility functions for Playwright E2E tests
 */

import { Page, Locator } from '@playwright/test';
import { mockAnkiResponses } from '../fixtures/anki-bridge-mock';

/**
 * Setup mock Anki bridge responses
 */
export async function setupMockBridge(page: Page) {
  await page.route('**/pycmd/**', async (route) => {
    const request = route.request();
    const postData = request.postDataJSON();
    const action = postData?.action;
    
    // Route to appropriate mock response
    const mockResponse = mockAnkiResponses[action as keyof typeof mockAnkiResponses];
    
    if (typeof mockResponse === 'function') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse(postData?.params)),
      });
    } else {
      await route.fulfill({
        status: 404,
        body: JSON.stringify({ error: 'Unknown action' }),
      });
    }
  });
}

/**
 * Wait for editor to be fully loaded
 */
export async function waitForEditorReady(page: Page) {
  // Wait for Craft.js editor to initialize
  await page.waitForSelector('[data-cy="craft-editor"]', { timeout: 10000 });
  
  // Wait for blocks panel to load
  await page.waitForSelector('[data-cy="blocks-panel"]', { timeout: 5000 });
  
  // Wait for any loading spinners to disappear
  await page.waitForSelector('[data-loading="true"]', { state: 'hidden', timeout: 5000 }).catch(() => {
    // Ignore if no loading spinner exists
  });
}

/**
 * Drag a block from the panel to the canvas
 */
export async function dragBlockToCanvas(
  page: Page,
  blockName: string,
  targetSelector: string = '[data-cy="craft-canvas"]'
) {
  const blockSelector = `[data-block="${blockName}"]`;
  const block = page.locator(blockSelector);
  const target = page.locator(targetSelector);
  
  // Get bounding boxes
  const blockBox = await block.boundingBox();
  const targetBox = await target.boundingBox();
  
  if (!blockBox || !targetBox) {
    throw new Error(`Cannot find block "${blockName}" or target`);
  }
  
  // Perform drag and drop
  await page.mouse.move(blockBox.x + blockBox.width / 2, blockBox.y + blockBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height / 2, { steps: 10 });
  await page.mouse.up();
  
  // Wait for block to appear in canvas
  await page.waitForTimeout(500);
}

/**
 * Select a block in the canvas
 */
export async function selectBlock(page: Page, blockSelector: string) {
  await page.click(blockSelector);
  
  // Wait for properties panel to update
  await page.waitForTimeout(300);
}

/**
 * Edit a block property
 */
export async function editBlockProperty(
  page: Page,
  propertyName: string,
  value: string | number | boolean
) {
  const inputSelector = `[data-property="${propertyName}"]`;
  const input = page.locator(inputSelector);
  
  const inputType = await input.getAttribute('type');
  
  if (inputType === 'checkbox') {
    const isChecked = await input.isChecked();
    if ((value === true && !isChecked) || (value === false && isChecked)) {
      await input.click();
    }
  } else {
    await input.fill(String(value));
    await input.blur(); // Trigger onChange
  }
  
  await page.waitForTimeout(200);
}

/**
 * Save the current template
 */
export async function saveTemplate(page: Page, templateName?: string) {
  // Click save button
  await page.click('[data-cy="save-button"]');
  
  // If name is provided, fill in the dialog
  if (templateName) {
    await page.fill('[data-cy="template-name-input"]', templateName);
  }
  
  // Confirm save
  await page.click('[data-cy="confirm-save"]');
  
  // Wait for success toast
  await page.waitForSelector('[data-cy="toast-success"]', { timeout: 5000 });
}

/**
 * Load a template
 */
export async function loadTemplate(page: Page, templateId: number) {
  // Open load dialog
  await page.click('[data-cy="load-button"]');
  
  // Select template from list
  await page.click(`[data-template-id="${templateId}"]`);
  
  // Wait for template to load
  await waitForEditorReady(page);
}

/**
 * Get the serialized template state
 */
export async function getTemplateState(page: Page): Promise<any> {
  return await page.evaluate(() => {
    // Access Craft.js state (this would need to match your actual implementation)
    return (window as any).__CRAFT_STATE__ || {};
  });
}

/**
 * Verify block exists in canvas
 */
export async function verifyBlockInCanvas(page: Page, blockType: string): Promise<boolean> {
  const blockSelector = `[data-block-type="${blockType}"]`;
  const count = await page.locator(blockSelector).count();
  return count > 0;
}

/**
 * Get block count in canvas
 */
export async function getBlockCount(page: Page, blockType?: string): Promise<number> {
  const selector = blockType ? `[data-block-type="${blockType}"]` : '[data-block-type]';
  return await page.locator(selector).count();
}

/**
 * Undo last action
 */
export async function undo(page: Page) {
  await page.click('[data-cy="undo-button"]');
  await page.waitForTimeout(300);
}

/**
 * Redo last undone action
 */
export async function redo(page: Page) {
  await page.click('[data-cy="redo-button"]');
  await page.waitForTimeout(300);
}

/**
 * Clear the canvas
 */
export async function clearCanvas(page: Page) {
  await page.click('[data-cy="clear-canvas-button"]');
  await page.click('[data-cy="confirm-clear"]');
  await page.waitForTimeout(300);
}

/**
 * Toggle theme (dark/light)
 */
export async function toggleTheme(page: Page) {
  await page.click('[data-cy="theme-toggle"]');
  await page.waitForTimeout(300);
}

/**
 * Open preview
 */
export async function openPreview(page: Page) {
  await page.click('[data-cy="preview-button"]');
  await page.waitForSelector('[data-cy="preview-dialog"]', { timeout: 3000 });
}

/**
 * Close preview
 */
export async function closePreview(page: Page) {
  await page.click('[data-cy="close-preview"]');
  await page.waitForSelector('[data-cy="preview-dialog"]', { state: 'hidden' });
}

/**
 * Take a screenshot with a descriptive name
 */
export async function takeScreenshot(page: Page, name: string) {
  await page.screenshot({ 
    path: `e2e-screenshots/${name}.png`,
    fullPage: true,
  });
}

/**
 * Wait for animation to complete
 */
export async function waitForAnimation(page: Page, duration: number = 500) {
  await page.waitForTimeout(duration);
}
