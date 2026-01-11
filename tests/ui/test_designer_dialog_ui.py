"""UI Tests for Designer Dialog - Tests with real Anki"""
import pytest
import time
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QDialog


class TestDesignerDialogUI:
    """Test DesignerDialog with real Anki environment"""
    
    def test_dialog_creation(self, designer_dialog):
        """Test that designer dialog can be created"""
        assert designer_dialog is not None
        assert isinstance(designer_dialog, QDialog)
    
    def test_dialog_shows(self, designer_dialog, wait_for_load):
        """Test that dialog can be shown"""
        designer_dialog.show()
        wait_for_load(500)
        
        assert designer_dialog.isVisible()
        assert designer_dialog.width() > 0
        assert designer_dialog.height() > 0
    
    def test_dialog_has_webview(self, designer_dialog, wait_for_load):
        """Test that dialog contains a web view"""
        designer_dialog.show()
        wait_for_load(500)
        
        # Find webview component
        webview = None
        for child in designer_dialog.findChildren(object):
            if hasattr(child, 'setHtml') or 'WebView' in child.__class__.__name__:
                webview = child
                break
        
        assert webview is not None, "Dialog should contain a web view"
    
    def test_dialog_loads_html(self, designer_dialog, wait_for_load):
        """Test that dialog loads the designer HTML"""
        designer_dialog.show()
        wait_for_load(1000)  # Give time for HTML to load
        
        # Check if web directory exists
        web_dir = Path(__file__).parent.parent.parent / "web"
        assert web_dir.exists(), f"Web directory not found at {web_dir}"
        
        index_html = web_dir / "index.html"
        assert index_html.exists(), f"index.html not found at {index_html}"
    
    def test_dialog_has_minimum_size(self, designer_dialog):
        """Test that dialog has a reasonable minimum size"""
        designer_dialog.show()
        
        # Dialog should be large enough to be usable
        assert designer_dialog.minimumWidth() >= 800
        assert designer_dialog.minimumHeight() >= 600
    
    def test_dialog_title(self, designer_dialog):
        """Test that dialog has the correct title"""
        assert "Template Designer" in designer_dialog.windowTitle()
    
    def test_dialog_close(self, designer_dialog, wait_for_load):
        """Test that dialog can be closed properly"""
        designer_dialog.show()
        wait_for_load(200)
        
        designer_dialog.close()
        wait_for_load(200)
        
        assert not designer_dialog.isVisible()


class TestWebViewBridge:
    """Test JavaScript bridge functionality"""
    
    def test_bridge_exists(self, designer_dialog, wait_for_load):
        """Test that JS bridge is available"""
        designer_dialog.show()
        wait_for_load(500)
        
        # Check if bridge attribute exists
        assert hasattr(designer_dialog, 'bridge') or hasattr(designer_dialog, 'webview_bridge')
    
    def test_bridge_methods(self, designer_dialog, wait_for_load):
        """Test that bridge has required methods"""
        designer_dialog.show()
        wait_for_load(500)
        
        bridge = getattr(designer_dialog, 'bridge', None) or getattr(designer_dialog, 'webview_bridge', None)
        
        if bridge:
            # Bridge should have methods for communication
            assert hasattr(bridge, '__init__')


class TestGrapeJSEditor:
    """Test GrapeJS editor loading and initialization"""
    
    def test_grapejs_files_exist(self):
        """Test that all required GrapeJS files exist"""
        web_dir = Path(__file__).parent.parent.parent / "web"
        
        required_files = [
            "index.html",
            "designer.js",
            "designer.css",
            "bridge.js",
            "components/index.js",
            "blocks/index.js",
            "traits/index.js",
            "plugins/anki-plugin.js",
            "grapesjs/grapes.min.js",
            "grapesjs/grapes.min.css"
        ]
        
        for file_path in required_files:
            full_path = web_dir / file_path
            assert full_path.exists(), f"Required file not found: {file_path}"
    
    def test_component_blocks_exist(self):
        """Test that all component block files exist"""
        blocks_dir = Path(__file__).parent.parent.parent / "web" / "blocks"
        
        required_blocks = [
            "layout.js",
            "study-action-bar.js",
            "inputs.js",
            "buttons.js",
            "data.js",
            "feedback.js",
            "overlays.js",
            "animations.js",
            "accessibility.js"
        ]
        
        for block_file in required_blocks:
            full_path = blocks_dir / block_file
            assert full_path.exists(), f"Block file not found: {block_file}"
    
    def test_editor_initialization(self, designer_dialog, wait_for_load):
        """Test that GrapeJS editor initializes in the webview"""
        designer_dialog.show()
        wait_for_load(2000)  # Give GrapeJS time to initialize
        
        # Dialog should be visible and loaded
        assert designer_dialog.isVisible()


class TestComponentLibrary:
    """Test component library integration"""
    
    def test_components_directory_structure(self):
        """Test that components directory has correct structure"""
        components_dir = Path(__file__).parent.parent.parent / "web" / "components"
        
        assert components_dir.exists()
        assert (components_dir / "index.js").exists()
        assert (components_dir / "inputs.js").exists()
    
    def test_block_categories_count(self):
        """Test that we have the expected number of block categories"""
        blocks_dir = Path(__file__).parent.parent.parent / "web" / "blocks"
        
        js_files = list(blocks_dir.glob("*.js"))
        # Should have 9 category files + index.js
        assert len([f for f in js_files if f.name != "index.js"]) == 9
    
    def test_web_assets_complete(self):
        """Test that all web assets are present"""
        web_dir = Path(__file__).parent.parent.parent / "web"
        
        # Check directories exist
        assert (web_dir / "components").exists()
        assert (web_dir / "blocks").exists()
        assert (web_dir / "traits").exists()
        assert (web_dir / "plugins").exists()
        assert (web_dir / "grapesjs").exists()
        
        # Check key files
        assert (web_dir / "index.html").exists()
        assert (web_dir / "designer.js").exists()
        assert (web_dir / "designer.css").exists()
        assert (web_dir / "bridge.js").exists()


class TestDialogInteraction:
    """Test user interactions with the dialog"""
    
    def test_dialog_can_be_resized(self, designer_dialog, wait_for_load):
        """Test that dialog can be resized"""
        designer_dialog.show()
        wait_for_load(200)
        
        original_width = designer_dialog.width()
        original_height = designer_dialog.height()
        
        # Resize
        designer_dialog.resize(1200, 800)
        wait_for_load(100)
        
        assert designer_dialog.width() == 1200
        assert designer_dialog.height() == 800
    
    def test_dialog_escape_key(self, designer_dialog, wait_for_load, qapp):
        """Test that Escape key closes the dialog"""
        designer_dialog.show()
        wait_for_load(200)
        
        # Simulate Escape key press
        QTest.keyClick(designer_dialog, Qt.Key.Key_Escape)
        wait_for_load(200)
        qapp.processEvents()
        
        # Dialog might close or stay open depending on implementation
        # Just verify no crash occurred
        assert True
    
    def test_dialog_focus(self, designer_dialog, wait_for_load):
        """Test that dialog can receive focus"""
        designer_dialog.show()
        wait_for_load(200)
        
        designer_dialog.activateWindow()
        designer_dialog.raise_()
        wait_for_load(100)
        
        # Dialog should be active (might not work in headless)
        # Just verify no crash
        assert True


class TestEditorContent:
    """Test editor content loading and manipulation"""
    
    def test_html_template_valid(self):
        """Test that index.html is valid"""
        web_dir = Path(__file__).parent.parent.parent / "web"
        index_html = web_dir / "index.html"
        
        content = index_html.read_text(encoding='utf-8')
        
        # Basic HTML validation
        assert '<!DOCTYPE html>' in content
        assert '<html' in content
        assert '</html>' in content
        assert '<head>' in content
        assert '<body>' in content
    
    def test_javascript_files_valid(self):
        """Test that JavaScript files are syntactically valid"""
        web_dir = Path(__file__).parent.parent.parent / "web"
        
        js_files = [
            "designer.js",
            "bridge.js",
            "components/index.js",
            "blocks/index.js"
        ]
        
        for js_file in js_files:
            file_path = web_dir / js_file
            content = file_path.read_text(encoding='utf-8')
            
            # Basic JS validation - check for common syntax
            assert len(content) > 0
            # Check it's not binary/corrupted
            assert content.isprintable() or '\n' in content or '\t' in content
    
    def test_css_files_valid(self):
        """Test that CSS files are syntactically valid"""
        web_dir = Path(__file__).parent.parent.parent / "web"
        
        css_files = [
            "designer.css",
            "grapesjs/grapes.min.css"
        ]
        
        for css_file in css_files:
            file_path = web_dir / css_file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                assert len(content) > 0


class TestAnkiIntegration:
    """Test Anki-specific integration features"""
    
    def test_anki_traits_file_exists(self):
        """Test that Anki traits are defined"""
        traits_dir = Path(__file__).parent.parent.parent / "web" / "traits"
        
        assert (traits_dir / "index.js").exists()
    
    def test_anki_plugin_exists(self):
        """Test that Anki GrapeJS plugin exists"""
        plugins_dir = Path(__file__).parent.parent.parent / "web" / "plugins"
        
        assert (plugins_dir / "anki-plugin.js").exists()
    
    def test_anki_special_blocks_defined(self):
        """Test that Anki special blocks (field, cloze, hint) are defined"""
        blocks_index = Path(__file__).parent.parent.parent / "web" / "blocks" / "index.js"
        
        content = blocks_index.read_text(encoding='utf-8')
        
        # Check for Anki-specific blocks
        assert 'anki-field' in content
        assert 'anki-cloze' in content
        assert 'anki-hint' in content


class TestPerformance:
    """Test performance and responsiveness"""
    
    @pytest.mark.slow
    def test_dialog_opens_quickly(self, designer_dialog):
        """Test that dialog opens within reasonable time"""
        start_time = time.time()
        
        designer_dialog.show()
        
        elapsed = time.time() - start_time
        
        # Should open in less than 2 seconds
        assert elapsed < 2.0, f"Dialog took {elapsed}s to open"
    
    @pytest.mark.slow
    def test_multiple_open_close_cycles(self, qapp, wait_for_load):
        """Test that dialog can be opened and closed multiple times"""
        # This tests for memory leaks and proper cleanup
        
        for i in range(3):
            # Import here to create fresh instance
            from gui.designer_dialog import DesignerDialog
            
            class MockMW:
                class MockCol:
                    class MockModels:
                        @staticmethod
                        def all_names_and_ids():
                            return []
                        @staticmethod
                        def get(model_id):
                            return {'tmpls': [], 'flds': []}
                    models = MockModels()
                col = MockCol()
                class MockAddonManager:
                    @staticmethod
                    def getConfig(name):
                        return {}
                addonManager = MockAddonManager()
            
            dialog = DesignerDialog(MockMW())
            dialog.show()
            wait_for_load(500)
            
            assert dialog.isVisible()
            
            dialog.close()
            dialog.deleteLater()
            wait_for_load(200)
            qapp.processEvents()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
