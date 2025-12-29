# Anki Template Designer - Requirements

## Anki Version
- Anki 2.1.45 or higher

## Python Version
- Python 3.9+ (included with Anki)

## Dependencies
All dependencies are included with Anki:
- PyQt6 (or PyQt5 depending on Anki version)
- aqt (Anki Qt library)

## Optional Dependencies
- AnkiJSApi add-on (recommended for enhanced JavaScript support)

## Development Dependencies
For development and testing:
- pytest (for unit tests)
- black (for code formatting)
- pylint (for linting)

## Installation

### For Users
1. Download the `.ankiaddon` file
2. Open Anki
3. Go to Tools → Add-ons → Install from file
4. Select the downloaded file
5. Restart Anki

### For Developers
1. Clone this repository
2. Create a symlink from Anki's addons21 folder to this directory:
   ```
   # Windows
   mklink /D "%APPDATA%\Anki2\addons21\AnkiTemplateDesigner" "D:\Development\Python\AnkiTemplateDesigner"
   
   # Linux/Mac
   ln -s /path/to/AnkiTemplateDesigner ~/.local/share/Anki2/addons21/
   ```
3. Restart Anki

## Platform Support
- ✅ Windows
- ✅ macOS
- ✅ Linux
- ✅ Anki Desktop (primary target)
- ⚠️ AnkiDroid (preview simulation only, not a native AnkiDroid add-on)
