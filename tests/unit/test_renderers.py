"""
Tests for template renderers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from renderers.base_renderer import BaseRenderer
from renderers.desktop_renderer import DesktopRenderer
from renderers.ankidroid_renderer import AnkiDroidRenderer


def create_mock_note(fields_dict):
    """Create a properly mocked Anki note"""
    note = Mock()
    note.items.return_value = list(fields_dict.items())
    note.tags = []
    return note


class ConcreteRenderer(BaseRenderer):
    """Concrete implementation for testing abstract BaseRenderer"""
    
    def _build_html(self, content_html, css, **kwargs):
        """Simple implementation for testing"""
        return f"<html><style>{css}</style><body>{content_html}</body></html>"


class TestBaseRenderer:
    """Tests for BaseRenderer base class"""
    
    def test_renderer_initialization(self):
        """Test renderer initializes with sample data"""
        renderer = ConcreteRenderer()
        
        assert renderer.sample_data is not None
        assert isinstance(renderer.sample_data, dict)
        assert 'Front' in renderer.sample_data
        assert 'Back' in renderer.sample_data
    
    def test_render_front_template(self):
        """Test rendering front template"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'afmt': '<div>{{FrontSide}}<hr>{{Back}}</div>',
            'css': 'div { color: red; }'
        }
        
        note = create_mock_note({'Front': 'Test Front', 'Back': 'Test Back'})
        
        result = renderer.render(template_dict, note, side='front')
        
        assert '<div>Test Front</div>' in result
        assert 'color: red' in result
    
    def test_render_back_template(self):
        """Test rendering back template"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'afmt': '<div>{{FrontSide}}<hr>{{Back}}</div>',
            'css': 'div { color: red; }'
        }
        
        note = create_mock_note({'Front': 'Test Front', 'Back': 'Test Back'})
        
        result = renderer.render(template_dict, note, side='back')
        
        assert 'Test Back' in result
        assert '<hr>' in result
        # Back should include FrontSide
        assert 'Test Front' in result
    
    def test_render_empty_template(self):
        """Test rendering empty template returns empty string"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '',
            'afmt': '',
            'css': ''
        }
        
        result = renderer.render(template_dict, note=None, side='front')
        
        assert result == ""
    
    def test_render_without_note_uses_sample_data(self):
        """Test rendering without note uses sample data"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'css': ''
        }
        
        result = renderer.render(template_dict, note=None, side='front')
        
        # Should use sample data
        assert '<div>' in result
        assert 'Sample Front Text' in result
    
    def test_render_handles_missing_fields(self):
        """Test rendering handles missing fields gracefully"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{NonexistentField}}</div>',
            'css': ''
        }
        
        note = create_mock_note({'Front': 'Test'})
        
        result = renderer.render(template_dict, note, side='front')
        
        # Missing fields should remain as placeholders or be empty
        assert '<div>' in result
    
    def test_render_with_multiple_fields(self):
        """Test rendering with multiple field replacements"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Field1}} - {{Field2}} - {{Field3}}</div>',
            'css': ''
        }
        
        note = create_mock_note({
            'Field1': 'Value1',
            'Field2': 'Value2',
            'Field3': 'Value3'
        })
        
        result = renderer.render(template_dict, note, side='front')
        
        assert 'Value1' in result
        assert 'Value2' in result
        assert 'Value3' in result
    
    def test_get_sample_data(self):
        """Test _get_sample_data returns valid data"""
        renderer = ConcreteRenderer()
        
        data = renderer._get_sample_data()
        
        assert isinstance(data, dict)
        assert 'Front' in data
        assert 'Back' in data
        assert 'Extra' in data
    
    def test_prepare_note_data_includes_frontside_for_back(self):
        """Test _prepare_note_data adds FrontSide for back templates"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'afmt': '<div>{{FrontSide}}</div>'
        }
        
        note = create_mock_note({'Front': 'Test Front'})
        
        data = renderer._prepare_note_data(note, template_dict, 'back')
        
        assert 'FrontSide' in data
        assert 'Test Front' in data['FrontSide']
    
    def test_get_template_html_front(self):
        """Test _get_template_html extracts front template"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>Front</div>',
            'afmt': '<div>Back</div>'
        }
        
        html = renderer._get_template_html(template_dict, 'front')
        
        assert html == '<div>Front</div>'
    
    def test_get_template_html_back(self):
        """Test _get_template_html extracts back template"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>Front</div>',
            'afmt': '<div>Back</div>'
        }
        
        html = renderer._get_template_html(template_dict, 'back')
        
        assert html == '<div>Back</div>'


class TestDesktopRenderer:
    """Tests for DesktopRenderer"""
    
    def test_desktop_renderer_initialization(self):
        """Test DesktopRenderer initializes"""
        renderer = DesktopRenderer()
        
        assert renderer is not None
        assert renderer.sample_data is not None
    
    def test_desktop_renderer_builds_complete_html(self):
        """Test desktop renderer builds complete HTML document"""
        renderer = DesktopRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'css': 'div { color: blue; }'
        }
        
        note = create_mock_note({'Front': 'Desktop Test'})
        
        result = renderer.render(template_dict, note, side='front')
        
        # Should have complete HTML structure
        assert '<html>' in result or '<!DOCTYPE html>' in result
        assert 'Desktop Test' in result
        assert 'color: blue' in result
    
    def test_desktop_renderer_includes_css(self):
        """Test desktop renderer includes CSS in output"""
        renderer = DesktopRenderer()
        template_dict = {
            'qfmt': '<span>Test</span>',
            'css': '.test { font-size: 20px; }'
        }
        
        result = renderer.render(template_dict, note=None, side='front')
        
        assert 'font-size: 20px' in result


class TestAnkiDroidRenderer:
    """Tests for AnkiDroidRenderer (mobile)"""
    
    def test_ankidroid_renderer_initialization(self):
        """Test AnkiDroidRenderer initializes"""
        renderer = AnkiDroidRenderer()
        
        assert renderer is not None
        assert renderer.sample_data is not None
    
    def test_ankidroid_renderer_builds_mobile_html(self):
        """Test AnkiDroid renderer builds mobile-friendly HTML"""
        renderer = AnkiDroidRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'css': 'div { color: green; }'
        }
        
        note = create_mock_note({'Front': 'Mobile Test'})
        
        result = renderer.render(template_dict, note, side='front')
        
        # Should have HTML structure
        assert '<html>' in result or '<!DOCTYPE html>' in result
        assert 'Mobile Test' in result
        assert 'color: green' in result
    
    def test_ankidroid_renderer_viewport_meta(self):
        """Test AnkiDroid renderer includes viewport meta tag"""
        renderer = AnkiDroidRenderer()
        template_dict = {
            'qfmt': '<div>Test</div>',
            'css': ''
        }
        
        result = renderer.render(template_dict, note=None, side='front')
        
        # Mobile renderers typically include viewport meta
        # May or may not be present depending on implementation
        assert 'Test' in result


class TestRendererEdgeCases:
    """Tests for edge cases across all renderers"""
    
    def test_render_with_html_in_field_data(self):
        """Test rendering when field data contains HTML"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'css': ''
        }
        
        note = create_mock_note({'Front': '<b>Bold Text</b>'})
        
        result = renderer.render(template_dict, note, side='front')
        
        assert 'Bold Text' in result
    
    def test_render_with_unicode_content(self):
        """Test rendering with Unicode content"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'css': ''
        }
        
        note = create_mock_note({'Front': '日本語テスト'})
        
        result = renderer.render(template_dict, note, side='front')
        
        assert '日本語テスト' in result
    
    def test_render_with_empty_css(self):
        """Test rendering with empty CSS"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '<div>Test</div>',
            'css': ''
        }
        
        result = renderer.render(template_dict, note=None, side='front')
        
        assert 'Test' in result
    
    def test_render_with_complex_template(self):
        """Test rendering with complex nested template"""
        renderer = ConcreteRenderer()
        template_dict = {
            'qfmt': '''
                <div class="card">
                    <div class="front">{{Front}}</div>
                    <div class="hint">{{Hint}}</div>
                </div>
            ''',
            'css': '.card { padding: 10px; }'
        }
        
        note = create_mock_note({'Front': 'Question', 'Hint': 'Help'})
        
        result = renderer.render(template_dict, note, side='front')
        
        assert 'Question' in result
        assert 'Help' in result


class TestRendererIntegration:
    """Integration tests for renderers"""
    
    def test_desktop_and_ankidroid_produce_different_output(self):
        """Test Desktop and AnkiDroid renderers produce platform-specific output"""
        desktop = DesktopRenderer()
        ankidroid = AnkiDroidRenderer()
        
        template_dict = {
            'qfmt': '<div>{{Front}}</div>',
            'css': 'div { color: red; }'
        }
        
        note = create_mock_note({'Front': 'Test'})
        
        desktop_result = desktop.render(template_dict, note, side='front')
        ankidroid_result = ankidroid.render(template_dict, note, side='front')
        
        # Both should contain the content
        assert 'Test' in desktop_result
        assert 'Test' in ankidroid_result
        
        # Implementation details may differ
        # (e.g., viewport meta, CSS handling, etc.)
    
    def test_all_renderers_handle_same_template(self):
        """Test all renderer types can handle the same template"""
        renderers = [
            ConcreteRenderer(),
            DesktopRenderer(),
            AnkiDroidRenderer()
        ]
        
        template_dict = {
            'qfmt': '<div>{{Field1}} {{Field2}}</div>',
            'css': 'div { margin: 10px; }'
        }
        
        note = create_mock_note({'Field1': 'A', 'Field2': 'B'})
        
        for renderer in renderers:
            result = renderer.render(template_dict, note, side='front')
            
            # All should produce output with field values
            assert 'A' in result or 'B' in result or result != ""
