"""Menu integration for Template Designer."""

try:
    from aqt import mw
    from aqt.qt import QAction
    ANKI_AVAILABLE = True
except ImportError:
    mw = None
    QAction = None
    ANKI_AVAILABLE = False


def setup_menu():
    """Add Template Designer to Tools menu."""
    if not ANKI_AVAILABLE or not mw:
        print("[Template Designer] Anki not available, skipping menu setup")
        return
    
    action = QAction("Template Designer", mw)
    action.setShortcut("Ctrl+Shift+T")
    action.triggered.connect(open_designer)
    mw.form.menuTools.addAction(action)
    
    print("[Template Designer] Menu item added to Tools menu")


def open_designer():
    """Open the template designer dialog."""
    if not ANKI_AVAILABLE:
        print("[Template Designer] Cannot open - Anki not available")
        return
    
    print("[Template Designer] ╔" + "═" * 66 + "╗")
    print("[Template Designer] ║ open_designer() CALLED                        " + " " * 17 + "║")
    print("[Template Designer] ╚" + "═" * 66 + "╝")
    
    from ..gui.designer_dialog import TemplateDesignerDialog
    
    try:
        print("[Template Designer] Creating TemplateDesignerDialog instance...")
        dialog = TemplateDesignerDialog(mw)
        print("[Template Designer] Dialog instance created successfully")
        print("[Template Designer] Calling dialog.exec() to show dialog...")
        result = dialog.exec()
        print(f"[Template Designer] dialog.exec() returned: {result}")
    except Exception as e:
        from aqt.utils import showWarning
        print(f"[Template Designer] EXCEPTION in open_designer: {e}")
        import traceback
        traceback.print_exc()
        showWarning(f"Failed to open Template Designer: {e}")
        print(f"[Template Designer] Error: {e}")
