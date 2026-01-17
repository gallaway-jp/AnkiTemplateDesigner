# Blocks Container - Debug Guide

## Problem
Blocks are not appearing in the `.blocks-container` in the right sidebar.

---

## Architecture Overview

### Block Registration Flow

```
1. HTML loads (index.html)
   ↓
2. index.html loads <script type="module" src="blocks/index.js">
   ↓
3. blocks/index.js imports all block category modules:
   - layout.js
   - inputs.js
   - buttons.js
   - data.js
   - feedback.js
   - overlays.js
   - animations.js
   - accessibility.js
   ↓
4. blocks/index.js sets window.registerAnkiBlocks function
   ↓
5. designer.js initializes editor
   ↓
6. designer.js calls registerAnkiBlocks(editor)
   ↓
7. registerAnkiBlocks adds all blocks to editor.BlockManager
   ↓
8. Blocks render in .blocks-container (right sidebar)
```

---

## File Locations

| File | Purpose |
|------|---------|
| [web/index.html](web/index.html#L129) | Container div: `<div class="blocks-container"></div>` |
| [web/blocks/index.js](web/blocks/index.js) | Main block registration (defines `window.registerAnkiBlocks`) |
| [web/blocks/layout.js](web/blocks/layout.js) | Layout block categories |
| [web/blocks/inputs.js](web/blocks/inputs.js) | Input/form block categories |
| [web/blocks/buttons.js](web/blocks/buttons.js) | Button block categories |
| [web/blocks/data.js](web/blocks/data.js) | Data display block categories |
| [web/blocks/feedback.js](web/blocks/feedback.js) | Feedback/status block categories |
| [web/blocks/overlays.js](web/blocks/overlays.js) | Overlay/modal block categories |
| [web/blocks/animations.js](web/blocks/animations.js) | Animation block categories |
| [web/blocks/accessibility.js](web/blocks/accessibility.js) | Accessibility block categories |
| [web/designer.js](web/designer.js#L264) | Calls `registerAnkiBlocks(editor)` |
| [web/designer.css](web/designer.css#L243) | Styles for `.blocks-container` |

---

## Debug Steps

### 1. Check Browser Console for Errors

Open DevTools (F12) and check for these messages:

```
✓ Should see: "[Modules] Blocks module loaded"
✓ Should see: "[Designer] Registering blocks..."
✓ Should see: "✓ Anki blocks registered successfully"
✗ Should NOT see: Any red errors
```

### 2. Check if Container is Visible

In browser console, run:
```javascript
// Check if container exists
const container = document.querySelector('.blocks-container');
console.log('Container exists:', !!container);
console.log('Container visible:', container?.style.display !== 'none');
console.log('Container has content:', container?.children.length > 0);
```

### 3. Check if Blocks Were Registered

In browser console, run:
```javascript
// Check if blocks exist
const allBlocks = window.editor?.BlockManager?.getAll();
console.log('Number of blocks:', allBlocks?.length || 0);
console.log('First 5 blocks:', allBlocks?.slice(0, 5).map(b => b.id));
```

### 4. Check Panel Switcher

The blocks are in a tabbed panel. Click the "Blocks" button in the right sidebar to show them.

```html
<!-- This is the button that shows/hides blocks -->
<button id="show-blocks" command="show-blocks">Blocks</button>
```

---

## Common Issues & Solutions

### Issue 1: "registerAnkiBlocks is not defined"

**Symptom:** Console shows warning: "registerAnkiBlocks function not available"

**Cause:** The `blocks/index.js` module failed to load

**Solution:**
1. Check all imported block files exist:
   - [ ] web/blocks/layout.js
   - [ ] web/blocks/inputs.js
   - [ ] web/blocks/buttons.js
   - [ ] web/blocks/data.js
   - [ ] web/blocks/feedback.js
   - [ ] web/blocks/overlays.js
   - [ ] web/blocks/animations.js
   - [ ] web/blocks/accessibility.js

2. Check for syntax errors in any block file:
   ```bash
   # Look for JS errors in console
   # Or validate syntax online
   ```

### Issue 2: Blocks Container is Empty

**Symptom:** Container div exists but has no children

**Cause:** `blockManager.add()` calls failed

**Solution:**
```javascript
// In browser console, check what went wrong:
const bm = window.editor?.BlockManager;
console.log('BlockManager exists:', !!bm);
console.log('BlockManager.add is function:', typeof bm?.add === 'function');

// Try adding a test block
bm?.add('test-block', {
    label: 'Test',
    category: 'Test',
    content: '<div>Test</div>'
});

// Check if it appeared
console.log('Test block added:', bm?.getAll()?.length);
```

### Issue 3: Container is Hidden

**Symptom:** Container exists but `display: none`

**Cause:** Right panel is showing a different tab (Layers, Styles, Traits)

**Solution:**
- Click the "Blocks" button in the panel switcher (top of right sidebar)
- Or in console:
```javascript
document.querySelector('.blocks-container').style.display = '';
```

### Issue 4: Wrong HTML Structure

**Symptom:** Container div is missing entirely

**Cause:** HTML structure changed

**Check:**
```html
<!-- Should have this in web/index.html around line 129 -->
<div class="panel__right">
    <div class="panel__switcher"></div>
    <div class="blocks-container"></div>    <!-- ← Check this exists -->
    <div class="layers-container" style="display: none;"></div>
    <div class="styles-container" style="display: none;"></div>
    <div class="traits-container" style="display: none;"></div>
</div>
```

---

## How Blocks Are Added

### Example: Adding a Simple Block

From `web/blocks/index.js`:

```javascript
blockManager.add('anki-field', {
    label: 'Anki Field',              // Display name
    category: 'Anki Special',         // Category grouping
    content: {
        type: 'text',
        content: '{{Front}}',          // Default content
        attributes: {
            'data-anki-field': 'Front',
            'class': 'anki-field'
        },
        traits: [/* traits config */]
    },
    attributes: {
        class: 'fa fa-bookmark'        // Icon class
    }
});
```

Each block is registered with:
- `id`: Unique identifier
- `label`: Display name
- `category`: Group/category name
- `content`: What gets added to canvas
- `attributes`: Icon and styling

---

## Testing Block Registration

### Manual Test in Console

```javascript
// 1. Check editor is initialized
console.log('Editor ready:', !!window.editor);

// 2. Check BlockManager exists
const bm = window.editor?.BlockManager;
console.log('BlockManager:', !!bm);

// 3. Count existing blocks
console.log('Total blocks:', bm?.getAll()?.length);

// 4. List block categories
const categories = new Set(
    bm?.getAll().map(b => b.category)
);
console.log('Categories:', Array.from(categories));

// 5. List blocks by category
Array.from(categories).forEach(cat => {
    const blocks = bm.getAll().filter(b => b.category === cat);
    console.log(`${cat}: ${blocks.length} blocks`);
});

// 6. Check if specific block exists
const ankiField = bm?.get('anki-field');
console.log('anki-field block:', ankiField?.label || 'NOT FOUND');
```

---

## Expected Block Categories

When fully loaded, you should see these categories:

- **Anki Special**
  - Anki Field
  - Cloze
  - Hint
  - Study Action Bar

- **Layout**
  - Container
  - Row
  - Column
  - etc.

- **Input**
  - Text Input
  - Checkbox
  - Radio
  - etc.

- **Buttons**
  - Default Button
  - Primary Button
  - etc.

- **Data**
  - Table
  - List
  - etc.

- **Feedback**
  - Alert
  - Badge
  - etc.

- **Overlays**
  - Modal
  - Tooltip
  - etc.

- **Animations**
  - Fade In
  - Slide In
  - etc.

- **Accessibility**
  - ARIA Label
  - Skip Link
  - etc.

---

## Next Steps

1. **Open browser DevTools (F12)**
2. **Run the debug checks above**
3. **Share console output** if blocks still don't appear
4. **Check `web/blocks/index.js`** imports - one might be missing

---

## Related Files

- [03b-GRAPEJS-EDITOR.md](docs/plans/03b-GRAPEJS-EDITOR.md) - GrapeJS initialization details
- [web/blocks/](web/blocks/) - Block definitions
- [web/designer.js](web/designer.js) - Block registration call
