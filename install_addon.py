"""
Install Anki Template Designer addon into Anki's addon directory

This script copies the addon to Anki's addon directory for testing.
"""

import shutil
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
SOURCE_DIR = PROJECT_ROOT / "anki_template_designer"  # Source from the new package structure
ANKI_ADDONS_DIR = Path.home() / "AppData/Roaming/Anki2/addons21"
ADDON_NAME = "AnkiTemplateDesigner"
ADDON_DIR = ANKI_ADDONS_DIR / ADDON_NAME

# Files/directories to copy from anki_template_designer/
ITEMS_TO_COPY = [
    "__init__.py",
    "template_designer.py",
    "manifest.json",
    "meta.json",
    "config.json",
    "core/",
    "gui/",
    "hooks/",
    "services/",
    "utils/",
    "web/"
]

def install_addon():
    """Install addon to Anki's addons directory"""
    print(f"\n{'='*70}")
    print("Installing Anki Template Designer Addon")
    print(f"{'='*70}\n")
    
    # Check if Anki addons directory exists
    if not ANKI_ADDONS_DIR.exists():
        print(f"[ERROR] Anki addons directory not found at:")
        print(f"   {ANKI_ADDONS_DIR}")
        print("\nPlease ensure Anki is installed and has been run at least once.")
        return False
    
    print(f"[OK] Anki addons directory found: {ANKI_ADDONS_DIR}")
    
    # Create addon directory
    if ADDON_DIR.exists():
        print(f"\n[WARN] Addon directory already exists: {ADDON_DIR}")
        response = input("  Remove and reinstall? (y/n): ")
        if response.lower() == 'y':
            print(f"  Removing existing addon...")
            shutil.rmtree(ADDON_DIR)
            print(f"  [REMOVED]")
        else:
            print("  Installation cancelled.")
            return False
    
    print(f"\n[INFO] Creating addon directory: {ADDON_DIR}")
    ADDON_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    print(f"\n[INFO] Copying addon files from {SOURCE_DIR}...")
    copied_count = 0
    
    for item_name in ITEMS_TO_COPY:
        src = SOURCE_DIR / item_name
        dst = ADDON_DIR / item_name
        
        if not src.exists():
            print(f"  ⚠ Skipped (not found): {item_name}")
            continue
        
        try:
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                file_count = sum(1 for _ in dst.rglob('*') if _.is_file())
                print(f"  [OK] {item_name}/ ({file_count} files)")
            else:
                shutil.copy2(src, dst)
                print(f"  [OK] {item_name}")
            copied_count += 1
        except Exception as e:
            print(f"  [ERROR] Error copying {item_name}: {e}")
            return False
    
    print(f"\n[SUCCESS] Installation complete!")
    print(f"   {copied_count}/{len(ITEMS_TO_COPY)} items copied")
    print(f"   Location: {ADDON_DIR}")
    
    print(f"\n{'='*70}")
    print("Next Steps:")
    print(f"{'='*70}")
    print("1. Start Anki")
    print("2. Go to Tools > Add-ons")
    print("3. Verify 'Anki Template Designer' appears in the list")
    print("4. Restart Anki if needed")
    print("5. Go to Tools > Anki Template Designer")
    print("6. Test the editor interface")
    print(f"{'='*70}\n")
    
    return True

def uninstall_addon():
    """Uninstall addon from Anki's addons directory"""
    print(f"\n{'='*70}")
    print("Uninstalling Anki Template Designer Addon")
    print(f"{'='*70}\n")
    
    if not ADDON_DIR.exists():
        print(f"[OK] Addon not installed (directory doesn't exist)")
        return True
    
    print(f"[INFO] Addon location: {ADDON_DIR}")
    response = input("\nAre you sure you want to uninstall? (y/n): ")
    
    if response.lower() == 'y':
        shutil.rmtree(ADDON_DIR)
        print(f"[SUCCESS] Addon uninstalled successfully")
        return True
    else:
        print("Uninstall cancelled")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Install/uninstall Anki Template Designer')
    parser.add_argument('action', choices=['install', 'uninstall'], 
                       help='Action to perform')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Force reinstall without prompting')
    
    args = parser.parse_args()
    
    if args.action == 'install':
        if args.force and ADDON_DIR.exists():
            print(f"\n[INFO] Force reinstalling (--force flag specified)")
            print(f"  Removing existing addon...")
            shutil.rmtree(ADDON_DIR)
            print(f"  [REMOVED]")
        success = install_addon()
    else:
        success = uninstall_addon()
    
    sys.exit(0 if success else 1)
