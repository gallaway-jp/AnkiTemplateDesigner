"""
Security utilities for the Anki Template Designer
Centralized security functions for input validation and sanitization
"""

import re
import html
import logging
from .exceptions import (
    TemplateSecurityError,
    ResourceLimitError,
    TemplateValidationError
)

# Configure security logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('template_designer.security')

# Security constants
MAX_TEMPLATE_SIZE = 1_000_000  # 1MB
MAX_CSS_SIZE = 500_000  # 500KB
MAX_COMPONENTS = 1000
MAX_FIELD_NAME_LENGTH = 100
MAX_NESTING_DEPTH = 10

# Dangerous patterns
DANGEROUS_HTML_TAGS = {
    'script', 'iframe', 'object', 'embed', 'applet',
    'meta', 'link', 'style', 'base', 'form', 'input',
    'button', 'textarea', 'select'
}

DANGEROUS_ATTRIBUTES = [
    'onload', 'onerror', 'onclick', 'onmouseover', 'onfocus',
    'onblur', 'onchange', 'onsubmit', 'ondblclick', 'onkeydown',
    'onkeypress', 'onkeyup', 'onmousedown', 'onmousemove',
    'onmouseout', 'onmouseup', 'onselect', 'onunload'
]

DANGEROUS_CSS_PROPS = [
    'expression', 'behavior', 'binding', '-moz-binding',
    'javascript:', 'vbscript:'
]

# Pre-compiled regex patterns for performance
_FIELD_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\- ]+$')
_JAVASCRIPT_PROTOCOL_PATTERN = re.compile(r'javascript:', re.IGNORECASE)
_VBSCRIPT_PROTOCOL_PATTERN = re.compile(r'vbscript:', re.IGNORECASE)
_CSS_IMPORT_PATTERN = re.compile(r'@import[^;]+;', re.IGNORECASE)

# Pre-compiled patterns for dangerous tags (compiled once for all tags)
_DANGEROUS_TAG_PATTERNS = {}
for tag in DANGEROUS_HTML_TAGS:
    _DANGEROUS_TAG_PATTERNS[tag] = (
        re.compile(f'<{tag}[^>]*>.*?</{tag}>', re.IGNORECASE | re.DOTALL),
        re.compile(f'<{tag}[^>]*/?>', re.IGNORECASE)
    )

# Pre-compiled patterns for dangerous attributes
_DANGEROUS_ATTR_PATTERNS = {}
for attr in DANGEROUS_ATTRIBUTES:
    _DANGEROUS_ATTR_PATTERNS[attr] = (
        re.compile(f'\\s+{attr}\\s*=\\s*["\'][^"\']*["\']', re.IGNORECASE),
        re.compile(f'\\s+{attr}\\s*=\\s*[^\\s>]+', re.IGNORECASE),
        re.compile(f'/{attr}\\s*=\\s*[^\\s>]+', re.IGNORECASE)
    )

# Pre-compiled patterns for dangerous CSS properties
_DANGEROUS_CSS_PATTERNS = {}
for prop in DANGEROUS_CSS_PROPS:
    _DANGEROUS_CSS_PATTERNS[prop] = re.compile(f'{re.escape(prop)}[^;]*;?', re.IGNORECASE)


class SecurityValidator:
    """Central security validation for templates"""
    
    @staticmethod
    def validate_field_name(field_name):
        """
        Validate field name for security.
        
        Args:
            field_name (str): Field name to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            TemplateValidationError: If field name is invalid
            ResourceLimitError: If field name exceeds length limit
        """
        if not field_name:
            return True
        
        # Check length
        if len(field_name) > MAX_FIELD_NAME_LENGTH:
            error = f"Field name exceeds maximum length of {MAX_FIELD_NAME_LENGTH}"
            logger.error(f"Security: {error}")
            raise ResourceLimitError(
                error,
                resource_type='field_name_length',
                current_value=len(field_name),
                limit_value=MAX_FIELD_NAME_LENGTH
            )
        
        # Only allow alphanumeric, underscore, hyphen, and space
        if not _FIELD_NAME_PATTERN.match(field_name):
            error = f"Field name contains invalid characters: {field_name}"
            logger.error(f"Security: {error}")
            raise TemplateValidationError(error, field=field_name)
        
        return True
    
    @staticmethod
    def sanitize_html(html_content):
        """
        Sanitize HTML to prevent XSS attacks.
        
        Removes dangerous tags, attributes, and protocols that could be exploited
        for cross-site scripting or other security vulnerabilities.
        
        Args:
            html_content (str): HTML string to sanitize
            
        Returns:
            str: Sanitized HTML with dangerous content removed
            
        Raises:
            ResourceLimitError: If HTML exceeds size limit
        """
        if not html_content:
            return ""
        
        # Check size limit
        if len(html_content) > MAX_TEMPLATE_SIZE:
            error = f"Template exceeds maximum size of {MAX_TEMPLATE_SIZE} bytes"
            logger.error(f"Security: {error}")
            raise ResourceLimitError(
                error,
                resource_type='html_size',
                current_value=len(html_content),
                limit_value=MAX_TEMPLATE_SIZE
            )
        
        # Remove dangerous tags (using pre-compiled patterns)
        for tag, (pattern_pair, pattern_self) in _DANGEROUS_TAG_PATTERNS.items():
            html_content = pattern_pair.sub('', html_content)
            html_content = pattern_self.sub('', html_content)
        
        # Remove event handler attributes (using pre-compiled patterns)
        for attr, (pattern_quoted, pattern_unquoted, pattern_compact) in _DANGEROUS_ATTR_PATTERNS.items():
            html_content = pattern_quoted.sub('', html_content)
            html_content = pattern_unquoted.sub('', html_content)
            html_content = pattern_compact.sub('', html_content)
        
        # Remove dangerous protocols (using pre-compiled patterns)
        html_content = _JAVASCRIPT_PROTOCOL_PATTERN.sub('', html_content)
        html_content = _VBSCRIPT_PROTOCOL_PATTERN.sub('', html_content)
        
        logger.debug("HTML sanitization completed")
        return html_content
    
    @staticmethod
    def sanitize_css(css_content):
        """
        Sanitize CSS to prevent injection attacks.
        
        Removes dangerous CSS properties like expression(), behavior, and
        imports that could be exploited for code execution or data theft.
        
        Args:
            css_content (str): CSS string to sanitize
            
        Returns:
            str: Sanitized CSS with dangerous properties removed
            
        Raises:
            ResourceLimitError: If CSS exceeds size limit
        """
        if not css_content:
            return ""
        
        # Check size limit
        if len(css_content) > MAX_CSS_SIZE:
            error = f"CSS exceeds maximum size of {MAX_CSS_SIZE} bytes"
            logger.error(f"Security: {error}")
            raise ResourceLimitError(
                error,
                resource_type='css_size',
                current_value=len(css_content),
                limit_value=MAX_CSS_SIZE
            )
        
        # Remove dangerous properties (using pre-compiled patterns)
        for prop, pattern in _DANGEROUS_CSS_PATTERNS.items():
            css_content = pattern.sub('', css_content)
        
        # Remove @import statements (using pre-compiled pattern)
        css_content = _CSS_IMPORT_PATTERN.sub('', css_content)
        
        logger.debug("CSS sanitization completed")
        return css_content
    
    @staticmethod
    def escape_html(text):
        """
        HTML escape a text string
        
        Args:
            text: Text to escape
            
        Returns:
            str: HTML-escaped text
        """
        if not text:
            return ""
        return html.escape(str(text))
    
    @staticmethod
    def check_size_limits(html_size=0, css_size=0, component_count=0):
        """
        Check if sizes are within allowed resource limits.
        
        Args:
            html_size (int): Size of HTML in bytes (default: 0)
            css_size (int): Size of CSS in bytes (default: 0)
            component_count (int): Number of components (default: 0)
            
        Returns:
            bool: True if all limits are satisfied
            
        Raises:
            ResourceLimitError: If any limit is exceeded
        """
        if html_size > MAX_TEMPLATE_SIZE:
            error = f"HTML size {html_size} exceeds limit {MAX_TEMPLATE_SIZE}"
            logger.error(f"Security: {error}")
            raise ResourceLimitError(
                error,
                resource_type='html_size',
                current_value=html_size,
                limit_value=MAX_TEMPLATE_SIZE
            )
        
        if css_size > MAX_CSS_SIZE:
            error = f"CSS size {css_size} exceeds limit {MAX_CSS_SIZE}"
            logger.error(f"Security: {error}")
            raise ResourceLimitError(
                error,
                resource_type='css_size',
                current_value=css_size,
                limit_value=MAX_CSS_SIZE
            )
        
        if component_count > MAX_COMPONENTS:
            error = f"Component count {component_count} exceeds limit {MAX_COMPONENTS}"
            logger.error(f"Security: {error}")
            raise ResourceLimitError(
                error,
                resource_type='component_count',
                current_value=component_count,
                limit_value=MAX_COMPONENTS
            )
        
        return True
    
    @staticmethod
    def validate_template_security(html_content):
        """
        Comprehensive security validation for templates
        
        Args:
            html_content: HTML to validate
            
        Returns:
            tuple: (is_safe, warnings_list)
        """
        warnings = []
        
        # Check for dangerous tags
        for tag in DANGEROUS_HTML_TAGS:
            pattern = f'<{tag}[^>]*>'
            if re.search(pattern, html_content, re.IGNORECASE):
                warning = f"Dangerous HTML tag detected: <{tag}>"
                warnings.append(warning)
                logger.warning(f"Security: {warning}")
        
        # Check for event handlers
        for attr in DANGEROUS_ATTRIBUTES:
            pattern = f'{attr}\\s*='
            if re.search(pattern, html_content, re.IGNORECASE):
                warning = f"Event handler detected: {attr}"
                warnings.append(warning)
                logger.warning(f"Security: {warning}")
        
        # Check for dangerous protocols
        if re.search(r'javascript:', html_content, re.IGNORECASE):
            warning = "javascript: protocol detected"
            warnings.append(warning)
            logger.warning(f"Security: {warning}")
        
        if re.search(r'data:text/html', html_content, re.IGNORECASE):
            warning = "data:text/html URL detected"
            warnings.append(warning)
            logger.warning(f"Security: {warning}")
        
        is_safe = len(warnings) == 0
        if not is_safe:
            logger.error(f"Template security validation failed with {len(warnings)} warnings")
        
        return is_safe, warnings


# Convenience functions for backward compatibility
sanitize_html = SecurityValidator.sanitize_html
sanitize_css = SecurityValidator.sanitize_css
validate_field_name = SecurityValidator.validate_field_name
