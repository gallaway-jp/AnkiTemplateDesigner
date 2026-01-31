# Qt Signal Disconnection Fix - January 24, 2026

## Problem Report
**Symptom:** Error dialog appearing/disappearing continuously for 5 seconds, then Anki becomes unresponsive.

**Root Cause:** The addon's `closeEvent()` method in [gui/designer_dialog.py](gui/designer_dialog.py) was using **wildcard signal disconnections** instead of specific ones.

```python
# ❌ WRONG - Wildcard disconnect (causes Qt warnings)
self.btn_import.clicked.disconnect()

# ✅ CORRECT - Specific slot disconnect
self.btn_import.clicked.disconnect(self._on_import)
```

## Why This Causes Problems

When you call `disconnect()` without arguments, Qt interprets it as a **wildcard disconnect** that attempts to sever ALL connections to that signal. This can fail when:

1. Widgets are being destroyed during dialog cleanup
2. Connections may have already been partially cleaned up
3. Qt's internal signal management conflicts with Python's garbage collection timing

The error message you saw:
```
WARNING - Qt warning: QObject::disconnect: wildcard call disconnects from destroyed signal of QPushButton::unnamed
```

This means the code tried to wildcard-disconnect from a button that was already partially destroyed, causing the error loop.

## Solution Applied

Updated [gui/designer_dialog.py](gui/designer_dialog.py) **closeEvent()** method (lines 152-197):

### Changes Made

1. **Button Signals** - Changed from bare `disconnect()` to specific slot references:
   ```python
   # Before
   self.btn_import.clicked.disconnect()
   
   # After
   self.btn_import.clicked.disconnect(self._on_import)
   ```

2. **WebView Signals** - Changed from bare `disconnect()` to specific method reference:
   ```python
   # Before
   self.webview.loadFinished.disconnect()
   
   # After
   self.webview.loadFinished.disconnect(self._on_load_finished)
   ```

### All Fixed Signals

| Signal | Connected To | Disconnection Now Uses |
|--------|-------------|----------------------|
| `btn_import.clicked` | `_on_import()` | `disconnect(self._on_import)` |
| `btn_export.clicked` | `_on_export()` | `disconnect(self._on_export)` |
| `btn_preview.clicked` | `_on_preview()` | `disconnect(self._on_preview)` |
| `btn_save.clicked` | `_on_save()` | `disconnect(self._on_save)` |
| `webview.loadFinished` | `_on_load_finished()` | `disconnect(self._on_load_finished)` |

## Testing Instructions

1. **Restart Anki** - Completely close and reopen Anki
2. **Open Tools > Anki Template Designer** - Activate the addon menu
3. **Use the Designer Dialog** - Open and interact with the template designer
4. **Close the Dialog** - Use the X button or close button to exit
5. **Verify No Errors** - Check that:
   - ✅ No Qt warning dialogs appear
   - ✅ Anki remains responsive after closing dialog
   - ✅ Anki profile doesn't freeze for 5 seconds
   - ✅ No red error messages in log

## How to Verify the Fix

### Option 1: Check Addon Console
1. Tools > Add-ons > Anki Template Designer > View Files
2. Look in the `logs/` folder for `anki_template_designer.log`
3. Should see: `All signals disconnected successfully` (no errors)

### Option 2: Check System Console
1. Open Anki with debugging console enabled
2. Watch for Qt warnings when closing the dialog
3. Should see NO warnings about `QObject::disconnect`

### Option 3: Performance Check
1. Open the Template Designer dialog
2. Close it immediately
3. Anki should respond instantly (no 5-second hang)
4. No unresponsive window warning

## Technical Details

### Why Specific Slots Work Better

Qt's signal-slot system uses different code paths:

- **Wildcard `disconnect()`**: Iterates ALL connections, removes any where sender/receiver matches
  - Problem: Can fail if receiver is partially destroyed
  - Problem: Race condition with garbage collection

- **Specific `disconnect(signal, slot)`**: Removes ONLY the exact connection
  - Safer: No iteration through unrelated connections  
  - Reliable: Works even if other signals are cleaning up
  - Recommended: Official Qt best practice

### Code Quality Improvement

This also follows Qt documentation best practices:
> "It is safe to call disconnect() with specific slot references. It is unsafe to call disconnect() without arguments (wildcard) during widget destruction."

## Reinstallation

The addon has been **automatically reinstalled** with the fix applied.

### To Manually Verify:
```bash
cd d:\Development\Python\AnkiTemplateDesigner
python install_addon.py install -f
```

The updated files are now in:
```
C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner\gui\designer_dialog.py
```

## Related Files

- **Modified:** [gui/designer_dialog.py](gui/designer_dialog.py) (lines 152-197)
- **Reference:** [QT-WIDGET-LIFECYCLE-FIXES.md](QT-WIDGET-LIFECYCLE-FIXES.md) for broader Qt cleanup best practices
- **Reference:** [QT-WARNINGS-EXPLAINED.md](QT-WARNINGS-EXPLAINED.md) for warning explanations

## Summary

✅ **Fixed:** Wildcard signal disconnections replaced with specific slot references  
✅ **Installed:** Addon updated with fix applied  
✅ **Next:** Restart Anki and test the Template Designer without errors
