# Quick Debugging Checklist

## When App Gets Stuck at "Step 2: Initializing Python bridge..."

### Step 1: Enable Debug Output (2 minutes)
- [ ] Edit `config.json` in addon folder
- [ ] Set `"debugLogging": true`
- [ ] Restart Anki
- [ ] Trigger the issue again

### Step 2: Check Python Log (2 minutes)
```powershell
# Windows PowerShell
$logFile = "$env:USERPROFILE\.anki_template_designer\template_designer.log"
Get-Content $logFile -Tail 50
```

**What to look for:**
- ❌ `QWebChannel not available` → Qt not properly initialized
- ❌ `ImportError` → Missing dependency (check pip install)
- ❌ `Bridge object not found` → QWebChannel registration failed
- ✅ `Bridge initialized successfully` → Python side OK

### Step 3: Check Browser Console (2 minutes)
- [ ] Press **F12** in the webview
- [ ] Click **Console** tab
- [ ] Look for red error messages
- [ ] Check for warnings about QWebChannel

**Common JS errors:**
- `QWebChannel is not defined` → WebEngine not available
- `window.bridge is null` → Bridge not exposed to JS
- `Cannot read property 'initialize'` → Bridge methods missing

### Step 4: Check Addon Data Folder (2 minutes)
```powershell
# List addon data folders
$addonDataPath = "$env:APPDATA\Anki2\addons21"
Get-ChildItem -Path $addonDataPath -Filter "*template*" -Directory
```

- [ ] Verify addon is installed
- [ ] Check for `logs/anki_template_designer.log`
- [ ] Verify logs folder exists and is writable

### Step 5: Collect Debug Info (5 minutes)

When reporting an issue, provide:
1. **Python log** (last 50 lines):
   ```
   ~/.anki_template_designer/template_designer.log
   ```

2. **Browser console** (screenshot or text):
   - Press F12
   - Errors/warnings visible

3. **System info**:
   - Anki version
   - Python version (`python --version`)
   - PyQt version

4. **Reproduction steps**:
   - Exact steps to trigger the issue

## Config.json Quick Ref

```json
{
  "debugLogging": true,        // Enable file logging (true/false)
  "logLevel": "DEBUG"          // Verbosity: DEBUG, INFO, WARNING, ERROR
}
```

## Log File Locations

| System | Path |
|--------|------|
| Windows | `%USERPROFILE%\.anki_template_designer\template_designer.log` |
| Mac | `~/.anki_template_designer/template_designer.log` |
| Linux | `~/.anki_template_designer/template_designer.log` |

## Most Common Issues & Fixes

### "Step 2" hangs forever
1. ✅ Enable debug logging
2. ✅ Check Python log for `Bridge object not found`
3. ✅ Verify PyQt6 installed: `pip list | grep PyQt`
4. ✅ Check WebEngine available: `pip install PyQt6-WebEngine`

### JavaScript errors in console
1. ✅ Check if QWebChannel defined: `console.log(window.QWebChannel)`
2. ✅ Check if bridge exists: `console.log(window.bridge)`
3. ✅ Look at Python log for initialization failures

### Empty log file
1. ✅ Verify `debugLogging: true` in config.json
2. ✅ Check folder permissions
3. ✅ Try deleting old logs and restarting Anki
4. ✅ Verify system time is correct

### Performance slow with logging
1. ✅ Set `"debugLogging": false` in config.json
2. ✅ Or set `"logLevel": "ERROR"` to reduce output

## Quick Command Reference

```powershell
# View last 50 lines of log
Get-Content "$env:USERPROFILE\.anki_template_designer\template_designer.log" -Tail 50

# View last 100 lines with timestamps
Get-Content "$env:USERPROFILE\.anki_template_designer\template_designer.log" -Tail 100 | Format-Table -AutoSize

# Search log for errors
Select-String "ERROR" "$env:USERPROFILE\.anki_template_designer\template_designer.log" | Format-Table

# Clear all logs
Remove-Item "$env:USERPROFILE\.anki_template_designer\template_designer.log*" -Force
```

## Getting Help

Include this info when reporting issues:

1. **Last 50 lines of Python log**
2. **Screenshot of browser console (F12)**
3. **Output of**: `pip list | grep -i "pyqt\|anki"`
4. **Exact error message** from debug dialog
5. **Steps to reproduce**

See [DEBUGGING-GUIDE.md](DEBUGGING-GUIDE.md) for detailed troubleshooting.

