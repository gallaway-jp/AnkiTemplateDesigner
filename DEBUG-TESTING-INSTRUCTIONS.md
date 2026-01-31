# Debug Testing Instructions - January 24, 2026

## Purpose
To find the exact location where the error dialog is being triggered repeatedly.

## Setup

The addon has been reinstalled with **comprehensive debug logging**. Now when you test it, you'll see detailed console output showing every step of initialization.

## Testing Steps

### 1. Start Anki with Console Output Visible
**Windows:**
```bash
# Open PowerShell in Anki installation directory, then run:
.\anki.exe 2>&1 | Tee-Object -FilePath anki_debug_output.txt
```

Or:
- Run Anki normally
- Open Tools > Add-ons > Anki Template Designer > View Files
- Open the `logs` folder to check the log file in real-time

### 2. Activate the Template Designer
1. Go to **Tools > Anki Template Designer**
2. Watch the console/log output carefully
3. **Note the exact point where the error dialog appears**

### 3. Capture the Output
When the error happens, save/copy:
- Console output showing the debug messages
- The error message in the dialog
- The time it happens relative to the debug messages

## What to Look For

You should see messages like this in the console:
```
[Template Designer] ╔════════════════════════════════════════════════════════════════╗
[Template Designer] ║ Starting Dialog Initialization                                 ║
[Template Designer] ╚════════════════════════════════════════════════════════════════╝
[Template Designer] step 1: ✓ super().__init__ complete
[Template Designer] step 2: ✓ window title set
[Template Designer] step 3: ✓ window flags set
[Template Designer] step 4: ✓ minimum size set
[Template Designer] step 5: ✓ optimal size set
[Template Designer] step 6: ✓ parsers/generators initialized
[Template Designer] step 7: ✓ WebViewBridge created
[Template Designer] step 8: ✓ webview reference initialized
[Template Designer] step 9: ✓ theme detected: light
[Template Designer] step 10: ✓ save state tracker created
[Template Designer] step 11: ✓ button references initialized
[Template Designer] step 12: ✓ _setup_ui() complete
[Template Designer] step 13: ✓ _setup_bridge() complete
[Template Designer] step 14: ✓ _load_editor() initiated
[Template Designer] step 15: ✓ _check_assets_async() initiated
```

**If you see an error message before all 15 steps, that's where the problem is!**

## What the Error Could Be

Based on the output you give, I can identify:
1. **Initialization step where it fails** (step 1-15)
2. **Whether it's in Python code or JavaScript**
3. **Exact error message and traceback**

## Next Actions After Testing

Once you run the test and see where it fails:
1. Copy the full console output
2. Note which step number shows an error
3. Tell me exactly what error message appears
4. I can then pinpoint the exact cause and fix it

## Alternative: Check the Log File

If Anki closes before you can see console output:
1. Go to: `C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner\logs`
2. Open `anki_template_designer.log`
3. Look for the last lines before the error
4. Copy those lines and send them to me

## Key Questions After Testing

1. **Does the dialog appear at all**, or does Anki freeze before it shows?
2. **What is the error message** in the dialog box?
3. **Which step number appears last** in the debug output before the error?
4. **How long does it take** before the error appears?

With this information, we can identify the exact cause!
