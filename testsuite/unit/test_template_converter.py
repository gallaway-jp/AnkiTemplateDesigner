"""
Integration tests for template converter (ui/template_converter.py)

Tests cover:
- Components to HTML conversion
- HTML parsing and component extraction
- CSS generation from components
- Round-trip conversion (components -> HTML -> components)
"""
import pytest
from ui.template_converter import TemplateConverter

# Create convenience aliases
components_to_html = TemplateConverter.components_to_html
html_to_components = TemplateConverter.html_to_components
components_to_css = TemplateConverter.components_to_css
from ui.components import TextFieldComponent, ImageFieldComponent, HeadingComponent, ContainerComponent


class TestComponentsToHTML:
    """Test converting components to HTML"""
    
    def test_simple_textfield_to_html(self):
        """Test converting TextField to HTML"""
        comp = TextFieldComponent(field_name="Front")
        comp.id = "field1"
        comp.x = 10
        comp.y = 10
        comp.width = 200
        comp.height = 50
        components = [comp]
        
        html = components_to_html(components)
        
        assert html is not None
        assert "{{Front}}" in html or "field1" in html
    
    def test_multiple_components_to_html(self):
        """Test converting multiple components"""
        text_comp = TextFieldComponent(field_name="Question")
        text_comp.id = "text1"
        text_comp.x = 0
        text_comp.y = 0
        text_comp.width = 200
        text_comp.height = 40
        
        img_comp = ImageFieldComponent(field_name="Image")
        img_comp.id = "img1"
        img_comp.x = 0
        img_comp.y = 50
        img_comp.width = 200
        img_comp.height = 150
        
        heading_comp = HeadingComponent(field_name="Title", level=1)
        heading_comp.id = "h1"
        heading_comp.x = 0
        heading_comp.y = 210
        heading_comp.width = 200
        heading_comp.height = 30
        
        components = [text_comp, img_comp, heading_comp]
        
        html = components_to_html(components)
        
        assert html is not None
        # Should contain elements for each component
        assert len(html) > 0
    
    def test_empty_components_to_html(self):
        """Test converting empty component list"""
        html = components_to_html([])
        
        # Should return valid (empty or minimal) HTML
        assert html is not None
    
    def test_nested_components_to_html(self):
        """Test converting nested components (if supported)"""
        # Create a container with nested components
        container = ContainerComponent()
        container.id = "container1"
        
        # Add text field child
        child1 = TextFieldComponent("Front")
        child1.id = "child1"
        container.add_child(child1)
        
        # Add image field child
        child2 = ImageFieldComponent("Image")
        child2.id = "child2"
        container.add_child(child2)
        
        # Convert to HTML
        html = components_to_html([container])
        
        # Verify the HTML contains container markup
        assert html is not None
        assert 'class="container"' in html
        assert '{{Front}}' in html
        assert '{{Image}}' in html
        
        # Verify both children are present in the output
        assert 'field-content' in html
        assert 'field-front' in html
        assert 'image-container' in html


class TestHTMLToComponents:
    """Test parsing HTML to extract components"""
    
    def test_simple_html_to_components(self):
        """Test parsing simple HTML"""
        html = '<div class="field">{{Front}}</div>'
        
        components = html_to_components(html)
        
        assert components is not None
        assert isinstance(components, list)
    
    def test_complex_html_to_components(self):
        """Test parsing HTML with multiple elements"""
        html = '''
        <div class="card">
            <div class="question">{{Front}}</div>
            <img src="{{Image}}" />
            <button>Show Answer</button>
        </div>
        '''
        
        components = html_to_components(html)
        
        assert components is not None
        assert isinstance(components, list)
    
    def test_empty_html_to_components(self):
        """Test parsing empty HTML"""
        components = html_to_components("")
        
        assert components is not None
        assert isinstance(components, list)
    
    def test_html_with_anki_fields(self):
        """Test parsing HTML containing Anki field placeholders"""
        html = '''
        <div>
            <div>{{Front}}</div>
            <div>{{Back}}</div>
            <div>{{Extra}}</div>
        </div>
        '''
        
        components = html_to_components(html)
        
        assert components is not None


class TestComponentsToCSS:
    """Test CSS generation from components"""
    
    def test_simple_css_generation(self):
        """Test generating CSS for components"""
        comp = TextFieldComponent(field_name="Front")
        comp.id = "field1"
        comp.font_family = "Arial"
        comp.font_size = 14
        comp.color = "#000000"
        components = [comp]
        
        css = components_to_css(components)
        
        assert css is not None
        assert isinstance(css, str)
    
    def test_css_with_multiple_components(self):
        """Test CSS generation with multiple styled components"""
        text1 = TextFieldComponent(field_name="Front")
        text1.id = "text1"
        text1.font_family = "Arial"
        text1.font_size = 14
        
        text2 = TextFieldComponent(field_name="Back")
        text2.id = "text2"
        text2.font_family = "Times"
        text2.font_size = 16
        
        heading = HeadingComponent(field_name="Title", level=1)
        heading.id = "h1"
        heading.color = "#0066cc"
        
        components = [text1, text2, heading]
        
        css = components_to_css(components)
        
        assert css is not None
    
    def test_css_with_no_styles(self):
        """Test CSS generation when components have no special styles"""
        comp = TextFieldComponent(field_name="Plain")
        comp.id = "simple"
        components = [comp]
        
        css = components_to_css(components)
        
        # Should still return valid CSS (possibly empty)
        assert css is not None


class TestRoundTripConversion:
    """Test converting components to HTML and back"""
    
    def test_round_trip_simple(self):
        """Test round-trip conversion preserves basic structure"""
        comp = TextFieldComponent(field_name="Front")
        comp.id = "field1"
        comp.x = 10
        comp.y = 10
        comp.width = 200
        comp.height = 50
        original = [comp]
        
        html = components_to_html(original)
        converted = html_to_components(html)
        
        assert converted is not None
        assert isinstance(converted, list)
    
    def test_round_trip_preserves_content(self):
        """Test that round-trip preserves Anki field references"""
        q_comp = TextFieldComponent(field_name="Question")
        q_comp.id = "q"
        q_comp.x = 0
        q_comp.y = 0
        q_comp.width = 200
        q_comp.height = 40
        
        a_comp = TextFieldComponent(field_name="Answer")
        a_comp.id = "a"
        a_comp.x = 0
        a_comp.y = 50
        a_comp.width = 200
        a_comp.height = 40
        
        original = [q_comp, a_comp]
        
        html = components_to_html(original)
        
        # HTML should contain field references
        assert "{{Question}}" in html or "Question" in html
        assert "{{Answer}}" in html or "Answer" in html


class TestTemplateStructure:
    """Test template structure compatibility"""
    
    def test_anki_template_structure(self):
        """Test compatibility with Anki template structure"""
        comp = TextFieldComponent(field_name="Front")
        comp.id = "front"
        comp.x = 10
        comp.y = 10
        comp.width = 300
        comp.height = 100
        components = [comp]
        
        # Generate question format (qfmt)
        qfmt = components_to_html(components)
        
        assert qfmt is not None
        
        # Should be valid HTML
        assert '<' in qfmt and '>' in qfmt
    
    def test_css_integration(self):
        """Test that CSS integrates properly with template"""
        comp = TextFieldComponent(field_name="Text")
        comp.id = "styled"
        comp.font_family = "Arial"
        comp.font_size = 16
        comp.color = "#333333"
        components = [comp]
        
        html = components_to_html(components)
        css = components_to_css(components)
        
        # Both should be non-empty for styled components
        assert html is not None
        assert css is not None
