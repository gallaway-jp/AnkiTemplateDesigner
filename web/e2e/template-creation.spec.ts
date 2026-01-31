/**
 * E2E Test: Template Creation Workflow
 * Tests the complete flow of creating a template from scratch
 */

import { test, expect } from '@playwright/test';
import {
  setupMockBridge,
  waitForEditorReady,
  dragBlockToCanvas,
  selectBlock,
  editBlockProperty,
  saveTemplate,
  verifyBlockInCanvas,
  getBlockCount,
} from './helpers/test-helpers';

test.describe('Template Creation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Setup mock Anki bridge
    await setupMockBridge(page);
    
    // Navigate to the editor
    await page.goto('/');
    
    // Wait for editor to be ready
    await waitForEditorReady(page);
  });

  test('should create a basic template with text block', async ({ page }) => {
    // 1. Verify editor is loaded
    await expect(page.locator('[data-cy="craft-editor"]')).toBeVisible();
    await expect(page.locator('[data-cy="blocks-panel"]')).toBeVisible();
    
    // 2. Drag a text block to canvas
    await dragBlockToCanvas(page, 'TextBlock');
    
    // 3. Verify block appeared in canvas
    const hasTextBlock = await verifyBlockInCanvas(page, 'TextBlock');
    expect(hasTextBlock).toBe(true);
    
    // 4. Select the block
    await selectBlock(page, '[data-block-type="TextBlock"]');
    
    // 5. Verify properties panel shows block properties
    await expect(page.locator('[data-cy="properties-panel"]')).toBeVisible();
    
    // 6. Edit block content
    await editBlockProperty(page, 'content', 'Hello, Anki!');
    
    // 7. Verify content updated
    const blockContent = await page.locator('[data-block-type="TextBlock"]').textContent();
    expect(blockContent).toContain('Hello, Anki!');
  });

  test('should create a template with multiple blocks', async ({ page }) => {
    // Add container block
    await dragBlockToCanvas(page, 'ContainerBlock');
    
    // Verify container added
    expect(await verifyBlockInCanvas(page, 'ContainerBlock')).toBe(true);
    
    // Add heading inside container
    await dragBlockToCanvas(page, 'HeadingBlock', '[data-block-type="ContainerBlock"]');
    
    // Add paragraph
    await dragBlockToCanvas(page, 'ParagraphBlock', '[data-block-type="ContainerBlock"]');
    
    // Verify total block count
    const totalBlocks = await getBlockCount(page);
    expect(totalBlocks).toBeGreaterThanOrEqual(3);
    
    // Verify heading exists
    expect(await verifyBlockInCanvas(page, 'HeadingBlock')).toBe(true);
    
    // Verify paragraph exists
    expect(await verifyBlockInCanvas(page, 'ParagraphBlock')).toBe(true);
  });

  test('should create template with Anki field block', async ({ page }) => {
    // Drag Anki Field block
    await dragBlockToCanvas(page, 'AnkiField');
    
    // Verify block added
    expect(await verifyBlockInCanvas(page, 'AnkiField')).toBe(true);
    
    // Select the field block
    await selectBlock(page, '[data-block-type="AnkiField"]');
    
    // Change field name in properties
    await page.selectOption('[data-property="fieldName"]', 'Front');
    
    // Verify field displays correct syntax
    const fieldContent = await page.locator('[data-block-type="AnkiField"]').textContent();
    expect(fieldContent).toContain('{{Front}}');
  });

  test('should edit block properties and see changes', async ({ page }) => {
    // Add a button block
    await dragBlockToCanvas(page, 'ButtonBlock');
    
    // Select it
    await selectBlock(page, '[data-block-type="ButtonBlock"]');
    
    // Edit button text
    await editBlockProperty(page, 'text', 'Click Me');
    
    // Edit button style
    await page.selectOption('[data-property="variant"]', 'primary');
    
    // Verify changes
    const buttonText = await page.locator('[data-block-type="ButtonBlock"]').textContent();
    expect(buttonText).toContain('Click Me');
    
    const buttonClass = await page.locator('[data-block-type="ButtonBlock"]').getAttribute('class');
    expect(buttonClass).toContain('primary');
  });

  test('should save template with custom name', async ({ page }) => {
    // Create a simple template
    await dragBlockToCanvas(page, 'TextBlock');
    await selectBlock(page, '[data-block-type="TextBlock"]');
    await editBlockProperty(page, 'content', 'Test Template Content');
    
    // Save template
    await saveTemplate(page, 'My Test Template');
    
    // Verify success toast appears
    await expect(page.locator('[data-cy="toast-success"]')).toBeVisible();
    
    // Verify success message
    const toastText = await page.locator('[data-cy="toast-success"]').textContent();
    expect(toastText).toContain('saved');
  });

  test('should handle template with nested structure', async ({ page }) => {
    // Create nested structure: Frame > Container > Heading + Text
    await dragBlockToCanvas(page, 'FrameBlock');
    
    // Add container inside frame
    await dragBlockToCanvas(page, 'ContainerBlock', '[data-block-type="FrameBlock"]');
    
    // Add heading inside container
    await dragBlockToCanvas(page, 'HeadingBlock', '[data-block-type="ContainerBlock"]');
    
    // Add text inside container
    await dragBlockToCanvas(page, 'TextBlock', '[data-block-type="ContainerBlock"]');
    
    // Verify structure
    const frameExists = await verifyBlockInCanvas(page, 'FrameBlock');
    const containerExists = await verifyBlockInCanvas(page, 'ContainerBlock');
    const headingExists = await verifyBlockInCanvas(page, 'HeadingBlock');
    const textExists = await verifyBlockInCanvas(page, 'TextBlock');
    
    expect(frameExists).toBe(true);
    expect(containerExists).toBe(true);
    expect(headingExists).toBe(true);
    expect(textExists).toBe(true);
    
    // Verify total count
    const totalBlocks = await getBlockCount(page);
    expect(totalBlocks).toBe(4);
  });

  test('should search for blocks in panel', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('[data-cy="blocks-search"]');
    await expect(searchInput).toBeVisible();
    
    // Search for "text"
    await searchInput.fill('text');
    
    // Verify only matching blocks visible
    const visibleBlocks = await page.locator('[data-cy="block-item"]:visible').count();
    
    // Should show TextBlock, TextFieldBlock, etc.
    expect(visibleBlocks).toBeGreaterThan(0);
    
    // Verify non-matching blocks are hidden
    await expect(page.locator('[data-block="ButtonBlock"]')).toBeHidden();
  });

  test('should toggle block categories', async ({ page }) => {
    // Find a category header
    const layoutCategory = page.locator('[data-category="Layout"]');
    await expect(layoutCategory).toBeVisible();
    
    // Click to collapse
    await layoutCategory.click();
    
    // Verify blocks hidden
    const layoutBlocks = page.locator('[data-category="Layout"] [data-cy="block-item"]');
    await expect(layoutBlocks.first()).toBeHidden();
    
    // Click again to expand
    await layoutCategory.click();
    
    // Verify blocks visible
    await expect(layoutBlocks.first()).toBeVisible();
  });
});
