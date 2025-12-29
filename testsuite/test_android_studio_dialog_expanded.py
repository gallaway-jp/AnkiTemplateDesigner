import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from ui.android_studio_dialog import AndroidStudioDesignerDialog

@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def dialog(app, services):
    d = AndroidStudioDesignerDialog(services, parent=None)
    d.show()
    QTest.qWaitForWindowExposed(d)
    yield d
    d.close()

def test_note_type_combo_exists_and_populates(dialog):
    combo = getattr(dialog, 'note_type_combo', None)
    assert combo is not None, "note_type_combo not found in dialog"
    assert combo.count() > 0, "No note types available in combo box"

def test_select_note_type_loads_note_type(dialog):
    combo = dialog.note_type_combo
    combo.setCurrentIndex(0)
    assert dialog.note_type is not None, "No note type loaded after selection"
    # Optionally check status label updates
    status = getattr(dialog, 'status_label', None)
    if status:
        assert dialog.note_type['name'] in status.text()

def test_toolbar_buttons_exist(dialog):
    toolbar = getattr(dialog, 'toolbar', None)
    assert toolbar is not None, "Toolbar not found"
    actions = [a.text() for a in toolbar.actions()]
    # Example: check for common actions
    for expected in ["Save", "Preview", "Settings"]:
        assert any(expected in a for a in actions), f"'{expected}' action missing in toolbar"

def test_design_surface_exists(dialog):
    surface = getattr(dialog, 'design_surface', None)
    assert surface is not None, "Design surface not found"

def test_code_editor_exists(dialog):
    editor = getattr(dialog, 'code_editor', None)
    assert editor is not None, "Code editor not found"

def test_switch_modes(dialog):
    # Simulate switching modes if mode selector exists
    mode_combo = getattr(dialog, 'mode_combo', None)
    if mode_combo:
        for i in range(mode_combo.count()):
            mode_combo.setCurrentIndex(i)
            QTest.qWait(100)
        assert True  # No crash
    else:
        assert True  # Mode combo not present, skip

def test_preview_widget_exists(dialog):
    preview = getattr(dialog, 'preview_widget', None)
    assert preview is not None, "Preview widget not found"

def test_close_dialog(dialog):
    dialog.close()
    assert not dialog.isVisible(), "Dialog did not close properly"
