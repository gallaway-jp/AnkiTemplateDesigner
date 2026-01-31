# Post-Fix Testing Checklist

## Before You Start

- [ ] Close Anki completely
- [ ] Close any open terminals
- [ ] Have administrative access to your system

## Step 1: Clear Old Logs (1 minute)

```powershell
# Run in PowerShell
$logDir = "$env:USERPROFILE\.anki_template_designer"
if (Test-Path $logDir) {
    Remove-Item "$logDir\template_designer.log*" -Force 2>$null
    Write-Host "Old logs cleared"
} else {
    Write-Host "Log directory doesn't exist yet (will be created)"
}
```

Expected output:
```
Old logs cleared
```

## Step 2: Enable Debug Logging (1 minute)

Edit `config.json` in your addon directory and set:
```json
{
  "preview_width": 1600,
  "preview_height": 900,
  "default_platform": "desktop",
  "ankidroid_theme": "light",
  "show_both_platforms": true,
  "auto_refresh": true,
  "debugLogging": true,
  "logLevel": "DEBUG"
}
```

- [ ] File saved and closed

## Step 3: Verify Dependencies (2 minutes)

```powershell
# Check PyQt6 is installed
pip list | Select-String "PyQt6"
```

Expected output:
```
PyQt6                    6.9.1
PyQt6-sip                13.9.1
PyQt6-WebEngine          6.9.1
```

If WebEngine is missing:
```powershell
pip install PyQt6-WebEngine
```

- [ ] All PyQt6 components verified

## Step 4: Start Anki with Clean State (1 minute)

```powershell
# Option A: If Anki is in PATH
anki --profile default

# Option B: If not in PATH, use full path
"C:\Program Files\Anki\anki.exe" --profile default
```

Wait for Anki to fully load (you should see the main window).

- [ ] Anki started successfully

## Step 5: Open Template Designer (2 minutes)

In Anki:
1. Click **Tools** → **Template Designer (Visual Editor)**
2. Watch for the progress dialog

Expected sequence:
```
Step 1: Starting initialization...
Step 2: Initializing Python bridge...
Step 3: Python bridge initialized successfully
Step 4: Loading Anki fields and behaviors...
Step 4b: Loaded 5 fields successfully
Step 4d: Loaded X behaviors successfully
Step 5: Initializing Anki store...
Step 6: Setting up event listeners...
Step 7: Applying theme...
Step 8: Initialization complete! Rendering editor...
```

**Outcome A - SUCCESS ✅**
- All steps complete
- Editor loads with buttons
- No error dialog

**Outcome B - STUCK AT STEP 2 ⏳**
- Hangs at "Step 2: Initializing Python bridge..."
- → Continue to Step 6

**Outcome C - OTHER ERROR ❌**
- Different error message shown
- → Note the error and go to Step 6

- [ ] Attempted to open Template Designer

## Step 6: Check Python Log (5 minutes)

If stuck or errored, check the log:

```powershell
$log = "$env:USERPROFILE\.anki_template_designer\template_designer.log"
Get-Content $log -Tail 100
```

**Copy the output and look for:**

### Pattern A: SUCCESS ✅
```
INFO - ... - UI setup complete
INFO - ... - QWebChannel registered successfully
INFO - ... - Bridge callbacks set successfully
INFO - ... - Load started for: file:///...
INFO - ... - Page loaded successfully
```

### Pattern B: STUCK AT BRIDGE INIT ⏳
```
WARNING - ... - Qt warning: QObject::disconnect: wildcard call
```
**← Qt warning suggests widget cleanup issue**

### Pattern C: MISSING HTML ❌
```
ERROR - ... - HTML file not found: ... web/dist/index.html
```
**← Need to rebuild web UI: `cd web && npm run build`**

### Pattern D: IMPORT ERROR ❌
```
ERROR - ... - ImportError: cannot import name 'X'
```
**← Missing dependency, install with pip**

**Share output in error report if not obvious**

## Step 7: Check Browser Console (if Step 5 succeeded)

Press **F12** in the Template Designer window:

1. Click **Console** tab
2. Look for red error messages
3. Type this to check bridge:
   ```javascript
   console.log('Bridge available:', typeof window.bridge !== 'undefined');
   console.log('Bridge initialized:', window.bridge !== null);
   ```

Expected output:
```
Bridge available: true
Bridge initialized: true
```

- [ ] Console checked and bridge available

## Step 8: Report Results

### SUCCESS ✅
Congratulations! Template Designer is working. You can:
- [ ] Set `debugLogging: false` to improve performance
- [ ] Enjoy using the template designer
- [ ] Report any feature issues

### STILL STUCK AT STEP 2
Please provide:
1. Last 100 lines of Python log
2. Output of `pip list | Select-String PyQt`
3. Browser console output (F12)
4. Your Anki version

### OTHER ERROR
Please provide:
1. Error message from dialog
2. Last 100 lines of Python log
3. System info (Windows version, Python version)
4. Steps to reproduce

---

## Quick Reference Commands

```powershell
# View Python log
Get-Content "$env:USERPROFILE\.anki_template_designer\template_designer.log" -Tail 100

# View system info
[System.Environment]::OSVersion
python --version
pip show PyQt6 PyQt6-WebEngine

# Clear logs
Remove-Item "$env:USERPROFILE\.anki_template_designer\template_designer.log*" -Force

# Check if addon installed
Test-Path "$env:APPDATA\Anki2\addons21\anki_template_designer"
```

---

## Troubleshooting Quick Links

- **Step 2 hang details**: See [STEP2-DIAGNOSTIC.md](STEP2-DIAGNOSTIC.md)
- **Logging setup**: See [DEBUGGING-GUIDE.md](DEBUGGING-GUIDE.md)
- **Complete logging**: See [LOGGING-IMPLEMENTATION.md](LOGGING-IMPLEMENTATION.md)
- **Fixes applied**: See [FIXES-APPLIED.md](FIXES-APPLIED.md)

---

## Expected Timeline

| Step | Time | Notes |
|------|------|-------|
| Clear logs | 1 min | Quick operation |
| Enable debug | 1 min | Edit one file |
| Check deps | 2 min | pip list verification |
| Start Anki | 1 min | Wait for load |
| Open designer | 2 min | Try the feature |
| Check log | 5 min | Read output |
| **Total** | **~12 minutes** | Or less if working |

