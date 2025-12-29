"""
Style utilities for CSS processing
"""

import re
import logging

# Configure security logging
logger = logging.getLogger('template_designer.security')

# Dangerous CSS patterns
DANGEROUS_CSS_PATTERNS = [
    r'expression\s*\(',  # IE expression()
    r'javascript:',  # javascript: protocol
    r'@import',  # @import can load external CSS
    r'behavior\s*:',  # IE behavior property
    r'-moz-binding',  # Firefox binding
    r'vbscript:',  # VBScript protocol
]


class StyleUtils:
    """Utility functions for CSS/style processing"""
    
    @staticmethod
    def validate_css_security(css):
        """
        Validate CSS for security issues
        
        Args:
            css: CSS string
        
        Returns:
            Tuple of (is_safe, warnings)
        """
        warnings = []
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_CSS_PATTERNS:
            if re.search(pattern, css, re.IGNORECASE):
                warning = f"Dangerous CSS pattern detected: {pattern}"
                warnings.append(warning)
                logger.warning(f"CSS Security: {warning}")
        
        # Check for url() with suspicious protocols
        url_pattern = r'url\s*\(\s*["\']?([^)"\'\']+)["\']?\s*\)'
        urls = re.findall(url_pattern, css, re.IGNORECASE)
        for url in urls:
            if any(proto in url.lower() for proto in ['javascript:', 'data:', 'vbscript:']):
                warning = f"Suspicious URL in CSS: {url}"
                warnings.append(warning)
                logger.warning(f"CSS Security: {warning}")
        
        is_safe = len(warnings) == 0
        return is_safe, warnings
    
    @staticmethod
    def minify_css(css):
        """
        Minify CSS by removing unnecessary whitespace and comments
        
        Args:
            css: CSS string
        
        Returns:
            Minified CSS
        """
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
        
        return css.strip()
    
    @staticmethod
    def validate_css(css):
        """
        Validate CSS syntax and security
        
        Args:
            css: CSS string
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Security validation first
        is_safe, security_warnings = StyleUtils.validate_css_security(css)
        if not is_safe:
            errors.extend(security_warnings)
            logger.error(f"CSS security validation failed: {len(security_warnings)} issues")
        
        # Check for unclosed braces
        open_braces = css.count('{')
        close_braces = css.count('}')
        
        if open_braces != close_braces:
            errors.append(f"Mismatched braces: {open_braces} opening, {close_braces} closing")
        
        # Check for basic syntax errors
        lines = css.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('/*'):
                continue
            
            # Check for missing semicolons in property declarations
            if ':' in line and not line.endswith((';', '{', '}')):
                # This might be a property without semicolon
                # Only warn, don't error
                pass
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def extract_colors(css):
        """
        Extract color values from CSS
        
        Args:
            css: CSS string
        
        Returns:
            List of color values found
        """
        colors = []
        
        # Match hex colors
        hex_colors = re.findall(r'#[0-9a-fA-F]{3,8}\b', css)
        colors.extend(hex_colors)
        
        # Match rgb/rgba
        rgb_colors = re.findall(r'rgba?\([^)]+\)', css)
        colors.extend(rgb_colors)
        
        # Match hsl/hsla
        hsl_colors = re.findall(r'hsla?\([^)]+\)', css)
        colors.extend(hsl_colors)
        
        # Match named colors (common ones)
        named_colors = re.findall(
            r'\b(black|white|red|green|blue|yellow|orange|purple|pink|brown|gray|grey)\b',
            css,
            re.IGNORECASE
        )
        colors.extend(named_colors)
        
        return list(set(colors))
    
    @staticmethod
    def add_prefix(css, prefix):
        """
        Add vendor prefixes to CSS properties
        
        Args:
            css: CSS string
            prefix: Prefix to add (e.g., '-webkit-', '-moz-')
        
        Returns:
            CSS with prefixes added
        """
        # Properties that commonly need prefixes
        properties = [
            'transform',
            'transition',
            'animation',
            'border-radius',
            'box-shadow',
            'user-select'
        ]
        
        for prop in properties:
            pattern = f'({prop}\\s*:)'
            replacement = f'{prefix}{prop}: /*prefixed*/\n{prop}:'
            css = re.sub(pattern, replacement, css)
        
        return css
    
    @staticmethod
    def convert_to_dark_mode(css):
        """
        Convert light mode CSS to dark mode
        
        Args:
            css: CSS string
        
        Returns:
            Dark mode CSS
        """
        # Basic color inversions
        color_map = {
            '#fff': '#1e1e1e',
            '#ffffff': '#1e1e1e',
            'white': '#1e1e1e',
            '#000': '#e0e0e0',
            '#000000': '#e0e0e0',
            'black': '#e0e0e0',
            '#f0f0f0': '#2d2d2d',
            '#e0e0e0': '#3a3a3a',
        }
        
        dark_css = css
        for light, dark in color_map.items():
            dark_css = dark_css.replace(light, dark)
        
        return dark_css
    
    @staticmethod
    def extract_font_families(css):
        """
        Extract font families from CSS
        
        Args:
            css: CSS string
        
        Returns:
            List of font families
        """
        fonts = []
        
        pattern = r'font-family\s*:\s*([^;]+);'
        matches = re.findall(pattern, css)
        
        for match in matches:
            # Split by comma and clean up
            font_list = [f.strip(' \'"') for f in match.split(',')]
            fonts.extend(font_list)
        
        return list(set(fonts))
