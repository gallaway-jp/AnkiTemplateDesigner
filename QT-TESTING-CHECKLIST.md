# Qt Widget Lifecycle Fixes - Testing & Verification Checklist

**Status**: Ready for Testing  
**Date**: January 24, 2026  
**Expected Duration**: 5-10 minutes

---

## Pre-Installation Checklist

### Validation
- [ ] Run `python validate_qt_fixes.py`
- [ ] Confirm: `7/7 checks passed` ✅
- [ ] All checks show green checkmarks (✅)
- [ ] No errors in validation output

### System Check
- [ ] Anki 25.07.5 or similar installed
- [ ] Python 3.13.5 installed
- [ ] PyQt 6.9.1 available
- [ ] Development directory: `d:\Development\Python\AnkiTemplateDesigner`

### Pre-Installation Backup (Optional but Recommended)
- [ ] Backup current addon (if previously installed):
  ```bash
  Copy-Item "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner" `
    -Destination "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner.backup" -Recurse
  ```

---

## Installation Checklist

### Step 1: Close Anki
- [ ] Close all Anki windows
- [ ] Wait 5 seconds (let processes finish)
- [ ] Verify Anki not in taskbar
- [ ] No Anki processes running: `Get-Process | grep anki` (should be empty)

### Step 2: Delete Old Addon
- [ ] Delete: `$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner`
- [ ] Verify deletion:
  ```bash
  Test-Path "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner"
  # Should output: False
  ```
- [ ] Confirm no "AnkiTemplateDesigner" folder visible

### Step 3: Reinstall Addon
- [ ] Navigate to: `d:\Development\Python\AnkiTemplateDesigner`
- [ ] Run: `python install_addon.py`
- [ ] Expected output: `✓ Addon installed successfully`
- [ ] Check destination folder exists:
  ```bash
  Test-Path "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner"
  # Should output: True
  ```

---

## Initial Testing Checklist

### Start Anki
- [ ] Open Anki
- [ ] Allow it to fully load (wait for main window)
- [ ] Check taskbar (should be "Anki" with happy face)
- [ ] Verify no errors on startup

### Open Template Designer
- [ ] Go to: **Tools** → **Template Designer**
- [ ] Dialog should appear without hang
- [ ] Note the time it takes to load (~2-3 seconds expected)

### Initial Load Success Indicators
- [ ] Dialog opens successfully ✅
- [ ] No hang at "Step 2: Initializing Python bridge..."
- [ ] Editor visible (GrapeJS canvas)
- [ ] Four buttons visible:
  - [ ] "Import HTML"
  - [ ] "Export to Anki"
  - [ ] "Preview Card"
  - [ ] "Save to Note Type"
- [ ] No Qt warnings in Anki console (bottom right)
- [ ] No Python error messages

### Console Check (Browser F12)
- [ ] Press F12 to open browser console
- [ ] Check for messages like:
  - [ ] `[Template Designer] Starting initialization...`
  - [ ] `[Template Designer] UI setup complete`
  - [ ] `[Template Designer] Bridge setup complete`
  - [ ] `[Template Designer] Editor load initiated`
  - [ ] `✓ Page loaded successfully`
- [ ] No red error messages (should only see blue info messages)

### Dialog Functionality
- [ ] Buttons are clickable (hover shows pointer)
- [ ] No warnings or error messages in dialog
- [ ] Editor canvas is visible and interactive
- [ ] Responsive layout (can see all buttons)

---

## Log File Verification Checklist

### Access Log File
- [ ] Navigate to: `C:\Users\<YourUsername>\AppData\Roaming\Anki2\AnkiTemplateDesigner`
- [ ] Find: `template_designer.log`
- [ ] Open with text editor (Notepad, VS Code, etc.)
- [ ] File has content (not empty)

### Check for Success Messages
- [ ] Log contains: `TemplateDesignerDialog.__init__ starting`
- [ ] Log contains: `UI setup complete - toolbar created with 4 buttons`
- [ ] Log contains: `QWebChannel registered successfully`
- [ ] Log contains: `_load_editor() starting`
- [ ] Log contains: `Page loaded successfully`
- [ ] Log contains: `_on_load_finished() called with ok=True`

### Check for Error Messages
- [ ] No lines starting with `ERROR`
- [ ] No traceback information
- [ ] No "Failed to" messages
- [ ] No "Exception" entries

### Check for Qt Warnings
- [ ] **No** warnings about "QPushButton::unnamed"
- [ ] **No** warnings about "disconnect from destroyed signal"
- [ ] **No** "QObject::disconnect: wildcard call" messages
- [ ] (Other Qt info messages are fine)

---

## Dialog Close/Cleanup Checklist

### Close Dialog
- [ ] Click the X button to close
- [ ] Dialog closes immediately (no hang)
- [ ] Returns to Anki main window
- [ ] No error messages on close

### Check Cleanup in Log
- [ ] Check log again (refresh file in text editor)
- [ ] Look for: `closeEvent() called - cleaning up resources`
- [ ] Look for: `All signals disconnected successfully`
- [ ] Look for: `Dialog closed`
- [ ] All signal disconnection lines should show (one per button)

### Verify Clean Shutdown
- [ ] No error or exception messages after close
- [ ] Log shows ordered cleanup sequence
- [ ] No hanging processes
- [ ] Anki remains responsive

---

## Advanced Testing (Optional)

### Button Functionality
- [ ] Click "Import HTML" button
- [ ] Should open file dialog or show message
- [ ] No crashes or errors
- [ ] Click "Export to Anki"
- [ ] Click "Preview Card"
- [ ] Click "Save to Note Type"
- [ ] None should cause errors

### Stress Testing
- [ ] Open Template Designer 3 times
- [ ] Close and reopen multiple times
- [ ] Check logs for repeated success messages
- [ ] No memory leaks (Anki window stays responsive)
- [ ] No increasing error counts in log

### Content Testing
- [ ] Try dragging elements in editor
- [ ] Try adding blocks
- [ ] Try exporting template
- [ ] Try importing template
- [ ] All should work without errors

---

## Troubleshooting Checklist

### If Dialog Hangs at Step 2
- [ ] Close Anki (force-quit if necessary)
- [ ] Delete addon folder again
- [ ] Reinstall addon
- [ ] Check Python installation: `python --version`
- [ ] Check validation: `python validate_qt_fixes.py`
- [ ] Check logs for specific error message

### If Qt Warnings Still Appear
- [ ] Run validation: `python validate_qt_fixes.py`
- [ ] Confirm 7/7 checks pass
- [ ] Check install location
- [ ] Verify old addon completely deleted
- [ ] Clear browser cache (optional): Delete `%temp%` files
- [ ] Restart computer (nuclear option)

### If Buttons Don't Work
- [ ] Check browser console for JS errors (F12)
- [ ] Check Python log for bridge errors
- [ ] Verify bridge initialized: look for "QWebChannel registered successfully"
- [ ] Check: `All callbacks set successfully` in log

### If Editor Doesn't Load
- [ ] Check HTML exists: `web/dist/index.html`
- [ ] Run build: `npm run build` (if needed)
- [ ] Check log for specific error message
- [ ] Look for: "Editor HTML not found" or "Load failed"

---

## Success Criteria

### Minimum Success (Issue Fixed)
- [ ] No hang at Step 2
- [ ] No Qt warnings about destroyed signals
- [ ] Dialog loads successfully
- [ ] Editor visible and responsive
- [ ] Clean shutdown with proper logging
- **Assessment**: ✅ FIX SUCCESSFUL

### Full Success (Everything Works)
- All minimum criteria +
- [ ] All buttons functional
- [ ] Can import/export templates
- [ ] Can preview cards
- [ ] No errors in logs at any point
- [ ] Can open/close dialog repeatedly
- **Assessment**: ✅ FULLY OPERATIONAL

---

## Results Recording

### Test Date
- **Date**: _______________
- **Time**: _______________
- **Tester**: _______________

### Overall Result
- [ ] ✅ SUCCESS - Fix working, no issues
- [ ] ⚠️  PARTIAL - Works but with minor issues:
  - **Issues**: ________________________________________
- [ ] ❌ FAILED - Still has problems:
  - **Problems**: ________________________________________

### Performance Metrics
- **Step 2 Load Time**: _______ seconds (expected: <1 sec)
- **Total Dialog Load Time**: _______ seconds (expected: 2-3 sec)
- **Close Time**: _______ seconds (expected: <1 sec)

### Qt Warnings
- **Before Fix**: ✅ Present (as reported)
- **After Fix**: ✅ None expected
- **Actual**: 
  - [ ] None ✅
  - [ ] Some still appear ⚠️
  - [ ] Same as before ❌

---

## Sign-Off

- [ ] Validation passed
- [ ] Installation completed
- [ ] Initial testing successful
- [ ] Log verification complete
- [ ] Cleanup verified
- [ ] All success criteria met

### Sign-Off Statement
```
I have tested the Qt Widget Lifecycle fixes and confirm:
1. All validation checks passed (7/7)
2. The addon installed successfully
3. Template Designer loads without hanging
4. No Qt warnings about destroyed signals appear
5. The editor initializes correctly
6. The dialog closes cleanly with proper logging

Date: _______________
Tester: _______________
Status: ✅ READY FOR PRODUCTION
```

---

## Next Steps After Success

- [ ] Commit changes to version control (if applicable)
- [ ] Mark issue as resolved
- [ ] Document results for team
- [ ] Update project status
- [ ] Begin Phase 6 development (next tasks)

---

## Support

If you encounter any issues:

1. **Check logs first**: `~/.anki_template_designer/template_designer.log`
2. **Run validation**: `python validate_qt_fixes.py`
3. **Read docs**: [QT-WIDGET-LIFECYCLE-FIXES.md](QT-WIDGET-LIFECYCLE-FIXES.md)
4. **Quick guide**: [QUICK-FIX-GUIDE.md](QUICK-FIX-GUIDE.md)

---

**Status**: ✅ Ready for Testing

Proceed with the checklist above. Record results when complete.
