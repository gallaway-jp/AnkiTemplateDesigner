"""
Validation script to verify that all Qt widget fixes are in place.
Run this to confirm the addon was updated correctly.
"""

import re
from pathlib import Path


def check_file_for_pattern(filepath: str, pattern: str, description: str) -> bool:
    """Check if a file contains a specific pattern."""
    filepath_obj = Path(filepath)
    
    if not filepath_obj.exists():
        print(f"File not found: {filepath}")
        return False
    
    content = filepath_obj.read_text(encoding='utf-8', errors='ignore')
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description}")
        print(f"   Looking for pattern: {pattern[:50]}...")
        return False


def main():
    """Run all validation checks."""
    addon_path = Path(__file__).parent
    
    print("=" * 70)
    print("ANKI TEMPLATE DESIGNER - QT FIX VALIDATION")
    print("=" * 70)
    print()
    
    checks = [
        # Check 1: toolbar_widget with explicit parent
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r"toolbar_widget\s*=\s*QWidget\(self\)",
            "Toolbar widget has explicit QWidget parent (self)"
        ),
        
        # Check 2: Buttons have parent widget
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r'QPushButton\(["\'].*?["\']\s*,\s*toolbar_widget\)',
            "Buttons created with toolbar_widget parent"
        ),
        
        # Check 3: closeEvent method exists
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r"def closeEvent\(self,\s*event\)",
            "closeEvent method defined for proper cleanup"
        ),
        
        # Check 4: Button signal cleanup in closeEvent
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r"self\.btn_import\.clicked\.disconnect\(\)",
            "Signal cleanup code for btn_import in closeEvent"
        ),
        
        # Check 5: WebView signal cleanup in closeEvent
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r"self\.webview\.loadFinished\.disconnect\(\)",
            "WebView signal cleanup in closeEvent"
        ),
        
        # Check 6: Button references initialized in __init__
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r"self\.btn_import\s*=\s*None\s*\n.*?self\.btn_export\s*=\s*None",
            "Button references initialized to None in __init__"
        ),
        
        # Check 7: QWidget imported
        (
            str(addon_path / "gui" / "designer_dialog.py"),
            r"from\s+.*\s+import\s+.*QWidget",
            "QWidget imported at top of file"
        ),
    ]
    
    results = []
    for filepath, pattern, description in checks:
        result = check_file_for_pattern(filepath, pattern, description)
        results.append(result)
    
    print()
    print("=" * 70)
    print(f"VALIDATION SUMMARY: {sum(results)}/{len(results)} checks passed")
    print("=" * 70)
    
    if all(results):
        print()
        print("🎉 All fixes are in place!")
        print()
        print("Next steps:")
        print("1. Close Anki completely")
        print("2. Delete: ~/.anki/addons21/AnkiTemplateDesigner/")
        print("3. Reinstall the addon using: python install_addon.py")
        print("4. Start Anki and test")
        print()
        return 0
    else:
        print()
        print("⚠️  Some fixes are missing! Please check the output above.")
        print()
        return 1


if __name__ == "__main__":
    exit(main())
