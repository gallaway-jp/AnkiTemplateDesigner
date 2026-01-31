"""Template service for managing Anki templates.

Provides CRUD operations for templates with persistence
and Anki integration.
"""

import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from ..core.models import Template

logger = logging.getLogger("anki_template_designer.services.template_service")


class TemplateService:
    """Service for managing templates.
    
    Handles loading, saving, and managing templates with
    local file storage and Anki integration.
    
    Attributes:
        storage_path: Path to template storage directory.
    """
    
    TEMPLATES_DIR = "templates"
    TEMPLATE_EXTENSION = ".json"
    
    def __init__(self, addon_dir: Optional[str] = None) -> None:
        """Initialize the template service.
        
        Args:
            addon_dir: Base addon directory. If None, uses current module's parent.
        """
        if addon_dir is None:
            addon_dir = str(Path(__file__).parent.parent)
        
        self._addon_dir = addon_dir
        self._storage_path = os.path.join(addon_dir, self.TEMPLATES_DIR)
        self._templates: Dict[str, Template] = {}
        self._current_template: Optional[Template] = None
        
        # Ensure storage directory exists
        os.makedirs(self._storage_path, exist_ok=True)
        
        logger.debug(f"TemplateService initialized. Storage: {self._storage_path}")
    
    @property
    def storage_path(self) -> str:
        """Get the template storage path."""
        return self._storage_path
    
    @property
    def current_template(self) -> Optional[Template]:
        """Get the currently active template."""
        return self._current_template
    
    def create_template(self, name: str = "Untitled Template") -> Template:
        """Create a new template.
        
        Args:
            name: Name for the new template.
            
        Returns:
            The newly created Template.
        """
        template = Template(name=name)
        self._templates[template.id] = template
        self._current_template = template
        
        logger.debug(f"Created template: {template.id} - {name}")
        return template
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID.
        
        Args:
            template_id: The template's unique identifier.
            
        Returns:
            The Template if found, None otherwise.
        """
        # Check memory cache first
        if template_id in self._templates:
            return self._templates[template_id]
        
        # Try loading from disk
        return self.load_template(template_id)
    
    def save_template(self, template: Optional[Template] = None) -> bool:
        """Save a template to disk.
        
        Args:
            template: Template to save. Uses current template if None.
            
        Returns:
            True if save succeeded, False otherwise.
        """
        template = template or self._current_template
        
        if template is None:
            logger.warning("No template to save")
            return False
        
        try:
            template.update_modified()
            
            file_path = self._get_template_path(template.id)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
            
            self._templates[template.id] = template
            logger.debug(f"Saved template: {template.id}")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to save template {template.id}: {e}")
            return False
    
    def load_template(self, template_id: str) -> Optional[Template]:
        """Load a template from disk.
        
        Args:
            template_id: The template's unique identifier.
            
        Returns:
            The loaded Template if found, None otherwise.
        """
        file_path = self._get_template_path(template_id)
        
        if not os.path.exists(file_path):
            logger.warning(f"Template file not found: {file_path}")
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            template = Template.from_dict(data)
            self._templates[template.id] = template
            
            logger.debug(f"Loaded template: {template.id}")
            return template
            
        except (IOError, OSError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template.
        
        Args:
            template_id: The template's unique identifier.
            
        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            file_path = self._get_template_path(template_id)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if template_id in self._templates:
                del self._templates[template_id]
            
            if self._current_template and self._current_template.id == template_id:
                self._current_template = None
            
            logger.debug(f"Deleted template: {template_id}")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False
    
    def list_templates(self) -> List[Dict]:
        """List all available templates.
        
        Returns:
            List of template metadata dictionaries.
        """
        templates = []
        
        try:
            for filename in os.listdir(self._storage_path):
                if filename.endswith(self.TEMPLATE_EXTENSION):
                    template_id = filename[:-len(self.TEMPLATE_EXTENSION)]
                    template = self.get_template(template_id)
                    
                    if template:
                        templates.append({
                            "id": template.id,
                            "name": template.name,
                            "modifiedAt": template.modified_at.isoformat(),
                        })
        except (IOError, OSError) as e:
            logger.error(f"Failed to list templates: {e}")
        
        # Sort by modified date, newest first
        templates.sort(key=lambda t: t["modifiedAt"], reverse=True)
        return templates
    
    def set_current_template(self, template_id: str) -> bool:
        """Set the current active template.
        
        Args:
            template_id: The template's unique identifier.
            
        Returns:
            True if template was found and set, False otherwise.
        """
        template = self.get_template(template_id)
        
        if template:
            self._current_template = template
            logger.debug(f"Set current template: {template_id}")
            return True
        
        return False
    
    def duplicate_template(self, template_id: str, new_name: Optional[str] = None) -> Optional[Template]:
        """Duplicate an existing template.
        
        Args:
            template_id: The template to duplicate.
            new_name: Name for the duplicate. Defaults to "{name} (Copy)".
            
        Returns:
            The new duplicated Template, or None if source not found.
        """
        source = self.get_template(template_id)
        
        if source is None:
            logger.warning(f"Cannot duplicate: template not found: {template_id}")
            return None
        
        import uuid as uuid_module
        
        # Create new template from source data
        new_template = Template.from_dict(source.to_dict())
        new_template.id = str(uuid_module.uuid4())
        new_template.name = new_name or f"{source.name} (Copy)"
        new_template.created_at = datetime.now()
        new_template.modified_at = datetime.now()
        new_template.version = 1
        
        self._templates[new_template.id] = new_template
        self.save_template(new_template)
        
        logger.debug(f"Duplicated template {template_id} -> {new_template.id}")
        return new_template
    
    def _get_template_path(self, template_id: str) -> str:
        """Get the file path for a template.
        
        Args:
            template_id: The template's unique identifier.
            
        Returns:
            Absolute file path for the template.
        """
        # Sanitize template_id to prevent path traversal
        safe_id = "".join(c for c in template_id if c.isalnum() or c in "-_")
        return os.path.join(self._storage_path, f"{safe_id}{self.TEMPLATE_EXTENSION}")
