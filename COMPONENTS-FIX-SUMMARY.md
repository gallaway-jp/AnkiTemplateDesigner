# Components Not Visible - Root Cause & Fix

## Root Cause

The components panel was empty because **blocks/index.js was not being loaded at all**. The module that registers all block components (Layout, Buttons, Inputs, etc.) was defined but never executed in the page lifecycle.

## Fix Applied

### 1. Added blocks/index.js to HTML (CRITICAL)
- **File**: `web/index.html`
- **Change**: Added `<script src="blocks/index.js">` before `designer.js`
- **Reason**: The blocks module must be loaded before designer.js calls the `registerAnkiBlocks()` function

```html
<!-- Block Module - MUST load before designer.js -->
<script src="blocks/index.js" onerror="console.error('[ERROR] Failed to load blocks/index.js')"></script>

<!-- GrapeJS Designer Configuration -->
<script src="designer.js"></script>
```

### 2. Enhanced Block Rendering in blocks/index.js
- **File**: `web/blocks/index.js`  
- **Changes**:
  - Added detailed logging of BlockManager methods and view status
  - Implemented multiple fallback approaches for rendering:
    1. Call `blockManager.render()` if available
    2. Directly append `blockManager.view.$el` to container
    3. Check for alternative `_view` property
  - Added 500ms timeout verification to check if blocks appear in DOM
  - Preserved search container during append operations

### 3. Pre-initialize BlockManager in designer.js
- **File**: `web/designer.js`
- **Changes**:
  - Before registering blocks, ensure BlockManager.view is already appended to `.blocks-container`
  - This prevents timing issues where blocks might not render properly
  - Added logging for BlockManager initialization status

## How It Works Now

1. **Page Load**:
   - `blocks/index.js` loads and defines `window.registerAnkiBlocks` function
   - `designer.js` loads and initializes GrapeJS editor
   - `startEditorInit()` is called

2. **Initialization**:
   - Editor managers are configured (BlockManager set to append to `.blocks-container`)
   - BlockManager view is pre-appended to container if it exists
   - `registerAnkiBlocks(editor)` is called asynchronously

3. **Block Registration**:
   - Dynamic imports of all block modules (layout.js, buttons.js, etc.) complete
   - Anki special blocks are added (anki-field, anki-cloze, anki-hint)
   - Module registration functions execute (registerLayoutBlocks, registerInputBlocks, etc.)
   - `blockManager.render()` is called to populate the view
   - Blocks appear in DOM with class `.gjs-block`

4. **Component Search**:
   - After blocks are registered, ComponentSearchUI is initialized
   - Search container is inserted with blocks visible underneath
   - User can see all blocks and search for specific components

## Testing

To verify the fix works:

1. Open developer console (F12)
2. Look for console logs starting with `[Blocks]`:
   - `[Blocks] Blocks before registration: X`
   - `[Blocks] Blocks after registration: Y (added: Z)`
   - `[Blocks] BlockManager view rendered` (or fallback messages)
   - `[Blocks] Block elements in DOM: N`

3. Expected results:
   - Block count should increase (from 3 Anki special blocks to 40+ total)
   - Block elements should be visible in DOM (N > 0)
   - Blocks should appear in the right-side components panel

## Files Modified

1. `web/index.html` - Added blocks/index.js script tag
2. `web/blocks/index.js` - Enhanced rendering logic with comprehensive debugging
3. `web/designer.js` - Added pre-initialization of BlockManager view

## Fallback Mechanisms

If blocks still don't appear, the code will:

1. Try alternative methods to access BlockManager view
2. Manually append view element if automatic rendering fails
3. Provide detailed error messages in console showing exact failure point
4. Log BlockManager state for debugging

All failures are caught and logged without breaking the application.
