"""
Template converter - converts between visual components and HTML/CSS
"""

import re
import html

from utils.security import (
    SecurityValidator, sanitize_html as sec_sanitize_html, 
    sanitize_css as sec_sanitize_css,
    validate_field_name as sec_validate_field_name, 
    MAX_TEMPLATE_SIZE, MAX_CSS_SIZE, 
    MAX_COMPONENTS, MAX_FIELD_NAME_LENGTH,
    DANGEROUS_HTML_TAGS, DANGEROUS_CSS_PROPS
)
from utils.exceptions import ResourceLimitError

from .components import (
    Component, TextFieldComponent, ImageFieldComponent,
    DividerComponent, HeadingComponent, ContainerComponent,
    ConditionalComponent, ComponentType, Alignment
)

# Re-export for backward compatibility
DANGEROUS_TAGS = DANGEROUS_HTML_TAGS
DANGEROUS_CSS_PROPS = DANGEROUS_CSS_PROPS


def sanitize_html(html_content):
    """Sanitize HTML - wrapper for SecurityValidator"""
    return sec_sanitize_html(html_content)


def sanitize_css(css_content):
    """Sanitize CSS - wrapper for SecurityValidator"""
    return sec_sanitize_css(css_content)


def validate_field_name(field_name):
    """Validate field name - wrapper for SecurityValidator"""
    return sec_validate_field_name(field_name)



class TemplateConverter:
    """
    Converts between visual components and HTML/CSS templates.
    
    This class provides bidirectional conversion between the visual component
    representation used in the designer and the HTML/CSS format used by Anki.
    All conversions include security sanitization to prevent XSS attacks.
    """
    
    @staticmethod
    def components_to_html(components):
        """
        Convert list of visual components to HTML template.
        
        Generates HTML markup for each component and wraps them in container divs.
        Validates all field names and sanitizes output to prevent security issues.
        
        Args:
            components (list): List of Component objects to convert.
                              Each component must have a to_html() method.
        
        Returns:
            str: Sanitized HTML string with all components rendered.
                 Each component is wrapped in a div with class "component component-N".
        
        Raises:
            ResourceLimitError: If number of components exceeds MAX_COMPONENTS (1000)
            TemplateValidationError: If any component has invalid field name
        
        Example:
            >>> components = [TextFieldComponent("Front"), ImageFieldComponent("Image")]
            >>> html = TemplateConverter.components_to_html(components)
            >>> print(html)
            <div class="component component-0">
            <div class="text-field">{{Front}}</div>
            </div>
            ...
        """
        # Check component count limit
        if len(components) > MAX_COMPONENTS:
            raise ResourceLimitError(
                f"Number of components exceeds maximum of {MAX_COMPONENTS}",
                resource_type='component_count',
                current_value=len(components),
                limit_value=MAX_COMPONENTS
            )
        
        # Validate all field names upfront (faster than in loop)
        for component in components:
            if hasattr(component, 'field_name') and component.field_name:
                validate_field_name(component.field_name)
        
        # Generate HTML using list comprehension (faster than loop + append)
        html_parts = [
            f'<div class="component component-{i}">\n{component.to_html()}\n</div>'
            for i, component in enumerate(components)
        ]
        
        result = '\n\n'.join(html_parts)
        # Single sanitization pass at the end (more efficient)
        return sanitize_html(result)
    
    @staticmethod
    def components_to_css(components):
        """
        Convert list of visual components to CSS stylesheet.
        
        Generates CSS rules for each component including base card styles,
        component-specific styles, and utility styles. Output is sanitized
        to prevent CSS injection attacks.
        
        Args:
            components (list): List of Component objects to convert.
                              Each component must have a to_css(selector) method.
        
        Returns:
            str: Sanitized CSS string containing:
                 - Base card styles (font, color, padding)
                 - Component-specific styles (fonts, sizes, alignment)
                 - Utility styles (responsive images, dividers)
        
        Raises:
            ResourceLimitError: If number of components exceeds MAX_COMPONENTS (1000)
                               or if generated CSS exceeds MAX_CSS_SIZE (500KB)
        
        Example:
            >>> components = [TextFieldComponent("Front", font_size=24)]
            >>> css = TemplateConverter.components_to_css(components)
            >>> print(css)
            /* Auto-generated styles from Visual Template Builder */
            .card {
                font-family: Arial, sans-serif;
                ...
            }
            .component-0 {
                font-size: 24px;
            }
        """
        # Check component count limit
        if len(components) > MAX_COMPONENTS:
            raise ResourceLimitError(
                f"Number of components exceeds maximum of {MAX_COMPONENTS}",
                resource_type='component_count',
                current_value=len(components),
                limit_value=MAX_COMPONENTS
            )
        
        # Base card styles (constant)
        base_styles = """/* Auto-generated styles from Visual Template Builder */
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
    padding: 20px;
}"""
        
        # Utility styles (constant)
        utility_styles = """
/* Utility styles */
img {
    max-width: 100%;
    height: auto;
}

.field-label {
    font-weight: bold;
    margin-bottom: 5px;
}

.divider {
    border: none;
    margin: 20px 0;
}"""
        
        # Generate component styles using list comprehension
        component_styles = [
            component.to_css(f'.component-{i}')
            for i, component in enumerate(components)
        ]
        
        # Join all parts (more efficient than multiple appends)
        all_styles = [base_styles] + component_styles + [utility_styles]
        result = '\n\n'.join(all_styles)
        
        # Single sanitization pass
        return sanitize_css(result)
    
    @staticmethod
    def html_to_components(html, css=""):
        """
        Convert HTML template to visual components (best-effort conversion).
        
        Parses HTML and CSS to reconstruct the visual component representation.
        This is a simplified parser that handles common Anki template patterns
        but may not handle all edge cases perfectly.
        
        Args:
            html (str): HTML template string to parse
            css (str, optional): CSS stylesheet string. Defaults to "".
        
        Returns:
            list: List of Component objects reconstructed from the HTML.
                  May not perfectly match original components if HTML was
                  manually edited or uses unsupported patterns.
        
        Note:
            This parser uses heuristics and may not handle:
            - Complex nested structures
            - Custom CSS beyond basic styling
            - Non-standard HTML patterns
            - JavaScript-generated content
            
            For best results, only parse HTML generated by components_to_html().
        
        Example:
            >>> html = '<div class="text-field">{{Front}}</div>'
            >>> components = TemplateConverter.html_to_components(html)
            >>> print(components[0].field_name)
            'Front'
        """
        # Sanitize inputs
        html = sanitize_html(html)
        css = sanitize_css(css)
        
        components = []
        
        # Try to extract field references
        field_pattern = r'\{\{([^{}]+)\}\}'
        fields = re.findall(field_pattern, html)
        
        # Simple heuristic: create components based on common patterns
        lines = html.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for heading tags
            h_match = re.match(r'<h(\d+)[^>]*>(.*?)</h\1>', line)
            if h_match:
                level = int(h_match.group(1))
                content = h_match.group(2)
                
                # Extract field if present
                field_match = re.search(r'\{\{([^{}]+)\}\}', content)
                if field_match:
                    field_name = field_match.group(1)
                    comp = HeadingComponent(field_name, level)
                    components.append(comp)
                continue
            
            # Check for hr/divider
            if '<hr' in line or '<div class="divider"' in line:
                components.append(DividerComponent())
                continue
            
            # Check for images
            if '<img' in line:
                # Try to extract field from src
                src_match = re.search(r'src="\{\{([^{}]+)\}\}"', line)
                if src_match:
                    field_name = src_match.group(1)
                    components.append(ImageFieldComponent(field_name))
                else:
                    components.append(ImageFieldComponent())
                continue
            
            # Check for field references
            field_match = re.search(r'\{\{([^{}#^/]+)\}\}', line)
            if field_match:
                field_name = field_match.group(1).strip()
                # Skip special fields
                if field_name not in ['FrontSide']:
                    components.append(TextFieldComponent(field_name))
        
        # If no components were created but we have fields, create basic text components
        if not components and fields:
            for field in fields:
                if field.strip() and not field.startswith('#') and not field.startswith('^') and not field.startswith('/'):
                    clean_field = field.strip()
                    if clean_field not in ['FrontSide']:
                        components.append(TextFieldComponent(clean_field))
        
        # If still no components, create a default one
        if not components:
            components.append(TextFieldComponent("Front"))
        
        return components
    
    @staticmethod
    def create_template_dict(components, side='front'):
        """Create a complete template dictionary from components"""
        html = TemplateConverter.components_to_html(components)
        css = TemplateConverter.components_to_css(components)
        
        # Create dict with both sides - important for preview
        template_dict = {
            'qfmt': html if side == 'front' else '{{FrontSide}}',
            'afmt': html if side == 'back' else '{{FrontSide}}<hr>',
            'css': css
        }
        
        return template_dict
    
    @staticmethod
    def extract_available_fields(note_type):
        """Extract available field names from note type"""
        if not note_type:
            return []
        
        fields = note_type.get('flds', [])
        return [field['name'] for field in fields]
