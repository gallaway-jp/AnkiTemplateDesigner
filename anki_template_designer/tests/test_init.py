"""Tests for addon initialization."""

import pytest
import sys
import os

# Add addon to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_version_defined():
    """Test that version is defined."""
    from anki_template_designer import __version__
    assert __version__ == "2.0.0"


def test_author_defined():
    """Test that author is defined."""
    from anki_template_designer import __author__
    assert __author__ == "Anki Template Designer Contributors"


def test_config_loading():
    """Test configuration loading with defaults."""
    from anki_template_designer import _load_config
    config = _load_config()
    assert "debugLogging" in config
    assert "logLevel" in config
    assert config["logLevel"] == "INFO"


def test_addon_dir():
    """Test addon directory detection."""
    from anki_template_designer import _get_addon_dir
    addon_dir = _get_addon_dir()
    assert os.path.isdir(addon_dir)
    assert os.path.exists(os.path.join(addon_dir, "__init__.py"))


def test_config_file_exists():
    """Test that config.json exists."""
    from anki_template_designer import _get_addon_dir
    addon_dir = _get_addon_dir()
    config_path = os.path.join(addon_dir, "config.json")
    assert os.path.exists(config_path)
