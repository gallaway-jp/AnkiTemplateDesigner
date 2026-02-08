"""Main designer dialog with WebView for GrapeJS editor."""

import os
import sys
import json
import time
import warnings
from typing import Optional, Any
import logging

# Suppress Qt/WebEngine warnings that trigger Anki error dialogs
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

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
        # Suppress Qt warnings before creating dialog
        self._setup_qt_message_handler()
        
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
    
    def _setup_qt_message_handler(self) -> None:
        """Install Qt message handler to suppress warnings."""
        try:
            if HAS_ANKI:
                from aqt.qt import qInstallMessageHandler, QtMsgType
            else:
                from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
            
            def qt_message_handler(msg_type, context, message):
                """Custom Qt message handler that suppresses non-critical warnings."""
                # Only log critical errors, suppress warnings
                if msg_type == QtMsgType.QtCriticalMsg or msg_type == QtMsgType.QtFatalMsg:
                    logger.error(f"Qt Error: {message}")
                elif msg_type == QtMsgType.QtWarningMsg:
                    # Log as debug instead of warning to avoid Anki error dialog
                    logger.debug(f"Qt Warning (suppressed): {message}")
                # Suppress debug and info messages completely
            
            qInstallMessageHandler(qt_message_handler)
            logger.debug("Qt message handler installed")
        except Exception as e:
            logger.debug(f"Could not install Qt message handler: {e}")
    
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
        
        # Initialize template service (kept for legacy compat, not used for Anki templates)
        from ..services.template_service import TemplateService
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_service = TemplateService(addon_dir)
        self._bridge.set_template_service(template_service)
        
        # Get the real Anki NoteTypeService (initialised in __init__.py)
        from ..services.note_type_service import get_note_type_service
        self._note_type_service = get_note_type_service()
        
        # Initialize undo/redo manager
        from ..services.undo_redo_manager import UndoRedoManager
        undo_manager = UndoRedoManager(max_history=100)
        self._bridge.set_undo_manager(undo_manager)
        
        # Initialize error handler
        from ..services.error_handler import ErrorHandler
        error_handler = ErrorHandler()
        self._bridge.set_error_handler(error_handler)
        
        # Register actions → these now talk to Anki's note types
        self._bridge.register_action("save_template", self._on_save_template)
        self._bridge.register_action("load_template", self._on_load_template)
        self._bridge.register_action("get_templates", self._on_get_templates)
        self._bridge.register_action("get_current_template", self._on_get_current_template)
        
        # Connect inspector toggle signal
        self._bridge.inspectorToggleRequested.connect(self._toggle_inspector)
        
        logger.debug("Bridge setup complete with NoteTypeService")
    
    # ------------------------------------------------------------------ #
    #  Template backup helpers                                            #
    # ------------------------------------------------------------------ #

    def _get_backup_dir(self) -> str:
        """Return (and create) the template-backup directory."""
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_dir = os.path.join(addon_dir, "backups", "templates")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def _backup_template(
        self,
        note_type_name: str,
        template_name: str,
        ordinal: int,
        front: str,
        back: str,
        css: str,
    ) -> str:
        """Write a timestamped backup of the current front/back/css.

        Returns the backup folder path.
        """
        ts = time.strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(
            c if c.isalnum() or c in "-_ " else "_" for c in note_type_name
        ).strip()
        safe_tmpl = "".join(
            c if c.isalnum() or c in "-_ " else "_" for c in template_name
        ).strip()
        folder = os.path.join(
            self._get_backup_dir(), f"{safe_name}_{safe_tmpl}_{ts}"
        )
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, "front.html"), "w", encoding="utf-8") as f:
            f.write(front)
        with open(os.path.join(folder, "back.html"), "w", encoding="utf-8") as f:
            f.write(back)
        with open(os.path.join(folder, "style.css"), "w", encoding="utf-8") as f:
            f.write(css)

        logger.info(f"Template backup saved to {folder}")
        return folder

    # ------------------------------------------------------------------ #
    #  Action handlers (connected to handleAction dispatch)               #
    # ------------------------------------------------------------------ #

    def _on_save_template(self, payload: dict) -> dict:
        """Save the front/back HTML + CSS back to Anki, creating a backup first.

        Expected payload keys from JS:
            noteTypeId  – int (the Anki model id)
            ordinal     – int (card template ordinal)
            frontHtml   – str (front HTML from GrapeJS)
            backHtml    – str (back HTML from GrapeJS)
            css         – str (shared CSS from GrapeJS)
        """
        logger.info("Save template requested")
        svc = self._note_type_service
        if svc is None:
            return {"success": False, "error": "NoteTypeService not available"}

        try:
            note_type_id = int(payload.get("noteTypeId", 0))
            ordinal = int(payload.get("ordinal", 0))
            front_html = payload.get("frontHtml", "")
            back_html = payload.get("backHtml", "")
            css = payload.get("css", "")

            # Fetch current state for backup
            nt = svc.get_note_type(note_type_id)
            if nt is None:
                return {"success": False, "error": f"Note type {note_type_id} not found"}

            if ordinal >= len(nt.templates):
                return {"success": False, "error": f"Template ordinal {ordinal} out of range"}

            old_tmpl = nt.templates[ordinal]
            self._backup_template(
                nt.name, old_tmpl.name, ordinal,
                old_tmpl.front, old_tmpl.back, nt.css,
            )

            # Write new values to Anki
            ok_tmpl = svc.update_template(note_type_id, ordinal, front=front_html, back=back_html)
            ok_css = svc.update_css(note_type_id, css)

            if ok_tmpl and ok_css:
                return {"success": True}
            else:
                return {"success": False, "error": "Anki save returned False"}

        except Exception as e:
            logger.error(f"Save template failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _on_load_template(self, payload: dict) -> dict:
        """Load the front/back HTML + CSS for one card template.

        Expected payload:
            noteTypeId – int
            ordinal    – int
        Returns dict with keys: noteTypeId, ordinal, templateName,
            frontHtml, backHtml, css, fields.
        """
        svc = self._note_type_service
        if svc is None:
            return {"error": "NoteTypeService not available"}

        try:
            note_type_id = int(payload.get("noteTypeId", 0))
            ordinal = int(payload.get("ordinal", 0))

            nt = svc.get_note_type(note_type_id)
            if nt is None:
                return {"error": f"Note type {note_type_id} not found"}

            if ordinal >= len(nt.templates):
                return {"error": f"Template ordinal {ordinal} out of range"}

            tmpl = nt.templates[ordinal]
            return {
                "noteTypeId": note_type_id,
                "ordinal": ordinal,
                "noteTypeName": nt.name,
                "templateName": tmpl.name,
                "frontHtml": tmpl.front,
                "backHtml": tmpl.back,
                "css": nt.css,
                "fields": nt.get_field_names(),
            }
        except Exception as e:
            logger.error(f"Load template failed: {e}", exc_info=True)
            return {"error": str(e)}

    def _on_get_templates(self, payload: dict) -> dict:
        """Return the flat list of selectable templates for the dropdown.

        Each entry is:
            { id: "<noteTypeId>:<ordinal>", name: "NoteType > Card 1" }
        """
        svc = self._note_type_service
        if svc is None:
            return {"templates": []}

        try:
            note_types = svc.get_all_note_types()
            templates = []
            for nt in note_types:
                for tmpl in nt.templates:
                    templates.append({
                        "id": f"{nt.id}:{tmpl.ordinal}",
                        "name": f"{nt.name} > {tmpl.name}",
                        "noteTypeId": nt.id,
                        "ordinal": tmpl.ordinal,
                    })
            return {"templates": templates}
        except Exception as e:
            logger.error(f"Get templates failed: {e}", exc_info=True)
            return {"templates": []}

    def _on_get_current_template(self, payload: dict) -> dict:
        """Return the first available template so the editor has something on load."""
        svc = self._note_type_service
        if svc is None:
            return {"templateId": None}

        try:
            note_types = svc.get_all_note_types()
            if not note_types:
                return {"templateId": None}

            nt = note_types[0]
            if not nt.templates:
                return {"templateId": None}

            tmpl = nt.templates[0]
            composite_id = f"{nt.id}:{tmpl.ordinal}"
            return {
                "templateId": composite_id,
                "noteTypeId": nt.id,
                "ordinal": tmpl.ordinal,
                "noteTypeName": nt.name,
                "templateName": tmpl.name,
                "frontHtml": tmpl.front,
                "backHtml": tmpl.back,
                "css": nt.css,
                "fields": nt.get_field_names(),
            }
        except Exception as e:
            logger.error(f"Get current template failed: {e}", exc_info=True)
            return {"templateId": None}
    
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
