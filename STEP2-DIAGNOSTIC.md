# Step 2 Bridge Initialization Hang - Diagnostic Guide

## Issue
Application gets stuck at **"Step 2: Initializing Python bridge..."** and never progresses to Step 3.

## Root Causes & Solutions

### 1. Qt Widget Lifecycle Issues (FIXED ✓)

**Symptoms:**
- Qt warnings about `QPushButton::disconnect: wildcard call disconnects from destroyed signal`
- Dialog UI appears but webview doesn't initialize

**What was wrong:**
- Button widgets created without parent, causing cleanup issues
- Layout hierarchy problems preventing proper widget destruction

**What was fixed:**
- All buttons now created with explicit parent: `QPushButton("Label", parent_widget)`
- Toolbar now has a parent QWidget instead of being parentless layout
- Proper widget ownership ensures clean initialization

**Status:** ✅ Fixed in designer_dialog.py

---

### 2. QWebChannel Registration Failure

**Symptoms:**
- Page loads but JavaScript shows `window.bridge is null`
- `bridge.initialize()` times out waiting for bridge object

**Check these:**
1. **QWebChannel is registered BEFORE webview loads:**
   ```python
   # Correct order (in _setup_ui):
   # 1. Create webview
   # 2. Setup bridge (register on channel)
   # 3. Load HTML
   ```

2. **Bridge object is properly exposed:**
   ```python
   channel = QWebChannel(self.webview.page())
   channel.registerObject("bridge", self.bridge)  # Must be "bridge"
   self.webview.page().setWebChannel(channel)
   ```

3. **PyQt QWebChannel is available:**
   ```bash
   python -c "from PyQt6.QtWebChannel import QWebChannel; print('OK')"
   ```

**Fix if needed:**
```bash
pip install --upgrade PyQt6-WebEngine
```

---

### 3. QWebEngineView Initialization Timeout

**Symptoms:**
- `bridge.initialize()` times out after 5 seconds
- No errors in Python logs
- Browser console (F12) shows no QWebChannel errors

**Check these:**
1. **WebView settings are correct:**
   ```python
   settings = self.webview.settings()
   settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
   settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
   ```

2. **QWebEngineView is created on main thread:**
   - WebEngine must be initialized on Qt event loop
   - Check that dialog creation is not happening in background thread

3. **Qt event loop is running:**
   ```bash
   # In Anki, this happens automatically
   # But if you're testing standalone, need:
   app.exec()
   ```

**Fix:**
- Ensure QWebEngineView created in main GUI thread
- Verify Qt event loop is active

---

### 4. HTML File Not Found

**Symptoms:**
- `Step 2` hangs
- Python log shows: `ERROR: Editor HTML not found`
- No HTML content loads in webview

**Check:**
```bash
# Verify the file exists
Test-Path "d:\Development\Python\AnkiTemplateDesigner\web\dist\index.html"
```

**Fix:**
```bash
# Rebuild the web UI
cd web
npm run build
# Should create dist/index.html
```

---

### 5. Bridge Object Initialization Failure

**Symptoms:**
- Python logs show: `WebViewBridge initialized successfully`
- But JavaScript never receives the bridge object

**Check Python log for:**
- `_setup_bridge() starting`
- `QWebChannel registered successfully`
- `Bridge callbacks set successfully`

If you see errors instead, check:
1. **Bridge constructor doesn't fail:**
   ```python
   def __init__(self, parent=None):
       super().__init__(parent)
       # No heavy imports here!
   ```

2. **No blocking operations in bridge methods:**
   - All pyqtSlots should return immediately
   - Database calls must be non-blocking

3. **Signal/slot connections are correct:**
   ```python
   self.webview.loadFinished.connect(self._on_load_finished)
   # No lambda captures
   ```

---

## Diagnostic Steps

### Step 1: Check Python Log
```powershell
$log = "$env:USERPROFILE\.anki_template_designer\template_designer.log"
Get-Content $log -Tail 100 | Select-String "Step 2|bridge|QWebChannel"
```

**Look for patterns:**
- ✅ `Bridge setup complete` - Python side OK
- ❌ `Bridge object not found` - Registration failed
- ❌ `QWebChannel not available` - Library missing

### Step 2: Check Browser Console (F12)
Press **F12** when stuck at Step 2:
- **Console** tab: Look for red errors
- **Network** tab: Check if index.html loaded successfully
- Type in console: `window.bridge` (should see object, not null)

**Common JS errors:**
```javascript
// Error: QWebChannel is not defined
// → PyQt6-WebEngine not installed

// Error: Cannot read property 'initialize'
// → Bridge not exposed to QWebChannel

// Timeout at bridge.initialize()
// → QWebChannel callback never fired
```

### Step 3: Enable Debug Logging
Edit `config.json`:
```json
{
  "debugLogging": true,
  "logLevel": "DEBUG"
}
```

Restart Anki and check log again:
```powershell
Get-Content "$env:USERPROFILE\.anki_template_designer\template_designer.log" -Tail 200
```

### Step 4: Check WebView Load Status
Add this to browser console (F12) and paste output:
```javascript
console.log('WebView loaded:', document.readyState);
console.log('QWebChannel available:', typeof QWebChannel !== 'undefined');
console.log('Qt available:', typeof qt !== 'undefined');
console.log('Bridge available:', typeof window.bridge !== 'undefined');
```

---

## Performance Metrics

When Step 2 works correctly, timing should be:
- `bridge.initialize()` → Should complete in **<100ms**
- If taking >100ms → Check Python log for delays
- If taking >5s → Timeout will trigger (see App.tsx timeout config)

---

## Collecting Diagnostic Info for Support

When reporting Step 2 hang:

1. **Python system info:**
   ```powershell
   python --version
   pip show PyQt6 PyQt6-WebEngine
   ```

2. **Last 100 lines of Python log:**
   ```powershell
   Get-Content "$env:USERPROFILE\.anki_template_designer\template_designer.log" -Tail 100 | Out-File debug_log.txt
   ```

3. **Browser console screenshot (F12):**
   - Paste full console output

4. **Anki version:**
   - Help → About

5. **Reproduction steps:**
   - Exactly what you do to trigger the hang

---

## Common Fixes Summary

| Issue | Fix | Time |
|-------|-----|------|
| Qt button warnings | ✅ Already fixed - widgets now have parents | 0 min |
| PyQt missing | `pip install PyQt6-WebEngine` | 2 min |
| HTML not found | `npm run build` in web folder | 5 min |
| QWebChannel timeout | Check Qt event loop running, restart Anki | 1 min |
| Bridge not exposed | Verify `channel.registerObject("bridge", ...)` | 1 min |

---

## Next Steps

After applying these fixes:
1. Clear old logs: `Remove-Item "$env:USERPROFILE\.anki_template_designer\template_designer.log*"`
2. Restart Anki
3. Try to open Template Designer again
4. Check if it gets past Step 2
5. Share the new log if still stuck

