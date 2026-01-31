/**
 * E2E Test: Drag and Drop Functionality
 * Tests block dragging, positioning, and nesting
 */

import { test, expect } from '@playwright/test';
import {
  setupMockBridge,
  waitForEditorReady,
  dragBlockToCanvas,
  getBlockCount,
  verifyBlockInCanvas,
} from './helpers/test-helpers';

test.describe('Drag and Drop Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
  });

  test('should drag block from panel to canvas', async ({ page }) => {
    // Get initial block count
    const initialCount = await getBlockCount(page);
    
    // Drag a block
    await dragBlockToCanvas(page, 'TextBlock');
    
    // Verify block count increased
    const newCount = await getBlockCount(page);
    expect(newCount).toBe(initialCount + 1);
    
    // Verify block is visible
    await expect(page.locator('[data-block-type="TextBlock"]')).toBeVisible();
  });

  test('should drag multiple blocks to canvas', async ({ page }) => {
    // Drag multiple blocks
    await dragBlockToCanvas(page, 'HeadingBlock');
    await dragBlockToCanvas(page, 'ParagraphBlock');
    await dragBlockToCanvas(page, 'ButtonBlock');
    
    // Verify all blocks exist
    expect(await verifyBlockInCanvas(page, 'HeadingBlock')).toBe(true);
    expect(await verifyBlockInCanvas(page, 'ParagraphBlock')).toBe(true);
    expect(await verifyBlockInCanvas(page, 'ButtonBlock')).toBe(true);
    
    // Verify total count
    const totalBlocks = await getBlockCount(page);
    expect(totalBlocks).toBeGreaterThanOrEqual(3);
  });

  test('should nest blocks inside containers', async ({ page }) => {
    // Add a container
    await dragBlockToCanvas(page, 'ContainerBlock');
    
    // Drag a block into the container
    await dragBlockToCanvas(page, 'TextBlock', '[data-block-type="ContainerBlock"]');
    
    // Verify text block is child of container
    const containerWithText = page.locator('[data-block-type="ContainerBlock"] [data-block-type="TextBlock"]');
    await expect(containerWithText).toBeVisible();
  });

  test('should handle deep nesting', async ({ page }) => {
    // Create: Frame > Container > Column > Text
    await dragBlockToCanvas(page, 'FrameBlock');
    await dragBlockToCanvas(page, 'ContainerBlock', '[data-block-type="FrameBlock"]');
    await dragBlockToCanvas(page, 'ColumnBlock', '[data-block-type="ContainerBlock"]');
    await dragBlockToCanvas(page, 'TextBlock', '[data-block-type="ColumnBlock"]');
    
    // Verify deep nesting structure
    const deeplyNested = page.locator(
      '[data-block-type="FrameBlock"] ' +
      '[data-block-type="ContainerBlock"] ' +
      '[data-block-type="ColumnBlock"] ' +
      '[data-block-type="TextBlock"]'
    );
    
    await expect(deeplyNested).toBeVisible();
  });

  test('should show drop indicators when dragging', async ({ page }) => {
    // Add a container
    await dragBlockToCanvas(page, 'ContainerBlock');
    
    // Start dragging a block
    const block = page.locator('[data-block="TextBlock"]');
    const container = page.locator('[data-block-type="ContainerBlock"]');
    
    const blockBox = await block.boundingBox();
    const containerBox = await container.boundingBox();
    
    if (blockBox && containerBox) {
      // Start drag
      await page.mouse.move(blockBox.x + blockBox.width / 2, blockBox.y + blockBox.height / 2);
      await page.mouse.down();
      
      // Move over container
      await page.mouse.move(containerBox.x + containerBox.width / 2, containerBox.y + containerBox.height / 2);
      
      // Verify drop indicator appears
      await expect(page.locator('[data-drop-indicator]')).toBeVisible();
      
      // Complete drag
      await page.mouse.up();
    }
  });

  test('should reorder blocks via drag and drop', async ({ page }) => {
    // Add three blocks
    await dragBlockToCanvas(page, 'HeadingBlock');
    await page.waitForTimeout(200);
    await dragBlockToCanvas(page, 'ParagraphBlock');
    await page.waitForTimeout(200);
    await dragBlockToCanvas(page, 'TextBlock');
    await page.waitForTimeout(200);
    
    // Get initial order
    const initialBlocks = await page.locator('[data-block-type]').all();
    const initialOrder = await Promise.all(
      initialBlocks.map(b => b.getAttribute('data-block-type'))
    );
    
    // Drag first block to last position
    const firstBlock = page.locator('[data-block-type="HeadingBlock"]');
    const lastBlock = page.locator('[data-block-type="TextBlock"]');
    
    const firstBox = await firstBlock.boundingBox();
    const lastBox = await lastBlock.boundingBox();
    
    if (firstBox && lastBox) {
      await page.mouse.move(firstBox.x + firstBox.width / 2, firstBox.y + firstBox.height / 2);
      await page.mouse.down();
      await page.mouse.move(lastBox.x + lastBox.width / 2, lastBox.y + lastBox.height + 10);
      await page.mouse.up();
      
      await page.waitForTimeout(300);
      
      // Verify order changed
      const newBlocks = await page.locator('[data-block-type]').all();
      const newOrder = await Promise.all(
        newBlocks.map(b => b.getAttribute('data-block-type'))
      );
      
      expect(newOrder).not.toEqual(initialOrder);
    }
  });

  test('should prevent invalid nesting', async ({ page }) => {
    // Try to nest a frame inside a text block (should fail)
    await dragBlockToCanvas(page, 'TextBlock');
    
    // Attempt to drag frame into text
    const frame = page.locator('[data-block="FrameBlock"]');
    const text = page.locator('[data-block-type="TextBlock"]');
    
    const frameBox = await frame.boundingBox();
    const textBox = await text.boundingBox();
    
    if (frameBox && textBox) {
      await page.mouse.move(frameBox.x + frameBox.width / 2, frameBox.y + frameBox.height / 2);
      await page.mouse.down();
      await page.mouse.move(textBox.x + textBox.width / 2, textBox.y + textBox.height / 2);
      
      // Verify invalid drop indicator
      await expect(page.locator('[data-drop-invalid]')).toBeVisible();
      
      await page.mouse.up();
      
      // Verify frame was not nested
      const nestedFrame = page.locator('[data-block-type="TextBlock"] [data-block-type="FrameBlock"]');
      await expect(nestedFrame).not.toBeVisible();
    }
  });

  test('should show visual feedback during drag', async ({ page }) => {
    const block = page.locator('[data-block="HeadingBlock"]');
    const canvas = page.locator('[data-cy="craft-canvas"]');
    
    const blockBox = await block.boundingBox();
    const canvasBox = await canvas.boundingBox();
    
    if (blockBox && canvasBox) {
      // Start drag
      await page.mouse.move(blockBox.x + blockBox.width / 2, blockBox.y + blockBox.height / 2);
      await page.mouse.down();
      
      // Verify dragging state
      await expect(page.locator('[data-dragging="true"]')).toBeVisible();
      
      // Move to canvas
      await page.mouse.move(canvasBox.x + canvasBox.width / 2, canvasBox.y + canvasBox.height / 2);
      
      // Verify ghost/preview element
      await expect(page.locator('[data-drag-ghost]')).toBeVisible();
      
      // Complete drag
      await page.mouse.up();
      
      // Verify dragging state cleared
      await expect(page.locator('[data-dragging="true"]')).not.toBeVisible();
    }
  });

  test('should cancel drag on escape key', async ({ page }) => {
    const block = page.locator('[data-block="TextBlock"]');
    const canvas = page.locator('[data-cy="craft-canvas"]');
    
    const initialCount = await getBlockCount(page);
    
    const blockBox = await block.boundingBox();
    const canvasBox = await canvas.boundingBox();
    
    if (blockBox && canvasBox) {
      // Start drag
      await page.mouse.move(blockBox.x + blockBox.width / 2, blockBox.y + blockBox.height / 2);
      await page.mouse.down();
      await page.mouse.move(canvasBox.x + canvasBox.width / 2, canvasBox.y + canvasBox.height / 2);
      
      // Press escape
      await page.keyboard.press('Escape');
      
      await page.waitForTimeout(200);
      
      // Verify block was not added
      const newCount = await getBlockCount(page);
      expect(newCount).toBe(initialCount);
    }
  });

  test('should handle rapid successive drags', async ({ page }) => {
    // Quickly drag multiple blocks
    await dragBlockToCanvas(page, 'TextBlock');
    await dragBlockToCanvas(page, 'HeadingBlock');
    await dragBlockToCanvas(page, 'ParagraphBlock');
    await dragBlockToCanvas(page, 'ButtonBlock');
    
    await page.waitForTimeout(500);
    
    // Verify all blocks added
    const blockCount = await getBlockCount(page);
    expect(blockCount).toBe(4);
  });
});
