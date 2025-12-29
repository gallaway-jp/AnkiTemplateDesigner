# Installation Instructions for Anki Template Designer

## Current Status
The addon is now configured to:
1. Wait for Anki profile to load before initializing
2. Show any initialization errors with a popup
3. Lazy-load heavy modules only when needed
4. Add "Template Designer (Visual Editor)" to Tools menu

## How to Install

### Step 1: Locate Anki's addons folder

**Windows:**
```
%APPDATA%\Anki2\addons21\
```
Full path is usually:
```
C:\Users\YourUsername\AppData\Roaming\Anki2\addons21\
```

**Mac:**
```
~/Library/Application Support/Anki2/addons21/
```

**Linux:**
```
~/.local/share/Anki2/addons21/
```

### Step 2: Copy the addon

1. Copy this entire folder to the addons21 directory
2. Rename it to just the addon name (remove spaces/special chars if any)
   
   Example structure:
   ```
   Anki2/
   └── addons21/
       └── anki_template_designer/
           ├── __init__.py
           ├── template_designer.py
           ├── manifest.json
           ├── ui/
           ├── utils/
           ├── services/
           └── ...
   ```

### Step 3: Restart Anki

**Important:** Completely quit and restart Anki (not just close the window)

### Step 4: Check for errors

When Anki starts:
- If there's an initialization error, you'll see a popup with the error message
- Check Anki's debug console: Tools → Add-ons → [addon name] → View Files → Check debug.log

### Step 5: Look for the menu item

1. Click **Tools** in the main menu
2. Look for **"Template Designer (Visual Editor)"**
3. Click it to open the designer

## Troubleshooting

### Menu item still not appearing?

1. **Check addon is enabled:**
   - Tools → Add-ons
   - Find "Anki Template Designer"
   - Make sure it's checked/enabled

2. **Check for error messages:**
   - If initialization fails, you should see an error popup
   - The error message will tell you what's wrong

3. **Check Anki version:**
   - This addon requires Anki 2.1.45 or later
   - Check: Help → About Anki

4. **Check debug console:**
   - Tools → Add-ons → Anki Template Designer → View Files
   - Look at the terminal/console output when Anki starts

5. **Manual initialization test:**
   - Tools → Add-ons → Anki Template Designer → View Files
   - Open debug console and type:
     ```python
     from . import template_designer
     template_designer.init_addon()
     ```

### Still having issues?

The error message popup (added in latest update) should tell you exactly what's wrong. Common issues:

- **Missing dependencies:** Check requirements.txt
- **PyQt6 vs PyQt5:** Addon uses PyQt6, ensure Anki uses PyQt6
- **Import errors:** Check if all files copied correctly

## What Changed (Latest Fix)

1. **Deferred initialization:** Now waits for profile to load
2. **Error reporting:** Shows popup with any errors
3. **Lazy imports:** Heavy modules only load when needed
4. **Better compatibility:** Works with Anki's addon loading system

The menu should now appear at: **Tools → Template Designer (Visual Editor)**
