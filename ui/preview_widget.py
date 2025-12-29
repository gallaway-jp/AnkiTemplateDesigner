"""
Preview widget for displaying rendered templates
"""

import re
from functools import lru_cache
from aqt.qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QWebEngineView, QSplitter,
    QWebEngineSettings, QTimer
)
from aqt.theme import theme_manager
import html as html_module
from .zoom_and_preview import ZoomController, ResponsivePreviewToolbar

# Pre-compile regex patterns for preview sanitization (performance optimization)
_PREVIEW_SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
_PREVIEW_SCRIPT_SELF_CLOSE = re.compile(r'<script[^>]*/>', re.IGNORECASE)
_PREVIEW_EVENT_HANDLERS = re.compile(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', re.IGNORECASE)


class PreviewWidget(QWidget):
    """Widget for previewing templates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.desktop_renderer = None
        self.ankidroid_renderer = None
        self.current_template = None
        self.current_note = None
        
        # Debounce timer for refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self._do_refresh)
        
        self.setup_ui()
        self._configure_security()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Top controls
        controls = QHBoxLayout()
        
        # Platform selector
        controls.addWidget(QLabel("Platform:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Desktop", "AnkiDroid", "Both"])
        self.platform_combo.currentTextChanged.connect(self.on_platform_changed)
        controls.addWidget(self.platform_combo)
        
        # Theme selector (for AnkiDroid)
        controls.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.refresh_preview)
        controls.addWidget(self.theme_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_preview)
        controls.addWidget(self.refresh_btn)
        
        # Add zoom controller
        self.zoom_controller = ZoomController()
        self.zoom_controller.zoom_changed.connect(self._on_zoom_changed)
        controls.addWidget(self.zoom_controller)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Add responsive preview toolbar
        self.responsive_toolbar = ResponsivePreviewToolbar()
        self.responsive_toolbar.size_changed.connect(self._on_preview_size_changed)
        self.responsive_toolbar.orientation_changed.connect(self._on_orientation_changed)
        layout.addWidget(self.responsive_toolbar)
        
        # Preview area
        self.splitter = QSplitter()
        
        # Desktop preview
        self.desktop_container = QWidget()
        desktop_layout = QVBoxLayout(self.desktop_container)
        desktop_layout.addWidget(QLabel("<b>Desktop Preview</b>"))
        self.desktop_preview = QWebEngineView()
        desktop_layout.addWidget(self.desktop_preview)
        
        # AnkiDroid preview
        self.ankidroid_container = QWidget()
        ankidroid_layout = QVBoxLayout(self.ankidroid_container)
        ankidroid_layout.addWidget(QLabel("<b>AnkiDroid Preview</b>"))
        self.ankidroid_preview = QWebEngineView()
        ankidroid_layout.addWidget(self.ankidroid_preview)
        
        self.splitter.addWidget(self.desktop_container)
        self.splitter.addWidget(self.ankidroid_container)
        
        layout.addWidget(self.splitter)
        
        # Set initial platform
        self.platform_combo.setCurrentText("Both")
    
    def _configure_security(self):
        """Configure security settings for web views"""
        # Configure desktop preview security
        desktop_settings = self.desktop_preview.settings()
        desktop_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        desktop_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        desktop_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
        desktop_settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        
        # Configure AnkiDroid preview security
        ankidroid_settings = self.ankidroid_preview.settings()
        ankidroid_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        ankidroid_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        ankidroid_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
        ankidroid_settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
    
    def on_platform_changed(self, platform):
        """Handle platform selection change"""
        if platform == "Desktop":
            self.desktop_container.show()
            self.ankidroid_container.hide()
        elif platform == "AnkiDroid":
            self.desktop_container.hide()
            self.ankidroid_container.show()
        else:  # Both
            self.desktop_container.show()
            self.ankidroid_container.show()
        
        self.refresh_preview()
    
    def set_renderers(self, desktop_renderer, ankidroid_renderer):
        """Set the renderers for preview"""
        self.desktop_renderer = desktop_renderer
        self.ankidroid_renderer = ankidroid_renderer
    
    def set_template(self, template_dict, note=None, side='front'):
        """Set the template to preview"""
        self.current_template = template_dict
        self.current_note = note
        self.current_side = side
        self.refresh_preview()
    
    def refresh_preview(self):
        """Refresh the preview with debouncing (300ms delay)"""
        # Stop any pending refresh
        self.refresh_timer.stop()
        # Start new timer (debounce)
        self.refresh_timer.start(300)
    
    def _do_refresh(self):
        """Actually perform the refresh (called after debounce)"""
        if not self.current_template:
            return
        
        platform = self.platform_combo.currentText()
        theme = self.theme_combo.currentText().lower()
        side = getattr(self, 'current_side', 'front')
        
        # Render desktop preview
        if platform in ["Desktop", "Both"] and self.desktop_renderer:
            html = self.desktop_renderer.render(
                self.current_template,
                self.current_note,
                side=side
            )
            # Sanitize HTML before rendering
            sanitized_html = self._sanitize_preview_html(html)
            self.desktop_preview.setHtml(sanitized_html)
        
        # Render AnkiDroid preview
        if platform in ["AnkiDroid", "Both"] and self.ankidroid_renderer:
            html = self.ankidroid_renderer.render(
                self.current_template,
                self.current_note,
                side=side,
                theme=theme
            )
            # Sanitize HTML before rendering
            sanitized_html = self._sanitize_preview_html(html)
            self.ankidroid_preview.setHtml(sanitized_html)
    
    def _sanitize_preview_html(self, html_content):
        """Sanitize HTML before rendering in preview (optimized with pre-compiled patterns)"""
        if not html_content:
            return ""
        
        # Use pre-compiled patterns for better performance
        html_content = _PREVIEW_SCRIPT_PATTERN.sub('', html_content)
        html_content = _PREVIEW_SCRIPT_SELF_CLOSE.sub('', html_content)
        html_content = _PREVIEW_EVENT_HANDLERS.sub('', html_content)
        
        return html_content
    
    def _on_zoom_changed(self, zoom_level: float):
        """Handle zoom level change"""
        # Apply zoom to web views
        self.desktop_preview.setZoomFactor(zoom_level)
        self.ankidroid_preview.setZoomFactor(zoom_level)
    
    def _on_preview_size_changed(self, width: int, height: int):
        """Handle preview size change"""
        # Set fixed size for preview containers
        self.desktop_container.setFixedSize(width, height)
        self.ankidroid_container.setFixedSize(width, height)
    
    def _on_orientation_changed(self, orientation: str):
        """Handle orientation change"""
        # Refresh preview with new orientation
        self.refresh_preview()
