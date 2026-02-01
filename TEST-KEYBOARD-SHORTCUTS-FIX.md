# Testing the Keyboard Shortcuts Fix

## Quick Test (5 minutes)

### Step 1: Restart Anki
1. Close Anki completely
2. Restart Anki to load the updated addon

### Step 2: Test Ctrl+Alt+D During Loading
1. Click "Tools" → "Anki Template Designer"
2. You should see "Loading editor..." overlay
3. **IMMEDIATELY press Ctrl+Alt+D** (don't wait for loading to finish)
4. **Expected:** Debug console should toggle open/closed

### Step 3: Check Debug Logs
If debug console opens during loading:
1. Look for these log messages:
   - `[Debug Console] Key combination detected: Ctrl+Alt+d`
   - `[Keyboard Shortcuts] ...` for other shortcuts
   - `[loadTemplates]` messages showing template loading progress

2. Scroll through the debug output to see:
   - How many note types are being fetched
   - How many templates are being processed
   - Whether loading completes or appears stuck

### Step 4: Test Other Shortcuts
While or after loading completes, test other keyboard shortcuts:
- **Ctrl+S** - Save (check for `[Keyboard Shortcuts] Ctrl+S detected`)
- **Ctrl+Z** - Undo (check for `[Keyboard Shortcuts] Ctrl+Z detected`)
- **Ctrl+E** - Export (check for `[Keyboard Shortcuts] Ctrl+E detected`)

## Detailed Testing

### Expected Behavior

#### Loading Phase (First 5-10 seconds)
```
=== Anki Template Designer Starting ===
Version: 1.0.0
Press Ctrl+Alt+D to toggle debug console
Initializing bridge...
✓ Bridge connected
✓ Bridge test passed
✓ Components initialized
✓ Canvas initialized
✓ Properties panel initialized
✓ Toolbar initialized
[loadTemplates] Starting to load all templates...
[loadTemplates] Bridge is available, calling getNoteTypes()...
[loadTemplates] Note types received. Processing X note types...
[loadTemplates] Loading templates for note type X/Y: [CardType]...
```

#### Keyboard Shortcuts Working
```
[Debug Console] Key combination detected: Ctrl+Alt+d
[Debug Console] Toggle debug console
Debug console toggled

[Keyboard Shortcuts] Ctrl+S detected - Save
[Keyboard Shortcuts] Ctrl+Z detected - Undo
[Keyboard Shortcuts] Ctrl+E detected - Export
```

### What If It Doesn't Work?

#### Issue: Debug console doesn't toggle when pressing Ctrl+Alt+D
1. Check the browser console (F12) for JavaScript errors
2. Verify these log messages appear:
   - `✓ Debug console ready`
   - `✓ Keyboard shortcuts initialized (available immediately)`
3. Try alternative: Click the 🐛 Debug button in the toolbar

#### Issue: Debug console opens but no [loadTemplates] logs visible
1. Make sure the debug console is actually showing messages
2. Try pressing Ctrl+S to trigger `[Keyboard Shortcuts]` logs
3. If you see `[Keyboard Shortcuts]` logs but not `[loadTemplates]` logs:
   - The template loading may have completed too quickly
   - Scroll up in debug console to see past messages

#### Issue: Loading never completes
1. Note the templates being loaded in debug output
2. Check if loading completes after 10 seconds
3. The loading overlay should hide automatically after 10 seconds timeout
4. If it doesn't, this indicates the issue

## Reporting Results

Please share:
1. **Did Ctrl+Alt+D work during loading?** (Yes/No)
2. **What logs appeared?** (Copy relevant debug console output)
3. **Did loading eventually complete?** (Yes/No/Stuck after X seconds)
4. **Any error messages?** (Copy exact error text)

## Success Criteria

This fix is successful when:
- ✅ Ctrl+Alt+D works before keyboard shortcuts finish initializing
- ✅ Debug console toggles open/closed immediately
- ✅ [loadTemplates] logs appear in debug console
- ✅ User can see loading progress in real-time
- ✅ User can identify why overlay stays visible

## Technical Notes

### What Changed
1. **Initialization order:** Keyboard shortcuts now initialize BEFORE template loading
2. **Loading overlay:** Added `pointer-events: none` to prevent event interception
3. **Enhanced logging:** Added `[Debug Console]` and `[Keyboard Shortcuts]` prefixes

### Why This Works
- Keyboard shortcuts are event listeners on `document.addEventListener('keydown')`
- They don't require any other systems to be initialized
- Moving them earlier means they're available within milliseconds
- The debug console has its own keyboard listener in `utils.js`

### Backward Compatibility
- All changes are additive (no removal of functionality)
- Initialization sequence doesn't affect final state
- Event handlers work the same regardless of when they're attached
- No changes to feature behavior or user experience (except the fix)

## Files Changed
- `web/js/app.js` - Reordered initialization sequence
- `web/css/designer.css` - Added pointer-events: none
- `web/js/utils.js` - Enhanced logging
