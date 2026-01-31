# Minimal Anki Addon - GrapeJS + React + TypeScript UI Testing
from aqt import gui_hooks, mw
from aqt.qt import QDialog, QVBoxLayout, QWebEngineView, QUrl, Qt
import os
import json


class TestUIDialog(QDialog):
    """Test dialog with GrapeJS web editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up webview with GrapeJS"""
        self.setWindowTitle("GrapeJS + React + TypeScript Test")
        
        # Set window flags for standard dialog with minimize/maximize buttons
        flags = Qt.WindowType.Dialog
        flags |= Qt.WindowType.WindowCloseButtonHint
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        flags |= Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        
        # Make window non-modal
        self.setModal(False)
        
        # Get screen resolution and calculate reasonable window size
        screen = mw.screen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Set window to 85% of screen size, but cap at reasonable maximums
        window_width = min(int(screen_width * 0.85), 1600)
        window_height = min(int(screen_height * 0.85), 1000)
        
        # Center on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        
        layout = QVBoxLayout()
        
        # Create web engine view
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)
        
        self.setLayout(layout)
        
        # Load HTML file
        html_path = os.path.join(os.path.dirname(__file__), "index.html")
        file_url = QUrl.fromLocalFile(html_path)
        self.webview.load(file_url)


def open_test_dialog():
    """Open the test dialog"""
    dialog = TestUIDialog(mw)
    dialog.exec()


def setup_menu():
    """Add menu action to open test dialog"""
    action = mw.form.menuTools.addAction("Open GrapeJS Test")
    action.triggered.connect(open_test_dialog)


# Initialize addon when main window is initialized
gui_hooks.main_window_did_init.append(setup_menu)
