"""
Template Service - Business logic for template operations

Centralizes template loading, saving, validation, and conversion.
Separates business logic from UI concerns.
"""

import sys
import os
from typing import Dict, List, Optional, Any

# Use absolute imports to avoid circular import issues
from ui.template_converter import TemplateConverter
from ui.components import Component
from utils import SecurityValidator, TemplateLoadError, TemplateSaveError
from utils.logging_config import get_logger

logger = get_logger('services.template_service')


class TemplateService:
    """
    Service for template-related business operations.
    
    Handles:
    - Template loading and validation
    - Component conversion (HTML ↔ Components)
    - Template saving with security checks
    - Sample note retrieval for previews
    """
    
    def __init__(
        self,
        collection: Any,
        security_validator: Optional[SecurityValidator] = None,
        converter: Optional[TemplateConverter] = None
    ):
        """
        Initialize the template service.
        
        Args:
            collection: Anki collection instance
            security_validator: Security validator (creates default if None)
            converter: Template converter (uses static TemplateConverter if None)
        """
        self.collection = collection
        self.security_validator = security_validator or SecurityValidator()
        self.converter = converter or TemplateConverter
    
    def load_note_type(self, note_type_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Load a note type by ID.
        
        Args:
            note_type_id: Note type ID (if None, returns first available)
            
        Returns:
            Note type dictionary or None if not found
            
        Raises:
            TemplateLoadError: If note type cannot be loaded
        """
        try:
            logger.info(f"Loading note type {note_type_id}")
            
            if note_type_id is None:
                # Get first available note type
                note_types = self.collection.models.all_names_and_ids()
                if not note_types:
                    logger.warning("No note types found in collection")
                    return None
                note_type_id = note_types[0].id
                logger.debug(f"Using first available note type: {note_type_id}")
            
            note_type = self.collection.models.get(note_type_id)
            
            if not note_type:
                raise TemplateLoadError(f"Note type {note_type_id} not found")
            
            logger.info(f"Loaded note type '{note_type.get('name', 'Unknown')}'")
            return note_type
            
        except TemplateLoadError:
            raise
        except KeyError as e:
            logger.error(f"Invalid note type ID: {e}")
            raise TemplateLoadError(f"Invalid note type ID: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error loading note type: {e}", exc_info=True)
            raise TemplateLoadError(f"Failed to load note type: {e}") from e
    
    def get_templates(self, note_type: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get templates from a note type.
        
        Args:
            note_type: Note type dictionary
            
        Returns:
            List of template dictionaries
        """
        return note_type.get('tmpls', [])
    
    def html_to_components(self, html: str, css: str = "") -> List[Component]:
        """
        Convert HTML/CSS to component list.
        
        Args:
            html: HTML template string
            css: CSS stylesheet string
            
        Returns:
            List of Component instances
            
        Raises:
            TemplateValidationError: If HTML is invalid or insecure
        """
        logger.debug(f"Converting HTML to components ({len(html)} chars)")
        
        # Security validation
        self.security_validator.validate_template_security(html)
        
        # Convert to components
        components = self.converter.html_to_components(html, css)
        logger.debug(f"Converted to {len(components)} components")
        
        return components
    
    def components_to_template(
        self,
        components: List[Component],
        side: str = 'front'
    ) -> Dict[str, str]:
        """
        Convert components to template dictionary.
        
        Args:
            components: List of Component instances
            side: 'front' or 'back'
            
        Returns:
            Dictionary with 'qfmt'/'afmt' and 'css' keys
        """
        return self.converter.create_template_dict(components, side)
    
    def save_templates(
        self,
        note_type: Dict[str, Any],
        templates: List[Dict[str, Any]]
    ) -> None:
        """
        Save templates to a note type.
        
        Args:
            note_type: Note type dictionary
            templates: List of template dictionaries to save
            
        Raises:
            TemplateSaveError: If save fails
        """
        try:
            note_type_name = note_type.get('name', 'Unknown')
            logger.info(f"Saving {len(templates)} template(s) to note type '{note_type_name}'")
            
            # Validate all templates before saving
            for i, template in enumerate(templates):
                logger.debug(f"Validating template {i+1}/{len(templates)}")
                for key in ['qfmt', 'afmt']:
                    if key in template:
                        self.security_validator.validate_template_security(
                            template[key]
                        )
            
            # Update and save
            note_type['tmpls'] = templates
            self.collection.models.save(note_type)
            
            logger.info(f"Successfully saved templates to '{note_type_name}'")
            
        except TemplateSaveError:
            raise
        except IOError as e:
            logger.error(f"Database error saving templates: {e}")
            raise TemplateSaveError(f"Database error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving templates: {e}", exc_info=True)
            raise TemplateSaveError(f"Failed to save templates: {e}") from e
    
    def get_sample_note(self, note_type: Dict[str, Any]) -> Optional[Any]:
        """
        Get a sample note for preview.
        
        Args:
            note_type: Note type dictionary
            
        Returns:
            Note instance or None if no notes found
        """
        try:
            # Find notes of this type
            note_name = note_type.get('name', '')
            note_ids = self.collection.find_notes(f'"note:{note_name}"')
            
            if note_ids:
                logger.debug(f"Found {len(note_ids)} sample note(s) for '{note_name}'")
                return self.collection.get_note(note_ids[0])
            
            logger.debug(f"No sample notes found for '{note_name}'")
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get sample note: {e}")
            return None
    
    def validate_template_dict(self, template: Dict[str, str]) -> bool:
        """
        Validate a template dictionary.
        
        Args:
            template: Template dictionary with 'qfmt'/'afmt' keys
            
        Returns:
            True if valid
            
        Raises:
            TemplateValidationError: If template is invalid
        """
        # Check required fields
        if 'qfmt' not in template and 'afmt' not in template:
            from utils import TemplateValidationError
            raise TemplateValidationError(
                "Template must have either 'qfmt' or 'afmt'"
            )
        
        # Validate security for all HTML fields
        for key in ['qfmt', 'afmt']:
            if key in template:
                self.security_validator.validate_template_security(template[key])
        
        return True
