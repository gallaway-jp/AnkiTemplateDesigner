"""Main designer dialog with QWebEngineView hosting GrapeJS."""

from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    from aqt.qt import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget,
        QWebEngineView, QWebChannel, QUrl, QSize, Qt, pyqtSlot
    )
    from aqt import mw
    from aqt.theme import theme_manager
    ANKI_AVAILABLE = True
except ImportError:
    # Fallback for testing without Anki
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebChannel import QWebChannel
    from PyQt6.QtCore import QUrl, QSize, Qt, pyqtSlot
    mw = None
    theme_manager = None
    ANKI_AVAILABLE = False

from .webview_bridge import WebViewBridge

# Handle both relative and absolute imports for flexibility
try:
    from ..services.downloader import GrapeJSDownloader
    from ..core.converter import AnkiTemplateParser, AnkiTemplateGenerator
    from ..utils import get_logger
except ImportError:
    # Fallback for when running as standalone module
    try:
        from services.downloader import GrapeJSDownloader
        from core.converter import AnkiTemplateParser, AnkiTemplateGenerator
        from utils import get_logger
    except ImportError:
        # Last resort: create stubs
        class GrapeJSDownloader:
            def assets_exist(self): return True
        class AnkiTemplateParser:
            pass
        class AnkiTemplateGenerator:
            pass
        import logging
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger('designer_dialog')


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
        logger.info("═" * 70)
        logger.info("TemplateDesignerDialog.__init__ STARTING")
        logger.info("═" * 70)
        print("[Template Designer] ╔" + "═" * 68 + "╗")
        print("[Template Designer] ║ Starting Dialog Initialization              " + " " * 21 + "║")
        print("[Template Designer] ╚" + "═" * 68 + "╝")
        
        try:
            logger.info("step 1: Calling super().__init__")
            super().__init__(parent or mw)
            logger.info("step 1: ✓ super().__init__ complete")
            print("[Template Designer] step 1: ✓ super().__init__ complete")
            
            logger.info("step 2: Setting window title")
            self.setWindowTitle("Anki Template Designer")
            logger.info("step 2: ✓ window title set")
            print("[Template Designer] step 2: ✓ window title set")
            
            logger.info("step 3: Setting window flags")
            # Make dialog resizable, minimizable, and maximizable
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
            logger.info("step 3: ✓ window flags set")
            print("[Template Designer] step 3: ✓ window flags set")
            
            logger.info("step 4: Setting minimum size")
            # Set size constraints but allow resizing
            self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
            logger.info("step 4: ✓ minimum size set")
            print("[Template Designer] step 4: ✓ minimum size set")
            
            logger.info("step 5: Setting optimal size")
            # Calculate and set optimal size based on available screen
            self._set_optimal_size()
            logger.info("step 5: ✓ optimal size set")
            print("[Template Designer] step 5: ✓ optimal size set")
            
            logger.info("step 6: Initializing parsers and generators")
            self.parser = AnkiTemplateParser()
            self.generator = AnkiTemplateGenerator()
            logger.info("step 6: ✓ parsers/generators initialized")
            print("[Template Designer] step 6: ✓ parsers/generators initialized")
            
            logger.info("step 7: Creating WebViewBridge")
            self.bridge = WebViewBridge(self)
            logger.info("step 7: ✓ WebViewBridge created")
            print("[Template Designer] step 7: ✓ WebViewBridge created")
            
            logger.info("step 8: Initializing webview reference")
            self.webview: QWebEngineView = None
            logger.info("step 8: ✓ webview reference initialized")
            print("[Template Designer] step 8: ✓ webview reference initialized")
            
            logger.info("step 9: Detecting theme")
            self._theme_mode = self._detect_theme()
            logger.info("step 9: ✓ theme detected: %s", self._theme_mode)
            print(f"[Template Designer] step 9: ✓ theme detected: {self._theme_mode}")
            
            logger.info("step 10: Creating save state tracker")
            self.save_state = SaveState()  # Track save operation state
            logger.info("step 10: ✓ save state tracker created")
            print("[Template Designer] step 10: ✓ save state tracker created")
            
            logger.info("step 11: Initializing button references")
            # Initialize button references for proper cleanup
            self.btn_import = None
            self.btn_export = None
            self.btn_preview = None
            self.btn_save = None
            logger.info("step 11: ✓ button references initialized")
            print("[Template Designer] step 11: ✓ button references initialized")
            
            logger.info("step 12: Calling _setup_ui()")
            self._setup_ui()
            logger.info("step 12: ✓ _setup_ui() complete")
            print("[Template Designer] step 12: ✓ _setup_ui() complete")
            
            logger.info("step 13: Calling _setup_bridge()")
            self._setup_bridge()
            logger.info("step 13: ✓ _setup_bridge() complete")
            print("[Template Designer] step 13: ✓ _setup_bridge() complete")
            
            logger.info("step 14: Calling _load_editor()")
            # IMPORTANT: Load editor FIRST, then check assets async
            # This allows the webview to start rendering immediately
            self._load_editor()
            logger.info("step 14: ✓ _load_editor() initiated")
            print("[Template Designer] step 14: ✓ _load_editor() initiated")
            
            logger.info("step 15: Calling _check_assets_async()")
            # Check assets asynchronously to avoid blocking the UI
            self._check_assets_async()
            logger.info("step 15: ✓ _check_assets_async() initiated")
            print("[Template Designer] step 15: ✓ _check_assets_async() initiated")
            
            logger.info("═" * 70)
            logger.info("TemplateDesignerDialog.__init__ COMPLETE")
            logger.info("═" * 70)
            print("[Template Designer] ╔" + "═" * 68 + "╗")
            print("[Template Designer] ║ Dialog Initialization COMPLETE              " + " " * 18 + "║")
            print("[Template Designer] ╚" + "═" * 68 + "╝")
        except Exception as e:
            logger.error("═" * 70)
            logger.error("EXCEPTION DURING __init__: %s", e, exc_info=True)
            logger.error("═" * 70)
            print("[Template Designer] ╔" + "═" * 68 + "╗")
            print(f"[Template Designer] ║ EXCEPTION: {str(e)[:64]:<64}║")
            print("[Template Designer] ╚" + "═" * 68 + "╝")
            # DO NOT re-raise - just log it and show to user
            # This prevents the error dialog loop
            try:
                from aqt.utils import showWarning
                showWarning(f"Failed to initialize Template Designer:\n\n{str(e)}")
            except:
                print(f"[Template Designer] Failed to show error dialog: {e}")
    
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
    
    def closeEvent(self, event):
        """Handle dialog close - properly disconnect signals and clean up.
        
        This prevents Qt warnings about disconnecting from destroyed signals.
        """
        logger.info("closeEvent() called - cleaning up resources")
        try:
            # Safely disconnect all button signals with specific slot references
            # This avoids wildcard disconnects which cause Qt warnings
            if self.btn_import:
                try:
                    self.btn_import.clicked.disconnect(self._on_import)
                except TypeError:
                    pass  # Signal not connected, that's fine
            
            if self.btn_export:
                try:
                    self.btn_export.clicked.disconnect(self._on_export)
                except TypeError:
                    pass
            
            if self.btn_preview:
                try:
                    self.btn_preview.clicked.disconnect(self._on_preview)
                except TypeError:
                    pass
            
            if self.btn_save:
                try:
                    self.btn_save.clicked.disconnect(self._on_save)
                except TypeError:
                    pass
            
            # Safely disconnect webview signals with specific slot reference
            if self.webview:
                try:
                    self.webview.loadFinished.disconnect(self._on_load_finished)
                except TypeError:
                    pass  # Signal not connected, that's fine
            
            logger.info("All signals disconnected successfully")
        except Exception as e:
            logger.warning("Error during cleanup: %s", e)
        
        # Call parent closeEvent
        super().closeEvent(event)
        logger.info("Dialog closed")
    
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
        logger.info("_setup_ui() starting")
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # WebView for GrapeJS
            self.webview = QWebEngineView(self)
            logger.info("WebEngineView created")
            
            # Enable developer tools and debugging
            settings = self.webview.settings()
            settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
            
            # Enable console messages for debugging
            self.webview.page().javaScriptConsoleMessage = self._on_js_console_message
            logger.info("WebView settings configured")
            
            layout.addWidget(self.webview, stretch=1)
            
            # Bottom toolbar - create parent widget first
            toolbar_widget = QWidget(self)  # Explicit parent
            toolbar = QHBoxLayout(toolbar_widget)
            toolbar.setContentsMargins(0, 0, 0, 0)
            
            # Create buttons with parent widget
            self.btn_import = QPushButton("Import HTML", toolbar_widget)
            self.btn_import.clicked.connect(self._on_import)
            toolbar.addWidget(self.btn_import)
            
            self.btn_export = QPushButton("Export to Anki", toolbar_widget)
            self.btn_export.clicked.connect(self._on_export)
            toolbar.addWidget(self.btn_export)
            
            toolbar.addStretch()
            
            self.btn_preview = QPushButton("Preview Card", toolbar_widget)
            self.btn_preview.clicked.connect(self._on_preview)
            toolbar.addWidget(self.btn_preview)
            
            self.btn_save = QPushButton("Save to Note Type", toolbar_widget)
            self.btn_save.clicked.connect(self._on_save)
            toolbar.addWidget(self.btn_save)
            
            layout.addWidget(toolbar_widget)
            logger.info("UI setup complete - toolbar created with %d buttons", 4)
        except Exception as e:
            logger.error("Failed to setup UI: %s", e, exc_info=True)
            raise
    
    def _setup_bridge(self):
        """Setup QWebChannel for Python-JS communication."""
        logger.info("_setup_bridge() starting")
        print("[Template Designer] _setup_bridge() starting")
        try:
            logger.info("Creating QWebChannel")
            print("[Template Designer]   - Creating QWebChannel...")
            channel = QWebChannel(self.webview.page())
            logger.info("QWebChannel created")
            print("[Template Designer]   ✓ QWebChannel created")
            
            logger.info("Registering bridge object")
            print("[Template Designer]   - Registering bridge object...")
            channel.registerObject("bridge", self.bridge)
            logger.info("Bridge object registered")
            print("[Template Designer]   ✓ Bridge object registered")
            
            logger.info("Setting web channel on page")
            print("[Template Designer]   - Setting web channel on page...")
            self.webview.page().setWebChannel(channel)
            logger.info("Web channel set on page")
            print("[Template Designer]   ✓ Web channel set on page")
            
            logger.info("Setting save callback")
            print("[Template Designer]   - Setting save callback...")
            self.bridge.set_save_callback(self._handle_save)
            logger.info("Save callback set")
            print("[Template Designer]   ✓ Save callback set")
            
            logger.info("Setting preview callback")
            print("[Template Designer]   - Setting preview callback...")
            self.bridge.set_preview_callback(self._handle_preview)
            logger.info("Preview callback set")
            print("[Template Designer]   ✓ Preview callback set")
            
            logger.info("Setting export callback")
            print("[Template Designer]   - Setting export callback...")
            self.bridge.set_export_callback(self._handle_export)
            logger.info("Export callback set")
            print("[Template Designer]   ✓ Export callback set")
            
            logger.info("QWebChannel registered successfully - all callbacks set")
            print("[Template Designer] _setup_bridge() COMPLETE")
        except Exception as e:
            logger.error("Failed to setup bridge: %s", e, exc_info=True)
            print(f"[Template Designer] ERROR in _setup_bridge: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _ensure_assets(self):
        """Ensure GrapeJS assets are downloaded."""
        downloader = GrapeJSDownloader()
        if not downloader.assets_exist():
            try:
                print("[Template Designer] GrapeJS assets missing, downloading...")
                downloader.download_assets()
                print("[Template Designer] ✓ GrapeJS assets downloaded successfully")
            except RuntimeError as e:
                print(f"[Template Designer] ✗ Failed to download GrapeJS assets: {e}")
                self.bridge.showError(f"Failed to download GrapeJS assets: {e}")
        else:
            print("[Template Designer] ✓ GrapeJS assets found")
    
    def _check_assets_async(self):
        """Check and download GrapeJS assets asynchronously to avoid blocking UI."""
        import threading
        
        def check_assets():
            try:
                downloader = GrapeJSDownloader()
                if not downloader.assets_exist():
                    print("[Template Designer] GrapeJS assets missing, downloading in background...")
                    downloader.download_assets()
                    print("[Template Designer] ✓ GrapeJS assets downloaded successfully")
                else:
                    print("[Template Designer] ✓ GrapeJS assets found")
            except Exception as e:
                print(f"[Template Designer] Warning: Could not download assets: {e}")
                # This is not critical - GrapeJS can be served from CDN
        
        # Run asset check in background thread
        asset_thread = threading.Thread(target=check_assets, daemon=True)
        asset_thread.start()
        print("[Template Designer] Asset check started in background thread")
    
    def _load_editor(self):
        """Load the GrapeJS editor HTML."""
        logger.info("_load_editor() starting")
        addon_path = Path(__file__).parent.parent
        # Use built version from dist directory
        html_path = addon_path / "web" / "dist" / "index.html"
        
        logger.info("Loading editor from: %s", html_path)
        logger.info("HTML exists: %s", html_path.exists())
        logger.info("Theme mode: %s", self._theme_mode)
        
        print(f"[Template Designer] Loading editor from: {html_path}")
        print(f"[Template Designer] HTML exists: {html_path.exists()}")
        print(f"[Template Designer] Theme mode: {self._theme_mode}")
        
        if not html_path.exists():
            error_msg = f"Editor HTML not found: {html_path}"
            logger.error("HTML file not found: %s", html_path)
            print(f"[Template Designer] ERROR: {error_msg}")
            self.bridge.showError(error_msg)
            return
        
        # Load HTML file
        url = QUrl.fromLocalFile(str(html_path.resolve()))
        logger.info("Loading URL: %s", url.toString())
        print(f"[Template Designer] Loading URL: {url.toString()}")
        
        # Connect load finished signal for debugging
        self.webview.loadFinished.connect(self._on_load_finished)
        
        self.webview.setUrl(url)
        logger.info("Load started for: %s", url.toString())
        print(f"[Template Designer] Load started for: {url.toString()}")
    
    @pyqtSlot(bool)
    def _on_load_finished(self, ok):
        """Handle page load completion."""
        logger.info("_on_load_finished() called with ok=%s", ok)
        if ok:
            logger.info("Page loaded successfully")
            print("[Template Designer] ✓ Page loaded successfully")
            # Inject theme preference
            self._inject_theme()
        else:
            logger.error("Page load failed!")
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
    
    @pyqtSlot(int, str, int, str)
    def _on_js_console_message(self, level, message, line, source):
        """Handle JavaScript console messages for debugging."""
        level_names = ['Info', 'Warning', 'Error']
        level_name = level_names[min(level, 2)]
        
        log_msg = f"JS {level_name}: {message} (line {line}, source: {source})"
        if level == 2:  # Error
            logger.error(log_msg)
        elif level == 1:  # Warning
            logger.warning(log_msg)
        else:  # Info
            logger.info(log_msg)
        
        print(f"[{log_msg}]")
    
    @pyqtSlot()
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
    
    @pyqtSlot()
    def _on_export(self):
        """Handle export button click - trigger JS to export current state."""
        self.webview.page().runJavaScript(
            "if (window.exportTemplate) window.exportTemplate('html')"
        )
    
    @pyqtSlot()
    def _on_preview(self):
        """Handle preview button click - trigger JS to send preview request."""
        self.webview.page().runJavaScript(
            "if (window.requestPreview) window.requestPreview()"
        )
    
    @pyqtSlot()
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
