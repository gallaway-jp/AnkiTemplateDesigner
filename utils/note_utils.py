"""
Note utilities for working with Anki notes and note types
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger('template_designer.note_utils')


class NoteUtils:
    """Utility functions for working with Anki notes"""
    
    @staticmethod
    def get_sample_note(mw, note_type: Optional[Dict[str, Any]] = None):
        """
        Get a sample note for preview purposes.
        
        Attempts to find an existing note of the given type. If none exists,
        returns None (caller should use default sample data).
        
        Args:
            mw: Anki main window instance
            note_type (dict, optional): Note type dictionary with 'name' key.
                                       If None, returns None.
        
        Returns:
            Note object if found, None otherwise
            
        Example:
            >>> note = NoteUtils.get_sample_note(mw, note_type)
            >>> if note:
            ...     field_data = {fld['name']: note[fld['name']] for fld in note_type['flds']}
            ... else:
            ...     field_data = NoteUtils.get_default_field_data()
        """
        if not note_type or not mw or not hasattr(mw, 'col'):
            return None
        
        try:
            # Try to find an existing note of this type
            note_type_name = note_type.get('name')
            if not note_type_name:
                return None
            
            note_ids = mw.col.find_notes(f'"note:{note_type_name}"')
            
            if note_ids:
                # Get the first note
                note = mw.col.get_note(note_ids[0])
                logger.debug(f"Found sample note for type '{note_type_name}'")
                return note
        except Exception as e:
            logger.warning(f"Failed to get sample note: {e}")
        
        # Return None to indicate sample data should be used
        return None
    
    @staticmethod
    def get_default_field_data() -> Dict[str, str]:
        """
        Get default sample field data for templates.
        
        Returns a dictionary with standard Anki fields populated with
        sample text suitable for preview rendering.
        
        Returns:
            dict: Dictionary mapping field names to sample content
            
        Example:
            >>> data = NoteUtils.get_default_field_data()
            >>> print(data['Front'])
            'Sample Front Text'
        """
        return {
            'Front': 'Sample Front Text',
            'Back': 'Sample Back Text',
            'Extra': 'Additional information',
            'Text': 'Sample text content',
            'Image': '[Image placeholder]',
            'Audio': '[Audio placeholder]',
            'Tags': 'sample, preview'
        }
    
    @staticmethod
    def get_templates(note_type: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Safely extract templates from a note type.
        
        Args:
            note_type (dict, optional): Note type dictionary
        
        Returns:
            list: List of template dictionaries, or empty list if note_type is None
            
        Example:
            >>> templates = NoteUtils.get_templates(note_type)
            >>> for template in templates:
            ...     print(template['name'])
        """
        if not note_type:
            return []
        
        return note_type.get('tmpls', [])
    
    @staticmethod
    def get_field_names(note_type: Optional[Dict[str, Any]]) -> List[str]:
        """
        Extract field names from a note type.
        
        Args:
            note_type (dict, optional): Note type dictionary
        
        Returns:
            list: List of field names, or empty list if note_type is None
            
        Example:
            >>> fields = NoteUtils.get_field_names(note_type)
            >>> print(fields)
            ['Front', 'Back', 'Extra']
        """
        if not note_type:
            return []
        
        fields = note_type.get('flds', [])
        return [field.get('name', '') for field in fields]
    
    @staticmethod
    def validate_note_type(note_type: Optional[Dict[str, Any]]) -> bool:
        """
        Validate that a note type has the required structure.
        
        Args:
            note_type (dict, optional): Note type dictionary to validate
        
        Returns:
            bool: True if note_type is valid, False otherwise
            
        Example:
            >>> if NoteUtils.validate_note_type(note_type):
            ...     templates = NoteUtils.get_templates(note_type)
        """
        if not note_type:
            return False
        
        required_keys = ['name', 'flds', 'tmpls']
        return all(key in note_type for key in required_keys)
    
    @staticmethod
    def get_note_field_data(note, note_type: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Extract field data from a note as a dictionary.
        
        Args:
            note: Anki note object
            note_type (dict, optional): Note type dictionary for field names.
                                       If None, uses note's fields directly.
        
        Returns:
            dict: Dictionary mapping field names to values
            
        Example:
            >>> note = mw.col.get_note(note_id)
            >>> data = NoteUtils.get_note_field_data(note, note_type)
            >>> print(data['Front'])
        """
        if not note:
            return NoteUtils.get_default_field_data()
        
        field_data = {}
        
        if note_type:
            # Use note type to get field names
            for field_dict in note_type.get('flds', []):
                field_name = field_dict.get('name', '')
                if field_name:
                    field_data[field_name] = note.get(field_name, '')
        else:
            # Use note's fields directly if available
            if hasattr(note, 'keys'):
                for key in note.keys():
                    field_data[key] = note[key]
        
        return field_data
