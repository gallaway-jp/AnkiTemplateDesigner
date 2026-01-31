"""Tests for designer dialog."""

import pytest
import os
import sys

# Add addon to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_web_path_exists():
    """Test that index.html exists."""
    addon_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    html_path = os.path.join(addon_dir, "web", "index.html")
    
    assert os.path.exists(html_path), f"index.html not found at {html_path}"


def test_constants_valid():
    """Test that size constants are valid."""
    from anki_template_designer.gui.designer_dialog import DesignerDialog
    
    assert DesignerDialog.MIN_WIDTH > 0
    assert DesignerDialog.MIN_HEIGHT > 0
    assert DesignerDialog.MIN_WIDTH <= DesignerDialog.MAX_WIDTH
    assert DesignerDialog.MIN_HEIGHT <= DesignerDialog.MAX_HEIGHT


def test_html_valid():
    """Test that index.html is valid HTML."""
    addon_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    html_path = os.path.join(addon_dir, "web", "index.html")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '<!DOCTYPE html>' in content
    assert '<html' in content
    assert '</html>' in content


def test_html_has_header():
    """Test that index.html has expected header."""
    addon_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    html_path = os.path.join(addon_dir, "web", "index.html")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'Anki Template Designer' in content


def test_gui_module_imports():
    """Test that GUI module can be imported."""
    from anki_template_designer.gui import DesignerDialog
    
    assert DesignerDialog is not None
