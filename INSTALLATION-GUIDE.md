# Installation Guide - Anki Template Designer v2.0.0

**Latest Version**: 2.0.0 (Production Release)  
**Release Date**: January 2026  
**License**: MIT

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Windows Installation](#windows-installation)
4. [macOS Installation](#macos-installation)
5. [Linux Installation](#linux-installation)
6. [From Source](#from-source)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)
9. [Uninstallation](#uninstallation)

---

## 🖥️ System Requirements

### Windows
- **OS**: Windows 10 or later
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for installation
- **Anki**: Version 2.1.50 or later
- **.NET Framework**: 4.7.2 or later (included in Windows 10+)

### macOS
- **OS**: macOS 10.13 or later
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for installation
- **Anki**: Version 2.1.50 or later
- **Python**: 3.8+ (included with Anki)

### Linux
- **OS**: Ubuntu 18.04+ or equivalent
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for installation
- **Anki**: Version 2.1.50 or later
- **Python**: 3.8+ (included with Anki)

---

## 📥 Installation Methods

### Quick Start (Recommended)

**For Windows**:
1. Download: `AnkiTemplateDesigner-2.0.0-installer.exe`
2. Run the installer
3. Follow on-screen instructions
4. Restart Anki
5. Done! ✅

**For macOS/Linux**:
1. Download: `AnkiTemplateDesigner-2.0.0.tar.gz`
2. Extract archive
3. Run `./install.sh`
4. Restart Anki
5. Done! ✅

### Portable Version (No Installation)

1. Download: `AnkiTemplateDesigner-2.0.0-portable.zip`
2. Extract to desired location
3. Run `AnkiTemplateDesigner.exe` (Windows) or `./AnkiTemplateDesigner` (macOS/Linux)
4. No installation or restart needed
5. Works immediately ✅

---

## 🪟 Windows Installation

### Method 1: Installer (Recommended)

**Step 1: Download**
- Visit: https://github.com/gallaway-jp/AnkiTemplateDesigner/releases
- Download: `AnkiTemplateDesigner-2.0.0-installer.exe`

**Step 2: Run Installer**
- Double-click the downloaded `.exe` file
- Windows SmartScreen may appear (click "More info" → "Run anyway")
- Accept User Account Control prompt

**Step 3: Follow Installation Wizard**
- Click "Install"
- Select installation directory (default: `C:\Program Files\AnkiTemplateDesigner`)
- Choose to create Start Menu shortcuts (recommended)
- Click "Finish"

**Step 4: Restart Anki**
- Close Anki completely
- Open Anki again
- The addon appears in the menu

**Step 5: Verify Installation**
- Open Anki
- Check: Tools → Add-ons → Anki Template Designer should be listed
- Status should show "Enabled"

### Method 2: Portable (No Installation)

**Step 1: Download**
- Visit: https://github.com/gallaway-jp/AnkiTemplateDesigner/releases
- Download: `AnkiTemplateDesigner-2.0.0-portable.zip`

**Step 2: Extract**
- Right-click → "Extract All"
- Choose desired location (e.g., `C:\Tools\AnkiTemplateDesigner`)
- Wait for extraction to complete

**Step 3: Run**
- Navigate to extracted folder
- Double-click `AnkiTemplateDesigner.exe`
- Application launches immediately

**Step 4: (Optional) Create Shortcut**
- Right-click `AnkiTemplateDesigner.exe`
- Select "Send to" → "Desktop (create shortcut)"
- Shortcut created on desktop

### Method 3: From Anki Addon Directory (Coming Soon)

**Step 1: Get Addon Code**
- Open Anki
- Tools → Add-ons → Get Add-ons
- Paste addon code: `2099209876` (when available)

**Step 2: Install**
- Click "OK"
- Addon installs automatically
- Restart Anki

**Step 3: Verify**
- Tools → Add-ons → Check for "Anki Template Designer"

---

## 🍎 macOS Installation

### Method 1: DMG Installer (Recommended)

**Step 1: Download**
- Visit: https://github.com/gallaway-jp/AnkiTemplateDesigner/releases
- Download: `AnkiTemplateDesigner-2.0.0.dmg`

**Step 2: Open DMG**
- Double-click the downloaded `.dmg` file
- Disk image mounts on desktop

**Step 3: Drag to Applications**
- Drag `AnkiTemplateDesigner.app` to Applications folder
- Wait for copy to complete

**Step 4: Run Application**
- Open Applications folder
- Double-click `AnkiTemplateDesigner.app`
- macOS may ask for security confirmation (click "Open")
- Application launches

**Step 5: Verify Anki Integration**
- Open Anki
- Check: Tools → Add-ons → Should show "Anki Template Designer"
- Status should show "Enabled"

### Method 2: Portable (No Installation)

**Step 1: Download**
- Download: `AnkiTemplateDesigner-2.0.0-portable.tar.gz`

**Step 2: Extract**
- Double-click to extract
- Or in Terminal: `tar -xzf AnkiTemplateDesigner-2.0.0-portable.tar.gz`

**Step 3: Run**
```bash
cd AnkiTemplateDesigner
./AnkiTemplateDesigner
```

---

## 🐧 Linux Installation

### Method 1: Installer Script (Recommended)

**Step 1: Download**
```bash
wget https://github.com/gallaway-jp/AnkiTemplateDesigner/releases/download/v2.0.0/AnkiTemplateDesigner-2.0.0.tar.gz
tar -xzf AnkiTemplateDesigner-2.0.0.tar.gz
cd AnkiTemplateDesigner
```

**Step 2: Install**
```bash
sudo ./install.sh
```

**Step 3: Verify**
```bash
AnkiTemplateDesigner --version
# Output: AnkiTemplateDesigner v2.0.0
```

**Step 4: Run**
```bash
AnkiTemplateDesigner
```

### Method 2: Manual Installation

**Step 1: Install Dependencies**
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python
```

**Step 2: Extract**
```bash
tar -xzf AnkiTemplateDesigner-2.0.0.tar.gz
cd AnkiTemplateDesigner
```

**Step 3: Install Python Dependencies**
```bash
pip3 install -r requirements.txt
```

**Step 4: Run**
```bash
python3 main.py
```

---

## ✅ Verification

### Verify Installation Success

**Windows/macOS/Linux**:
1. Open Anki
2. Go to: Tools → Add-ons
3. Look for "Anki Template Designer"
4. Verify status shows "Enabled"

### Test Basic Functionality

**Step 1: Create Test Card**
- Open Anki
- Create new deck: "Test"
- Create new note type with fields: Front, Back

**Step 2: Launch Template Designer**
- Open Anki
- Tools → Anki Template Designer
- Window opens with editor

**Step 3: Check Features**
- Template editing pane loads
- Components palette visible
- Preview updates in real-time
- Undo/redo works

**Step 4: Export Test**
- Create simple template
- Click "Export"
- Verify HTML exports correctly

---

## 🔧 Troubleshooting

### Issue: Addon doesn't appear in Anki

**Solution 1**: Restart Anki
- Close Anki completely (File → Quit)
- Open Anki again
- Check Tools → Add-ons

**Solution 2**: Verify installation location
- Windows: Check `C:\Program Files\AnkiTemplateDesigner`
- macOS: Check `/Applications/AnkiTemplateDesigner.app`
- Linux: Run `which AnkiTemplateDesigner`

**Solution 3**: Check Anki version
- Open Anki
- Help → About
- Verify version is 2.1.50 or later

### Issue: "Permission Denied" on Linux/macOS

**Solution**:
```bash
# Make executable
chmod +x ./install.sh
chmod +x ./AnkiTemplateDesigner

# Run with sudo if needed
sudo ./install.sh
```

### Issue: Windows Defender/SmartScreen warning

**Solution**:
- This is normal for new software
- Click "More info" → "Run anyway"
- File is digitally signed and safe

### Issue: Application crashes on startup

**Solution 1**: Clear cache
```bash
# Windows
del %APPDATA%\AnkiTemplateDesigner\cache\*

# macOS/Linux
rm -rf ~/.config/AnkiTemplateDesigner/cache/
```

**Solution 2**: Reinstall
- Uninstall completely
- Delete application folder
- Reinstall from fresh download

**Solution 3**: Check logs
- Logs located at: `AnkiTemplateDesigner.log`
- Copy error message and create GitHub issue

### Issue: Template changes not saving to Anki

**Solution 1**: Verify permissions
- Check Anki has write permissions to template folder
- Try "Save As" instead of "Save"

**Solution 2**: Restart bridge
- Close application
- Reopen Anki
- Reopen application

**Solution 3**: Export template
- Use "Export" button to save template
- Manually import to Anki if needed

### Issue: Slow performance

**Solution 1**: Disable animations
- Settings → Appearance → Disable animations

**Solution 2**: Reduce preview size
- Settings → Preview → Reduce resolution

**Solution 3**: Close unused tabs
- Close other Anki windows
- Reduce browser tabs open

**Solution 4**: Increase memory
- Close other applications
- Increase available RAM

---

## 🗑️ Uninstallation

### Windows (Installer Version)

**Step 1: Open Control Panel**
- Control Panel → Programs → Programs and Features

**Step 2: Find Addon**
- Scroll to "Anki Template Designer"
- Click and select "Uninstall"

**Step 3: Confirm**
- Click "Yes" when prompted
- Wait for removal

**Step 4: Cleanup**
- Delete shortcut from Desktop (if exists)
- Delete from Start Menu (if exists)

### Windows (Portable Version)

**Step 1: Stop application**
- Close `AnkiTemplateDesigner.exe`

**Step 2: Delete folder**
- Navigate to extraction location
- Right-click folder → Delete

### macOS

**Step 1: Drag to Trash**
- Open Applications folder
- Drag `AnkiTemplateDesigner.app` to Trash
- Empty Trash

**Step 2: Cleanup**
```bash
# Remove user data
rm -rf ~/.config/AnkiTemplateDesigner
rm -rf ~/Library/Application\ Support/AnkiTemplateDesigner
```

### Linux

**Step 1: Uninstall**
```bash
sudo ./uninstall.sh
# Or manually:
sudo rm /usr/local/bin/AnkiTemplateDesigner
```

**Step 2: Cleanup**
```bash
rm -rf ~/.config/AnkiTemplateDesigner
```

---

## 🎯 Next Steps

1. **Launch Application**: Open Anki and access Tools → Anki Template Designer
2. **Read User Guide**: See `USER-GUIDE.md` for complete feature documentation
3. **Watch Tutorial**: Visit our website for video tutorials (coming soon)
4. **Join Community**: Discuss with other users in Anki forums
5. **Report Issues**: Found a bug? File an issue on GitHub

---

## 📞 Support

### Getting Help
- **Documentation**: https://github.com/gallaway-jp/AnkiTemplateDesigner/wiki
- **Issues**: https://github.com/gallaway-jp/AnkiTemplateDesigner/issues
- **Discussions**: https://github.com/gallaway-jp/AnkiTemplateDesigner/discussions
- **Email**: support@example.com

### Providing Feedback
- Found a bug? File an issue on GitHub
- Have a feature request? Post in Discussions
- Want to contribute? See CONTRIBUTING.md

---

## ⚖️ License & Legal

**License**: MIT  
**Copyright**: 2026 Anki Template Designer Contributors  
**Warranty**: Provided "as is" without warranty (see LICENSE file)

---

*Installation Guide v2.0.0 - January 2026*
