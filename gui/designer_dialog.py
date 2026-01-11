"""Main designer dialog with QWebEngineView hosting GrapeJS."""

from pathlib import Path

try:
    from aqt.qt import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
        QWebEngineView, QWebChannel, QUrl, QSize
    )
    from aqt import mw
    ANKI_AVAILABLE = True
except ImportError:
    # Fallback for testing without Anki
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebChannel import QWebChannel
    from PyQt6.QtCore import QUrl, QSize
    mw = None
    ANKI_AVAILABLE = False

from .webview_bridge import WebViewBridge
from services.downloader import GrapeJSDownloader
from core.converter import AnkiTemplateParser, AnkiTemplateGenerator


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
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        
        self.parser = AnkiTemplateParser()
        self.generator = AnkiTemplateGenerator()
        self.bridge = WebViewBridge(self)
        self.webview: QWebEngineView = None
        
        self._setup_ui()
        self._setup_bridge()
        self._ensure_assets()
        self._load_editor()
    
    def _setup_ui(self):
        """Setup dialog UI with webview and toolbar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # WebView for GrapeJS
        self.webview = QWebEngineView(self)
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
        
        if html_path.exists():
            self.webview.setUrl(QUrl.fromLocalFile(str(html_path)))
        else:
            self.bridge.showError(f"Editor HTML not found: {html_path}")
    
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
        """Handle save callback from JS.
        
        Args:
            grapejs_data: GrapeJS project data
        """
        template = self.generator.generate(grapejs_data)
        
        # Placeholder for saving to Anki
        print(f"Saving template: {template.name}")
        print(f"  Cards: {len(template.cards)}")
        print(f"  Fields: {template.fields}")
        
        if ANKI_AVAILABLE:
            # Real implementation would save to note type
            from aqt.utils import showInfo
            showInfo(f"Template '{template.name}' saved successfully!")
    
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
