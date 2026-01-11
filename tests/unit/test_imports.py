"""
Test imports after fixing circular dependency issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing import fixes...")
print("=" * 60)

try:
    print("\n1. Testing ui.template_converter import...")
    from ui.template_converter import TemplateConverter
    print("   ✅ TemplateConverter imports successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")

try:
    print("\n2. Testing ui.components import...")
    from ui.components import Component, TextFieldComponent
    print("   ✅ Components import successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")

try:
    print("\n3. Testing services.template_service import...")
    # Mock Anki if needed
    if 'aqt' not in sys.modules:
        from unittest.mock import MagicMock
        sys.modules['aqt'] = MagicMock()
        sys.modules['aqt.qt'] = MagicMock()
        sys.modules['aqt.utils'] = MagicMock()
    
    from services.template_service import TemplateService
    print("   ✅ TemplateService imports successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")

try:
    print("\n4. Testing ui.android_studio_dialog import...")
    from ui.android_studio_dialog import AndroidStudioDesignerDialog
    print("   ✅ AndroidStudioDesignerDialog imports successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print("\n" + "=" * 60)
print("Import test complete!")
print("\nIf all ✅, the circular import issue is fixed.")
print("Copy the updated files to Anki and restart.")
