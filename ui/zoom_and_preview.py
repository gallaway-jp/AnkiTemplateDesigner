"""
Zoom and responsive preview functionality.

Provides zoom controls and multiple screen size previews for templates.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QLabel, QSlider, QToolBar, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from typing import Dict, Tuple
from config.constants import LayoutDefaults


class ScreenSize:
    """Predefined screen sizes for responsive preview."""
    
    # Mobile devices
    MOBILE_SMALL = ("Mobile Small", 360, 640)    # Small phone
    MOBILE_MEDIUM = ("Mobile Medium", 375, 667)  # iPhone 8
    MOBILE_LARGE = ("Mobile Large", 414, 896)    # iPhone 11
    
    # Tablets
    TABLET_SMALL = ("Tablet Small", 768, 1024)   # iPad Mini
    TABLET_MEDIUM = ("Tablet Medium", 820, 1180) # iPad Air
    TABLET_LARGE = ("Tablet Large", 1024, 1366)  # iPad Pro
    
    # Desktop
    DESKTOP_SMALL = ("Desktop Small", 1366, 768)  # Small laptop
    DESKTOP_MEDIUM = ("Desktop Medium", 1920, 1080) # Full HD
    DESKTOP_LARGE = ("Desktop Large", 2560, 1440)  # 2K
    
    # Anki defaults
    ANKI_DESKTOP = ("Anki Desktop", 800, 600)     # Typical Anki window
    ANKIDROID = ("AnkiDroid", 400, 600)          # AnkiDroid default
    
    CUSTOM = ("Custom", 0, 0)  # User-defined size
    
    @staticmethod
    def get_all_sizes() -> Dict[str, Tuple[str, int, int]]:
        """Get all predefined screen sizes."""
        return {
            'mobile_small': ScreenSize.MOBILE_SMALL,
            'mobile_medium': ScreenSize.MOBILE_MEDIUM,
            'mobile_large': ScreenSize.MOBILE_LARGE,
            'tablet_small': ScreenSize.TABLET_SMALL,
            'tablet_medium': ScreenSize.TABLET_MEDIUM,
            'tablet_large': ScreenSize.TABLET_LARGE,
            'desktop_small': ScreenSize.DESKTOP_SMALL,
            'desktop_medium': ScreenSize.DESKTOP_MEDIUM,
            'desktop_large': ScreenSize.DESKTOP_LARGE,
            'anki_desktop': ScreenSize.ANKI_DESKTOP,
            'ankidroid': ScreenSize.ANKIDROID,
        }
    
    @staticmethod
    def get_mobile_sizes() -> list:
        """Get mobile screen sizes."""
        return [
            ScreenSize.MOBILE_SMALL,
            ScreenSize.MOBILE_MEDIUM,
            ScreenSize.MOBILE_LARGE,
        ]
    
    @staticmethod
    def get_tablet_sizes() -> list:
        """Get tablet screen sizes."""
        return [
            ScreenSize.TABLET_SMALL,
            ScreenSize.TABLET_MEDIUM,
            ScreenSize.TABLET_LARGE,
        ]
    
    @staticmethod
    def get_desktop_sizes() -> list:
        """Get desktop screen sizes."""
        return [
            ScreenSize.DESKTOP_SMALL,
            ScreenSize.DESKTOP_MEDIUM,
            ScreenSize.DESKTOP_LARGE,
        ]


class ZoomController(QWidget):
    """
    Zoom control widget with buttons and slider.
    
    Provides UI for controlling zoom level with zoom in/out buttons,
    reset button, and a slider for precise control.
    """
    
    zoom_changed = pyqtSignal(float)  # Emits new zoom level
    
    def __init__(self, parent=None):
        """
        Initialize zoom controller.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._zoom_level = 1.0
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Zoom out button
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        layout.addWidget(self.zoom_out_btn)
        
        # Zoom slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(int(LayoutDefaults.MIN_ZOOM * 100))
        self.zoom_slider.setMaximum(int(LayoutDefaults.MAX_ZOOM * 100))
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.setTickInterval(20)
        self.zoom_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.zoom_slider)
        
        # Zoom level label
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.zoom_label)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        layout.addWidget(self.zoom_in_btn)
        
        # Reset button
        self.reset_btn = QPushButton("100%")
        self.reset_btn.setToolTip("Reset Zoom (Ctrl+0)")
        self.reset_btn.setFixedWidth(50)
        self.reset_btn.clicked.connect(self.reset_zoom)
        layout.addWidget(self.reset_btn)
    
    def _on_slider_changed(self, value: int):
        """Handle slider value change."""
        new_zoom = value / 100.0
        if new_zoom != self._zoom_level:
            self.set_zoom(new_zoom, emit_signal=True)
    
    def set_zoom(self, zoom_level: float, emit_signal: bool = False):
        """
        Set the zoom level.
        
        Args:
            zoom_level: New zoom level (1.0 = 100%)
            emit_signal: Whether to emit zoom_changed signal
        """
        # Clamp to valid range
        zoom_level = max(LayoutDefaults.MIN_ZOOM,
                        min(LayoutDefaults.MAX_ZOOM, zoom_level))
        
        if zoom_level == self._zoom_level:
            return
        
        self._zoom_level = zoom_level
        
        # Update UI
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(zoom_level * 100))
        self.zoom_slider.blockSignals(False)
        
        self.zoom_label.setText(f"{int(zoom_level * 100)}%")
        
        if emit_signal:
            self.zoom_changed.emit(zoom_level)
    
    def get_zoom(self) -> float:
        """Get current zoom level."""
        return self._zoom_level
    
    def zoom_in(self):
        """Zoom in by zoom step amount."""
        new_zoom = self._zoom_level * LayoutDefaults.ZOOM_STEP
        self.set_zoom(new_zoom, emit_signal=True)
    
    def zoom_out(self):
        """Zoom out by zoom step amount."""
        new_zoom = self._zoom_level / LayoutDefaults.ZOOM_STEP
        self.set_zoom(new_zoom, emit_signal=True)
    
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.set_zoom(1.0, emit_signal=True)


class ResponsivePreviewToolbar(QWidget):
    """
    Toolbar for responsive preview controls.
    
    Provides screen size selection and orientation toggle.
    """
    
    size_changed = pyqtSignal(int, int)  # Emits (width, height)
    orientation_changed = pyqtSignal(str)  # Emits 'portrait' or 'landscape'
    
    def __init__(self, parent=None):
        """
        Initialize responsive preview toolbar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_width = ScreenSize.ANKI_DESKTOP[1]
        self._current_height = ScreenSize.ANKI_DESKTOP[2]
        self._orientation = 'portrait'
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Screen size label
        layout.addWidget(QLabel("Screen Size:"))
        
        # Screen size selector
        self.size_combo = QComboBox()
        self._populate_size_combo()
        self.size_combo.currentIndexChanged.connect(self._on_size_changed)
        layout.addWidget(self.size_combo)
        
        # Orientation toggle
        self.orientation_btn = QPushButton("⟲ Rotate")
        self.orientation_btn.setToolTip("Switch between portrait and landscape")
        self.orientation_btn.clicked.connect(self._toggle_orientation)
        layout.addWidget(self.orientation_btn)
        
        # Dimensions display
        self.dimensions_label = QLabel(f"{self._current_width} × {self._current_height}")
        self.dimensions_label.setMinimumWidth(100)
        self.dimensions_label.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.dimensions_label)
        
        layout.addStretch()
    
    def _populate_size_combo(self):
        """Populate screen size combo box."""
        # Add category headers and sizes
        self.size_combo.addItem("─── Mobile ───")
        self.size_combo.model().item(0).setEnabled(False)
        
        for size in ScreenSize.get_mobile_sizes():
            self.size_combo.addItem(size[0], size)
        
        self.size_combo.addItem("─── Tablet ───")
        self.size_combo.model().item(self.size_combo.count() - 1).setEnabled(False)
        
        for size in ScreenSize.get_tablet_sizes():
            self.size_combo.addItem(size[0], size)
        
        self.size_combo.addItem("─── Desktop ───")
        self.size_combo.model().item(self.size_combo.count() - 1).setEnabled(False)
        
        for size in ScreenSize.get_desktop_sizes():
            self.size_combo.addItem(size[0], size)
        
        self.size_combo.addItem("─── Anki ───")
        self.size_combo.model().item(self.size_combo.count() - 1).setEnabled(False)
        
        self.size_combo.addItem(ScreenSize.ANKI_DESKTOP[0], ScreenSize.ANKI_DESKTOP)
        self.size_combo.addItem(ScreenSize.ANKIDROID[0], ScreenSize.ANKIDROID)
        
        # Set default to Anki Desktop
        self.size_combo.setCurrentIndex(self.size_combo.count() - 2)
    
    def _on_size_changed(self, index: int):
        """Handle screen size selection change."""
        size_data = self.size_combo.itemData(index)
        if size_data and len(size_data) == 3:
            _, width, height = size_data
            self._current_width = width
            self._current_height = height
            self._update_dimensions_label()
            self._emit_size()
    
    def _toggle_orientation(self):
        """Toggle between portrait and landscape orientation."""
        # Swap width and height
        self._current_width, self._current_height = self._current_height, self._current_width
        
        # Update orientation state
        self._orientation = 'landscape' if self._orientation == 'portrait' else 'portrait'
        
        self._update_dimensions_label()
        self._emit_size()
        self.orientation_changed.emit(self._orientation)
    
    def _update_dimensions_label(self):
        """Update the dimensions display label."""
        self.dimensions_label.setText(f"{self._current_width} × {self._current_height}")
    
    def _emit_size(self):
        """Emit the current size."""
        self.size_changed.emit(self._current_width, self._current_height)
    
    def get_current_size(self) -> Tuple[int, int]:
        """Get current screen size."""
        return (self._current_width, self._current_height)
    
    def set_custom_size(self, width: int, height: int):
        """
        Set a custom screen size.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        """
        self._current_width = width
        self._current_height = height
        self._update_dimensions_label()
        
        # Add or update custom entry
        custom_index = self.size_combo.findText("Custom")
        if custom_index >= 0:
            self.size_combo.removeItem(custom_index)
        
        self.size_combo.addItem("Custom", ("Custom", width, height))
        self.size_combo.setCurrentIndex(self.size_combo.count() - 1)
