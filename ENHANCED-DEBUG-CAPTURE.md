# Enhanced Debug Capture - How to Get the Error Message

## Critical: Run Anki from Command Line to See Stderr Output

The addon now sends all its debug output to **stderr** (standard error stream). This is the ONLY way to see what's happening.

### Windows PowerShell

**Option 1: Direct Console Output**
```powershell
# Navigate to Anki installation directory
cd "C:\Program Files\Anki"

# Or wherever Anki is installed on your system
# Run Anki with output captured
& ".\anki.exe" 2>&1 | Tee-Object -FilePath "C:\temp\anki_debug.log"
```

**Option 2: Using Redirect to File**
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
& "C:\Program Files\Anki\anki.exe" 2>&1 | Tee-Object -FilePath "$env:TEMP\anki_$timestamp.log"
```

**Option 3: Simple File Redirect**
```powershell
C:\Program Files\Anki\anki.exe 2> C:\temp\anki_stderr.txt
```

Then open C:\temp\anki_stderr.txt to see the output.

## Anki Location Finder

If you don't know where Anki is installed:

```powershell
Get-Command anki -ErrorAction SilentlyContinue
# Or search for it
Get-ChildItem -Path "$env:ProgramFiles" -Filter "anki.exe" -Recurse
Get-ChildItem -Path "$env:LOCALAPPDATA" -Filter "anki.exe" -Recurse
```

## Test Sequence

1. **Open PowerShell as Administrator**
2. **Run one of the commands above** to start Anki with console output
3. **Immediately go to Tools > Anki Template Designer**
4. **Watch the console output** - you should see:
   ```
   [Template Designer] __init__.py LOADED - Starting addon initialization
   [Template Designer] Importing Anki modules...
   [Template Designer] Anki modules imported successfully
   [Template Designer] Calling _setup_logging()...
   ...etc...
   ```
5. **When the error appears, capture the console output**
6. **Look for any red text or ERROR messages**

## What You'll See

### Success Path
```
[Template Designer] __init__.py LOADED
[Template Designer] Importing Anki modules...
[Template Designer] Anki modules imported successfully
[Template Designer] _setup_logging() called
[Template Designer] Logging utils imported
[Template Designer] Config loaded: {...}
[Template Designer] Log file: C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner\logs\anki_template_designer.log
[Template Designer] Logging configured successfully
[Template Designer] on_profile_loaded() called
[Template Designer] Menu item added to Tools menu
[Template Designer] open_designer() CALLED
[Template Designer] Creating TemplateDesignerDialog instance...
[Template Designer] step 1: ✓ super().__init__ complete
...
```

### Error Path
```
[Template Designer] [ERROR SOMEWHERE]
[Template Designer] EXCEPTION: [actual error message]
Traceback (most recent call last):
  ...
```

## After Capturing Output

1. **Copy the entire console output** (scroll up to see all of it)
2. **Save it to a text file**
3. **Share with me** - this will show exactly what's failing

## Alternative: Check the Log File After Restarting

Even if Anki crashes, the log file might have been written:

```powershell
# Check if log file exists
Test-Path "C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner\logs\anki_template_designer.log"

# View it
Get-Content "C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner\logs\anki_template_designer.log" -Tail 50
```

This will show the last 50 lines of the log file.

## Key Information to Capture

When you see the error, note:
1. **First line that says ERROR or EXCEPTION**
2. **The actual error message** (not just the class name)
3. **The traceback** - which file and line number caused it
4. **How many initialization steps completed** (step 1? step 5? step 14?)

This will pinpoint EXACTLY where the bug is!
