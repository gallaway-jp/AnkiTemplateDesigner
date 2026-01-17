# Block Registration - Complete Architecture

## Where Blocks Come From

### Step 1: Load Block Modules

**File:** [web/index.html](web/index.html#L146)

```html
<!-- Load block module (ES6) -->
<script type="module" src="blocks/index.js"></script>
```

### Step 2: Module Initialization

**File:** [web/blocks/index.js](web/blocks/index.js)

The module uses ES6 imports to load all block category files:

```javascript
import { registerLayoutBlocks } from './layout.js';
import { registerStudyActionBar } from './study-action-bar.js';
import { registerInputBlocks } from './inputs.js';
import { registerButtonBlocks } from './buttons.js';
import { registerDataBlocks } from './data.js';
import { registerFeedbackBlocks } from './feedback.js';
import { registerOverlayBlocks } from './overlays.js';
import { registerAnimationBlocks } from './animations.js';
import { registerAccessibilityBlocks } from './accessibility.js';
```

### Step 3: Export Registration Function

The module exports a function that gets attached to `window`:

```javascript
window.registerAnkiBlocks = function(editor) {
    const blockManager = editor.BlockManager;
    
    // Add individual blocks
    blockManager.add('anki-field', { /* config */ });
    blockManager.add('anki-cloze', { /* config */ });
    // ... more blocks
    
    // Call modular registration functions
    registerStudyActionBar(editor);
    registerLayoutBlocks(editor);
    registerInputBlocks(editor);
    // ... etc
    
    console.log('✓ Anki blocks registered successfully');
};

window.ankiBlocksModuleReady = true;
```

### Step 4: Call Registration from Editor Init

**File:** [web/designer.js](web/designer.js#L264)

When the editor is initialized, `registerAnkiBlocks()` is called:

```javascript
if (typeof registerAnkiBlocks === 'function') {
    console.log('[Designer] Registering blocks...');
    registerAnkiBlocks(editor);
    console.log('[Designer] Blocks registered');
} else {
    console.warn('[Designer] registerAnkiBlocks function not available');
}
```

---

## Block Manager Configuration

### Initial Config

**File:** [web/designer.js](web/designer.js#L170)

After GrapeJS initializes, the BlockManager is configured to append to the DOM:

```javascript
// Configure managers after initialization
editor.LayerManager.getConfig().appendTo = '.layers-container';
editor.BlockManager.getConfig().appendTo = '.blocks-container';
editor.StyleManager.getConfig().appendTo = '.styles-container';
editor.TraitManager.getConfig().appendTo = '.traits-container';
```

This tells GrapeJS to render all registered blocks inside `.blocks-container`.

### HTML Container

**File:** [web/index.html](web/index.html#L129)

```html
<div class="panel__right">
    <div class="panel__switcher"></div>
    <div class="blocks-container"></div>    <!-- ← Blocks render here -->
    <div class="layers-container" style="display: none;"></div>
    <div class="styles-container" style="display: none;"></div>
    <div class="traits-container" style="display: none;"></div>
</div>
```

---

## Complete Block Registration Example

### How a Single Block is Registered

From [web/blocks/index.js](web/blocks/index.js):

```javascript
blockManager.add('anki-field', {
    // Unique ID for the block
    id: 'anki-field',
    
    // Display name in the blocks panel
    label: 'Anki Field',
    
    // Category grouping (creates section headers)
    category: 'Anki Special',
    
    // HTML/content to insert when dragged
    content: {
        type: 'text',
        content: '{{Front}}',
        
        // Attributes on the inserted element
        attributes: {
            'data-anki-field': 'Front',
            'class': 'anki-field'
        },
        
        // Properties panel traits
        traits: [
            {
                type: 'anki-field-select',
                label: 'Field',
                name: 'data-anki-field'
            }
        ]
    },
    
    // Icon in blocks panel
    attributes: {
        class: 'fa fa-bookmark'
    }
});
```

### How Modular Blocks are Registered

**File:** [web/blocks/layout.js](web/blocks/layout.js) (example)

```javascript
export function registerLayoutBlocks(editor) {
    const blockManager = editor.BlockManager;
    
    // Add container block
    blockManager.add('layout-container', {
        label: 'Container',
        category: 'Layout',
        content: {
            type: 'default',
            tagName: 'div',
            components: [
                { type: 'text', content: 'Add content here' }
            ],
            styles: {
                padding: '10px',
                'border-radius': '4px'
            }
        },
        attributes: {
            class: 'fa fa-square'
        }
    });
    
    // Add row block
    blockManager.add('layout-row', {
        label: 'Row',
        category: 'Layout',
        content: {
            type: 'default',
            tagName: 'div',
            styles: {
                display: 'flex',
                gap: '10px'
            },
            components: [
                { tagName: 'div', content: 'Col 1' },
                { tagName: 'div', content: 'Col 2' }
            ]
        },
        attributes: {
            class: 'fa fa-columns'
        }
    });
}
```

---

## Module Dependency Map

```
blocks/index.js (Main)
├── layout.js               → registerLayoutBlocks()
├── study-action-bar.js     → registerStudyActionBar()
├── inputs.js               → registerInputBlocks()
├── buttons.js              → registerButtonBlocks()
├── data.js                 → registerDataBlocks()
├── feedback.js             → registerFeedbackBlocks()
├── overlays.js             → registerOverlayBlocks()
├── animations.js           → registerAnimationBlocks()
└── accessibility.js        → registerAccessibilityBlocks()

    ↓ (All import paths)

blocks/index.js exports window.registerAnkiBlocks

    ↓ (Called by)

designer.js → registerAnkiBlocks(editor)

    ↓ (Which calls)

editor.BlockManager.add() → Blocks appear in UI
```

---

## Troubleshooting: Where Blocks Get Added

### If blocks don't appear, check:

| Location | What to Check |
|----------|--------------|
| [web/index.html](web/index.html) | Does `.blocks-container` div exist? |
| [web/blocks/index.js](web/blocks/index.js) | Does `window.registerAnkiBlocks` exist? |
| [web/blocks/*.js](web/blocks/) | Do all imported block files exist? |
| [web/designer.js](web/designer.js#L264) | Is `registerAnkiBlocks()` being called? |
| Browser DevTools Console | Any JavaScript errors? |

### Test in Browser Console

```javascript
// 1. Check module loaded
console.log('Module ready:', window.ankiBlocksModuleReady);

// 2. Check function exists
console.log('Function exists:', typeof window.registerAnkiBlocks === 'function');

// 3. Check editor exists
console.log('Editor exists:', !!window.editor);

// 4. Check container exists
console.log('Container exists:', !!document.querySelector('.blocks-container'));

// 5. Check blocks were registered
console.log('Total blocks:', window.editor?.BlockManager?.getAll()?.length || 0);

// 6. Check first few blocks
const blocks = window.editor?.BlockManager?.getAll() || [];
console.log('First 5 blocks:', blocks.slice(0, 5).map(b => b.id));
```

---

## Visual Block Appearance

Once registered, each block appears in the right sidebar:

```
╔════════════════════════════╗
║        Blocks Panel        │
╠════════════════════════════╣
║  📑 Anki Special           │  ← Category
║  ┌──────────────────────┐  │
║  │ 📖 Anki Field        │  │  ← Block with icon & label
║  └──────────────────────┘  │
║  ┌──────────────────────┐  │
║  │ 👁 Cloze             │  │
║  └──────────────────────┘  │
║  ┌──────────────────────┐  │
║  │ ❓ Hint              │  │
║  └──────────────────────┘  │
║                            │
║  📐 Layout                 │  ← Category
║  ┌──────────────────────┐  │
║  │ ⊞ Container          │  │
║  └──────────────────────┘  │
║  ┌──────────────────────┐  │
║  │ ⬜ Row               │  │
║  └──────────────────────┘  │
║  ┌──────────────────────┐  │
║  │ ⬜ Column            │  │
║  └──────────────────────┘  │
║                            │
║  ... more categories ...   │
╚════════════════════════════╝
```

---

## Block Lifecycle

1. **Load** - `blocks/index.js` loaded as ES6 module
2. **Import** - All block category modules imported
3. **Export** - `window.registerAnkiBlocks` function created
4. **Initialize** - Designer initializes GrapeJS editor
5. **Register** - `registerAnkiBlocks(editor)` called
6. **Add** - `blockManager.add()` called for each block
7. **Render** - Blocks rendered in `.blocks-container` div
8. **Display** - User sees blocks in right sidebar panel
9. **Drag** - User can drag blocks onto canvas to create components

---

## Files Modified When Adding New Blocks

To add a new block category:

1. **Create new file:** `web/blocks/new-category.js`
   ```javascript
   export function registerNewCategoryBlocks(editor) {
       const blockManager = editor.BlockManager;
       blockManager.add('block-id', { /* config */ });
   }
   ```

2. **Import in:** [web/blocks/index.js](web/blocks/index.js#L5)
   ```javascript
   import { registerNewCategoryBlocks } from './new-category.js';
   ```

3. **Call in function:** [web/blocks/index.js](web/blocks/index.js#L89)
   ```javascript
   registerNewCategoryBlocks(editor);
   ```

That's it! GrapeJS will handle the rest.

---

## Summary

**Blocks are added through this chain:**

```
blocks/index.js
    ↓ (ES6 imports)
layout.js, inputs.js, buttons.js, ...
    ↓ (exports functions)
window.registerAnkiBlocks = function(editor)
    ↓ (called by)
designer.js during editor init
    ↓ (executes)
editor.BlockManager.add() calls
    ↓ (renders to)
<div class="blocks-container"></div>
    ↓ (visible as)
Blocks panel in right sidebar
```

If blocks don't appear, the chain is broken somewhere. Use the debugging guide to find where!
