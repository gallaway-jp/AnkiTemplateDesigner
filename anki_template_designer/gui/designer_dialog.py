"""Main designer dialog with WebView for GrapeJS editor."""

import os
from typing import Optional, Any
import logging

try:
    from aqt.qt import (
        QDialog, QVBoxLayout, QWebEngineView, QUrl, 
        QSize, Qt, QScreen
    )
    from aqt import mw
    HAS_ANKI = True
except ImportError:
    from PyQt6.QtWidgets import QDialog, QVBoxLayout
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl, QSize, Qt
    from PyQt6.QtGui import QScreen
    mw = None
    HAS_ANKI = False

from .webview_bridge import WebViewBridge

logger = logging.getLogger("anki_template_designer.gui.designer_dialog")


class DesignerDialog(QDialog):
    """Main template designer dialog with embedded WebView editor.
    
    Hosts a QWebEngineView that loads the GrapeJS-based template editor.
    Supports responsive sizing based on screen dimensions.
    
    Attributes:
        MIN_WIDTH: Minimum dialog width in pixels.
        MIN_HEIGHT: Minimum dialog height in pixels.
        DEFAULT_WIDTH_RATIO: Default width as ratio of screen width.
        DEFAULT_HEIGHT_RATIO: Default height as ratio of screen height.
    """
    
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    DEFAULT_WIDTH_RATIO = 0.85
    DEFAULT_HEIGHT_RATIO = 0.85
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """Initialize the designer dialog.
        
        Args:
            parent: Parent widget, defaults to Anki main window.
        """
        super().__init__(parent or mw)
        
        self._webview: Optional[QWebEngineView] = None
        self._bridge: Optional[WebViewBridge] = None
        self._inspector_dialog: Optional[QDialog] = None
        self._inspector_view: Optional[QWebEngineView] = None
        
        self._setup_window()
        self._setup_ui()
        self._setup_inspector()
        self._load_editor()
        
        logger.debug("DesignerDialog initialized")
    
    def _setup_window(self) -> None:
        """Configure window properties and sizing."""
        self.setWindowTitle("Anki Template Designer")
        
        # Window flags for standard dialog behavior
        flags = Qt.WindowType.Window
        flags |= Qt.WindowType.WindowCloseButtonHint
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        flags |= Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        
        # Non-modal allows Anki interaction
        self.setModal(False)
        
        # Set size constraints
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        
        # Calculate optimal size
        self._set_optimal_size()
    
    def _get_screen(self) -> Optional[QScreen]:
        """Get the screen for size calculations.
        
        Returns:
            QScreen object or None if unavailable.
        """
        if mw is not None:
            return mw.screen()
        return None
    
    def _set_optimal_size(self) -> None:
        """Set optimal window size based on screen dimensions."""
        screen = self._get_screen()
        
        if screen is None:
            # Fallback to minimum size
            self.resize(self.MIN_WIDTH, self.MIN_HEIGHT)
            return
        
        geometry = screen.geometry()
        screen_width = geometry.width()
        screen_height = geometry.height()
        
        # Calculate size as percentage of screen
        width = int(screen_width * self.DEFAULT_WIDTH_RATIO)
        height = int(screen_height * self.DEFAULT_HEIGHT_RATIO)
        
        # Apply constraints
        width = max(self.MIN_WIDTH, min(width, self.MAX_WIDTH))
        height = max(self.MIN_HEIGHT, min(height, self.MAX_HEIGHT))
        
        # Center on screen
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.setGeometry(x, y, width, height)
        logger.debug(f"Dialog size set to {width}x{height} at ({x}, {y})")
    
    def _setup_ui(self) -> None:
        """Set up the user interface with WebView."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins for full WebView
        
        # Create WebEngine view
        self._webview = QWebEngineView(self)
        layout.addWidget(self._webview)
        
        self.setLayout(layout)
        
        # Set up bridge after webview creation
        self._setup_bridge()
    
    def _setup_inspector(self) -> None:
        """Set up the WebView inspector in a separate window.
        
        Creates a dev tools inspector that can be toggled with Ctrl+Shift+I.
        """
        logger.debug("Setting up inspector")
        if self._webview is None:
            logger.debug("_webview is None, aborting inspector setup")
            return
        
        try:
            # Create inspector dialog
            self._inspector_dialog = QDialog(self)
            self._inspector_dialog.setWindowTitle("Template Designer - Inspector")
            self._inspector_dialog.resize(900, 600)
            
            # Window flags for independent window
            flags = Qt.WindowType.Window
            flags |= Qt.WindowType.WindowCloseButtonHint
            flags |= Qt.WindowType.WindowMinimizeButtonHint
            flags |= Qt.WindowType.WindowMaximizeButtonHint
            self._inspector_dialog.setWindowFlags(flags)
            
            # Create inspector webview
            inspector_layout = QVBoxLayout(self._inspector_dialog)
            inspector_layout.setContentsMargins(0, 0, 0, 0)
            self._inspector_view = QWebEngineView(self._inspector_dialog)
            inspector_layout.addWidget(self._inspector_view)
            
            # Connect inspector to main webview
            page = self._webview.page()
            if page:
                page.setDevToolsPage(self._inspector_view.page())
            
            logger.debug("Inspector setup complete. Use F12 to toggle.")
            
        except Exception as e:
            logger.warning(f"Could not setup inspector: {e}")
    
    def keyPressEvent(self, event: Any) -> None:
        """Handle key press events at Qt level.
        
        F12 toggles the inspector window (handled here to bypass WebView).
        """
        if event.key() == Qt.Key.Key_F12:
            self._toggle_inspector()
            event.accept()
            return
        super().keyPressEvent(event)
    
    def _toggle_inspector(self) -> None:
        """Toggle the inspector window visibility."""
        if self._inspector_dialog is None:
            return
        
        if self._inspector_dialog.isVisible():
            self._inspector_dialog.hide()
        else:
            self._inspector_dialog.show()
            self._inspector_dialog.raise_()
            self._inspector_dialog.activateWindow()
    
    def _get_web_path(self) -> str:
        """Get the path to the web content.
        
        Returns:
            Absolute path to the index.html file.
        """
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(addon_dir, "web", "index.html")
    
    def _load_editor(self) -> None:
        """Load the editor HTML into the WebView."""
        if self._webview is None:
            logger.error("WebView not initialized")
            return
        
        html_path = self._get_web_path()
        
        if not os.path.exists(html_path):
            logger.error(f"Editor HTML not found: {html_path}")
            self._show_error("Editor files not found. Please reinstall the addon.")
            return
        
        file_url = QUrl.fromLocalFile(html_path)
        self._webview.load(file_url)
        logger.debug(f"Loading editor from: {html_path}")
    
    def _show_error(self, message: str) -> None:
        """Display an error message in the WebView.
        
        Args:
            message: Error message to display.
        """
        if self._webview is None:
            return
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }}
                .error {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }}
                .error h2 {{
                    color: #d32f2f;
                    margin-top: 0;
                }}
                .error p {{
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>Error</h2>
                <p>{message}</p>
            </div>
        </body>
        </html>
        """
        self._webview.setHtml(error_html)
    
    def closeEvent(self, event: Any) -> None:
        """Handle dialog close event.
        
        Args:
            event: Close event object.
        """
        logger.debug("DesignerDialog closing")
        # Clean up WebView
        if self._webview is not None:
            self._webview.setUrl(QUrl("about:blank"))
        
        super().closeEvent(event)
    
    def _setup_bridge(self) -> None:
        """Set up the WebView bridge for Python-JS communication."""
        if self._webview is None:
            logger.error("Cannot setup bridge: webview not initialized")
            return
        
        self._bridge = WebViewBridge(self)
        self._bridge.setup_channel(self._webview)
        
        # Initialize template service
        from ..services.template_service import TemplateService
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_service = TemplateService(addon_dir)
        self._bridge.set_template_service(template_service)
        
        # Initialize undo/redo manager
        from ..services.undo_redo_manager import UndoRedoManager
        undo_manager = UndoRedoManager(max_history=100)
        self._bridge.set_undo_manager(undo_manager)
        
        # Initialize error handler
        from ..services.error_handler import ErrorHandler
        error_handler = ErrorHandler()
        self._bridge.set_error_handler(error_handler)
        
        # Register default actions
        self._bridge.register_action("save_template", self._on_save_template)
        self._bridge.register_action("load_template", self._on_load_template)
        
        # Connect inspector toggle signal
        self._bridge.inspectorToggleRequested.connect(self._toggle_inspector)
        
        logger.debug("Bridge setup complete with template service, undo manager, and error handler")
    
    def _on_save_template(self, payload: dict) -> dict:
        """Handle save template action from JS.
        
        Args:
            payload: Template data to save.
            
        Returns:
            Result dictionary.
        """
        logger.info("Save template requested")
        # Actual implementation in Plan 06
        return {"saved": True}
    
    def _on_load_template(self, payload: dict) -> dict:
        """Handle load template action from JS.
        
        Args:
            payload: Contains template_id.
            
        Returns:
            Template data.
        """
        template_id = payload.get("template_id")
        logger.info(f"Load template requested: {template_id}")
        # Actual implementation in Plan 06
        return {"template_id": template_id, "content": ""}
    
    @property
    def bridge(self) -> Optional[WebViewBridge]:
        """Get the WebView bridge.
        
        Returns:
            The WebViewBridge instance.
        """
        return self._bridge
    
    @property
    def webview(self) -> Optional[QWebEngineView]:
        """Get the WebView widget.
        
        Returns:
            The QWebEngineView instance.
        """
        return self._webview
