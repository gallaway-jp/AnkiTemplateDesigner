# CRITICAL: Complete These Steps RIGHT NOW to Test the Qt Fixes

**Status**: Fixes are in the source code, but addon NOT yet reinstalled  
**Current Issue**: You're running the OLD addon version  
**Solution**: Follow these 4 steps (takes 5 minutes)

---

## Step 1: Close Anki Completely

**IMPORTANT**: Make sure Anki is FULLY closed (not just minimized)

```powershell
# On Windows PowerShell, verify Anki is closed:
Get-Process | grep -i anki
# Should show NOTHING (no anki processes)

# If Anki is still running, close it:
Stop-Process -Name anki -Force
Stop-Process -Name python -Force  # Optional - only if needed
```

---

## Step 2: Delete the Old Addon

Run this command in PowerShell:

```powershell
$addonPath = "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner"
Remove-Item $addonPath -Recurse -Force
Write-Host "Addon deleted from: $addonPath"

# Verify it's gone:
Test-Path $addonPath  # Should output: False
```

---

## Step 3: Reinstall the Fixed Addon

```powershell
cd d:\Development\Python\AnkiTemplateDesigner
python install_addon.py
```

Expected output:
```
Installing addon from: d:\Development\Python\AnkiTemplateDesigner
Installing to: C:\Users\...\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner
✓ Addon installed successfully
```

---

## Step 4: Test in Anki

1. Open Anki
2. Go to: **Tools** → **Template Designer**
3. Check these indicators of success:
   - ✅ Dialog opens without hanging at Step 2
   - ✅ No Qt warnings in the console (bottom-right of Anki)
   - ✅ Editor loads successfully in 2-3 seconds
   - ✅ All 4 buttons visible: Import, Export, Preview, Save

---

## What to Expect After Fix

### Console Output (should see):
```
[Template Designer] Starting initialization...
[Template Designer] UI setup complete
[Template Designer] Bridge setup complete
[Template Designer] Editor load initiated
✓ Page loaded successfully
```

### What NOT to See (these should be GONE):
```
❌ WARNING - Qt warning: QObject::disconnect: wildcard call disconnects from destroyed signal of QPushButton::unnamed
```

---

## If You Still See Warnings After Reinstall

1. **Close Anki again**
2. **Verify the addon folder:**
   ```powershell
   dir "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner\gui\designer_dialog.py"
   # File should exist
   ```

3. **Check if the fixes are in the file:**
   ```powershell
   # Should find "def closeEvent" in designer_dialog.py
   Select-String -Path "$env:APPDATA\Anki2\addons21\AnkiTemplateDesigner\gui\designer_dialog.py" -Pattern "def closeEvent"
   # Should output: def closeEvent(self, event):
   ```

4. **Run validation again:**
   ```powershell
   cd d:\Development\Python\AnkiTemplateDesigner
   python validate_qt_fixes.py
   ```

---

## Summary

| Step | Action | Indicator |
|------|--------|-----------|
| 1 | Close Anki | Task manager shows no anki.exe |
| 2 | Delete addon | Folder gone from %APPDATA%\Anki2\addons21 |
| 3 | Reinstall | `✓ Addon installed successfully` message |
| 4 | Test | Editor loads, no warnings, buttons visible |

---

## Get Back to Me When:

- [ ] You've completed all 4 steps
- [ ] You've opened Template Designer in the fresh Anki
- [ ] You can report whether you see the Qt warnings or not

---

**Do this NOW, then come back and let me know if the warnings are gone!**
