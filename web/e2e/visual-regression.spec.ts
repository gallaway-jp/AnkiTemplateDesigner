/**
 * E2E Test: Visual Regression Testing
 * Tests visual appearance of Anki-specific components
 */

import { test, expect } from '@playwright/test';
import {
  setupMockBridge,
  waitForEditorReady,
  dragBlockToCanvas,
  selectBlock,
  editBlockProperty,
  toggleTheme,
} from './helpers/test-helpers';

test.describe('Visual Regression Testing', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
  });

  test('Anki field block should render correctly', async ({ page }) => {
    // Add Anki field block
    await dragBlockToCanvas(page, 'AnkiField');
    
    // Wait for rendering
    await page.waitForTimeout(500);
    
    // Take screenshot
    const fieldBlock = page.locator('[data-block-type="AnkiField"]');
    await expect(fieldBlock).toHaveScreenshot('anki-field-default.png');
  });

  test('Anki field block with custom field should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'AnkiField');
    await selectBlock(page, '[data-block-type="AnkiField"]');
    
    // Change field to 'Back'
    await page.selectOption('[data-property="fieldName"]', 'Back');
    await page.waitForTimeout(300);
    
    // Screenshot
    const fieldBlock = page.locator('[data-block-type="AnkiField"]');
    await expect(fieldBlock).toHaveScreenshot('anki-field-back.png');
  });

  test('Anki cloze block should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'AnkiCloze');
    await page.waitForTimeout(300);
    
    const clozeBlock = page.locator('[data-block-type="AnkiCloze"]');
    await expect(clozeBlock).toHaveScreenshot('anki-cloze-default.png');
  });

  test('Anki conditional block should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'AnkiConditional');
    await page.waitForTimeout(300);
    
    const conditionalBlock = page.locator('[data-block-type="AnkiConditional"]');
    await expect(conditionalBlock).toHaveScreenshot('anki-conditional-default.png');
  });

  test('template with multiple Anki blocks should render correctly', async ({ page }) => {
    // Create a complex Anki template
    await dragBlockToCanvas(page, 'ContainerBlock');
    await dragBlockToCanvas(page, 'AnkiField', '[data-block-type="ContainerBlock"]');
    await dragBlockToCanvas(page, 'AnkiCloze', '[data-block-type="ContainerBlock"]');
    
    await page.waitForTimeout(500);
    
    // Screenshot entire canvas
    const canvas = page.locator('[data-cy="craft-canvas"]');
    await expect(canvas).toHaveScreenshot('anki-template-complex.png');
  });

  test('blocks panel should render correctly', async ({ page }) => {
    const blocksPanel = page.locator('[data-cy="blocks-panel"]');
    await expect(blocksPanel).toHaveScreenshot('blocks-panel.png');
  });

  test('properties panel with Anki field selected should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'AnkiField');
    await selectBlock(page, '[data-block-type="AnkiField"]');
    await page.waitForTimeout(300);
    
    const propertiesPanel = page.locator('[data-cy="properties-panel"]');
    await expect(propertiesPanel).toHaveScreenshot('properties-panel-anki-field.png');
  });

  test('editor toolbar should render correctly', async ({ page }) => {
    const toolbar = page.locator('[data-cy="editor-toolbar"]');
    await expect(toolbar).toHaveScreenshot('editor-toolbar.png');
  });

  test('dark theme should render correctly', async ({ page }) => {
    // Switch to dark theme
    await toggleTheme(page);
    await page.waitForTimeout(300);
    
    // Add some blocks
    await dragBlockToCanvas(page, 'AnkiField');
    await dragBlockToCanvas(page, 'TextBlock');
    
    await page.waitForTimeout(300);
    
    // Screenshot full page
    await expect(page).toHaveScreenshot('full-page-dark-theme.png', {
      fullPage: true,
    });
  });

  test('light theme should render correctly', async ({ page }) => {
    // Ensure light theme
    await page.waitForTimeout(300);
    
    // Add blocks
    await dragBlockToCanvas(page, 'AnkiField');
    await dragBlockToCanvas(page, 'TextBlock');
    
    await page.waitForTimeout(300);
    
    // Screenshot
    await expect(page).toHaveScreenshot('full-page-light-theme.png', {
      fullPage: true,
    });
  });

  test('template preview dialog should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'AnkiField');
    await page.click('[data-cy="preview-button"]');
    await page.waitForTimeout(500);
    
    const previewDialog = page.locator('[data-cy="preview-dialog"]');
    await expect(previewDialog).toHaveScreenshot('preview-dialog.png');
  });

  test('save dialog should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="save-button"]');
    await page.waitForTimeout(300);
    
    const saveDialog = page.locator('[data-cy="save-dialog"]');
    await expect(saveDialog).toHaveScreenshot('save-dialog.png');
  });

  test('load dialog should render correctly', async ({ page }) => {
    await page.click('[data-cy="load-button"]');
    await page.waitForTimeout(300);
    
    const loadDialog = page.locator('[data-cy="load-dialog"]');
    await expect(loadDialog).toHaveScreenshot('load-dialog.png');
  });

  test('error toast should render correctly', async ({ page }) => {
    // Trigger error
    await page.route('**/pycmd/**', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Test error' }),
      });
    });
    
    await page.click('[data-cy="reload-fields"]');
    await page.waitForTimeout(500);
    
    const errorToast = page.locator('[data-cy="toast-error"]');
    await expect(errorToast).toHaveScreenshot('error-toast.png');
  });

  test('success toast should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'TextBlock');
    await page.click('[data-cy="save-button"]');
    await page.fill('[data-cy="template-name-input"]', 'Test');
    await page.click('[data-cy="confirm-save"]');
    await page.waitForTimeout(500);
    
    const successToast = page.locator('[data-cy="toast-success"]');
    await expect(successToast).toHaveScreenshot('success-toast.png');
  });

  test('responsive design at 768px should render correctly', async ({ page }) => {
    // Set viewport to tablet size
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(300);
    
    await dragBlockToCanvas(page, 'AnkiField');
    await page.waitForTimeout(300);
    
    await expect(page).toHaveScreenshot('responsive-768px.png', {
      fullPage: true,
    });
  });

  test('responsive design at 375px should render correctly', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(300);
    
    await expect(page).toHaveScreenshot('responsive-375px.png', {
      fullPage: true,
    });
  });

  test('block hover state should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'TextBlock');
    
    const block = page.locator('[data-block-type="TextBlock"]');
    await block.hover();
    await page.waitForTimeout(200);
    
    await expect(block).toHaveScreenshot('block-hover-state.png');
  });

  test('block selected state should render correctly', async ({ page }) => {
    await dragBlockToCanvas(page, 'TextBlock');
    await selectBlock(page, '[data-block-type="TextBlock"]');
    await page.waitForTimeout(200);
    
    const block = page.locator('[data-block-type="TextBlock"]');
    await expect(block).toHaveScreenshot('block-selected-state.png');
  });

  test('empty canvas state should render correctly', async ({ page }) => {
    const canvas = page.locator('[data-cy="craft-canvas"]');
    await expect(canvas).toHaveScreenshot('empty-canvas.png');
  });

  test('canvas with nested blocks should render correctly', async ({ page }) => {
    // Create nested structure
    await dragBlockToCanvas(page, 'FrameBlock');
    await dragBlockToCanvas(page, 'ContainerBlock', '[data-block-type="FrameBlock"]');
    await dragBlockToCanvas(page, 'AnkiField', '[data-block-type="ContainerBlock"]');
    await dragBlockToCanvas(page, 'TextBlock', '[data-block-type="ContainerBlock"]');
    
    await page.waitForTimeout(500);
    
    const canvas = page.locator('[data-cy="craft-canvas"]');
    await expect(canvas).toHaveScreenshot('canvas-nested-blocks.png');
  });
});
