"""
Base renderer interface
"""

from abc import ABC, abstractmethod
import logging
import re

logger = logging.getLogger('template_designer.renderer')


class BaseRenderer(ABC):
    """Base class for template renderers"""
    
    def __init__(self):
        self.sample_data = self._get_sample_data()
    
    def render(self, template_dict, note=None, side='front', **kwargs):
        """
        Render a template with the given note data
        
        Args:
            template_dict: Dictionary containing template information
                - qfmt: Front template HTML
                - afmt: Back template HTML
                - css: Template CSS
            note: Note object with field data (optional)
            side: 'front' or 'back'
            **kwargs: Additional rendering options
        
        Returns:
            Rendered HTML string
            
        Raises:
            ValueError: If template is empty or invalid
            Exception: If rendering fails
        """
        try:
            logger.debug(f"Rendering {side} template")
            
            # Get template HTML for the specified side
            template_html = self._get_template_html(template_dict, side)
            
            if not template_html:
                logger.warning(f"Empty template for side '{side}'")
                return ""
            
            # Get CSS
            css = template_dict.get('css', '')
            
            # Prepare note data
            data = self._prepare_note_data(note, template_dict, side)
            
            # Apply template to get content
            content_html = self._apply_template(template_html, data)
            
            # Build final HTML (platform-specific)
            result = self._build_html(content_html, css, **kwargs)
            
            logger.debug(f"Rendered {side} template ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Render failed for {side}: {e}", exc_info=True)
            raise
    
    def _get_template_html(self, template_dict, side):
        """
        Extract the appropriate template HTML based on side
        
        Args:
            template_dict: Template dictionary
            side: 'front' or 'back'
            
        Returns:
            Template HTML string
        """
        if side == 'front':
            return template_dict.get('qfmt', '')
        else:
            return template_dict.get('afmt', '')
    
    def _prepare_note_data(self, note, template_dict, side):
        """
        Prepare note data for template rendering
        
        Args:
            note: Note object
            template_dict: Template dictionary
            side: 'front' or 'back'
            
        Returns:
            Dictionary of field data
        """
        data = self._get_note_data(note)
        
        # Add FrontSide field for back template
        if side == 'back':
            front_html = self._apply_template(
                template_dict.get('qfmt', ''), 
                data
            )
            data['FrontSide'] = front_html
        
        return data
    
    @abstractmethod
    def _build_html(self, content_html, css, **kwargs):
        """
        Build the final HTML output (platform-specific)
        
        Args:
            content_html: Rendered content HTML
            css: Template CSS
            **kwargs: Additional platform-specific options
            
        Returns:
            Complete HTML document
        """
        pass
    
    def _get_sample_data(self):
        """Get sample note data for preview"""
        return {
            'Front': 'Sample Front Text',
            'Back': 'Sample Back Text',
            'Extra': 'Additional information',
            'Tags': 'sample tag1 tag2',
            'Type': 'Sample Type'
        }
    
    def _apply_template(self, template_html, data):
        """
        Apply template variables to HTML
        
        Args:
            template_html: Template HTML string with {{Field}} placeholders
            data: Dictionary of field name -> value mappings
        
        Returns:
            HTML with placeholders replaced
            
        Raises:
            re.error: If template contains invalid regex pattern
            Exception: If template application fails
        """
        try:
            html = template_html
            
            # Replace field placeholders
            for field, value in data.items():
                html = html.replace(f'{{{{{field}}}}}', str(value))
            
            # Handle conditional fields
            # {{#Field}}...{{/Field}} - show if field has content
            # {{^Field}}...{{/Field}} - show if field is empty
            
            # Positive conditionals
            for field, value in data.items():
                pattern = r'\{\{#' + re.escape(field) + r'\}\}(.*?)\{\{/' + re.escape(field) + r'\}\}'
                if value:
                    html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
                else:
                    html = re.sub(pattern, '', html, flags=re.DOTALL)
            
            # Negative conditionals
            for field, value in data.items():
                pattern = r'\{\{\^' + re.escape(field) + r'\}\}(.*?)\{\{/' + re.escape(field) + r'\}\}'
                if not value:
                    html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
                else:
                    html = re.sub(pattern, '', html, flags=re.DOTALL)
            
            # Log any unreplaced placeholders
            unreplaced = re.findall(r'\{\{([^}]+)\}\}', html)
            if unreplaced:
                logger.debug(f"Unreplaced template fields: {unreplaced}")
            
            return html
            
        except re.error as e:
            logger.error(f"Invalid template regex pattern: {e}")
            raise ValueError(f"Invalid template pattern: {e}") from e
        except Exception as e:
            logger.error(f"Template application failed: {e}", exc_info=True)
            raise
    
    def _get_note_data(self, note):
        """
        Extract field data from a note
        
        Args:
            note: Anki note object
        
        Returns:
            Dictionary of field name -> value mappings
        """
        if not note:
            return self.sample_data
        
        data = {}
        for field_name, field_value in note.items():
            data[field_name] = field_value
        
        # Add special fields
        if hasattr(note, 'tags'):
            data['Tags'] = ' '.join(note.tags)
        
        return data
