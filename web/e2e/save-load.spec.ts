/**
 * E2E Test: Save and Load Template
 * Tests template persistence, saving, and loading
 */

import { test, expect } from '@playwright/test';
import {
  setupMockBridge,
  waitForEditorReady,
  dragBlockToCanvas,
  selectBlock,
  editBlockProperty,
  saveTemplate,
  loadTemplate,
  getBlockCount,
  verifyBlockInCanvas,
  clearCanvas,
  undo,
  redo,
} from './helpers/test-helpers';

test.describe('Save and Load Template', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
  });

  test('should save template successfully', async ({ page }) => {
    // Create a simple template
    await dragBlockToCanvas(page, 'TextBlock');
    await selectBlock(page, '[data-block-type="TextBlock"]');
    await editBlockProperty(page, 'content', 'Saved Content');
    
    // Save template
    await saveTemplate(page, 'Test Template');
    
    // Verify success notification
    await expect(page.locator('[data-cy="toast-success"]')).toBeVisible();
    
    // Verify template marked as clean (not dirty)
    const isDirty = await page.locator('[data-dirty="true"]').count();
    expect(isDirty).toBe(0);
  });

  test('should load template and restore state', async ({ page }) => {
    // Load a template
    await loadTemplate(page, 123);
    
    // Verify editor loaded
    await waitForEditorReady(page);
    
    // Verify template name displayed
    const templateName = await page.locator('[data-cy="template-name"]').textContent();
    expect(templateName).toContain('Loaded Template');
    
    // Verify content loaded (mocked data has TextBlock)
    // This depends on your mock data structure
  });

  test('should prompt before closing with unsaved changes', async ({ page }) => {
    // Make changes
    await dragBlockToCanvas(page, 'TextBlock');
    
    // Verify dirty state
    const isDirty = await page.locator('[data-dirty="true"]').count();
    expect(isDirty).toBeGreaterThan(0);
    
    // Setup dialog handler
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('unsaved');
      await dialog.dismiss();
    });
    
    // Attempt to navigate away
    await page.click('[data-cy="new-template"]');
  });

  test('should clear dirty flag after save', async ({ page }) => {
    // Make changes
    await dragBlockToCanvas(page, 'HeadingBlock');
    
    // Verify dirty
    await expect(page.locator('[data-dirty="true"]')).toBeVisible();
    
    // Save
    await saveTemplate(page, 'Clean Template');
    
    // Verify clean
    const isDirty = await page.locator('[data-dirty="true"]').count();
    expect(isDirty).toBe(0);
  });

  test('should preserve template after save and reload', async ({ page }) => {
    // Create template
    await dragBlockToCanvas(page, 'HeadingBlock');
    await dragBlockToCanvas(page, 'ParagraphBlock');
    await dragBlockToCanvas(page, 'ButtonBlock');
    
    const initialCount = await getBlockCount(page);
    
    // Save
    await saveTemplate(page, 'Persistent Template');
    
    // Clear canvas
    await clearCanvas(page);
    
    // Verify empty
    expect(await getBlockCount(page)).toBe(0);
    
    // Load template
    await loadTemplate(page, 123);
    
    // Verify blocks restored
    const restoredCount = await getBlockCount(page);
    expect(restoredCount).toBe(initialCount);
  });

  test('should handle save errors gracefully', async ({ page }) => {
    // Override mock to return error
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Save failed' }),
      });
    });
    
    // Attempt save
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="save-button"]');
    await page.fill('[data-cy="template-name-input"]', 'Error Template');
    await page.click('[data-cy="confirm-save"]');
    
    // Verify error toast
    await expect(page.locator('[data-cy="toast-error"]')).toBeVisible();
    
    // Verify still dirty
    const isDirty = await page.locator('[data-dirty="true"]').count();
    expect(isDirty).toBeGreaterThan(0);
  });

  test('should support undo/redo', async ({ page }) => {
    // Add a block
    await dragBlockToCanvas(page, 'TextBlock');
    
    expect(await getBlockCount(page)).toBe(1);
    
    // Undo
    await undo(page);
    
    // Verify block removed
    expect(await getBlockCount(page)).toBe(0);
    
    // Redo
    await redo(page);
    
    // Verify block back
    expect(await getBlockCount(page)).toBe(1);
  });

  test('should maintain undo history across multiple actions', async ({ page }) => {
    // Perform multiple actions
    await dragBlockToCanvas(page, 'HeadingBlock');
    await dragBlockToCanvas(page, 'ParagraphBlock');
    await dragBlockToCanvas(page, 'TextBlock');
    
    expect(await getBlockCount(page)).toBe(3);
    
    // Undo all
    await undo(page);
    expect(await getBlockCount(page)).toBe(2);
    
    await undo(page);
    expect(await getBlockCount(page)).toBe(1);
    
    await undo(page);
    expect(await getBlockCount(page)).toBe(0);
    
    // Redo all
    await redo(page);
    expect(await getBlockCount(page)).toBe(1);
    
    await redo(page);
    expect(await getBlockCount(page)).toBe(2);
    
    await redo(page);
    expect(await getBlockCount(page)).toBe(3);
  });

  test('should clear redo stack after new action', async ({ page }) => {
    // Add blocks
    await dragBlockToCanvas(page, 'TextBlock');
    await dragBlockToCanvas(page, 'HeadingBlock');
    
    // Undo once
    await undo(page);
    
    // Verify redo available
    const redoButton = page.locator('[data-cy="redo-button"]');
    await expect(redoButton).toBeEnabled();
    
    // Perform new action
    await dragBlockToCanvas(page, 'ParagraphBlock');
    
    // Verify redo disabled (stack cleared)
    await expect(redoButton).toBeDisabled();
  });

  test('should export template to HTML/CSS', async ({ page }) => {
    // Create template
    await dragBlockToCanvas(page, 'TextBlock');
    await selectBlock(page, '[data-block-type="TextBlock"]');
    await editBlockProperty(page, 'content', 'Export Test');
    
    // Click export button
    await page.click('[data-cy="export-button"]');
    
    // Wait for download dialog
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-cy="export-html"]');
    const download = await downloadPromise;
    
    // Verify download started
    expect(download.suggestedFilename()).toContain('.html');
  });

  test('should show template metadata', async ({ page }) => {
    // Load template
    await loadTemplate(page, 123);
    
    // Open info panel
    await page.click('[data-cy="template-info"]');
    
    // Verify metadata displayed
    await expect(page.locator('[data-cy="template-id"]')).toBeVisible();
    await expect(page.locator('[data-cy="template-created"]')).toBeVisible();
    await expect(page.locator('[data-cy="template-updated"]')).toBeVisible();
  });

  test('should autosave periodically', async ({ page }) => {
    // Enable autosave
    await page.click('[data-cy="settings"]');
    await page.click('[data-cy="enable-autosave"]');
    await page.selectOption('[data-cy="autosave-interval"]', '5');
    await page.click('[data-cy="close-settings"]');
    
    // Make changes
    await dragBlockToCanvas(page, 'TextBlock');
    
    // Wait for autosave (5 seconds)
    await page.waitForTimeout(6000);
    
    // Verify autosave notification
    await expect(page.locator('[data-cy="autosave-indicator"]')).toContainText('Saved');
  });
});
