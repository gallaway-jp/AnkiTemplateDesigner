"""
Security tests for the Anki Template Designer
Tests XSS protection, input validation, and other security measures
"""

import pytest
from ui.template_converter import TemplateConverter, sanitize_html, sanitize_css, validate_field_name
from ui.components import TextFieldComponent, ImageFieldComponent, HeadingComponent
from utils.security import SecurityValidator
from utils.exceptions import TemplateValidationError, ResourceLimitError, TemplateSecurityError


class TestXSSProtection:
    """Test XSS attack prevention"""
    
    def test_script_tag_removal(self):
        """Test that script tags are removed"""
        malicious_html = '<div>Hello</div><script>alert("XSS")</script>'
        sanitized = sanitize_html(malicious_html)
        
        assert '<script>' not in sanitized.lower()
        assert 'alert' not in sanitized
    
    def test_event_handler_removal(self):
        """Test that event handlers are stripped"""
        malicious_html = '<img src="x" onerror="alert(\'XSS\')">'
        sanitized = sanitize_html(malicious_html)
        
        assert 'onerror' not in sanitized.lower()
        assert 'alert' not in sanitized
    
    def test_javascript_protocol_removal(self):
        """Test that javascript: protocol is removed"""
        malicious_html = '<a href="javascript:alert(\'XSS\')">Click</a>'
        sanitized = sanitize_html(malicious_html)
        
        assert 'javascript:' not in sanitized.lower()
    
    def test_iframe_removal(self):
        """Test that iframe tags are removed"""
        malicious_html = '<iframe src="evil.com"></iframe>'
        sanitized = sanitize_html(malicious_html)
        
        assert '<iframe' not in sanitized.lower()
    
    def test_multiple_xss_attempts(self):
        """Test multiple XSS vectors at once"""
        malicious_html = '''
        <script>alert(1)</script>
        <img src=x onerror=alert(2)>
        <svg onload=alert(3)>
        <a href="javascript:alert(4)">
        '''
        sanitized = sanitize_html(malicious_html)
        
        assert '<script>' not in sanitized.lower()
        assert 'onerror' not in sanitized.lower()
        assert 'onload' not in sanitized.lower()
        assert 'javascript:' not in sanitized.lower()
    
    def test_field_name_escaping_in_text_component(self):
        """Test that field names are HTML escaped"""
        malicious_field = '<script>alert("XSS")</script>'
        comp = TextFieldComponent(field_name=malicious_field)
        html = comp.to_html()
        
        # Should be escaped
        assert '&lt;script&gt;' in html or '<script>' not in html
    
    def test_field_name_escaping_in_image_component(self):
        """Test that field names in image src are escaped"""
        malicious_field = '"><script>alert("XSS")</script>'
        comp = ImageFieldComponent(field_name=malicious_field)
        html = comp.to_html()
        
        # Should be escaped
        assert '<script>' not in html.lower()


class TestCSSInjection:
    """Test CSS injection prevention"""
    
    def test_expression_removal(self):
        """Test that IE expression() is removed"""
        malicious_css = 'width: expression(alert("XSS"));'
        sanitized = sanitize_css(malicious_css)
        
        assert 'expression' not in sanitized.lower()
    
    def test_javascript_url_removal(self):
        """Test that javascript: URLs in CSS are removed"""
        malicious_css = 'background: url("javascript:alert(\'XSS\')")'
        sanitized = sanitize_css(malicious_css)
        
        assert 'javascript:' not in sanitized.lower()
    
    def test_import_removal(self):
        """Test that @import is removed"""
        malicious_css = '@import url("http://evil.com/steal.css");'
        sanitized = sanitize_css(malicious_css)
        
        assert '@import' not in sanitized.lower()
    
    def test_behavior_removal(self):
        """Test that IE behavior property is removed"""
        malicious_css = 'behavior: url(evil.htc);'
        sanitized = sanitize_css(malicious_css)
        
        assert 'behavior:' not in sanitized.lower()


class TestInputValidation:
    """Test input validation"""
    
    def test_valid_field_names(self):
        """Test that valid field names are accepted"""
        valid_names = [
            'Front',
            'Back',
            'Extra Field',
            'Field_1',
            'My-Field',
            'Field123'
        ]
        
        for name in valid_names:
            assert validate_field_name(name) == True
    
    def test_invalid_field_names(self):
        """Test that invalid field names are rejected"""
        invalid_names = [
            '<script>',
            'Field<>',
            'Field{{',
            'Field}}',
            'Field;alert(1)',
            'Field"onclick="alert(1)'
        ]
        
        for name in invalid_names:
            with pytest.raises(TemplateValidationError):
                validate_field_name(name)
    
    def test_field_name_length_limit(self):
        """Test that overly long field names are rejected"""
        long_name = 'A' * 150  # Exceeds MAX_FIELD_NAME_LENGTH
        
        with pytest.raises(ResourceLimitError, match="exceeds maximum length"):
            validate_field_name(long_name)
    
    def test_empty_field_name(self):
        """Test that empty field names are allowed"""
        assert validate_field_name('') == True
        assert validate_field_name(None) == True


class TestResourceLimits:
    """Test resource limit enforcement"""
    
    def test_html_size_limit(self):
        """Test that oversized HTML is rejected"""
        huge_html = '<div>' * 500000  # > 1MB
        
        with pytest.raises(ResourceLimitError, match="exceeds maximum size"):
            sanitize_html(huge_html)
    
    def test_css_size_limit(self):
        """Test that oversized CSS is rejected"""
        huge_css = '.class{} ' * 300000  # > 500KB
        
        with pytest.raises(ResourceLimitError, match="exceeds maximum size"):
            sanitize_css(huge_css)
    
    def test_component_count_limit(self):
        """Test that too many components are rejected"""
        too_many_components = [TextFieldComponent(f"Field{i}") for i in range(1500)]
        
        with pytest.raises(ResourceLimitError, match="exceeds maximum"):
            TemplateConverter.components_to_html(too_many_components)


class TestSecurityValidator:
    """Test SecurityValidator class"""
    
    def test_validate_template_security_safe(self):
        """Test that safe templates pass validation"""
        safe_html = '<div class="field">{{Front}}</div>'
        is_safe, warnings = SecurityValidator.validate_template_security(safe_html)
        
        assert is_safe == True
        assert len(warnings) == 0
    
    def test_validate_template_security_dangerous(self):
        """Test that dangerous templates are detected"""
        dangerous_html = '<script>alert("XSS")</script><div>{{Front}}</div>'
        is_safe, warnings = SecurityValidator.validate_template_security(dangerous_html)
        
        assert is_safe == False
        assert len(warnings) > 0
        assert any('script' in w.lower() for w in warnings)
    
    def test_escape_html(self):
        """Test HTML escaping utility"""
        dangerous = '<script>alert("XSS")</script>'
        escaped = SecurityValidator.escape_html(dangerous)
        
        assert '&lt;' in escaped
        assert '&gt;' in escaped
        assert '<script>' not in escaped


class TestTemplateConverter:
    """Test TemplateConverter security integration"""
    
    def test_components_to_html_validates_fields(self):
        """Test that components_to_html validates field names"""
        comp = TextFieldComponent(field_name="Valid_Field")
        html = TemplateConverter.components_to_html([comp])
        
        # Should work fine
        assert 'Valid_Field' in html or 'Valid_Field' in html
    
    def test_components_to_html_sanitizes_output(self):
        """Test that generated HTML is sanitized"""
        comps = [
            TextFieldComponent(field_name="Front"),
            ImageFieldComponent(field_name="Image")
        ]
        
        html = TemplateConverter.components_to_html(comps)
        
        # Should be valid HTML without dangerous content
        assert '<script>' not in html.lower()
        assert 'javascript:' not in html.lower()
    
    def test_html_to_components_sanitizes_input(self):
        """Test that HTML input is sanitized before parsing"""
        malicious_html = '''
        <div>{{Front}}</div>
        <script>alert("XSS")</script>
        <img src="{{Image}}">
        '''
        
        # Should not raise exception and should sanitize
        components = TemplateConverter.html_to_components(malicious_html)
        
        # Components should be created from safe parts only
        assert len(components) > 0


class TestRealWorldAttacks:
    """Test against real-world XSS payloads"""
    
    def test_svg_xss(self):
        """Test SVG-based XSS"""
        svg_xss = '<svg/onload=alert("XSS")>'
        sanitized = sanitize_html(svg_xss)
        
        assert 'onload' not in sanitized.lower()
    
    def test_img_xss(self):
        """Test image-based XSS"""
        img_xss = '<img src=x onerror=alert(String.fromCharCode(88,83,83))>'
        sanitized = sanitize_html(img_xss)
        
        assert 'onerror' not in sanitized.lower()
    
    def test_encoded_xss(self):
        """Test encoded XSS attempts"""
        encoded = '<img src=x onerror="&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;">'
        sanitized = sanitize_html(encoded)
        
        assert 'onerror' not in sanitized.lower()
    
    def test_case_variation_xss(self):
        """Test case variation XSS"""
        case_xss = '<ScRiPt>alert("XSS")</sCrIpT>'
        sanitized = sanitize_html(case_xss)
        
        assert '<script>' not in sanitized.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
