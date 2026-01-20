# React + Craft.js + Vite Migration Plan

**Status**: Planning Phase  
**Start Date**: January 20, 2026  
**Target Completion**: Phase-based rollout

---

## Executive Summary

This document outlines a comprehensive migration from:
- **GrapeJS** → **Craft.js** (better maintainability, component-based)
- **Vanilla JS** → **React** (component framework)
- **Raw imports** → **Vite** (modern bundler)
- **Plain JS** → **TypeScript** (type safety)
- **Manual testing** → **Vitest** (automated testing)

### Why This Matters

Current pain points:
- 25+ loose `.js` files with unclear dependencies
- Global state scattered across multiple files
- Difficult for AI agents to generate correct code
- No automated testing
- Brittle Python ↔ JS bridge
- GrapeJS is poorly maintained

Expected improvements:
- Cleaner, type-safe codebase
- Component-based architecture (easier to maintain)
- Proper state management with Zustand
- TypeScript prevents whole categories of bugs
- Vite provides fast HMR and proper module resolution
- Vitest enables AI-assisted test generation
- React ecosystem provides better tooling

---

## Architecture Overview

### Current Architecture (GrapeJS-based)
```
web/
  ├── index.html          # Single HTML file
  ├── designer.js         # 2400+ lines of GrapeJS init
  ├── bridge.js           # Python ↔ JS communication
  ├── designer.css        # 1000+ lines of styles
  ├── blocks/*.js         # 10 block definition files
  ├── traits/*.js         # Custom trait definitions
  ├── plugins/*.js        # Custom plugins
  └── 25+ UI files        # analytics, backup, history, etc.

Python (gui/):
  ├── designer_dialog.py  # PyQt6 webview host
  └── webview_bridge.py   # QWebChannel bridge
```

### Target Architecture (React + Craft.js)
```
web/src/
  ├── main.tsx              # Entry point
  ├── App.tsx               # Root component
  ├── index.html            # Minimal HTML template
  │
  ├── components/
  │   ├── Editor.tsx        # Main editor (Craft.js canvas)
  │   ├── Toolbar.tsx       # Top toolbar
  │   ├── Panels/
  │   │   ├── BlocksPanel.tsx       # Draggable blocks list
  │   │   ├── PropertiesPanel.tsx   # Component properties
  │   │   ├── LayersPanel.tsx       # DOM tree view
  │   │   └── HistoryPanel.tsx      # Undo/redo timeline
  │   ├── Blocks/
  │   │   ├── LayoutBlocks.tsx      # Container, Row, Column
  │   │   ├── InputBlocks.tsx       # Field, Input, Textarea
  │   │   ├── ButtonBlocks.tsx      # Button, Link
  │   │   ├── AnkiBlocks.tsx        # AnkiField, AnkiCloze, AnkiHint
  │   │   └── index.ts              # Block registry
  │   └── Preview.tsx       # Device preview panes
  │
  ├── stores/
  │   ├── editorStore.ts    # Template, selection, history
  │   ├── ankiStore.ts      # Fields, behaviors, config
  │   ├── uiStore.ts        # Panel visibility, theme
  │   └── index.ts          # Store exports
  │
  ├── services/
  │   ├── pythonBridge.ts   # Type-safe Python API
  │   ├── craftjsAdapter.ts # Craft.js integration helpers
  │   ├── templateParser.ts # HTML ↔ Craft.js conversion
  │   └── index.ts          # Service exports
  │
  ├── types/
  │   ├── index.ts          # All TypeScript interfaces
  │   ├── api.ts            # Python bridge message types
  │   ├── editor.ts         # Editor domain types
  │   └── anki.ts           # Anki-specific types
  │
  ├── styles/
  │   ├── globals.css       # Global styles
  │   ├── theme.css         # Dark theme variables
  │   └── components.module.css
  │
  ├── utils/
  │   ├── logger.ts         # Structured logging
  │   ├── formatting.ts     # Text/HTML utilities
  │   └── validators.ts     # Data validation
  │
  └── tests/
      ├── setup.ts          # Vitest configuration
      ├── mocks/            # Mock bridge, Craft.js, etc.
      ├── stores.test.ts    # Store tests
      ├── components.test.tsx # Component tests
      └── integration.test.ts # E2E flow tests

vite.config.ts             # Vite configuration
tsconfig.json              # TypeScript config
package.json               # Dependencies (React, Craft.js, etc.)
```

Python code stays mostly the same:
```
gui/
  ├── designer_dialog.py    # Still hosts the webview (minimal changes)
  └── webview_bridge.py     # Still provides QWebChannel (interface may change)
```

---

## Key Concepts

### 1. Craft.js Fundamentals

**Craft.js** is a React-based page builder framework:

```typescript
import { Canvas, useNode } from '@craftjs/core';

// Define a component that can be edited
const TextComponent = ({ text, color }) => {
  const { connectors: { connect, drag } } = useNode();
  
  return (
    <div ref={node => connect(drag(node))}>
      <p style={{ color }}>{text}</p>
    </div>
  );
};

// Register craft properties
TextComponent.craft = {
  props: {
    text: 'Enter text',
    color: '#000000'
  },
  rules: {
    canDrag: () => true
  },
  related: {
    settings: TextSettings
  }
};

// Use in canvas
<Canvas>
  <TextComponent text="Hello" color="blue" />
</Canvas>
```

**Key Craft.js Concepts:**
- `Canvas`: Editable container for components
- `useNode()`: Hook to access current node and connectors
- Drag/drop: Built-in via `connectors.drag()`
- Serialization: `useHistory()` for undo/redo
- Settings panel: Custom React components
- Resolvers: Component lookup system

**Mapping GrapeJS → Craft.js:**

| GrapeJS | Craft.js |
|---------|----------|
| `editor.getComponents()` | `useSelected()`, `useTree()` |
| `editor.getSelected()` | `useNode()` |
| `editor.select()` | `node.actions.setProp()` |
| Block registration | Component.craft definition |
| Traits (properties) | Settings components |
| Panel rendering | React components in sidebar |
| Undo/redo | `useHistory()` |
| Project data | `useHistory().query()` |
| Serialization | JSON-friendly by default |

### 2. State Management (Zustand)

**Zustand** is a lightweight state management library:

```typescript
import { create } from 'zustand';

interface EditorState {
  // State
  template: string;
  selectedComponentId: string | null;
  isDirty: boolean;
  
  // Actions
  setTemplate: (html: string) => void;
  selectComponent: (id: string) => void;
  markDirty: () => void;
  markSaved: () => void;
}

export const useEditorStore = create<EditorState>((set) => ({
  template: '',
  selectedComponentId: null,
  isDirty: false,
  
  setTemplate: (html) => set({ template: html }),
  selectComponent: (id) => set({ selectedComponentId: id }),
  markDirty: () => set({ isDirty: true }),
  markSaved: () => set({ isDirty: false }),
}));

// In component:
const { template, selectComponent } = useEditorStore();
```

**Store Structure:**

1. **editorStore.ts** - Template data & selection
   - `template: GrapeJSData` (Craft.js JSON)
   - `selectedComponentId: string | null`
   - `isDirty: boolean`
   - `history: TemplateSnapshot[]`

2. **ankiStore.ts** - Anki-specific state
   - `fields: AnkiField[]`
   - `behaviors: AnkiBehavior[]`
   - `notetype: string`

3. **uiStore.ts** - UI state
   - `activePanels: { blocks: boolean; properties: boolean; ... }`
   - `theme: 'light' | 'dark'`
   - `sidebarWidth: number`

### 3. Python ↔ JavaScript Bridge (Improved)

**Current bridge:**
```javascript
// bridge.js - global window functions
window.bridge.saveProject(jsonString);
window.notifySaveSuccess(name);
```

**New bridge (Type-safe):**
```typescript
// services/pythonBridge.ts
export class PythonBridge {
  // Request/response with correlation IDs
  async saveTemplate(data: TemplateData): Promise<SaveResult> {
    const requestId = this.generateId();
    const promise = this.waitForResponse(requestId);
    
    this.send({
      method: 'saveTemplate',
      requestId,
      params: { data }
    });
    
    return promise;
  }
  
  // Listen for updates from Python
  onFieldsUpdated(callback: (fields: AnkiField[]) => void) {
    this.listeners.set('fieldsUpdated', callback);
  }
}
```

**Python side (minimal changes):**
```python
# gui/webview_bridge.py - still use QWebChannel
class WebViewBridge(QObject):
    # Same as before, but JS interface is cleaner
    
    @pyqtSlot(str)
    def saveProject(self, json_str: str):
        # Same implementation
        pass
```

**Bridge Message Format:**
```typescript
interface BridgeMessage {
  method: string;           // 'saveTemplate', 'loadTemplate', etc.
  requestId?: string;       // For request/response correlation
  params?: any;             // Method parameters
  result?: any;             // Response data
  error?: string;           // Error message
}
```

### 4. Testing Strategy with Vitest

**Vitest** replaces Jest for testing:

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
  }
});

// src/tests/stores.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { useEditorStore } from '../stores/editorStore';

describe('EditorStore', () => {
  beforeEach(() => {
    useEditorStore.setState({
      template: '',
      isDirty: false
    });
  });
  
  it('should mark template as dirty when modified', () => {
    const { markDirty, isDirty } = useEditorStore.getState();
    
    markDirty();
    
    expect(useEditorStore.getState().isDirty).toBe(true);
  });
});
```

---

## Phase-Based Implementation

### Phase 1: Foundation (Week 1)
- [x] Plan architecture (this document)
- [ ] Set up Vite project
- [ ] Create TypeScript type definitions
- [ ] Set up Zustand stores
- [ ] Refactor Python bridge API

### Phase 2: Core Editor (Week 2)
- [ ] Implement Editor component with Craft.js
- [ ] Port block definitions
- [ ] Implement panel components
- [ ] Connect stores to components

### Phase 3: UI & Polish (Week 3)
- [ ] Port styles
- [ ] Implement search/filter
- [ ] Add device previews
- [ ] Theme support

### Phase 4: Testing & Quality (Week 4)
- [ ] Set up Vitest infrastructure
- [ ] Write unit tests (80%+ coverage)
- [ ] Write integration tests
- [ ] Performance optimization

### Phase 5: Python Integration & Launch (Week 5)
- [ ] Verify bridge communication
- [ ] Anki integration testing
- [ ] Bug fixes & refinements
- [ ] Documentation

---

## File Mapping: GrapeJS → React/Craft.js

| Old File | New Location | Purpose |
|----------|--------------|---------|
| `designer.js` | `src/components/Editor.tsx` | Main editor initialization |
| `blocks/index.js` | `src/components/Blocks/index.ts` | Block registry |
| `blocks/layout.js` | `src/components/Blocks/LayoutBlocks.tsx` | Layout components |
| `blocks/inputs.js` | `src/components/Blocks/InputBlocks.tsx` | Input components |
| `traits/index.js` | Settings in component.craft | Property panels |
| `bridge.js` | `src/services/pythonBridge.ts` | Type-safe bridge |
| `designer.css` | `src/styles/globals.css` | Global styles |
| `designer.css` | `src/components/*.module.css` | Component styles |
| All UI files | Various components | Break into smaller pieces |

---

## Dependencies

### New npm packages:
```json
{
  "dependencies": {
    "@craftjs/core": "^0.3.0",
    "@craftjs/utils": "^0.3.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.0",
    "typescript": "^5.3.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0"
  }
}
```

### Python changes:
- No major changes to `designer_dialog.py`
- `webview_bridge.py` API stays mostly the same
- Update docstrings to reference new JS API

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Large breaking change | Phased rollout, keep old system running in parallel initially |
| Bridge compatibility | Create compatibility layer that maps old → new messages |
| Performance regression | Benchmark with Craft.js from day 1 |
| Missing features | Map all GrapeJS features before starting |
| Craft.js learning curve | Keep documentation and examples readily available |

---

## Success Criteria

- ✅ All current features working in React + Craft.js
- ✅ TypeScript with <5 type errors across codebase
- ✅ 80%+ test coverage
- ✅ Vite build completes in <5 seconds
- ✅ Python ↔ JS bridge works for save/load/preview
- ✅ No performance regression vs current system
- ✅ Code cleaner and easier for AI agents to maintain

---

## Next Steps

1. **Immediate**: Review and approve this plan
2. **Start Phase 1**: Set up Vite project structure
3. **Collaborate**: Get feedback on design choices
4. **Iterate**: Build incrementally with checkpoints

---

**Document Version**: 1.0  
**Last Updated**: January 20, 2026  
**Prepared By**: GitHub Copilot (Claude Haiku 4.5)
