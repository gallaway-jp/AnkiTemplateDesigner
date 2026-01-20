# Quick Start Guide - React + Craft.js Migration

**Time to get running**: 5 minutes

---

## Prerequisites

- Node.js 18+ installed
- npm or pnpm package manager
- (Optional) Anki 2.1.45+ for testing with real Python bridge

## Installation

```bash
# Navigate to web folder
cd web

# Install dependencies
npm install

# This downloads ~600 MB (React, Craft.js, etc.)
# Takes 2-3 minutes on decent internet
```

## Development

```bash
# Start development server
npm run dev

# Output:
#   VITE v5.0.0  ready in 123 ms
#   ➜  Local:   http://localhost:5173/

# Open http://localhost:5173 in browser
```

Press `q` to stop the server.

## Testing

```bash
# Run all tests
npm test

# Watch mode (reruns on file changes)
npm test -- --watch

# Interactive UI
npm run test:ui

# Coverage report
npm run test:coverage
```

## Type Checking

```bash
# Check for type errors
npm run type-check

# Should complete with "No errors found"
```

## Building

```bash
# Production build
npm run build

# Output goes to dist/ folder
# Generated files are optimized and minified
```

## Project Structure

```
src/
├── stores/        # State management (Zustand)
├── components/    # React components
├── services/      # Business logic & bridges
├── types/         # TypeScript definitions
├── utils/         # Helper functions
├── styles/        # CSS files
└── tests/         # Unit tests
```

## Key Files to Explore

1. **Start here**:
   - `src/App.tsx` - Root component
   - `src/stores/editorStore.ts` - Template state management

2. **Bridge integration**:
   - `src/services/pythonBridge.ts` - Python communication
   - `src/tests/mocks/mockBridge.ts` - Mock for testing

3. **Types**:
   - `src/types/editor.ts` - Editor domain types
   - `src/types/api.ts` - Bridge message types

4. **Tests**:
   - `src/stores/editorStore.test.ts` - Example test suite

## Common Commands

```bash
# Development
npm run dev              # Start dev server with HMR

# Testing
npm test                 # Run all tests
npm run test:ui        # Interactive test UI
npm run test:coverage  # Coverage report

# Type checking
npm run type-check     # Find type errors
npm run lint           # Lint code

# Building
npm run build          # Production build
npm run preview        # Preview production build

# Utility
npm run type-check     # TypeScript check
```

## Understanding the Architecture

### State Management (Zustand)

Three independent stores:

```typescript
import { useEditorStore, useAnkiStore, useUiStore } from '@stores';

// In a component:
const { currentTemplate } = useEditorStore();
const { fields } = useAnkiStore();
const { theme } = useUiStore();
```

### Python Bridge

```typescript
import { bridge } from '@services';

// Save template
const result = await bridge.saveTemplate(template);

// Listen for updates
bridge.onFieldsUpdated((fields) => {
  console.log('Fields updated:', fields);
});
```

### Type Safety

```typescript
import { Template, BridgeRequest, AnkiField } from '@types';

// Fully typed throughout
const template: Template = {
  id: '123',
  name: 'My Template',
  html: '<div>HTML</div>',
  css: 'body { color: black; }',
};
```

## Debugging

### Browser Console
- All logs prefixed with module name: `[Bridge]`, `[Editor]`, etc.
- Use logger for structured logging:
  ```typescript
  import { createLogger } from '@utils';
  const logger = createLogger('MyModule');
  logger.info('Message', { data: 'here' });
  ```

### VS Code
- TypeScript hints built-in
- ESLint integration
- Vitest inline test results

### Mock Bridge
When running outside Anki, mock bridge auto-activates:
- Simulates all API methods
- Provides realistic data
- No Python needed for development

## Common Tasks

### Add a new store
1. Create file in `src/stores/myStore.ts`
2. Export from `src/stores/index.ts`
3. Import in components: `import { useMyStore } from '@stores'`

### Add a new component
1. Create file in `src/components/MyComponent.tsx`
2. Use hooks for state management
3. Add types to `src/types/` if needed

### Add a new utility function
1. Create in `src/utils/myUtils.ts`
2. Export from `src/utils/index.ts`
3. Import in files: `import { myFunction } from '@utils'`

### Call Python from JavaScript
```typescript
import { bridge } from '@services';

try {
  const result = await bridge.saveTemplate(template);
  console.log('Saved:', result);
} catch (error) {
  console.error('Save failed:', error);
}
```

### Write a test
1. Create `src/components/MyComponent.test.tsx`
2. Use Vitest syntax:
   ```typescript
   import { describe, it, expect } from 'vitest';
   
   describe('MyComponent', () => {
     it('should work', () => {
       expect(true).toBe(true);
     });
   });
   ```
3. Run: `npm test`

## Performance Tips

- Use React.memo for expensive components
- Lazy load with React.lazy()
- Zustand selectors are memoized
- Avoid console.log in production (use logger)

## Troubleshooting

**Q: `npm install` fails**
A: Try clearing cache: `npm cache clean --force && npm install`

**Q: TypeScript errors in editor**
A: Run `npm run type-check` and fix reported errors

**Q: Tests failing**
A: Run `npm test -- --reporter=verbose` for details

**Q: Bridge not connecting**
A: Check browser console. Mock bridge should activate if QWebChannel unavailable

**Q: Hot reload not working**
A: Restart dev server: `npm run dev`

## Next Phase (Phase 2)

The foundation is ready. Phase 2 focuses on:
- Craft.js canvas integration
- Block definitions as React components
- Draggable UI panels
- Property editing

Start with `src/components/Editor.tsx` - replace the placeholder with Craft.js Canvas component.

---

## Resources

- **TypeScript**: https://www.typescriptlang.org/
- **React**: https://react.dev/
- **Zustand**: https://github.com/pmndrs/zustand
- **Vite**: https://vitejs.dev/
- **Vitest**: https://vitest.dev/
- **Craft.js**: https://craft.js.org/

## Getting Help

1. Check console for error messages
2. Review test files for usage examples
3. Look at type definitions for expected shapes
4. Check browser DevTools for React/state issues

---

**Happy coding!** 🚀

If something isn't working, the error message usually points to the solution. Read it carefully!
