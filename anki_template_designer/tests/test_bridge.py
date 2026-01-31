"""Tests for WebView bridge."""

import pytest
import json
import sys
import os

# Add addon to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_bridge_initialization():
    """Test bridge can be created."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    assert bridge is not None
    assert not bridge.is_connected


def test_action_registration():
    """Test action registration."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    
    test_result = {"called": False}
    
    def test_callback(payload):
        test_result["called"] = True
        return {"success": True}
    
    bridge.register_action("test_action", test_callback)
    
    # Simulate calling the action
    result = bridge.handleAction("test_action", "{}")
    data = json.loads(result)
    
    assert data["success"]
    assert test_result["called"]


def test_unknown_action():
    """Test handling of unknown action."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    result = bridge.handleAction("nonexistent", "{}")
    data = json.loads(result)
    
    assert not data["success"]
    assert "error" in data


def test_get_version():
    """Test version retrieval."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    result = bridge.getVersion()
    data = json.loads(result)
    
    assert "version" in data
    assert data["version"] == "2.0.0"


def test_log():
    """Test logging from JS."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    result = bridge.log("Test message")
    data = json.loads(result)
    
    assert data["success"]


def test_action_unregistration():
    """Test action unregistration."""
    from anki_template_designer.gui.webview_bridge import WebViewBridge
    
    bridge = WebViewBridge()
    
    def test_callback(payload):
        return {"success": True}
    
    bridge.register_action("test", test_callback)
    bridge.unregister_action("test")
    
    result = bridge.handleAction("test", "{}")
    data = json.loads(result)
    
    assert not data["success"]
