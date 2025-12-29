"""
Template utilities for processing and validating templates
"""

import re
import logging
from .security import SecurityValidator

# Configure logging
logger = logging.getLogger('template_designer.template_utils')


class TemplateUtils:
    """Utility functions for template processing"""
    
    @staticmethod
    def validate_security(template_html):
        """
        Validate template for security issues.
        
        Delegates to SecurityValidator for consistent security checks.
        
        Args:
            template_html (str): Template HTML string
        
        Returns:
            tuple: (is_safe, security_warnings) where is_safe is bool
                   and security_warnings is list of warning strings
        """
        # Delegate to centralized security validator
        return SecurityValidator.validate_template_security(template_html)
    
    @staticmethod
    def extract_fields(template_html: str) -> set:
        """
        Extract all field references from a template.
        
        Parses template HTML to find all Anki field references in the
        {{FieldName}} format, including conditional fields.
        
        Args:
            template_html (str): Template HTML string
        
        Returns:
            set: Set of field names referenced in the template
        
        Example:
            >>> html = '<div>{{Front}}</div>{{#Extra}}{{Extra}}{{/Extra}}'
            >>> fields = TemplateUtils.extract_fields(html)
            >>> print(sorted(fields))
            ['Extra', 'Front']
        """
        fields = set()
        
        # Match {{FieldName}} patterns
        pattern = r'\{\{([^{}]+)\}\}'
        matches = re.findall(pattern, template_html)
        
        for match in matches:
            # Remove special prefixes
            field = match.strip()
            
            # Skip special fields
            if field.startswith('#') or field.startswith('^') or field.startswith('/'):
                # Extract field name from conditional
                field = field[1:]
            
            # Skip special Anki fields
            if field not in ['FrontSide', 'Tags', 'Type', 'Deck', 'Subdeck', 'Card']:
                fields.add(field)
        
        return fields
    
    @staticmethod
    def validate_template(template_html: str) -> tuple:
        """
        Validate template syntax and security.
        
        Checks for:
        - Security issues (XSS, dangerous patterns)
        - Unclosed conditional tags
        - Mismatched conditional pairs
        - Empty field references
        
        Args:
            template_html (str): Template HTML string
        
        Returns:
            tuple: (is_valid, error_messages) where is_valid is bool
                   and error_messages is list of error strings
        
        Example:
            >>> html = '<div>{{Front}}</div>{{#Extra}}content{{/Wrong}}'
            >>> valid, errors = TemplateUtils.validate_template(html)
            >>> print(valid)
            False
            >>> print(errors[0])
            'Mismatched closing tag for field: Wrong'
        """
        errors = []
        
        # Security validation first
        is_safe, security_warnings = TemplateUtils.validate_security(template_html)
        if not is_safe:
            errors.extend(security_warnings)
            logger.error(f"Security validation failed: {len(security_warnings)} issues")
        
        # Check for unclosed conditional tags
        conditional_stack = []
        
        # Find all conditional tags
        open_pattern = r'\{\{[#^]([^{}]+)\}\}'
        close_pattern = r'\{\{/([^{}]+)\}\}'
        
        open_matches = [(m.group(1), m.start()) for m in re.finditer(open_pattern, template_html)]
        close_matches = [(m.group(1), m.start()) for m in re.finditer(close_pattern, template_html)]
        
        # Check if conditionals are properly paired
        for field, pos in open_matches:
            conditional_stack.append(field)
        
        for field, pos in close_matches:
            if not conditional_stack or conditional_stack[-1] != field:
                errors.append(f"Mismatched closing tag for field: {field}")
            else:
                conditional_stack.pop()
        
        if conditional_stack:
            errors.append(f"Unclosed conditional tags: {', '.join(conditional_stack)}")
        
        # Check for empty field references
        if re.search(r'\{\{\s*\}\}', template_html):
            errors.append("Empty field reference found: {{}}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def get_template_info(template_dict: dict) -> dict:
        """
        Get comprehensive information about a template.
        
        Analyzes both front and back templates to extract fields,
        validate syntax, and provide a summary of the template.
        
        Args:
            template_dict (dict): Template dictionary with 'qfmt', 'afmt', 'name'
        
        Returns:
            dict: Dictionary containing:
                - name: Template name
                - front_fields: List of fields on front
                - back_fields: List of fields on back
                - all_fields: Combined list of all fields
                - front_valid: Whether front template is valid
                - back_valid: Whether back template is valid
                - front_errors: List of front template errors
                - back_errors: List of back template errors
                - is_valid: Whether entire template is valid
        """
        front_fields = TemplateUtils.extract_fields(template_dict.get('qfmt', ''))
        back_fields = TemplateUtils.extract_fields(template_dict.get('afmt', ''))
        
        front_valid, front_errors = TemplateUtils.validate_template(template_dict.get('qfmt', ''))
        back_valid, back_errors = TemplateUtils.validate_template(template_dict.get('afmt', ''))
        
        return {
            'name': template_dict.get('name', 'Unnamed'),
            'front_fields': list(front_fields),
            'back_fields': list(back_fields),
            'all_fields': list(front_fields | back_fields),
            'front_valid': front_valid,
            'back_valid': back_valid,
            'front_errors': front_errors,
            'back_errors': back_errors,
            'is_valid': front_valid and back_valid
        }
    
    @staticmethod
    def optimize_template(template_html: str) -> str:
        """
        Optimize template HTML by removing unnecessary content.
        
        Removes:
        - Excessive whitespace and blank lines
        - HTML comments
        - Leading/trailing whitespace
        
        Args:
            template_html (str): Template HTML string
        
        Returns:
            str: Optimized template HTML
        """
        # Remove excessive whitespace
        html = re.sub(r'\n\s*\n', '\n', template_html)
        
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        return html.strip()
