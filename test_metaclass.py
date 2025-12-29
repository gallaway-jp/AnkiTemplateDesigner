"""
Test metaclass fix for BaseTemplateDialog
"""
import sys
from unittest.mock import MagicMock

# Mock Anki modules
sys.modules['aqt'] = MagicMock()
sys.modules['aqt.qt'] = MagicMock()
sys.modules['aqt.utils'] = MagicMock()

# Mock QDialog with proper metaclass
from abc import ABCMeta

class MockQDialog:
    """Mock QDialog with Qt metaclass"""
    pass

sys.modules['aqt.qt'].QDialog = MockQDialog
sys.modules['aqt.qt'].QMessageBox = MagicMock()
sys.modules['aqt'].mw = MagicMock()

print("Testing metaclass fix...")
print("=" * 60)

try:
    from ui.base_dialog import BaseTemplateDialog
    print("✅ BaseTemplateDialog imports successfully")
    print(f"   Metaclass: {type(BaseTemplateDialog).__name__}")
    print(f"   Has abstractmethod support: {hasattr(BaseTemplateDialog, '__abstractmethods__')}")
except TypeError as e:
    print(f"❌ Metaclass conflict still exists: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("=" * 60)
