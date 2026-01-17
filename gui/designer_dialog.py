"""Main designer dialog with QWebEngineView hosting GrapeJS."""

from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    from aqt.qt import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
        QWebEngineView, QWebChannel, QUrl, QSize, Qt
    )
    from aqt import mw
    from aqt.theme import theme_manager
    ANKI_AVAILABLE = True
except ImportError:
    # Fallback for testing without Anki
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebChannel import QWebChannel
    from PyQt6.QtCore import QUrl, QSize, Qt
    mw = None
    theme_manager = None
    ANKI_AVAILABLE = False

from .webview_bridge import WebViewBridge
from ..services.downloader import GrapeJSDownloader
from ..core.converter import AnkiTemplateParser, AnkiTemplateGenerator


@dataclass
class SaveState:
    """Tracks the state of save operations."""
    is_saving: bool = False
    last_save_time: Optional[datetime] = None
    save_success: bool = False
    save_error: Optional[str] = None
    last_saved_data: dict = field(default_factory=dict)
    
    def mark_saving(self):
        """Mark that a save operation has started."""
        self.is_saving = True
        self.save_error = None
        self.save_success = False
    
    def mark_success(self):
        """Mark that a save operation completed successfully."""
        self.is_saving = False
        self.save_success = True
        self.save_error = None
        self.last_save_time = datetime.now()
    
    def mark_error(self, error_message: str):
        """Mark that a save operation failed.
        
        Args:
            error_message: Description of the error
        """
        self.is_saving = False
        self.save_success = False
        self.save_error = error_message


class TemplateDesignerDialog(QDialog):
    """Main template designer dialog with embedded GrapeJS editor."""
    
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    
    def __init__(self, parent=None):
        """Initialize designer dialog.
        
        Args:
            parent: Parent widget (defaults to Anki main window if available)
        """
        super().__init__(parent or mw)
        self.setWindowTitle("Anki Template Designer")
        
        # Make dialog resizable, minimizable, and maximizable
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Set size constraints but allow resizing
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        # Calculate and set optimal size based on available screen
        self._set_optimal_size()
        
        self.parser = AnkiTemplateParser()
        self.generator = AnkiTemplateGenerator()
        self.bridge = WebViewBridge(self)
        self.webview: QWebEngineView = None
        self._theme_mode = self._detect_theme()
        self.save_state = SaveState()  # Track save operation state
        
        self._setup_ui()
        self._setup_bridge()
        self._ensure_assets()
        self._load_editor()
    
    def _set_optimal_size(self):
        """Calculate and set optimal dialog size based on available screen."""
        screen = self.screen()
        available_geom = screen.availableGeometry()
        
        # Use 85-90% of available space
        # Minimum 1200x800, Maximum reasonable size
        width = max(
            self.MIN_WIDTH,
            min(1400, int(available_geom.width() * 0.90))
        )
        height = max(
            self.MIN_HEIGHT,
            min(900, int(available_geom.height() * 0.85))
        )
        
        self.resize(QSize(width, height))
        
        # Center dialog on screen
        center_point = available_geom.center()
        self.move(
            center_point.x() - width // 2,
            center_point.y() - height // 2
        )
        
        print(f"[Designer] Dialog sized to {width}x{height}")
        print(f"[Designer] Screen: {available_geom.width()}x{available_geom.height()}")
    
    def _detect_theme(self):
        """Detect if Anki is using light or dark theme.
        
        Returns:
            str: 'dark' or 'light'
        """
        if ANKI_AVAILABLE and theme_manager:
            # Check Anki's theme
            if hasattr(theme_manager, 'night_mode'):
                return 'dark' if theme_manager.night_mode else 'light'
            # Fallback to checking theme name
            theme_name = str(theme_manager.default_palette).lower()
            if 'dark' in theme_name or 'night' in theme_name:
                return 'dark'
        return 'light'
    
    def _setup_ui(self):
        """Setup dialog UI with webview and toolbar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # WebView for GrapeJS
        self.webview = QWebEngineView(self)
        
        # Enable developer tools and debugging
        settings = self.webview.settings()
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
        
        # Enable console messages for debugging
        self.webview.page().javaScriptConsoleMessage = self._on_js_console_message
        
        layout.addWidget(self.webview, stretch=1)
        
        # Bottom toolbar
        toolbar = QHBoxLayout()
        
        self.btn_import = QPushButton("Import HTML")
        self.btn_import.clicked.connect(self._on_import)
        toolbar.addWidget(self.btn_import)
        
        self.btn_export = QPushButton("Export to Anki")
        self.btn_export.clicked.connect(self._on_export)
        toolbar.addWidget(self.btn_export)
        
        toolbar.addStretch()
        
        self.btn_preview = QPushButton("Preview Card")
        self.btn_preview.clicked.connect(self._on_preview)
        toolbar.addWidget(self.btn_preview)
        
        self.btn_save = QPushButton("Save to Note Type")
        self.btn_save.clicked.connect(self._on_save)
        toolbar.addWidget(self.btn_save)
        
        layout.addLayout(toolbar)
    
    def _setup_bridge(self):
        """Setup QWebChannel for Python-JS communication."""
        channel = QWebChannel(self.webview.page())
        channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(channel)
        
        # Set callbacks
        self.bridge.set_save_callback(self._handle_save)
        self.bridge.set_preview_callback(self._handle_preview)
        self.bridge.set_export_callback(self._handle_export)
    
    def _ensure_assets(self):
        """Ensure GrapeJS assets are downloaded."""
        downloader = GrapeJSDownloader()
        if not downloader.assets_exist():
            try:
                downloader.download_assets()
            except RuntimeError as e:
                self.bridge.showError(f"Failed to download GrapeJS assets: {e}")
    
    def _load_editor(self):
        """Load the GrapeJS editor HTML."""
        addon_path = Path(__file__).parent.parent
        html_path = addon_path / "web" / "index.html"
        
        print(f"[Template Designer] Loading editor from: {html_path}")
        print(f"[Template Designer] Theme mode: {self._theme_mode}")
        
        if not html_path.exists():
            error_msg = f"Editor HTML not found: {html_path}"
            print(f"[Template Designer] ERROR: {error_msg}")
            self.bridge.showError(error_msg)
            return
        
        # Load HTML file
        url = QUrl.fromLocalFile(str(html_path.resolve()))
        print(f"[Template Designer] Loading URL: {url.toString()}")
        self.webview.setUrl(url)
        
        # Connect load finished signal for debugging
        self.webview.loadFinished.connect(self._on_load_finished)
    
    def _on_load_finished(self, ok):
        """Handle page load completion."""
        if ok:
            print("[Template Designer] ✓ Page loaded successfully")
            # Inject theme preference
            self._inject_theme()
        else:
            print("[Template Designer] ✗ Page load failed!")
            error_msg = "Failed to load editor. Check console for details."
            if ANKI_AVAILABLE:
                from aqt.utils import showWarning
                showWarning(error_msg)
    
    def _inject_theme(self):
        """Inject theme preference into the editor."""
        js_code = f"""
            if (typeof window.setTheme === 'function') {{
                window.setTheme('{self._theme_mode}');
            }} else {{
                document.body.setAttribute('data-theme', '{self._theme_mode}');
                console.log('Theme set to: {self._theme_mode}');
            }}
        """
        self.webview.page().runJavaScript(js_code)
    
    def _on_js_console_message(self, level, message, line, source):
        """Handle JavaScript console messages for debugging."""
        level_names = ['Info', 'Warning', 'Error']
        level_name = level_names[min(level, 2)]
        print(f"[JS {level_name}] {message} (line {line})")
        if level == 2:  # Error
            print(f"  Source: {source}")
    
    def _on_import(self):
        """Handle import button click - import existing Anki template."""
        if not ANKI_AVAILABLE:
            self.bridge.showError("Import requires Anki")
            return
        
        # Placeholder for import dialog
        # Real implementation would show file picker or note type selector
        html = "<div class='card'>{{Front}}</div>"
        css = ".card { padding: 20px; }"
        
        grapejs_data = self.parser.parse(html, css)
        self.bridge.load_template(grapejs_data)
    
    def _on_export(self):
        """Handle export button click - trigger JS to export current state."""
        self.webview.page().runJavaScript(
            "if (window.exportTemplate) window.exportTemplate('html')"
        )
    
    def _on_preview(self):
        """Handle preview button click - trigger JS to send preview request."""
        self.webview.page().runJavaScript(
            "if (window.requestPreview) window.requestPreview()"
        )
    
    def _on_save(self):
        """Handle save button click - trigger JS to save project."""
        self.webview.page().runJavaScript(
            "if (window.saveProject) window.saveProject()"
        )
    
    def _handle_save(self, grapejs_data: dict):
        """Handle save callback from JS with user feedback.
        
        Args:
            grapejs_data: GrapeJS project data
        """
        try:
            # Mark save as in progress
            self.save_state.mark_saving()
            self._notify_save_start()
            
            # Validate template data
            if not grapejs_data:
                raise ValueError("No template data to save")
            
            if 'html' not in grapejs_data:
                raise ValueError("Template missing HTML content")
            
            # Generate template
            template = self.generator.generate(grapejs_data)
            
            # Store the successfully saved data
            self.save_state.last_saved_data = grapejs_data.copy()
            
            print(f"[Save] Saving template: {template.name}")
            print(f"[Save]   Cards: {len(template.cards)}")
            print(f"[Save]   Fields: {template.fields}")
            
            # Mark save as successful
            self.save_state.mark_success()
            
            if ANKI_AVAILABLE:
                from aqt.utils import showInfo
                showInfo(f"Template '{template.name}' saved successfully!")
            
            # Notify JS that save was successful
            self._notify_save_success(template.name)
            
        except ValueError as e:
            # Validation errors
            error_msg = f"Template validation failed: {str(e)}"
            self.save_state.mark_error(error_msg)
            print(f"[Save] Error: {error_msg}")
            self._notify_save_error(error_msg)
            
            if ANKI_AVAILABLE:
                from aqt.utils import showWarning
                showWarning(error_msg)
        
        except Exception as e:
            # Unexpected errors
            error_msg = f"Failed to save template: {str(e)}"
            self.save_state.mark_error(error_msg)
            print(f"[Save] Error: {error_msg}")
            self._notify_save_error(error_msg)
            
            if ANKI_AVAILABLE:
                from aqt.utils import showWarning
                showWarning(error_msg)
    
    def _notify_save_start(self):
        """Notify JS that save operation is starting."""
        try:
            self.bridge.execute_javascript(
                "if (window.notifySaveStart) window.notifySaveStart();"
            )
        except Exception as e:
            print(f"[Save] Failed to notify save start: {e}")
    
    def _notify_save_success(self, template_name: str):
        """Notify JS that save operation succeeded.
        
        Args:
            template_name: Name of saved template
        """
        try:
            js_code = f"""
            if (window.notifySaveSuccess) {{
                window.notifySaveSuccess('{template_name}');
            }}
            """
            self.bridge.execute_javascript(js_code)
        except Exception as e:
            print(f"[Save] Failed to notify save success: {e}")
    
    def _notify_save_error(self, error_message: str):
        """Notify JS that save operation failed.
        
        Args:
            error_message: Description of the error
        """
        try:
            # Escape quotes in error message
            safe_error = error_message.replace('"', '\\"').replace("'", "\\'")
            js_code = f"""
            if (window.notifySaveError) {{
                window.notifySaveError('{safe_error}');
            }}
            """
            self.bridge.execute_javascript(js_code)
        except Exception as e:
            print(f"[Save] Failed to notify save error: {e}")
    
    def _handle_preview(self, grapejs_data: dict):
        """Handle preview callback from JS.
        
        Args:
            grapejs_data: GrapeJS project data
        """
        template = self.generator.generate(grapejs_data)
        
        # Placeholder for preview dialog
        print(f"Previewing template: {template.name}")
        
        if template.cards:
            card = template.cards[0]
            front_html = self.generator.components_to_html(card.front_components)
            print(f"Front HTML:\n{front_html}")
    
    def _handle_export(self, format_type: str, grapejs_data: dict):
        """Handle export callback from JS.
        
        Args:
            format_type: Export format ('html', 'json', etc.)
            grapejs_data: GrapeJS project data
        """
        template = self.generator.generate(grapejs_data)
        
        print(f"Exporting template as {format_type}: {template.name}")
        
        if format_type == "html":
            # Generate HTML/CSS for all cards
            for card in template.cards:
                front_html = self.generator.components_to_html(card.front_components)
                back_html = self.generator.components_to_html(card.back_components)
                print(f"\n{card.name} Front:\n{front_html}")
                print(f"\n{card.name} Back:\n{back_html}")
            
            print(f"\nCSS:\n{template.css}")
    
    def load_existing_template(self, html: str, css: str = ""):
        """Load an existing Anki template into the editor.
        
        Args:
            html: Template HTML content
            css: Template CSS content
        """
        grapejs_data = self.parser.parse(html, css)
        self.bridge.load_template(grapejs_data)
