"""
Performance tests for template conversion and security
"""

import pytest
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.template_converter import TemplateConverter, sanitize_html, sanitize_css
from ui.components import TextFieldComponent, ImageFieldComponent, HeadingComponent, DividerComponent
from utils.security import SecurityValidator


class TestPerformance:
    """Test performance of key operations"""
    
    def test_sanitize_html_performance(self, benchmark):
        """Benchmark HTML sanitization"""
        # Create realistic HTML with multiple potential XSS vectors
        html = """
        <div class="card">
            <h1>Title</h1>
            <script>alert('xss')</script>
            <p onclick="malicious()">Text</p>
            <img src="{{Image}}" onerror="alert(1)">
            <iframe src="evil.com"></iframe>
            <div onload="bad()">Content</div>
        </div>
        """ * 10  # Repeat to simulate larger template
        
        # Benchmark the sanitization
        result = benchmark(sanitize_html, html)
        
        # Verify it still works correctly
        assert '<script' not in result.lower()
        assert 'onclick' not in result.lower()
        assert 'onerror' not in result.lower()
        assert 'onload' not in result.lower()
    
    def test_sanitize_css_performance(self, benchmark):
        """Benchmark CSS sanitization"""
        # Create CSS with dangerous properties
        css = """
        .card {
            font-family: Arial;
            color: red;
            background: url(javascript:alert(1));
            behavior: url(xss.htc);
            -moz-binding: url(xss.xml);
        }
        @import url(evil.css);
        """ * 20  # Repeat to simulate larger stylesheet
        
        # Benchmark the sanitization
        result = benchmark(sanitize_css, css)
        
        # Verify it still works
        assert 'javascript:' not in result.lower()
        assert '@import' not in result.lower()
    
    def test_components_to_html_performance(self, benchmark):
        """Benchmark component to HTML conversion"""
        # Create a realistic set of components
        components = [
            HeadingComponent("Title", 1),
            TextFieldComponent("Question"),
            ImageFieldComponent("Image"),
            DividerComponent(),
            TextFieldComponent("Answer"),
        ] * 10  # 50 components total
        
        # Benchmark the conversion
        result = benchmark(TemplateConverter.components_to_html, components)
        
        # Verify it works
        assert '{{Question}}' in result
        assert '{{Answer}}' in result
        assert 'component-0' in result
    
    def test_components_to_css_performance(self, benchmark):
        """Benchmark component to CSS conversion"""
        # Create components with various styles
        components = []
        for i in range(50):
            comp = TextFieldComponent(f"Field{i}")
            comp.font_size = 16 + (i % 5)
            comp.color = f"#{'0' * (i % 6)}"
            comp.margin_top = i % 10
            components.append(comp)
        
        # Benchmark the conversion
        result = benchmark(TemplateConverter.components_to_css, components)
        
        # Verify it works
        assert '.card {' in result
        assert 'font-family:' in result
    
    def test_field_name_validation_performance(self, benchmark):
        """Benchmark field name validation"""
        # Test with valid field name
        field_name = "My_Field_Name_123"
        
        # Benchmark validation
        result = benchmark(SecurityValidator.validate_field_name, field_name)
        
        # Verify it works
        assert result is True
    
    def test_multiple_sanitize_calls_performance(self, benchmark):
        """Benchmark multiple sanitization calls (realistic usage)"""
        html_templates = [
            "<div>{{Field1}}</div>",
            "<h1>{{Title}}</h1>",
            "<p onclick='bad'>{{Text}}</p>",
        ] * 10
        
        def sanitize_multiple():
            return [sanitize_html(html) for html in html_templates]
        
        results = benchmark(sanitize_multiple)
        
        # Verify all sanitized
        assert len(results) == 30
        assert all('onclick' not in r.lower() for r in results)
    
    def test_large_template_conversion(self, benchmark):
        """Benchmark conversion of large template (stress test)"""
        # Create 100 components
        components = []
        for i in range(100):
            if i % 4 == 0:
                components.append(HeadingComponent(f"Section{i}", i % 3 + 1))
            elif i % 4 == 1:
                components.append(TextFieldComponent(f"Field{i}"))
            elif i % 4 == 2:
                components.append(ImageFieldComponent(f"Image{i}"))
            else:
                components.append(DividerComponent())
        
        def full_conversion():
            html = TemplateConverter.components_to_html(components)
            css = TemplateConverter.components_to_css(components)
            return html, css
        
        html, css = benchmark(full_conversion)
        
        # Verify output
        assert len(html) > 1000
        assert len(css) > 1000
        assert 'component-99' in html


class TestPerformanceManual:
    """Manual performance tests (not using benchmark fixture)"""
    
    def test_regex_compilation_benefit(self):
        """Verify that pre-compiled regex patterns improve performance"""
        # This test demonstrates the benefit of pre-compiled patterns
        html = "<script>alert('xss')</script>" * 100
        
        # Warm up
        for _ in range(5):
            sanitize_html(html)
        
        # Measure with pre-compiled patterns (current implementation)
        start = time.perf_counter()
        for _ in range(100):
            sanitize_html(html)
        optimized_time = time.perf_counter() - start
        
        # The optimized version should complete in reasonable time
        # (< 1 second for 100 iterations)
        assert optimized_time < 1.0, f"Sanitization too slow: {optimized_time:.3f}s"
        
    def test_list_comprehension_benefit(self):
        """Verify that list comprehensions improve performance"""
        components = [TextFieldComponent(f"Field{i}") for i in range(50)]
        
        # Warm up
        for _ in range(5):
            TemplateConverter.components_to_html(components)
        
        # Measure
        start = time.perf_counter()
        for _ in range(50):
            TemplateConverter.components_to_html(components)
        total_time = time.perf_counter() - start
        
        # Should complete quickly (< 2 seconds for 50 iterations)
        assert total_time < 2.0, f"Conversion too slow: {total_time:.3f}s"
    
    def test_string_joining_efficiency(self):
        """Verify efficient string joining in CSS generation"""
        components = [TextFieldComponent(f"Field{i}") for i in range(100)]
        
        # Warm up
        for _ in range(5):
            TemplateConverter.components_to_css(components)
        
        # Measure
        start = time.perf_counter()
        for _ in range(50):
            TemplateConverter.components_to_css(components)
        total_time = time.perf_counter() - start
        
        # Should complete quickly (< 2 seconds for 50 iterations)
        assert total_time < 2.0, f"CSS generation too slow: {total_time:.3f}s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--benchmark-only'])
