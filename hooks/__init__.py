"""Hooks module for Anki Template Designer.

This module contains Anki hooks for menu integration and
webview customization.
"""

from .menu import setup_menu, open_designer

__all__ = [
    "setup_menu",
    "open_designer",
]
