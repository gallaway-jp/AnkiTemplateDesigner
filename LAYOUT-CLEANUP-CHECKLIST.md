# Layout.js Cleanup Checklist

**Purpose:** Document required changes to clean up unsuitable blocks and add missing ones  
**File:** `web/blocks/layout.js`  
**Date:** February 1, 2026

---

## BLOCKS TO REMOVE (9 total)

These blocks are not compatible with Anki's rendering model or flashcard paradigm:

### 1. ❌ `modal-container` (Lines ~120-140)
**Reason:** Modals don't work in Anki cards (no DOM overlay capability)
**Action:** Remove entire `bm.add('modal-container', ...)` block
```javascript
// REMOVE THIS SECTION:
// Modal Container
bm.add('modal-container', {
    label: 'Modal Container',
    category,
    content: {
        tagName: 'div',
        classes: ['atd-modal-container'],
        style: {
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            ...
        },
        ...
    }
});
```

### 2. ❌ `drawer` (Lines ~141-160)
**Reason:** Sidebar navigation irrelevant for flashcards
**Action:** Remove entire `bm.add('drawer', ...)` block

### 3. ❌ `split-view` (Lines ~161-190)
**Reason:** Too complex, use grid layouts instead
**Action:** Remove entire `bm.add('split-view', ...)` block

### 4. ❌ `accordion` (Lines ~191-220)
**Reason:** JavaScript-dependent interactive behavior won't work in Anki
**Action:** Remove entire `bm.add('accordion', ...)` block

### 5. ❌ `tab-container` (Lines ~221-250)
**Reason:** Requires JavaScript event handling (won't work in Anki)
**Action:** Remove entire `bm.add('tab-container', ...)` block

### 6. ❌ `tabs-nav` (Lines ~376-395)
**Reason:** Requires JavaScript event handling
**Action:** Remove entire `bm.add('tabs-nav', ...)` block

### 7. ❌ `stepper` (Lines ~397-420)
**Reason:** Multi-step workflow UI irrelevant for flashcard templates
**Action:** Remove entire `bm.add('stepper', ...)` block

### 8. ❌ `masonry` (Lines ~311-330)
**Reason:** CSS columns too complex for flashcard layouts
**Action:** Remove entire `bm.add('masonry', ...)` block

### 9. ❌ `frame` (Lines ~13-31)
**Reason:** Device mockup (iPhone frame) confuses template editing purpose
**Action:** Remove entire `bm.add('frame', ...)` block

---

## BLOCKS TO KEEP (16 total)

These blocks are essential for Anki template editing:

### Containers (6)
- ✅ `section` - Semantic section grouping
- ✅ `panel` - Bordered content container
- ✅ `card` - Card-style layout
- ✅ `surface` - Background container
- ✅ `padding-wrapper` - Padding control
- ✅ `margin-wrapper` - Margin control

### Grid Layouts (3)
- ✅ `grid` - 3-column grid
- ✅ `row-2-col` - 2-column layout
- ✅ `row-3-col` - 3-column layout

### Flexbox (3)
- ✅ `h-stack` - Horizontal stack
- ✅ `v-stack` - Vertical stack
- ✅ `flow-layout` - Flex wrap layout

### Alignment (1)
- ✅ `center` - Center content

### Spacing (2)
- ✅ `spacer` - Vertical spacing
- ✅ `divider` - Horizontal separator

### Navigation (1)
- ✅ `anchor-link` - Internal link jumps

---

## BLOCKS TO ADD (2 total)

### 1. ✅ `container` - ADD AFTER `surface` block

**Purpose:** Generic centered max-width container  
**Location:** After the `surface` block (around line 115)

```javascript
// Container
bm.add('container', {
    label: 'Container',
    category,
    content: {
        tagName: 'div',
        classes: ['atd-container'],
        style: {
            'max-width': '800px',
            margin: '0 auto',
            padding: '16px'
        },
        components: []
    }
});
```

**Why:** Commonly needed for centered, width-constrained content

---

## REGISTER ANKI BLOCKS

### 2. ✅ Import and register anki-blocks.js

**Location:** At the end of the `registerLayoutBlocks` function export, before the closing brace

```javascript
// At the very end of layout.js, add this import at the top:
import { registerAnkiBlocks } from './anki-blocks.js';

// Then in the main initialization section (where registerLayoutBlocks is called):
// Add this line after registerLayoutBlocks(editor):
registerAnkiBlocks(editor);
```

---

## SUMMARY OF CHANGES

| Action | Count | Blocks |
|--------|-------|--------|
| **Remove** | 9 | modal, drawer, split-view, accordion, tab-container, tabs-nav, stepper, masonry, frame |
| **Keep** | 16 | section, panel, card, surface, padding-wrapper, margin-wrapper, grid, row-2-col, row-3-col, h-stack, v-stack, flow-layout, center, spacer, divider, anchor-link |
| **Add** | 1 | container |
| **Register** | 1 | anki-blocks (import + call) |
| **Total After** | 23 | 17 layout blocks + 6 anki blocks |

---

## VERIFICATION STEPS

After making changes:

```javascript
// In browser console, verify block count:
editor.Blocks.getAll().length  // Should show ~23 blocks total

// Check categories:
editor.Blocks.getAll()
  .map(b => b.get('category'))
  .filter((v, i, a) => a.indexOf(v) === i)
  // Should show: Layout & Structure, Anki Fields, etc.

// Verify specific blocks exist:
editor.Blocks.get('container')     // Should NOT be undefined
editor.Blocks.get('anki-field')    // Should NOT be undefined
editor.Blocks.get('modal-container')  // Should be undefined (removed)
```

---

## NOTES

1. **Line numbers are approximate** - Check actual content to find exact locations
2. **Order matters** - Anki blocks should register AFTER layout blocks
3. **Test in Anki** - After cleanup, open Template Designer and verify blocks appear correctly
4. **Browser console** - Check DevTools console for any registration errors

---

**Status:** Ready for implementation  
**Risk Level:** Low (removing unused blocks, adding simple ones)  
**Testing:** Manual UI testing after implementation
