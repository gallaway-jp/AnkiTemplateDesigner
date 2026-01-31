"""
Note Type Service for Anki Template Designer.

Plan 11: Provides interface to Anki's note types, fields, and templates.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from anki.models import NotetypeDict
    from aqt.main import AnkiQt

logger = logging.getLogger("anki_template_designer.services.note_type_service")


@dataclass
class AnkiField:
    """Represents a field in an Anki note type."""
    name: str
    ordinal: int
    sticky: bool = False
    rtl: bool = False
    font: str = "Arial"
    size: int = 20
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "ordinal": self.ordinal,
            "sticky": self.sticky,
            "rtl": self.rtl,
            "font": self.font,
            "size": self.size,
            "description": self.description
        }
    
    @classmethod
    def from_anki_field(cls, field_dict: Dict[str, Any], ordinal: int) -> "AnkiField":
        """Create from Anki field dictionary."""
        return cls(
            name=field_dict.get("name", ""),
            ordinal=ordinal,
            sticky=field_dict.get("sticky", False),
            rtl=field_dict.get("rtl", False),
            font=field_dict.get("font", "Arial"),
            size=field_dict.get("size", 20),
            description=field_dict.get("description", "")
        )


@dataclass
class CardTemplate:
    """Represents a card template in an Anki note type."""
    name: str
    ordinal: int
    front: str
    back: str
    browser_font: str = ""
    browser_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "ordinal": self.ordinal,
            "front": self.front,
            "back": self.back,
            "browserFont": self.browser_font,
            "browserSize": self.browser_size
        }
    
    @classmethod
    def from_anki_template(cls, tmpl_dict: Dict[str, Any], ordinal: int) -> "CardTemplate":
        """Create from Anki template dictionary."""
        return cls(
            name=tmpl_dict.get("name", "Card"),
            ordinal=ordinal,
            front=tmpl_dict.get("qfmt", ""),  # question format
            back=tmpl_dict.get("afmt", ""),   # answer format
            browser_font=tmpl_dict.get("bfont", ""),
            browser_size=tmpl_dict.get("bsize", 0)
        )


@dataclass
class NoteType:
    """Represents an Anki note type (model)."""
    id: int
    name: str
    fields: List[AnkiField] = field(default_factory=list)
    templates: List[CardTemplate] = field(default_factory=list)
    css: str = ""
    sort_field: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "fields": [f.to_dict() for f in self.fields],
            "templates": [t.to_dict() for t in self.templates],
            "css": self.css,
            "sortField": self.sort_field
        }
    
    def get_field_names(self) -> List[str]:
        """Get list of field names."""
        return [f.name for f in self.fields]
    
    def get_template_names(self) -> List[str]:
        """Get list of template names."""
        return [t.name for t in self.templates]
    
    @classmethod
    def from_anki_model(cls, model: Dict[str, Any]) -> "NoteType":
        """Create from Anki model dictionary."""
        fields = [
            AnkiField.from_anki_field(f, i)
            for i, f in enumerate(model.get("flds", []))
        ]
        
        templates = [
            CardTemplate.from_anki_template(t, i)
            for i, t in enumerate(model.get("tmpls", []))
        ]
        
        return cls(
            id=model.get("id", 0),
            name=model.get("name", "Unknown"),
            fields=fields,
            templates=templates,
            css=model.get("css", ""),
            sort_field=model.get("sortf", 0)
        )


class NoteTypeService:
    """Service for interacting with Anki note types.
    
    Provides methods to:
    - List all note types
    - Get note type details
    - Get fields for a note type
    - Update note type templates and CSS
    - Create sample data for preview
    """
    
    def __init__(self, mw: Optional["AnkiQt"] = None) -> None:
        """Initialize the service.
        
        Args:
            mw: Anki main window instance.
        """
        self._mw = mw
        self._cache: Dict[int, NoteType] = {}
        self._cache_valid = False
    
    def set_main_window(self, mw: "AnkiQt") -> None:
        """Set the Anki main window reference.
        
        Args:
            mw: Anki main window instance.
        """
        self._mw = mw
        self._invalidate_cache()
    
    def _invalidate_cache(self) -> None:
        """Invalidate the note type cache."""
        self._cache.clear()
        self._cache_valid = False
    
    def _get_collection(self) -> Optional[Any]:
        """Get the Anki collection.
        
        Returns:
            Collection instance or None if not available.
        """
        if self._mw is None:
            return None
        return getattr(self._mw, 'col', None)
    
    def get_all_note_types(self) -> List[NoteType]:
        """Get all note types from Anki.
        
        Returns:
            List of NoteType objects.
        """
        col = self._get_collection()
        if col is None:
            logger.warning("No collection available")
            return []
        
        try:
            models = col.models.all()
            note_types = []
            
            for model in models:
                nt = NoteType.from_anki_model(model)
                self._cache[nt.id] = nt
                note_types.append(nt)
            
            self._cache_valid = True
            logger.debug(f"Loaded {len(note_types)} note types")
            return note_types
            
        except Exception as e:
            logger.error(f"Failed to get note types: {e}")
            return []
    
    def get_note_type(self, note_type_id: int) -> Optional[NoteType]:
        """Get a specific note type by ID.
        
        Args:
            note_type_id: The note type ID.
            
        Returns:
            NoteType or None if not found.
        """
        # Check cache first
        if note_type_id in self._cache:
            return self._cache[note_type_id]
        
        col = self._get_collection()
        if col is None:
            return None
        
        try:
            model = col.models.get(note_type_id)
            if model is None:
                return None
            
            nt = NoteType.from_anki_model(model)
            self._cache[note_type_id] = nt
            return nt
            
        except Exception as e:
            logger.error(f"Failed to get note type {note_type_id}: {e}")
            return None
    
    def get_note_type_by_name(self, name: str) -> Optional[NoteType]:
        """Get a note type by name.
        
        Args:
            name: The note type name.
            
        Returns:
            NoteType or None if not found.
        """
        col = self._get_collection()
        if col is None:
            return None
        
        try:
            model = col.models.by_name(name)
            if model is None:
                return None
            
            nt = NoteType.from_anki_model(model)
            self._cache[nt.id] = nt
            return nt
            
        except Exception as e:
            logger.error(f"Failed to get note type '{name}': {e}")
            return None
    
    def get_fields(self, note_type_id: int) -> List[AnkiField]:
        """Get fields for a note type.
        
        Args:
            note_type_id: The note type ID.
            
        Returns:
            List of AnkiField objects.
        """
        nt = self.get_note_type(note_type_id)
        if nt is None:
            return []
        return nt.fields
    
    def get_templates(self, note_type_id: int) -> List[CardTemplate]:
        """Get card templates for a note type.
        
        Args:
            note_type_id: The note type ID.
            
        Returns:
            List of CardTemplate objects.
        """
        nt = self.get_note_type(note_type_id)
        if nt is None:
            return []
        return nt.templates
    
    def get_css(self, note_type_id: int) -> str:
        """Get CSS for a note type.
        
        Args:
            note_type_id: The note type ID.
            
        Returns:
            CSS string.
        """
        nt = self.get_note_type(note_type_id)
        if nt is None:
            return ""
        return nt.css
    
    def update_template(
        self,
        note_type_id: int,
        template_ordinal: int,
        front: Optional[str] = None,
        back: Optional[str] = None
    ) -> bool:
        """Update a card template.
        
        Args:
            note_type_id: The note type ID.
            template_ordinal: The template ordinal (0-based index).
            front: New front template HTML (optional).
            back: New back template HTML (optional).
            
        Returns:
            True if successful.
        """
        col = self._get_collection()
        if col is None:
            return False
        
        try:
            model = col.models.get(note_type_id)
            if model is None:
                logger.error(f"Note type {note_type_id} not found")
                return False
            
            tmpls = model.get("tmpls", [])
            if template_ordinal >= len(tmpls):
                logger.error(f"Template ordinal {template_ordinal} out of range")
                return False
            
            tmpl = tmpls[template_ordinal]
            
            if front is not None:
                tmpl["qfmt"] = front
            if back is not None:
                tmpl["afmt"] = back
            
            col.models.save(model)
            self._invalidate_cache()
            
            logger.info(f"Updated template {template_ordinal} for note type {note_type_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            return False
    
    def update_css(self, note_type_id: int, css: str) -> bool:
        """Update CSS for a note type.
        
        Args:
            note_type_id: The note type ID.
            css: New CSS string.
            
        Returns:
            True if successful.
        """
        col = self._get_collection()
        if col is None:
            return False
        
        try:
            model = col.models.get(note_type_id)
            if model is None:
                logger.error(f"Note type {note_type_id} not found")
                return False
            
            model["css"] = css
            col.models.save(model)
            self._invalidate_cache()
            
            logger.info(f"Updated CSS for note type {note_type_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update CSS: {e}")
            return False
    
    def get_sample_data(self, note_type_id: int) -> Dict[str, str]:
        """Get sample data for template preview.
        
        Uses field names as placeholder values.
        
        Args:
            note_type_id: The note type ID.
            
        Returns:
            Dictionary mapping field names to sample values.
        """
        nt = self.get_note_type(note_type_id)
        if nt is None:
            return {}
        
        sample = {}
        for f in nt.fields:
            # Create sample text based on field name
            sample[f.name] = f"[{f.name}]"
        
        return sample
    
    def get_sample_note_data(self, note_type_id: int) -> Optional[Dict[str, str]]:
        """Get sample data from an actual note.
        
        Finds a note of the given type and extracts field values.
        
        Args:
            note_type_id: The note type ID.
            
        Returns:
            Dictionary mapping field names to actual values, or None.
        """
        col = self._get_collection()
        if col is None:
            return None
        
        try:
            # Find a note with this model
            note_ids = col.find_notes(f"mid:{note_type_id}")
            if not note_ids:
                return None
            
            note = col.get_note(note_ids[0])
            nt = self.get_note_type(note_type_id)
            if nt is None:
                return None
            
            data = {}
            for i, f in enumerate(nt.fields):
                if i < len(note.fields):
                    data[f.name] = note.fields[i]
                else:
                    data[f.name] = ""
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get sample note data: {e}")
            return None
    
    def render_preview(
        self,
        note_type_id: int,
        template_ordinal: int = 0,
        field_values: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Render a card preview.
        
        Args:
            note_type_id: The note type ID.
            template_ordinal: Which template to render.
            field_values: Field values to use (uses sample if not provided).
            
        Returns:
            Dictionary with 'front' and 'back' HTML.
        """
        nt = self.get_note_type(note_type_id)
        if nt is None:
            return {"front": "", "back": ""}
        
        if template_ordinal >= len(nt.templates):
            return {"front": "", "back": ""}
        
        tmpl = nt.templates[template_ordinal]
        
        # Get field values
        if field_values is None:
            field_values = self.get_sample_data(note_type_id)
        
        # Simple template rendering (replace {{field}} with values)
        front = tmpl.front
        back = tmpl.back
        
        for field_name, value in field_values.items():
            # Replace {{field}} patterns
            front = front.replace(f"{{{{{field_name}}}}}", value)
            back = back.replace(f"{{{{{field_name}}}}}", value)
            
            # Also handle special patterns
            front = front.replace(f"{{{{edit:{field_name}}}}}", value)
            back = back.replace(f"{{{{edit:{field_name}}}}}", value)
        
        # Replace {{FrontSide}} in back with rendered front
        back = back.replace("{{FrontSide}}", front)
        
        return {
            "front": front,
            "back": back,
            "css": nt.css
        }


# Global service instance
_global_service: Optional[NoteTypeService] = None


def get_note_type_service() -> Optional[NoteTypeService]:
    """Get the global note type service.
    
    Returns:
        NoteTypeService instance or None.
    """
    return _global_service


def init_note_type_service(mw: Optional["AnkiQt"] = None) -> NoteTypeService:
    """Initialize the global note type service.
    
    Args:
        mw: Anki main window instance.
        
    Returns:
        Initialized NoteTypeService.
    """
    global _global_service
    _global_service = NoteTypeService(mw)
    return _global_service
