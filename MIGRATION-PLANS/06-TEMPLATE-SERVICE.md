# Plan 06: Template Service

## Objective
Implement the core template service for loading, saving, and managing Anki templates.

---

## Prerequisites
- [ ] Plans 01-05 completed and tested
- [ ] UI shell functional
- [ ] Bridge communication working

---

## Step 6.1: Create Template Data Models

### Task
Define data models for template representation.

### Implementation

**anki_template_designer/core/models.py**
```python
"""Data models for template representation.

This module defines the core data structures used throughout
the template designer for representing templates, components,
and related data.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class ComponentType(Enum):
    """Enumeration of available component types."""
    CONTAINER = "container"
    ROW = "row"
    COLUMN = "column"
    TEXT = "text"
    HEADING = "heading"
    FIELD = "field"
    CLOZE = "cloze"
    IMAGE = "image"
    AUDIO = "audio"


@dataclass
class ComponentStyle:
    """Style properties for a component.
    
    Attributes:
        background: Background color or image.
        color: Text color.
        font_size: Font size (with units, e.g., "16px").
        font_family: Font family name.
        padding: Padding value.
        margin: Margin value.
        border: Border specification.
        border_radius: Border radius value.
        custom_css: Additional custom CSS.
    """
    background: Optional[str] = None
    color: Optional[str] = None
    font_size: Optional[str] = None
    font_family: Optional[str] = None
    padding: Optional[str] = None
    margin: Optional[str] = None
    border: Optional[str] = None
    border_radius: Optional[str] = None
    custom_css: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in {
            "background": self.background,
            "color": self.color,
            "fontSize": self.font_size,
            "fontFamily": self.font_family,
            "padding": self.padding,
            "margin": self.margin,
            "border": self.border,
            "borderRadius": self.border_radius,
            "customCss": self.custom_css,
        }.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentStyle":
        """Create instance from dictionary."""
        return cls(
            background=data.get("background"),
            color=data.get("color"),
            font_size=data.get("fontSize"),
            font_family=data.get("fontFamily"),
            padding=data.get("padding"),
            margin=data.get("margin"),
            border=data.get("border"),
            border_radius=data.get("borderRadius"),
            custom_css=data.get("customCss"),
        )


@dataclass
class Component:
    """A template component (block).
    
    Attributes:
        id: Unique identifier for the component.
        type: Component type from ComponentType enum.
        content: Text content (for text-based components).
        field_name: Anki field name (for field components).
        style: Style properties.
        children: Child components (for containers).
        attributes: Additional attributes.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: ComponentType = ComponentType.CONTAINER
    content: str = ""
    field_name: Optional[str] = None
    style: ComponentStyle = field(default_factory=ComponentStyle)
    children: List["Component"] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "fieldName": self.field_name,
            "style": self.style.to_dict(),
            "children": [c.to_dict() for c in self.children],
            "attributes": self.attributes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Component":
        """Create instance from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            type=ComponentType(data.get("type", "container")),
            content=data.get("content", ""),
            field_name=data.get("fieldName"),
            style=ComponentStyle.from_dict(data.get("style", {})),
            children=[cls.from_dict(c) for c in data.get("children", [])],
            attributes=data.get("attributes", {}),
        )


@dataclass
class TemplateSide:
    """One side (front or back) of a template.
    
    Attributes:
        html: Raw HTML content.
        components: Component tree representation.
    """
    html: str = ""
    components: List[Component] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "html": self.html,
            "components": [c.to_dict() for c in self.components],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateSide":
        """Create instance from dictionary."""
        return cls(
            html=data.get("html", ""),
            components=[Component.from_dict(c) for c in data.get("components", [])],
        )


@dataclass
class Template:
    """Complete Anki card template.
    
    Attributes:
        id: Unique template identifier.
        name: Template name.
        front: Front side of the card.
        back: Back side of the card.
        css: Shared CSS styles.
        note_type: Associated note type name.
        created_at: Creation timestamp.
        modified_at: Last modification timestamp.
        version: Template version number.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Template"
    front: TemplateSide = field(default_factory=TemplateSide)
    back: TemplateSide = field(default_factory=TemplateSide)
    css: str = ""
    note_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "front": self.front.to_dict(),
            "back": self.back.to_dict(),
            "css": self.css,
            "noteType": self.note_type,
            "createdAt": self.created_at.isoformat(),
            "modifiedAt": self.modified_at.isoformat(),
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create instance from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Template"),
            front=TemplateSide.from_dict(data.get("front", {})),
            back=TemplateSide.from_dict(data.get("back", {})),
            css=data.get("css", ""),
            note_type=data.get("noteType"),
            created_at=datetime.fromisoformat(data.get("createdAt", datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(data.get("modifiedAt", datetime.now().isoformat())),
            version=data.get("version", 1),
        )
    
    def update_modified(self) -> None:
        """Update the modification timestamp."""
        self.modified_at = datetime.now()
        self.version += 1
```

### Quality Checks

#### Security
- [ ] UUID generation for IDs (unpredictable)
- [ ] No sensitive data in models
- [ ] Input validation in from_dict methods

#### Performance
- [ ] Dataclasses for efficiency
- [ ] Lazy loading not needed (small objects)

#### Best Practices
- [ ] Type hints throughout
- [ ] Default factory for mutable defaults
- [ ] Enum for type safety

#### Maintainability
- [ ] Clear data structure
- [ ] Easy to extend with new fields

#### Documentation
- [ ] All classes documented
- [ ] All attributes documented

#### Testing
- [ ] Serialization round-trip testable
- [ ] Default values work correctly

#### Accessibility
- [ ] N/A (data models)

#### Scalability
- [ ] Can add more component types
- [ ] Can add more style properties

#### Compatibility
- [ ] Python 3.9+ dataclasses

#### Error Handling
- [ ] Default values for missing data
- [ ] Type coercion in from_dict

#### Complexity
- [ ] Simple, flat structure where possible

#### Architecture
- [ ] Clear domain model

#### License
- [ ] N/A

#### Specification
- [ ] Matches Anki template structure

---

## Step 6.2: Create Template Service

### Task
Implement the service for template CRUD operations.

### Implementation

**anki_template_designer/services/template_service.py**
```python
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
        
        logger.info(f"TemplateService initialized. Storage: {self._storage_path}")
    
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
        
        logger.info(f"Created template: {template.id} - {name}")
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
            logger.info(f"Saved template: {template.id}")
            return True
            
        except (IOError, OSError, json.JSONEncodeError) as e:
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
            
            logger.info(f"Loaded template: {template.id}")
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
            
            logger.info(f"Deleted template: {template_id}")
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
            logger.info(f"Set current template: {template_id}")
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
        
        # Create new template from source data
        new_template = Template.from_dict(source.to_dict())
        new_template.id = str(__import__("uuid").uuid4())
        new_template.name = new_name or f"{source.name} (Copy)"
        new_template.created_at = datetime.now()
        new_template.modified_at = datetime.now()
        new_template.version = 1
        
        self._templates[new_template.id] = new_template
        self.save_template(new_template)
        
        logger.info(f"Duplicated template {template_id} -> {new_template.id}")
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
```

### Quality Checks

#### Security
- [ ] Path traversal prevention in _get_template_path
- [ ] No arbitrary file access
- [ ] Safe JSON encoding (ensure_ascii=False but controlled)

#### Performance
- [ ] In-memory caching of templates
- [ ] Lazy loading from disk
- [ ] Efficient file operations

#### Best Practices
- [ ] Type hints throughout
- [ ] Single responsibility methods
- [ ] Clear error handling

#### Maintainability
- [ ] Configuration via constants
- [ ] Easy to change storage backend

#### Documentation
- [ ] All methods documented
- [ ] Clear return value documentation

#### Testing
- [ ] All methods testable
- [ ] Mock filesystem possible

#### Accessibility
- [ ] N/A (service layer)

#### Scalability
- [ ] Pagination needed for large template lists (TODO)

#### Compatibility
- [ ] Cross-platform paths
- [ ] UTF-8 encoding

#### Error Handling
- [ ] All exceptions caught and logged
- [ ] Graceful failure returns

#### Complexity
- [ ] Simple CRUD operations

#### Architecture
- [ ] Service layer pattern
- [ ] Separation from UI

#### License
- [ ] N/A

#### Specification
- [ ] Matches expected template operations

---

## Step 6.3: Integrate Service with Bridge

### Task
Connect the template service to the WebView bridge.

### Implementation

Update **anki_template_designer/gui/webview_bridge.py** - add template service methods:

Add to imports:
```python
from ..services.template_service import TemplateService
```

Add to `__init__`:
```python
        self._template_service: Optional[TemplateService] = None
```

Add new property and methods:
```python
    def set_template_service(self, service: TemplateService) -> None:
        """Set the template service instance.
        
        Args:
            service: TemplateService instance.
        """
        self._template_service = service
    
    @pyqtSlot(result=str)
    def listTemplates(self) -> str:
        """List all available templates.
        
        Returns:
            JSON-encoded list of template metadata.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            templates = self._template_service.list_templates()
            return json.dumps({"success": True, "templates": templates})
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def loadTemplate(self, template_id: str) -> str:
        """Load a template by ID.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            JSON-encoded template data.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            template = self._template_service.get_template(template_id)
            
            if template:
                self._template_service.set_current_template(template_id)
                return json.dumps({"success": True, "template": template.to_dict()})
            else:
                return json.dumps({"success": False, "error": "Template not found"})
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def saveTemplate(self, template_json: str) -> str:
        """Save a template.
        
        Args:
            template_json: JSON-encoded template data.
            
        Returns:
            JSON-encoded result.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            from ..core.models import Template
            data = json.loads(template_json)
            template = Template.from_dict(data)
            
            success = self._template_service.save_template(template)
            return json.dumps({"success": success})
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def createTemplate(self, name: str) -> str:
        """Create a new template.
        
        Args:
            name: Name for the new template.
            
        Returns:
            JSON-encoded new template data.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            template = self._template_service.create_template(name)
            return json.dumps({"success": True, "template": template.to_dict()})
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def deleteTemplate(self, template_id: str) -> str:
        """Delete a template.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            JSON-encoded result.
        """
        if self._template_service is None:
            return json.dumps({"success": False, "error": "Service not initialized"})
        
        try:
            success = self._template_service.delete_template(template_id)
            return json.dumps({"success": success})
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return json.dumps({"success": False, "error": str(e)})
```

Update **anki_template_designer/gui/designer_dialog.py** - initialize service:

Add to `_setup_bridge`:
```python
        # Initialize template service
        from ..services.template_service import TemplateService
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_service = TemplateService(addon_dir)
        self._bridge.set_template_service(template_service)
```

### Quality Checks

Same as previous steps - ensure integration is clean.

---

## User Testing Checklist

### Automated Tests

```python
# anki_template_designer/tests/test_models.py
"""Tests for data models."""

import pytest
from anki_template_designer.core.models import (
    Component, ComponentType, ComponentStyle, 
    Template, TemplateSide
)


def test_component_serialization():
    """Test component round-trip serialization."""
    component = Component(
        type=ComponentType.TEXT,
        content="Hello World",
        style=ComponentStyle(color="#333", font_size="16px")
    )
    
    data = component.to_dict()
    restored = Component.from_dict(data)
    
    assert restored.type == component.type
    assert restored.content == component.content


def test_template_serialization():
    """Test template round-trip serialization."""
    template = Template(name="Test Template")
    template.css = "body { color: red; }"
    
    data = template.to_dict()
    restored = Template.from_dict(data)
    
    assert restored.name == template.name
    assert restored.css == template.css


# anki_template_designer/tests/test_template_service.py
"""Tests for template service."""

import pytest
import tempfile
import os
from anki_template_designer.services.template_service import TemplateService


@pytest.fixture
def temp_service():
    """Create a service with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield TemplateService(tmpdir)


def test_create_template(temp_service):
    """Test template creation."""
    template = temp_service.create_template("Test")
    assert template.name == "Test"
    assert temp_service.current_template == template


def test_save_and_load(temp_service):
    """Test save and load round-trip."""
    template = temp_service.create_template("Test")
    template.css = "body { color: red; }"
    
    assert temp_service.save_template(template)
    
    # Clear cache
    temp_service._templates.clear()
    
    # Load from disk
    loaded = temp_service.load_template(template.id)
    assert loaded is not None
    assert loaded.name == "Test"
    assert loaded.css == "body { color: red; }"


def test_list_templates(temp_service):
    """Test template listing."""
    temp_service.create_template("First")
    temp_service.save_template()
    
    temp_service.create_template("Second")
    temp_service.save_template()
    
    templates = temp_service.list_templates()
    assert len(templates) == 2


def test_delete_template(temp_service):
    """Test template deletion."""
    template = temp_service.create_template("ToDelete")
    temp_service.save_template()
    
    assert temp_service.delete_template(template.id)
    assert temp_service.get_template(template.id) is None
```

Run tests:
```bash
python -m pytest anki_template_designer/tests/test_models.py -v
python -m pytest anki_template_designer/tests/test_template_service.py -v
```

### Manual Verification in Anki

1. [ ] Open Template Designer
2. [ ] Click "New" - verify template created
3. [ ] Click "Save" - verify no errors
4. [ ] Close and reopen dialog
5. [ ] Verify template persisted (check templates folder)
6. [ ] Test via console: `bridge.listTemplates(console.log)`

---

## Success Criteria

- [ ] All quality checks pass
- [ ] Models serialize correctly
- [ ] Service CRUD operations work
- [ ] Templates persist to disk
- [ ] Integration with bridge works

---

## Next Step

After successful completion, proceed to [07-UNDO-REDO-SYSTEM.md](07-UNDO-REDO-SYSTEM.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
