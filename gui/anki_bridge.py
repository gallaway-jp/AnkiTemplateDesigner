"""
Anki Bridge Module for Advanced Integration

Provides comprehensive integration with Anki's data structures:
- Real-time note type synchronization
- Field type validation and mapping
- Conditional field display support
- Field CSS scope customization
- Model inheritance templates
- Backend field metadata access
- Card template front/back detection

This module acts as the bridge between the template designer and Anki's
internal data structures, ensuring compatibility and preventing errors.
"""

import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnkiField:
    """Represents an Anki field with metadata"""
    name: str
    type: str  # 'text', 'number', 'select', 'email', etc.
    ord: int
    size: int = 20
    sticky: bool = False
    rtl: bool = False
    prefix: str = ''
    suffix: str = ''
    options: List[str] = field(default_factory=list)
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AnkiField':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CardTemplate:
    """Represents a card template"""
    name: str
    ord: int
    qfmt: str  # question format
    afmt: str  # answer format
    bafmt: str = ''  # browser answer format
    bqfmt: str = ''  # browser question format
    did: Optional[int] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CardTemplate':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AnkiModel:
    """Represents an Anki model/note type"""
    id: int
    name: str
    fields: List[AnkiField]
    templates: List[CardTemplate]
    css: str
    did: int  # deck id
    usn: int
    tags: List[str] = field(default_factory=list)
    req: List[List] = field(default_factory=list)  # required fields

    def field_count(self) -> int:
        """Get number of fields"""
        return len(self.fields)

    def get_field(self, index: int) -> Optional[AnkiField]:
        """Get field by index"""
        if 0 <= index < len(self.fields):
            return self.fields[index]
        return None

    def get_field_by_name(self, name: str) -> Optional[AnkiField]:
        """Get field by name"""
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def get_field_names(self) -> List[str]:
        """Get all field names"""
        return [f.name for f in self.fields]

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'fields': [f.to_dict() for f in self.fields],
            'templates': [t.to_dict() for t in self.templates],
            'css': self.css,
            'did': self.did,
            'usn': self.usn,
            'tags': self.tags,
            'req': self.req,
        }


class FieldValidator:
    """Validates field configurations and references"""

    VALID_FIELD_TYPES = {'text', 'number', 'select', 'email', 'image', 'audio', 'date', 'checkbox'}

    def validate_field(self, field: AnkiField) -> bool:
        """Validate a field configuration"""
        if not field.name or not field.type:
            return False

        if field.type not in self.VALID_FIELD_TYPES:
            return False

        if field.type == 'select' and not field.options:
            return False

        if field.type == 'number':
            if field.min_value is not None and field.max_value is not None:
                if field.min_value > field.max_value:
                    return False

        return True

    def validate_field_references(
        self, template: str, available_fields: List[str], field_types: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Validate field references in a template.

        Args:
            template: Template string with {{field}} references
            available_fields: List of available field names
            field_types: Optional dict of field names to their types

        Returns:
            List of error messages
        """
        errors = []

        # Find all field references (supports mustache syntax)
        pattern = r'\{\{[#/^]?(\w+)[^}]*\}\}'
        matches = set(re.findall(pattern, template))

        for field_name in matches:
            if field_name not in available_fields:
                errors.append(f"Field '{field_name}' not found in available fields")

        return errors

    def cast_field_type(self, value: str, field_type: str) -> Any:
        """Cast field value to appropriate type"""
        if field_type == 'number':
            try:
                return int(value) if '.' not in value else float(value)
            except ValueError:
                return 0

        if field_type == 'checkbox':
            return value.lower() in ('true', 'yes', '1', 'on')

        return str(value)


class ConditionalFieldRenderer:
    """Renders templates with conditional field blocks"""

    def render_template(
        self, template: str, fields: Dict[str, str], model: Optional[AnkiModel] = None
    ) -> str:
        """
        Render a template with field values.

        Supports Mustache-style conditionals:
        {{#fieldname}}...{{/fieldname}} - renders if field is truthy
        {{^fieldname}}...{{/fieldname}} - renders if field is falsy

        Args:
            template: Template string
            fields: Dictionary of field names to values
            model: Optional AnkiModel for additional context

        Returns:
            Rendered template
        """
        result = template

        # Process conditionals (innermost first)
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            # Find innermost conditionals
            pattern = r'\{\{[#^](\w+)\}\}((?:(?!\{\{[#^]).)*?)\{\{/\1\}\}'

            def replacer(match):
                field_name = match.group(1)
                content = match.group(2)
                is_positive = template[match.start():match.start()+3] == '{{#'

                field_value = fields.get(field_name, '')
                is_truthy = bool(field_value)

                if (is_positive and is_truthy) or (not is_positive and not is_truthy):
                    # Process nested field references in content
                    processed = content
                    for fname, fvalue in fields.items():
                        processed = processed.replace('{{' + fname + '}}', str(fvalue))
                    return processed

                return ''

            new_result = re.sub(pattern, replacer, result, flags=re.DOTALL)

            if new_result == result:
                break

            result = new_result
            iteration += 1

        # Replace simple field references
        for field_name, field_value in fields.items():
            result = result.replace('{{' + field_name + '}}', str(field_value))

        return result


class FieldCSSScoper:
    """Manages CSS scoping for field-specific styling"""

    def scope_css_for_field(self, css: str, field_name: str) -> str:
        """
        Scope CSS to a specific field.

        Args:
            css: CSS rules
            field_name: Field name to scope to

        Returns:
            Scoped CSS
        """
        lines = css.strip().split('\n')
        scoped_lines = []

        for line in lines:
            if '{' in line:
                selector = line.split('{')[0].strip()
                rest = '{' + line.split('{', 1)[1]
                scoped_lines.append(f'.field-{field_name} {selector} {rest}')
            else:
                scoped_lines.append(line)

        return '\n'.join(scoped_lines)

    def scope_multiple_fields(self, css_config: Dict[str, str]) -> str:
        """
        Scope CSS for multiple fields.

        Args:
            css_config: Dictionary of field names to CSS rules

        Returns:
            Combined scoped CSS
        """
        result = []
        for field_name, css in css_config.items():
            result.append(self.scope_css_for_field(css, field_name))
        return '\n'.join(result)

    def extract_field_selectors(self, css: str) -> Dict[str, List[str]]:
        """
        Extract all field selectors from CSS.

        Returns:
            Dictionary mapping field names to their selectors
        """
        selectors = {}
        pattern = r'\.field-(\w+)\s*\{([^}]+)\}'

        matches = re.findall(pattern, css)
        for field_name, rules in matches:
            if field_name not in selectors:
                selectors[field_name] = []
            selectors[field_name].append(rules)

        return selectors


class ModelComposer:
    """Manages model inheritance and template composition"""

    def inherit_model(self, base_model: AnkiModel) -> List[AnkiField]:
        """
        Inherit fields from a base model.

        Args:
            base_model: Base model to inherit from

        Returns:
            List of inherited fields
        """
        return [AnkiField.from_dict(f.to_dict()) for f in base_model.fields]

    def extend_inherited_model(self, base_model: AnkiModel, new_fields: List[AnkiField]) -> List[AnkiField]:
        """
        Extend inherited model with new fields.

        Args:
            base_model: Base model
            new_fields: Fields to add

        Returns:
            Extended field list
        """
        inherited = self.inherit_model(base_model)
        return inherited + new_fields

    def override_field(self, base_field: AnkiField, override_data: Dict) -> AnkiField:
        """
        Override properties of an inherited field.

        Args:
            base_field: Base field
            override_data: Properties to override

        Returns:
            Overridden field
        """
        field_dict = base_field.to_dict()
        field_dict.update(override_data)
        return AnkiField.from_dict(field_dict)

    def compose_template(self, base_template: str, extra_fields: List[str]) -> str:
        """
        Compose a template from a base and extra fields.

        Args:
            base_template: Base template
            extra_fields: Additional fields to potentially add

        Returns:
            Composed template
        """
        return base_template


class FieldMetadataProvider:
    """Provides comprehensive field metadata"""

    def __init__(self):
        self._cache: Dict[str, Dict] = {}

    @lru_cache(maxsize=128)
    def get_metadata(self, field: AnkiField) -> Dict[str, Any]:
        """
        Get complete metadata for a field.

        Args:
            field: Field to get metadata for

        Returns:
            Metadata dictionary
        """
        return {
            'name': field.name,
            'type': field.type,
            'ord': field.ord,
            'size': field.size,
            'sticky': field.sticky,
            'rtl': field.rtl,
            'prefix': field.prefix,
            'suffix': field.suffix,
            'options': field.options or [],
        }

    def get_constraints(self, field: AnkiField) -> Dict[str, Any]:
        """Get field constraints"""
        constraints = {}

        if field.type == 'number':
            if field.min_value is not None:
                constraints['min'] = field.min_value
            if field.max_value is not None:
                constraints['max'] = field.max_value

        if field.type == 'select':
            constraints['options'] = field.options or []

        return constraints

    def get_validation_rules(self, field: AnkiField) -> List[str]:
        """Get validation rules for a field"""
        rules = []

        if field.type == 'email':
            rules.append('email_format')
            rules.append('required')

        if field.type == 'number':
            rules.append('numeric')

        if field.sticky:
            rules.append('sticky')

        return rules

    def list_field_metadata(self, model: AnkiModel) -> List[Dict[str, Any]]:
        """List metadata for all fields in a model"""
        return [self.get_metadata(f) for f in model.fields]

    def clear_cache(self):
        """Clear metadata cache"""
        self._cache.clear()
        self.get_metadata.cache_clear()


class CardTemplateDetector:
    """Detects and analyzes card templates"""

    def extract_fields(self, template: str) -> Set[str]:
        """
        Extract all field references from a template.

        Args:
            template: Template string

        Returns:
            Set of field names
        """
        pattern = r'\{\{[#/^]?(\w+)[^}]*\}\}'
        return set(re.findall(pattern, template))

    def is_front_template(self, template: str) -> bool:
        """Check if template is a front (question) template"""
        # Front templates typically don't have <hr> separator
        return '<hr>' not in template and bool(self.extract_fields(template))

    def is_back_template(self, template: str) -> bool:
        """Check if template is a back (answer) template"""
        # Back templates typically have <hr> separator
        return '<hr>' in template and bool(self.extract_fields(template))

    def get_card_type(self, template: str) -> str:
        """
        Determine card type from template.

        Returns:
            'front', 'back', or 'unknown'
        """
        if self.is_back_template(template):
            return 'back'
        elif self.is_front_template(template):
            return 'front'
        return 'unknown'

    def is_template_complete(self, template: str) -> bool:
        """Check if template has required field references"""
        return bool(self.extract_fields(template))

    def validate_template(self, template: str, available_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a template against available fields.

        Args:
            template: Template to validate
            available_fields: List of available field names

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.is_template_complete(template):
            errors.append("Template has no field references")

        fields = self.extract_fields(template)
        for field in fields:
            if field not in available_fields:
                errors.append(f"Field '{field}' not found in model")

        return len(errors) == 0, errors


class AnkiBridge:
    """
    Main bridge for Anki integration.

    Coordinates all Anki-related operations and provides a unified interface.
    """

    def __init__(self):
        self.current_model: Optional[AnkiModel] = None
        self.previous_model: Optional[AnkiModel] = None
        self._connected = False
        self._model_cache: Dict[int, AnkiModel] = {}

        self.validator = FieldValidator()
        self.renderer = ConditionalFieldRenderer()
        self.css_scoper = FieldCSSScoper()
        self.composer = ModelComposer()
        self.metadata = FieldMetadataProvider()
        self.detector = CardTemplateDetector()

    @property
    def connected(self) -> bool:
        """Check if Anki is connected"""
        return self._connected

    @connected.setter
    def connected(self, value: bool):
        """Set connection status"""
        self._connected = value

    def get_current_model(self) -> Optional[AnkiModel]:
        """Get currently selected Anki model"""
        return self.current_model

    def set_current_model(self, model: AnkiModel):
        """Set current model and track previous"""
        self.previous_model = self.current_model
        self.current_model = model
        self._model_cache[model.id] = model

    def sync_model_fields(self) -> List[AnkiField]:
        """Sync fields from current Anki model"""
        if not self.current_model:
            return []
        return self.current_model.fields

    def sync_card_templates(self) -> List[CardTemplate]:
        """Sync card templates from current model"""
        if not self.current_model:
            return []
        return self.current_model.templates

    def detect_model_change(self, old_model: Optional[AnkiModel], new_model: AnkiModel) -> Optional[Dict]:
        """
        Detect changes between two models.

        Returns:
            Dictionary with 'added' and 'removed' fields, or None if no changes
        """
        if not old_model:
            return None

        old_names = {f.name for f in old_model.fields}
        new_names = {f.name for f in new_model.fields}

        added = [f for f in new_model.fields if f.name not in old_names]
        removed = [f for f in old_model.fields if f.name not in new_names]

        if added or removed:
            return {
                'added': added,
                'removed': removed,
                'timestamp': datetime.now().isoformat(),
            }

        return None

    def validate_template_references(self, template: str) -> Tuple[bool, List[str]]:
        """Validate template against current model"""
        if not self.current_model:
            return False, ["No model selected"]

        field_names = self.current_model.get_field_names()
        return self.detector.validate_template(template, field_names)

    def render_template_preview(self, template: str, field_values: Dict[str, str]) -> str:
        """Render template for preview"""
        return self.renderer.render_template(template, field_values, self.current_model)

    def get_field_metadata_all(self) -> List[Dict[str, Any]]:
        """Get metadata for all fields in current model"""
        if not self.current_model:
            return []
        return self.metadata.list_field_metadata(self.current_model)

    def export_model_config(self) -> Dict:
        """Export current model configuration"""
        if not self.current_model:
            return {}
        return self.current_model.to_dict()

    def import_model_config(self, config: Dict) -> AnkiModel:
        """Import model configuration"""
        fields = [AnkiField.from_dict(f) for f in config.get('fields', [])]
        templates = [CardTemplate.from_dict(t) for t in config.get('templates', [])]

        model = AnkiModel(
            id=config.get('id', 0),
            name=config.get('name', ''),
            fields=fields,
            templates=templates,
            css=config.get('css', ''),
            did=config.get('did', 0),
            usn=config.get('usn', -1),
            tags=config.get('tags', []),
            req=config.get('req', []),
        )

        return model


# Global instance for singleton access
_anki_bridge: Optional[AnkiBridge] = None


def get_anki_bridge() -> AnkiBridge:
    """Get or create the global AnkiBridge instance"""
    global _anki_bridge
    if _anki_bridge is None:
        _anki_bridge = AnkiBridge()
    return _anki_bridge


def reset_anki_bridge():
    """Reset the global AnkiBridge instance"""
    global _anki_bridge
    _anki_bridge = None
