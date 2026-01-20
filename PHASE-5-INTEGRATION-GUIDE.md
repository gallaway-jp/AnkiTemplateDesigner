# Phase 5 Integration Guide - CraftEditor Integration

## 🎯 Overview

This guide covers integrating Phase 5 services into the CraftEditor React component. Phase 5 adds:
- Canvas optimization (virtual scrolling, caching)
- Keyboard navigation (shortcuts, arrow keys)
- Clipboard management (copy/paste/undo/redo)
- Template library (save/load/search)
- Theme system (dark/light modes)
- Anki synchronization (field detection, validation)
- Mobile responsivity (touch gestures, responsive layout)

---

## 📦 Installation

### 1. Ensure Files Exist
All Phase 5 service files should be in `web/src/services/`:
```
web/src/services/
├── canvasOptimization.ts
├── keyboardNavigation.ts
├── clipboardManager.ts
├── templateLibraryManager.ts
├── themeManager.ts
├── ankiSyncService.ts
├── mobileResponsivityService.ts
└── phase5Integration.test.ts
```

### 2. Update Type Definitions
Create `web/src/types/phase5.ts`:
```typescript
export * from '@/services/canvasOptimization';
export * from '@/services/keyboardNavigation';
export * from '@/services/clipboardManager';
export * from '@/services/templateLibraryManager';
export * from '@/services/themeManager';
export * from '@/services/ankiSyncService';
export * from '@/services/mobileResponsivityService';
```

---

## 🔌 Basic Integration

### Step 1: Import Services
```typescript
// CraftEditor.tsx
import { canvasOptimization } from '@/services/canvasOptimization';
import { keyboardNavigation } from '@/services/keyboardNavigation';
import { clipboardManager } from '@/services/clipboardManager';
import { templateLibrary } from '@/services/templateLibraryManager';
import { themeManager } from '@/services/themeManager';
import { ankiSync } from '@/services/ankiSyncService';
import { mobileResponsivity } from '@/services/mobileResponsivityService';
```

### Step 2: Initialize in useEffect
```typescript
useEffect(() => {
  // Initialize all Phase 5 services
  try {
    canvasOptimization.initialize();
    mobileResponsivity.initialize();
    themeManager.initialize();
    
    logger.info('Phase 5 services initialized');
  } catch (error) {
    logger.error('Failed to initialize Phase 5 services', error);
  }

  return () => {
    // Cleanup if needed
  };
}, []);
```

### Step 3: Add Event Listeners
```typescript
// Add to CraftEditor component
const handleKeyDown = (e: KeyboardEvent) => {
  // Let keyboard navigation handle it
  const action = keyboardNavigation.handleKeyDown(e);
  if (action) {
    // Process navigation
    processNavigation(action);
  }
};

const handleTouchEvent = (e: TouchEvent) => {
  const gesture = mobileResponsivity.handleTouchEvent(e);
  if (gesture) {
    processGesture(gesture);
  }
};

useEffect(() => {
  window.addEventListener('keydown', handleKeyDown);
  document.addEventListener('touchstart', (e) => handleTouchEvent(e));
  document.addEventListener('touchmove', (e) => handleTouchEvent(e));
  document.addEventListener('touchend', (e) => handleTouchEvent(e));

  return () => {
    window.removeEventListener('keydown', handleKeyDown);
    document.removeEventListener('touchstart', (e) => handleTouchEvent(e));
    document.removeEventListener('touchmove', (e) => handleTouchEvent(e));
    document.removeEventListener('touchend', (e) => handleTouchEvent(e));
  };
}, []);
```

---

## 🎨 Feature Implementation

### Canvas Optimization

#### Enable Virtual Scrolling
```typescript
const canvasRef = useRef<HTMLCanvasElement>(null);

useEffect(() => {
  const optimizer = canvasOptimization;
  
  // Get performance stats
  const stats = optimizer.getStats();
  console.log(`FPS: ${stats.fps}, Cache hit: ${stats.cacheHitRate}%`);
  
  // Apply optimizations
  if (stats.fps < 50) {
    optimizer.updateBatchSize(32); // Increase batching
  }
}, []);
```

### Keyboard Navigation

#### Implement Navigation
```typescript
const processNavigation = (context: NavigationContext) => {
  const { currentNode, direction } = context;
  
  switch (direction) {
    case 'up':
      selectNode(currentNode.parent);
      break;
    case 'down':
      selectNode(currentNode.nodes[0]);
      break;
    case 'left':
      selectNode(currentNode.previousSibling);
      break;
    case 'right':
      selectNode(currentNode.nextSibling);
      break;
  }
};

// Register custom actions
keyboardNavigation.registerAction('Ctrl+S', () => {
  saveTemplate();
});

keyboardNavigation.registerAction('Ctrl+1', () => {
  themeManager.setThemeMode('light');
});
```

### Clipboard Management

#### Implement Copy/Paste UI
```typescript
const handleCopy = () => {
  if (selectedNodes.length > 0) {
    clipboardManager.copy(selectedNodes);
    showToast('Copied to clipboard');
  }
};

const handlePaste = async () => {
  try {
    const pasted = await clipboardManager.paste();
    if (pasted) {
      insertNodes(pasted);
      showToast('Pasted successfully');
    }
  } catch (error) {
    showError('Paste failed');
  }
};

// Undo/Redo
const handleUndo = () => {
  const previousState = clipboardManager.undo();
  if (previousState) {
    restoreState(previousState);
  }
};
```

### Template Library

#### Save Template Dialog
```typescript
const saveTemplateDialog = async () => {
  const name = await promptUser('Template name:');
  if (!name) return;

  const metadata: TemplateMetadata = {
    id: generateId(),
    name,
    category: selectedCategory,
    tags: selectedTags,
    created: Date.now(),
    modified: Date.now(),
    version: '1.0',
    author: userProfile.name,
    isPublic: false,
    usageCount: 0,
    rating: 0,
  };

  const result = templateLibrary.saveTemplate({
    metadata,
    frontNode,
    backNode,
    styleNode,
  });

  if (result) {
    showToast(`Template "${name}" saved`);
  }
};
```

#### Load Template
```typescript
const loadTemplate = async (templateId: string) => {
  const template = templateLibrary.getTemplate(templateId);
  if (template) {
    setFrontNode(template.frontNode);
    setBackNode(template.backNode);
    showToast(`Loaded "${template.metadata.name}"`);
  }
};

// Search templates
const handleSearch = (query: string) => {
  const results = templateLibrary.searchTemplates({
    query,
    category: selectedCategory,
    tags: selectedTags,
    limit: 10,
  });
  
  setSearchResults(results);
};
```

### Theme System

#### Theme Selector UI
```typescript
const handleThemeChange = (themeName: string) => {
  themeManager.setTheme(themeName);
  showToast(`Theme changed to ${themeName}`);
};

const handleThemeModeChange = (mode: 'light' | 'dark' | 'auto') => {
  themeManager.setThemeMode(mode);
};

// Custom color picker
const handleColorUpdate = (colorName: string, value: string) => {
  const palette = themeManager.getColorPalette();
  palette[colorName as keyof typeof palette] = value;
  themeManager.updateColorPalette(palette);
};

// Apply theme changes
useEffect(() => {
  themeManager.applyTheme();
}, [themeConfig]);
```

### Anki Synchronization

#### Validate Before Sync
```typescript
const validateForAnki = async () => {
  const html = generateTemplateHTML(frontNode, backNode);
  
  const fields = ankiSync.analyzeTemplate(html);
  const validation = ankiSync.validateAgainstNoteType(html, ankiNoteType);
  
  if (validation.some(r => !r.valid)) {
    // Show errors to user
    validation
      .filter(r => !r.valid)
      .forEach(r => {
        showError(`${r.field}: ${r.errors.join(', ')}`);
        r.suggestions.forEach(s => showInfo(`Suggestion: ${s}`));
      });
    return false;
  }
  
  return true;
};

// Sync to Anki
const syncToAnki = async () => {
  if (!await validateForAnki()) return;
  
  const result = await ankiSync.syncToAnki(
    ankiNoteTypeId,
    frontNode,
    backNode,
    cssStyles
  );
  
  if (result.success) {
    showSuccess('Synced to Anki');
  } else {
    showError(`Sync failed: ${result.message}`);
    result.warnings.forEach(w => showWarning(w));
  }
};
```

### Mobile Responsivity

#### Handle Gestures
```typescript
const processGesture = (gesture: GestureEvent) => {
  const { type, details, direction } = gesture;
  
  switch (type) {
    case 'tap':
      selectNodeAtPosition(details.centerX, details.centerY);
      break;
      
    case 'double-tap':
      zoomToFit();
      break;
      
    case 'long-press':
      openContextMenu(details.centerX, details.centerY);
      break;
      
    case 'pinch':
      zoomCanvas(details.scale);
      break;
      
    case 'swipe':
      navigateDirection(direction!);
      break;
      
    case 'pan':
      panCanvas(details.velocity.x, details.velocity.y);
      break;
  }
};
```

#### Responsive Layout
```typescript
const viewportInfo = mobileResponsivity.getViewportInfo();
const uiState = mobileResponsivity.getUIState();

// Adjust layout based on device
const layoutStyles = {
  container: {
    flexDirection: viewportInfo?.isMobile ? 'column' : 'row',
  },
  toolbar: {
    position: uiState.toolbarPosition === 'bottom' ? 'fixed' : 'relative',
    bottom: uiState.toolbarPosition === 'bottom' ? 0 : 'auto',
  },
  propertyPanel: {
    display: uiState.showPropertyPanel ? 'block' : 'none',
    width: viewportInfo?.isMobile ? '100%' : '300px',
  },
};
```

---

## 🏗️ Zustand Store Integration

### Create Store Slice
```typescript
// store/canvasStore.ts
import { create } from 'zustand';
import { 
  CanvasOptimizationService,
  KeyboardNavigationManager,
  ClipboardManagerWithHistory,
  TemplateLibraryManager,
  ThemeManager,
  AnkiSyncService,
  MobileResponsivityService,
} from '@/types/phase5';

interface CanvasState {
  // Services
  optimization: CanvasOptimizationService;
  keyboard: KeyboardNavigationManager;
  clipboard: ClipboardManagerWithHistory;
  templates: TemplateLibraryManager;
  theme: ThemeManager;
  ankiSync: AnkiSyncService;
  mobile: MobileResponsivityService;

  // State
  selectedTemplate: string | null;
  currentTheme: string;
  canvasStats: any;
  
  // Actions
  setSelectedTemplate: (id: string) => void;
  setCurrentTheme: (name: string) => void;
  updateCanvasStats: () => void;
}

export const useCanvasStore = create<CanvasState>((set) => ({
  optimization: canvasOptimization,
  keyboard: keyboardNavigation,
  clipboard: clipboardManager,
  templates: templateLibrary,
  theme: themeManager,
  ankiSync: ankiSync,
  mobile: mobileResponsivity,

  selectedTemplate: null,
  currentTheme: 'default-light',
  canvasStats: {},

  setSelectedTemplate: (id: string) =>
    set({ selectedTemplate: id }),

  setCurrentTheme: (name: string) => {
    themeManager.setTheme(name);
    set({ currentTheme: name });
  },

  updateCanvasStats: () =>
    set({ canvasStats: canvasOptimization.getStats() }),
}));
```

### Use in Components
```typescript
const { templates, theme, mobile } = useCanvasStore();

const templates = useMemo(() => 
  templates.searchTemplates({ query, limit: 10 }),
  [query]
);
```

---

## 🧪 Testing

### Test Template Save/Load
```typescript
describe('Template Library Integration', () => {
  it('should save and load template', () => {
    const template = {
      metadata: { name: 'Test' },
      frontNode: mockNode,
      backNode: mockNode,
    };
    
    templateLibrary.saveTemplate(template);
    const loaded = templateLibrary.getTemplate(template.metadata.id);
    
    expect(loaded).toEqual(template);
  });
});
```

### Test Keyboard Navigation
```typescript
describe('Keyboard Navigation', () => {
  it('should navigate on arrow keys', () => {
    const event = new KeyboardEvent('keydown', { key: 'ArrowUp' });
    const result = keyboardNavigation.handleKeyDown(event);
    
    expect(result?.direction).toBe('up');
  });
});
```

### Test Mobile Gestures
```typescript
describe('Mobile Gestures', () => {
  it('should recognize pinch zoom', () => {
    const event = new TouchEvent('touchmove', {
      touches: [touch1, touch2],
    });
    
    const gesture = mobileResponsivity.handleTouchEvent(event);
    expect(gesture?.type).toBe('pinch');
  });
});
```

---

## 🔍 Debugging

### Enable Debug Logging
```typescript
import { logger } from '@/utils/logger';

// Set log level
logger.setLevel('debug');

// All Phase 5 services will log detailed info
// [CanvasOptimization] Virtual scroll update: 100 items
// [KeyboardNavigation] Action executed: navigateUp
// [MobileResponsive] Gesture: pinch (scale: 1.2)
```

### Monitor Performance
```typescript
setInterval(() => {
  const stats = canvasOptimization.getStats();
  
  console.group('Canvas Performance');
  console.log(`FPS: ${stats.fps}`);
  console.log(`Render time: ${stats.averageRenderTime.toFixed(2)}ms`);
  console.log(`Cache hit: ${stats.cacheHitRate.toFixed(1)}%`);
  console.log(`Active nodes: ${stats.activeNodeCount}`);
  console.groupEnd();
}, 5000);
```

### Check Mobile State
```typescript
const viewport = mobileResponsivity.getViewportInfo();
const uiState = mobileResponsivity.getUIState();

console.log('Viewport:', viewport?.mode);
console.log('UI State:', uiState);
console.log('Gestures:', mobileResponsivity.getGestureHistory());
```

---

## ✅ Integration Checklist

- [ ] All Phase 5 service files present in `web/src/services/`
- [ ] Type definitions exported from services
- [ ] Services imported in CraftEditor.tsx
- [ ] Services initialized in useEffect
- [ ] Event listeners attached (keyboard, touch)
- [ ] Theme manager applied on mount
- [ ] Mobile responsivity initialized
- [ ] Zustand store slice created
- [ ] Template library UI components added
- [ ] Keyboard shortcuts configured
- [ ] Touch gesture handlers implemented
- [ ] Anki sync validation integrated
- [ ] Performance monitoring active
- [ ] Error handling in place
- [ ] Tests passing
- [ ] Documentation updated
- [ ] User-facing features tested on mobile
- [ ] Accessibility verified (WCAG)

---

## 🚀 Deployment

### Production Build
```bash
# Build all services
npm run build

# Verify no errors
npm run lint

# Run tests
npm test

# Check bundle size
npm run analyze
```

### Rollout Steps
1. Deploy to staging environment
2. Test all features on multiple devices
3. Load testing with 1000+ templates
4. Mobile testing on real devices
5. Accessibility audit
6. Performance profiling
7. Deploy to production
8. Monitor error rates

---

## 📞 Support

### Common Issues

**Problem**: Services not initialized
- **Solution**: Ensure services are initialized in useEffect with proper error handling

**Problem**: Theme not applying
- **Solution**: Call `themeManager.applyTheme()` after initialization

**Problem**: Mobile layout broken
- **Solution**: Check viewport info with `mobileResponsivity.getViewportInfo()`

**Problem**: Keyboard shortcuts not working
- **Solution**: Verify event listener is attached and not prevented

**Problem**: Templates not saving
- **Solution**: Check localStorage quota and verify metadata is complete

---

## 📚 Additional Resources

- Phase 5 Completion Summary: `PHASE-5-COMPLETION-SUMMARY.md`
- Quick Reference: `PHASE-5-QUICK-REFERENCE.md`
- Type Definitions: `web/src/services/*.ts`
- Tests: `phase5Integration.test.ts`

---

**Status**: Integration guide complete
**Last Updated**: 2024
**Phase**: 5 Integration
