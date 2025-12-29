import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# Import the dialog to test
from ui.android_studio_dialog import AndroidStudioDesignerDialog

@pytest.fixture(scope="session")
def app():
    """Ensure a QApplication exists for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_dialog_opens_and_selects_note_type(app, services):
    dialog = AndroidStudioDesignerDialog(services, parent=None)
    dialog.show()
    QTest.qWaitForWindowExposed(dialog)

    # Simulate selecting the first note type
    combo = getattr(dialog, 'note_type_combo', None)
    assert combo is not None, "note_type_combo not found in dialog"
    assert combo.count() > 0, "No note types available in combo box"
    combo.setCurrentIndex(0)
    assert dialog.note_type is not None, "No note type loaded after selection"

    dialog.close()
