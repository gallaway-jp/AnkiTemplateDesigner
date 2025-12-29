"""
Debug script to test addon initialization without Anki
This helps identify import errors
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Anki Template Designer Initialization")
print("=" * 60)

print("\n1. Testing basic imports...")
try:
    from aqt.qt import QAction
    print("   ✅ aqt.qt imports work (QAction)")
except ImportError as e:
    print(f"   ❌ aqt.qt import failed: {e}")
    print("   Note: This is expected outside Anki environment")

print("\n2. Testing template_designer.py imports...")
try:
    # Mock the Anki modules if needed
    if 'aqt' not in sys.modules:
        print("   Creating mock Anki modules...")
        from unittest.mock import MagicMock
        sys.modules['aqt'] = MagicMock()
        sys.modules['aqt.qt'] = MagicMock()
        sys.modules['aqt.utils'] = MagicMock()
        sys.modules['aqt'].mw = MagicMock()
        sys.modules['aqt'].gui_hooks = MagicMock()
    
    # Now try importing template_designer
    import template_designer
    print("   ✅ template_designer.py imports successfully")
    
    # Check if key functions exist
    if hasattr(template_designer, 'init_addon'):
        print("   ✅ init_addon() function exists")
    else:
        print("   ❌ init_addon() function missing")
    
    if hasattr(template_designer, 'setup_menu'):
        print("   ✅ setup_menu() function exists")
    else:
        print("   ❌ setup_menu() function missing")
        
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testing UI module imports...")
try:
    # Check if ui modules can be imported
    from ui import components
    print("   ✅ ui.components imports successfully")
except Exception as e:
    print(f"   ❌ ui.components import failed: {e}")

try:
    from ui import template_converter
    print("   ✅ ui.template_converter imports successfully")
except Exception as e:
    print(f"   ❌ ui.template_converter import failed: {e}")

print("\n4. Testing service module imports...")
try:
    from services import ServiceContainer
    print("   ✅ services.ServiceContainer imports successfully")
except Exception as e:
    print(f"   ❌ services import failed: {e}")

print("\n5. Testing utils module imports...")
try:
    from utils import SecurityValidator
    print("   ✅ utils.SecurityValidator imports successfully")
except Exception as e:
    print(f"   ❌ utils import failed: {e}")

print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)
print("If all ✅ (except aqt imports outside Anki), the addon should work.")
print("If you see ❌, check the error messages above.")
print("\nTo install in Anki:")
print("1. Copy this folder to: %APPDATA%\\Anki2\\addons21\\")
print("2. Restart Anki")
print("3. Check Tools menu for 'Template Designer (Visual Editor)'")
print("=" * 60)
