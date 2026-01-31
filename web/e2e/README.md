# E2E Testing with Playwright

End-to-end tests for the Anki Template Designer using Playwright.

## 📁 Directory Structure

```
e2e/
├── fixtures/           # Mock data and test fixtures
│   └── anki-bridge-mock.ts
├── helpers/           # Test utility functions
│   └── test-helpers.ts
├── template-creation.spec.ts  # Template creation workflow tests
├── drag-drop.spec.ts          # Drag and drop functionality tests
└── save-load.spec.ts          # Save/load persistence tests
```

## 🚀 Running E2E Tests

### All Tests
```bash
npm run test:e2e
```

### With UI Mode (Recommended for Development)
```bash
npm run test:e2e:ui
```

### Headed Mode (See Browser)
```bash
npm run test:e2e:headed
```

### Debug Mode (Step Through Tests)
```bash
npm run test:e2e:debug
```

### Specific Browser
```bash
npm run test:e2e:chromium
npm run test:e2e:firefox
```

### View Last Report
```bash
npm run test:e2e:report
```

## 📝 Test Files

### **template-creation.spec.ts** (9 tests)
Tests the complete template creation workflow:
- ✅ Create basic template with text block
- ✅ Create template with multiple blocks
- ✅ Create template with Anki field blocks
- ✅ Edit block properties and see changes
- ✅ Save template with custom name
- ✅ Handle nested block structures
- ✅ Search for blocks in panel
- ✅ Toggle block categories

### **drag-drop.spec.ts** (10 tests)
Tests drag and drop functionality:
- ✅ Drag block from panel to canvas
- ✅ Drag multiple blocks
- ✅ Nest blocks inside containers
- ✅ Handle deep nesting
- ✅ Show drop indicators
- ✅ Reorder blocks via drag and drop
- ✅ Prevent invalid nesting
- ✅ Visual feedback during drag
- ✅ Cancel drag on escape key
- ✅ Handle rapid successive drags

### **save-load.spec.ts** (12 tests)
Tests template persistence:
- ✅ Save template successfully
- ✅ Load template and restore state
- ✅ Prompt before closing with unsaved changes
- ✅ Clear dirty flag after save
- ✅ Preserve template after save and reload
- ✅ Handle save errors gracefully
- ✅ Support undo/redo
- ✅ Maintain undo history
- ✅ Clear redo stack after new action
- ✅ Export template to HTML/CSS
- ✅ Show template metadata
- ✅ Autosave periodically

## 🔧 Configuration

E2E tests are configured in [playwright.config.ts](../playwright.config.ts):

- **Browsers**: Chromium, Firefox
- **Timeout**: 30 seconds per test
- **Retries**: 2 on CI, 0 locally
- **Screenshots**: On failure
- **Video**: On failure
- **Trace**: On first retry

## 🛠️ Writing New Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';
import { setupMockBridge, waitForEditorReady } from './helpers/test-helpers';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
    await waitForEditorReady(page);
  });

  test('should do something', async ({ page }) => {
    // Your test code here
    await expect(page.locator('[data-cy="element"]')).toBeVisible();
  });
});
```

### Using Helper Functions

```typescript
import {
  dragBlockToCanvas,
  selectBlock,
  editBlockProperty,
  saveTemplate,
} from './helpers/test-helpers';

test('example', async ({ page }) => {
  // Drag a block
  await dragBlockToCanvas(page, 'TextBlock');
  
  // Select it
  await selectBlock(page, '[data-block-type="TextBlock"]');
  
  // Edit property
  await editBlockProperty(page, 'content', 'Hello');
  
  // Save
  await saveTemplate(page, 'My Template');
});
```

## 🎯 Data Attributes for Testing

Use these data attributes in your components for reliable test selectors:

- `data-cy="component-name"` - Main component identifier
- `data-block="BlockName"` - Block in panel
- `data-block-type="BlockName"` - Block in canvas
- `data-property="propertyName"` - Property input
- `data-category="CategoryName"` - Block category

## 📊 CI/CD Integration

E2E tests run automatically on:
- Pull requests
- Pushes to main branch
- Before deployment

Results are uploaded as artifacts:
- HTML report
- Screenshots (on failure)
- Videos (on failure)
- Trace files (on retry)

## 🐛 Debugging Tips

1. **Use UI Mode**: `npm run test:e2e:ui`
   - Best for debugging
   - Visual test explorer
   - Time travel debugging

2. **Use Debug Mode**: `npm run test:e2e:debug`
   - Step through tests
   - Inspect page state
   - Interactive console

3. **View Trace**: 
   ```bash
   npx playwright show-trace trace.zip
   ```

4. **Run Single Test**:
   ```bash
   npx playwright test template-creation.spec.ts
   ```

5. **Run Specific Test**:
   ```bash
   npx playwright test -g "should create basic template"
   ```

## 📈 Coverage Goals

- **Critical Paths**: 100%
- **User Workflows**: 90%+
- **Edge Cases**: 80%+

## 🔗 Resources

- [Playwright Documentation](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Test Generator](https://playwright.dev/docs/codegen)

---

**Total E2E Tests**: 31+  
**Estimated Runtime**: 2-5 minutes  
**Browsers**: Chromium, Firefox
