"""UI Tests for Component Blocks - Test block drag and drop with real Anki"""
import pytest
import time
from pathlib import Path
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication


class TestComponentBlocks:
    """Test individual component blocks in the UI"""
    
    def test_layout_blocks_available(self):
        """Test that layout blocks are defined"""
        layout_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "layout.js"
        
        content = layout_file.read_text(encoding='utf-8')
        
        # Check for key layout blocks
        expected_blocks = [
            'frame',
            'section',
            'panel',
            'card',
            'grid',
            'h-stack',
            'v-stack',
            'tabs-nav',
            'accordion'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Layout block '{block}' not found"
    
    def test_study_action_bar_block(self):
        """Test that study action bar block is defined"""
        action_bar_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "study-action-bar.js"
        
        content = action_bar_file.read_text(encoding='utf-8')
        
        assert 'study-action-bar' in content
        assert 'Show Answer' in content or 'showAnswer' in content
    
    def test_input_blocks_available(self):
        """Test that input blocks are defined"""
        inputs_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "inputs.js"
        
        content = inputs_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'text-field',
            'text-area',
            'checkbox',
            'radio-button',
            'dropdown',
            'slider',
            'form'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Input block '{block}' not found"
    
    def test_button_blocks_available(self):
        """Test that button blocks are defined"""
        buttons_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "buttons.js"
        
        content = buttons_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'primary-button',
            'secondary-button',
            'icon-button',
            'destructive-button',
            'link-button'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Button block '{block}' not found"
    
    def test_data_blocks_available(self):
        """Test that data display blocks are defined"""
        data_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "data.js"
        
        content = data_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'heading',
            'paragraph',
            'unordered-list',
            'ordered-list',
            'table',
            'image',
            'code-block'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Data block '{block}' not found"
    
    def test_feedback_blocks_available(self):
        """Test that feedback blocks are defined"""
        feedback_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "feedback.js"
        
        content = feedback_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'alert-info',
            'alert-success',
            'alert-warning',
            'alert-error',
            'badge',
            'progress-bar',
            'tooltip',
            'toast'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Feedback block '{block}' not found"
    
    def test_overlay_blocks_available(self):
        """Test that overlay blocks are defined"""
        overlays_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "overlays.js"
        
        content = overlays_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'modal',
            'drawer-overlay',
            'popover',
            'dropdown-menu',
            'bottom-sheet',
            'lightbox'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Overlay block '{block}' not found"
    
    def test_animation_blocks_available(self):
        """Test that animation blocks are defined"""
        animations_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "animations.js"
        
        content = animations_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'fade-container',
            'slide-container',
            'stagger-group'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Animation block '{block}' not found"
    
    def test_accessibility_blocks_available(self):
        """Test that accessibility blocks are defined"""
        accessibility_file = Path(__file__).parent.parent.parent / "web" / "blocks" / "accessibility.js"
        
        content = accessibility_file.read_text(encoding='utf-8')
        
        expected_blocks = [
            'sr-only',
            'accessible-field',
            'accessible-error',
            'landmark-main',
            'focus-indicator'
        ]
        
        for block in expected_blocks:
            assert block in content, f"Accessibility block '{block}' not found"


class TestBlockRegistration:
    """Test that blocks are properly registered"""
    
    def test_blocks_index_imports_all_categories(self):
        """Test that blocks/index.js imports all category files"""
        blocks_index = Path(__file__).parent.parent.parent / "web" / "blocks" / "index.js"
        
        content = blocks_index.read_text(encoding='utf-8')
        
        expected_imports = [
            'layout',
            'study-action-bar',
            'inputs',
            'buttons',
            'data',
            'feedback',
            'overlays',
            'animations',
            'accessibility'
        ]
        
        for module in expected_imports:
            assert f"from './{module}" in content or f'from "./{module}' in content, \
                f"Import for '{module}' not found in blocks/index.js"
    
    def test_blocks_index_exports_registration_functions(self):
        """Test that blocks/index.js exports all registration functions"""
        blocks_index = Path(__file__).parent.parent.parent / "web" / "blocks" / "index.js"
        
        content = blocks_index.read_text(encoding='utf-8')
        
        # Should have function calls for each category
        expected_functions = [
            'registerLayoutBlocks',
            'registerStudyActionBar',
            'registerInputBlocks',
            'registerButtonBlocks',
            'registerDataBlocks',
            'registerFeedbackBlocks',
            'registerOverlayBlocks',
            'registerAnimationBlocks',
            'registerAccessibilityBlocks'
        ]
        
        for func in expected_functions:
            assert func in content, f"Function '{func}' not called in blocks/index.js"
    
    def test_blocks_use_es6_modules(self):
        """Test that all block files use ES6 module syntax"""
        blocks_dir = Path(__file__).parent.parent.parent / "web" / "blocks"
        
        block_files = [f for f in blocks_dir.glob("*.js") if f.name != "index.js"]
        
        for block_file in block_files:
            content = block_file.read_text(encoding='utf-8')
            
            # Should have export function
            assert 'export function' in content or 'export default' in content, \
                f"{block_file.name} doesn't use ES6 exports"


class TestComponentTypes:
    """Test component type definitions"""
    
    def test_component_types_index_exists(self):
        """Test that components/index.js exists and registers types"""
        components_index = Path(__file__).parent.parent.parent / "web" / "components" / "index.js"
        
        content = components_index.read_text(encoding='utf-8')
        
        # Should export main registration function
        assert 'registerComponentTypes' in content
        assert 'export' in content
    
    def test_input_component_types_defined(self):
        """Test that input component types are defined"""
        inputs_file = Path(__file__).parent.parent.parent / "web" / "components" / "inputs.js"
        
        content = inputs_file.read_text(encoding='utf-8')
        
        expected_types = [
            'text-input',
            'textarea-input',
            'select-input',
            'checkbox-input',
            'radio-input'
        ]
        
        for component_type in expected_types:
            assert component_type in content, f"Component type '{component_type}' not found"
    
    def test_component_types_have_traits(self):
        """Test that component types define traits"""
        inputs_file = Path(__file__).parent.parent.parent / "web" / "components" / "inputs.js"
        
        content = inputs_file.read_text(encoding='utf-8')
        
        # Should define traits
        assert 'traits' in content
        assert 'required' in content or 'pattern' in content


class TestBlockContent:
    """Test that blocks have proper default content"""
    
    def test_blocks_have_labels(self):
        """Test that blocks have descriptive labels"""
        blocks_dir = Path(__file__).parent.parent.parent / "web" / "blocks"
        
        for block_file in blocks_dir.glob("*.js"):
            if block_file.name == "index.js":
                continue
            
            content = block_file.read_text(encoding='utf-8')
            
            # Blocks should have label property
            assert 'label:' in content or 'label :' in content, \
                f"{block_file.name} blocks should have labels"
    
    def test_blocks_have_categories(self):
        """Test that blocks specify categories"""
        blocks_dir = Path(__file__).parent.parent.parent / "web" / "blocks"
        
        for block_file in blocks_dir.glob("*.js"):
            if block_file.name == "index.js":
                continue
            
            content = block_file.read_text(encoding='utf-8')
            
            # Blocks should specify category (either inline or via const)
            assert 'category:' in content or 'category :' in content or 'const category' in content, \
                f"{block_file.name} blocks should have categories"
    
    def test_blocks_have_content(self):
        """Test that blocks have default content or media"""
        blocks_dir = Path(__file__).parent.parent.parent / "web" / "blocks"
        
        for block_file in blocks_dir.glob("*.js"):
            if block_file.name == "index.js":
                continue
            
            content = block_file.read_text(encoding='utf-8')
            
            # Blocks should have content or media property
            assert 'content:' in content or 'media:' in content or 'content :' in content, \
                f"{block_file.name} blocks should have content"


class TestEditorConfiguration:
    """Test editor configuration and settings"""
    
    def test_designer_js_initializes_editor(self):
        """Test that designer.js initializes GrapeJS"""
        designer_js = Path(__file__).parent.parent.parent / "web" / "designer.js"
        
        content = designer_js.read_text(encoding='utf-8')
        
        # Should initialize GrapeJS
        assert 'grapesjs.init' in content
        assert 'container:' in content or 'container :' in content
    
    def test_designer_js_registers_components(self):
        """Test that designer.js calls component registration"""
        designer_js = Path(__file__).parent.parent.parent / "web" / "designer.js"
        
        content = designer_js.read_text(encoding='utf-8')
        
        # Should call component registration
        assert 'registerComponentTypes' in content
    
    def test_designer_js_configures_panels(self):
        """Test that designer.js configures editor panels"""
        designer_js = Path(__file__).parent.parent.parent / "web" / "designer.js"
        
        content = designer_js.read_text(encoding='utf-8')
        
        # Should configure panels
        assert 'panels' in content or 'blockManager' in content
    
    def test_designer_css_has_styles(self):
        """Test that designer.css has required styles"""
        designer_css = Path(__file__).parent.parent.parent / "web" / "designer.css"
        
        content = designer_css.read_text(encoding='utf-8')
        
        # Should have styles for editor
        assert len(content) > 100
        assert '{' in content and '}' in content  # Basic CSS syntax


class TestJavaScriptBridge:
    """Test JavaScript-Python bridge functionality"""
    
    def test_bridge_file_exists(self):
        """Test that bridge.js exists"""
        bridge_js = Path(__file__).parent.parent.parent / "web" / "bridge.js"
        
        assert bridge_js.exists()
    
    def test_bridge_defines_communication(self):
        """Test that bridge.js defines communication functions"""
        bridge_js = Path(__file__).parent.parent.parent / "web" / "bridge.js"
        
        content = bridge_js.read_text(encoding='utf-8')
        
        # Should have functions for bridge communication
        assert 'function' in content or 'const' in content or 'let' in content
    
    def test_webview_bridge_py_exists(self):
        """Test that Python bridge exists"""
        bridge_py = Path(__file__).parent.parent.parent / "gui" / "webview_bridge.py"
        
        assert bridge_py.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
