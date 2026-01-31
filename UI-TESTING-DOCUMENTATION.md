# UI Testing Documentation - Complete Guide

**Last Updated:** January 2025  
**Status:** Complete - 110+ Tests Implemented  
**Sessions:** Foundation + E2E + Anki Integration

## Table of Contents

- [Overview](#overview)
- [Test Infrastructure](#test-infrastructure)
- [Test Types](#test-types)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [CI/CD Integration](#cicd-integration)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

The Anki Template Designer has comprehensive automated testing covering:
- **35 Unit/Integration Tests** - Component snapshots and accessibility
- **31 E2E Tests** - User workflows with Playwright
- **11 Bridge Integration Tests** - Python ↔ React communication
- **13 Error Handling Tests** - Failure scenarios and recovery
- **20+ Visual Regression Tests** - Screenshot comparison

### Testing Tools

| Tool | Purpose | Version |
|------|---------|---------|
| Vitest | Unit/Integration testing | ^1.6.1 |
| React Testing Library | Component testing | ^14.0.0 |
| jest-axe | Accessibility testing | ^9.0.0 |
| Playwright | E2E browser testing | Latest |

---

## Test Infrastructure

### Configuration Files

#### `vitest.config.ts`
```typescript
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/tests/']
    },
    snapshotFormat: {
      printBasicPrototype: false,
      escapeString: false
    }
  }
});
```

#### `playwright.config.ts`
```typescript
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI
  }
});
```

### Setup Files

#### `src/tests/setup.ts`
Global test setup with jest-axe matchers:
```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, expect } from 'vitest';
import { toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

afterEach(() => {
  cleanup();
});
```

---

## Test Types

### 1. Snapshot Tests

**Purpose:** Catch unintended UI changes by comparing component output to saved snapshots.

**Location:** `src/components/**/*.snapshot.test.tsx`

**Coverage:**
- `Editor.snapshot.test.tsx` (3 tests) - Main editor states
- `CraftEditor.snapshot.test.tsx` (4 tests) - Craft.js integration
- `AnkiBlocks.snapshot.test.tsx` (5 tests) - Anki-specific blocks
- `TemplatePreview.snapshot.test.tsx` (3 tests) - Preview rendering
- `BlocksPanel.snapshot.test.tsx` (3 tests) - Blocks panel variations

**Example:**
```typescript
it('renders with empty template', () => {
  const { container } = render(
    <Editor template={emptyTemplate} onSave={vi.fn()} />
  );
  expect(container).toMatchSnapshot();
});
```

### 2. Accessibility Tests

**Purpose:** Ensure components meet WCAG 2.1 AA standards.

**Location:** `src/components/Panels/Panels.accessibility.test.tsx`

**Coverage:**
- BlocksPanel (6 tests)
- SettingsPanel (5 tests)
- LayersPanel (6 tests)

**Example:**
```typescript
it('BlocksPanel has no accessibility violations', async () => {
  const { container } = render(<BlocksPanel />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### 3. E2E Tests (Playwright)

**Purpose:** Test complete user workflows in real browsers.

**Location:** `web/e2e/`

**Coverage:**
- `template-creation.spec.ts` (9 tests) - Creating templates
- `drag-drop.spec.ts` (10 tests) - Drag and drop interactions
- `save-load.spec.ts` (12 tests) - Template persistence

**Example:**
```typescript
test('should create basic template with text block', async ({ page }) => {
  await setupMockBridge(page);
  await dragBlockToCanvas(page, 'Text');
  await saveTemplate(page);
  await expect(page.getByText('Template saved')).toBeVisible();
});
```

### 4. Anki Bridge Integration Tests

**Purpose:** Test Python ↔ React communication.

**Location:** `web/e2e/anki-bridge.spec.ts`

**Coverage (11 tests):**
- Field loading from Anki
- Template save/load requests
- Concurrent request handling
- Request batching
- Response deduplication
- Retry logic
- Response caching
- Cache invalidation

**Example:**
```typescript
test('should load Anki fields on initialization', async ({ page }) => {
  await page.route('**/anki/fields', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        fields: ['Front', 'Back', 'Extra']
      })
    });
  });
  
  await page.goto('/');
  await expect(page.getByText('Front')).toBeVisible();
});
```

### 5. Error Handling Tests

**Purpose:** Test failure scenarios and recovery.

**Location:** `web/e2e/error-handling.spec.ts`

**Coverage (13 tests):**
- Bridge initialization failures
- Request timeouts
- HTTP 500/404 errors
- Invalid JSON responses
- Network disconnections
- Version conflicts
- Quota exceeded errors
- Transient error retry
- Permission denials
- Offline mode handling

**Example:**
```typescript
test('should handle timeout errors gracefully', async ({ page }) => {
  await page.route('**/anki/save', route => {
    // Delay response beyond timeout
    setTimeout(() => route.abort(), 35000);
  });
  
  await saveTemplate(page);
  await expect(page.getByText(/request timed out/i)).toBeVisible();
});
```

### 6. Visual Regression Tests

**Purpose:** Detect visual changes using screenshot comparison.

**Location:** `web/e2e/visual-regression.spec.ts`

**Coverage (20+ tests):**
- Anki blocks (Field, Cloze, Conditional)
- Panels (Blocks, Settings, Layers)
- Toolbar components
- Theme variations (light/dark)
- Responsive layouts (desktop/tablet/mobile)
- Dialog components
- Toast notifications
- Hover/selected states
- Nested block structures

**Example:**
```typescript
test('visual: Anki field block', async ({ page }) => {
  await page.goto('/');
  await dragBlockToCanvas(page, 'Anki Field');
  await expect(page.locator('canvas')).toHaveScreenshot('anki-field-block.png');
});
```

---

## Quick Start

### Installation

```bash
cd web
npm install
```

### Run All Tests

```bash
# Unit + Integration tests
npm test

# E2E tests (both browsers)
npm run test:e2e

# All tests
npm run test:all
```

### Development Mode

```bash
# Unit tests with watch mode
npm test

# E2E tests with UI
npm run test:e2e:ui

# E2E tests with debugging
npm run test:e2e:debug
```

---

## Running Tests

### Unit/Integration Tests

```bash
# Run all tests once
npm test -- --run

# Watch mode
npm test

# With coverage
npm run test:coverage

# Specific file
npm test Editor.snapshot.test.tsx

# Update snapshots
npm test -- -u
```

### E2E Tests

```bash
# All E2E tests
npm run test:e2e

# Specific browser
npm run test:e2e:chromium
npm run test:e2e:firefox

# Interactive UI mode
npm run test:e2e:ui

# Debug mode (headed browser)
npm run test:e2e:debug

# Specific test file
npx playwright test template-creation.spec.ts

# Update visual snapshots
npx playwright test --update-snapshots
```

### Accessibility Tests

```bash
# Run only accessibility tests
npm test -- --run src/components/Panels/Panels.accessibility.test.tsx

# Watch mode for a11y
npm test Panels.accessibility.test.tsx
```

---

## Test Organization

### Directory Structure

```
web/
├── src/
│   ├── components/
│   │   ├── Editor.snapshot.test.tsx
│   │   ├── CraftEditor.snapshot.test.tsx
│   │   ├── AnkiBlocks.snapshot.test.tsx
│   │   ├── TemplatePreview.snapshot.test.tsx
│   │   └── Panels/
│   │       ├── BlocksPanel.snapshot.test.tsx
│   │       └── Panels.accessibility.test.tsx
│   └── tests/
│       └── setup.ts
├── e2e/
│   ├── template-creation.spec.ts
│   ├── drag-drop.spec.ts
│   ├── save-load.spec.ts
│   ├── anki-bridge.spec.ts
│   ├── error-handling.spec.ts
│   ├── visual-regression.spec.ts
│   ├── fixtures/
│   │   └── anki-bridge-mock.ts
│   ├── helpers/
│   │   └── test-helpers.ts
│   └── README.md
├── vitest.config.ts
├── playwright.config.ts
└── package.json
```

### Test File Naming Conventions

| Test Type | Pattern | Example |
|-----------|---------|---------|
| Snapshot | `*.snapshot.test.tsx` | `Editor.snapshot.test.tsx` |
| Accessibility | `*.accessibility.test.tsx` | `Panels.accessibility.test.tsx` |
| E2E | `*.spec.ts` | `template-creation.spec.ts` |
| Integration | `*.integration.test.tsx` | `store.integration.test.tsx` |

---

## CI/CD Integration

### GitHub Actions Workflow

**Location:** `.github/workflows/ui-tests.yml`

**Jobs:**
1. **Unit Tests** - Vitest with coverage reporting
2. **E2E Tests** - Playwright matrix (Chromium + Firefox)
3. **Accessibility Tests** - jest-axe validation
4. **Snapshot Tests** - Snapshot verification
5. **Performance Tests** - Performance benchmarks
6. **Test Summary** - Aggregated results

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Artifacts:**
- Coverage reports (30 days retention)
- Playwright test results (30 days retention)
- Failure screenshots (7 days retention)
- Trace files for debugging (7 days retention)

### Running Tests in CI

```yaml
# Example job configuration
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --run --reporter=verbose
      - run: npm run test:coverage
```

### Viewing CI Results

1. Navigate to **Actions** tab in GitHub repository
2. Select **UI Tests** workflow
3. View individual job results
4. Download artifacts for detailed reports

---

## Writing New Tests

### Snapshot Test Template

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent - Snapshots', () => {
  it('renders default state', () => {
    const { container } = render(<MyComponent />);
    expect(container).toMatchSnapshot();
  });

  it('renders with props', () => {
    const { container } = render(
      <MyComponent title="Test" enabled={true} />
    );
    expect(container).toMatchSnapshot();
  });
});
```

### Accessibility Test Template

```typescript
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { MyComponent } from './MyComponent';

describe('MyComponent - Accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<MyComponent />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### E2E Test Template

```typescript
import { test, expect } from '@playwright/test';
import { setupMockBridge } from './fixtures/anki-bridge-mock';

test.describe('My Feature', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockBridge(page);
    await page.goto('/');
  });

  test('should perform action', async ({ page }) => {
    await page.click('button[aria-label="Action"]');
    await expect(page.getByText('Success')).toBeVisible();
  });
});
```

### Mock Bridge Helper

```typescript
// e2e/fixtures/anki-bridge-mock.ts
export async function setupMockBridge(page: Page) {
  await page.route('**/anki/fields', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        fields: ['Front', 'Back']
      })
    });
  });
}
```

---

## Troubleshooting

### Common Issues

#### 1. Snapshot Mismatch

**Error:** `Snapshot doesn't match`

**Solution:**
```bash
# Review changes
npm test -- --run Editor.snapshot.test.tsx

# Update if intentional
npm test -- -u
```

#### 2. Playwright Browser Not Found

**Error:** `browserType.launch: Executable doesn't exist`

**Solution:**
```bash
npx playwright install chromium firefox
```

#### 3. Dev Server Not Starting

**Error:** `Error: connect ECONNREFUSED 127.0.0.1:5173`

**Solution:**
```bash
# Ensure dev server is running
npm run dev

# Or let Playwright start it automatically
npm run test:e2e
```

#### 4. Accessibility Violations

**Error:** `Expected no accessibility violations but received 2`

**Solution:**
```typescript
// Check the violation details in test output
// Common issues:
// - Missing alt text: <img alt="Description" />
// - Insufficient color contrast
// - Missing ARIA labels: <button aria-label="Close" />
```

#### 5. Visual Regression Failures

**Error:** `Screenshot comparison failed`

**Solution:**
```bash
# View the diff
npx playwright show-report

# Update baseline if intentional
npx playwright test --update-snapshots
```

#### 6. PowerShell Execution Policy (Windows)

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
# Use cmd workaround
cmd /c "npm test"

# Or update execution policy (admin required)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## Best Practices

### 1. Test Independence
- Each test should be self-contained
- Use `beforeEach` for setup, `afterEach` for cleanup
- Don't rely on test execution order

### 2. Mock Strategy
- Mock external dependencies (Anki bridge, network)
- Use fixtures for consistent test data
- Avoid testing implementation details

### 3. Accessibility First
- Run accessibility tests on all UI components
- Test with keyboard navigation
- Verify ARIA attributes and roles

### 4. Snapshot Hygiene
- Keep snapshots focused and minimal
- Review snapshot changes carefully
- Don't snapshot dynamic data (timestamps, IDs)

### 5. E2E Test Patterns
```typescript
// ✅ Good: Use page object pattern
const editor = new EditorPage(page);
await editor.addBlock('Text');
await editor.save();

// ❌ Avoid: Hardcoded selectors everywhere
await page.click('.editor > div:nth-child(2) > button');
```

### 6. Visual Testing
- Use consistent viewport sizes
- Test both light and dark themes
- Update snapshots deliberately

### 7. Coverage Goals
- Aim for 80%+ code coverage
- Focus on critical user paths
- Don't chase 100% at expense of test quality

### 8. Performance
- Parallelize E2E tests when possible
- Use test.describe.parallel() for independent tests
- Clean up resources after tests

---

## Test Coverage Summary

| Category | Tests | Files |
|----------|-------|-------|
| Snapshot | 18 | 5 |
| Accessibility | 17 | 1 |
| E2E Workflows | 31 | 3 |
| Bridge Integration | 11 | 1 |
| Error Handling | 13 | 1 |
| Visual Regression | 20+ | 1 |
| **Total** | **110+** | **12** |

---

## Resources

### Documentation
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [React Testing Library](https://testing-library.com/react)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)

### Related Files
- [E2E README](./web/e2e/README.md)
- [CI/CD Workflow](./.github/workflows/ui-tests.yml)
- [Testing Setup](./web/src/tests/setup.ts)

---

## Maintenance

### Updating Dependencies
```bash
# Update testing dependencies
npm update vitest @testing-library/react jest-axe @playwright/test

# Reinstall Playwright browsers
npx playwright install
```

### Adding New Test Types
1. Install required packages
2. Update configuration files
3. Create test template files
4. Add npm scripts to `package.json`
5. Update CI/CD workflow
6. Document in this guide

---

**For questions or issues, please refer to the project's GitHub Issues or contact the development team.**
