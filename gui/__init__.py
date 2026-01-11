"""GUI module for Anki Template Designer.

This module contains the graphical user interface components,
including the GrapeJS designer dialog and preview panel.
"""

from .webview_bridge import WebViewBridge
from .designer_dialog import TemplateDesignerDialog

__all__ = [
    "WebViewBridge",
    "TemplateDesignerDialog",
]
