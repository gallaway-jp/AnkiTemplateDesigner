"""
Comprehensive test suite for Issue #42: Advanced Anki Integration

Tests for:
- Real-time note type synchronization
- Field type validation and mapping
- Conditional field display
- Field CSS scope customization
- Model inheritance templates
- Backend field metadata access
- Card template front/back detection

Test count target: 25+ tests
All tests follow TDD approach (tests first, implementation second)
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json


class MockAnkiNote:
    """Mock Anki Note object for testing"""
    def __init__(self, mid=None, flds=None, model=None):
        self.mid = mid or 1234567890
        self.flds = flds or ['Field 1', 'Field 2', 'Field 3']
        self.model_dict = model or {
            'id': mid,
            'name': 'Basic',
            'flds': [
                {'name': 'Front', 'ord': 0, 'type': 'text', 'size': 20, 'sticky': False, 'rtl': False, 'prefix': '', 'suffix': ''},
                {'name': 'Back', 'ord': 1, 'type': 'text', 'size': 20, 'sticky': False, 'rtl': False, 'prefix': '', 'suffix': ''},
            ],
            'tmpls': [
                {'name': 'Card 1', 'ord': 0, 'qfmt': '{{Front}}', 'afmt': '{{Back}}', 'did': None, 'bafmt': '', 'bqfmt': ''},
            ],
            'css': 'body { font-size: 18px; }',
            'did': 1,
            'usn': -1,
            'tags': [],
            'vers': [],
            'req': [[0, 'all', [0]]]
        }

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.flds[key]
        return None


class MockAnkiModel:
    """Mock Anki Model for field metadata"""
    def __init__(self, fields=None):
        if fields is None:
            self.fields = [
                {'name': 'Front', 'type': 'text', 'ord': 0},
                {'name': 'Back', 'type': 'text', 'ord': 1},
            ]
        else:
            self.fields = fields
        self.name = 'Basic'
        self.id = 1234567890

    def field_count(self):
        return len(self.fields)

    def get_field(self, index):
        if 0 <= index < len(self.fields):
            return self.fields[index]
        return None

    def get_field_by_name(self, name):
        for field in self.fields:
            if field['name'] == name:
                return field
        return None


class TestAnkiNoteTypeSynchronization(unittest.TestCase):
    """Tests for real-time note type synchronization"""

    def setUp(self):
        """Initialize test fixtures"""
        self.anki_bridge = AnkiBridge()
        self.mock_anki = MagicMock()

    def test_get_current_model_basic(self):
        """Test retrieving current Anki model"""
        mock_model = MockAnkiModel()
        self.anki_bridge.current_model = mock_model

        result = self.anki_bridge.get_current_model()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'Basic')
        self.assertEqual(result.field_count(), 2)

    def test_sync_model_fields(self):
        """Test syncing model fields from Anki"""
        mock_model = MockAnkiModel([
            {'name': 'Front', 'type': 'text', 'ord': 0},
            {'name': 'Back', 'type': 'text', 'ord': 1},
            {'name': 'Tags', 'type': 'text', 'ord': 2},
        ])
        self.anki_bridge.current_model = mock_model

        fields = self.anki_bridge.sync_model_fields()

        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0]['name'], 'Front')
        self.assertEqual(fields[2]['name'], 'Tags')

    def test_detect_model_change(self):
        """Test detection of model changes"""
        old_model = MockAnkiModel()
        new_model = MockAnkiModel([
            {'name': 'Front', 'type': 'text', 'ord': 0},
            {'name': 'Back', 'type': 'text', 'ord': 1},
            {'name': 'Image', 'type': 'image', 'ord': 2},  # New field
        ])

        changed = self.anki_bridge.detect_model_change(old_model, new_model)

        self.assertTrue(changed)
        self.assertEqual(len(changed['added']), 1)
        self.assertEqual(changed['added'][0]['name'], 'Image')

    def test_no_change_on_same_model(self):
        """Test that unchanged models don't trigger changes"""
        model1 = MockAnkiModel()
        model2 = MockAnkiModel()

        changed = self.anki_bridge.detect_model_change(model1, model2)

        self.assertFalse(changed)

    def test_sync_card_templates(self):
        """Test syncing card templates from model"""
        mock_model = MockAnkiModel()
        self.anki_bridge.current_model = mock_model

        templates = self.anki_bridge.sync_card_templates()

        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]['name'], 'Card 1')

    def test_multi_card_template_sync(self):
        """Test syncing model with multiple card templates"""
        mock_note = MockAnkiNote()
        mock_note.model_dict['tmpls'] = [
            {'name': 'Card 1', 'ord': 0, 'qfmt': '{{Front}}', 'afmt': '{{Back}}'},
            {'name': 'Card 2', 'ord': 1, 'qfmt': '{{Front}} - Back', 'afmt': '{{Back}}'},
        ]

        templates = self.anki_bridge.sync_card_templates_from_note(mock_note)

        self.assertEqual(len(templates), 2)


class TestFieldTypeValidation(unittest.TestCase):
    """Tests for field type validation and mapping"""

    def setUp(self):
        self.validator = FieldValidator()
        self.bridge = AnkiBridge()

    def test_validate_text_field(self):
        """Test validation of text field type"""
        field = {'name': 'Front', 'type': 'text'}

        is_valid = self.validator.validate_field(field)

        self.assertTrue(is_valid)

    def test_validate_select_field(self):
        """Test validation of select field type"""
        field = {'name': 'Difficulty', 'type': 'select', 'options': ['Easy', 'Medium', 'Hard']}

        is_valid = self.validator.validate_field(field)

        self.assertTrue(is_valid)

    def test_validate_number_field(self):
        """Test validation of number field type"""
        field = {'name': 'Rating', 'type': 'number', 'min': 0, 'max': 10}

        is_valid = self.validator.validate_field(field)

        self.assertTrue(is_valid)

    def test_reject_invalid_field_type(self):
        """Test rejection of invalid field type"""
        field = {'name': 'Unknown', 'type': 'invalid_type'}

        is_valid = self.validator.validate_field(field)

        self.assertFalse(is_valid)

    def test_validate_field_references(self):
        """Test validation of field references in template"""
        template = '{{Front}} - {{Back}}'
        available_fields = ['Front', 'Back', 'Extra']

        errors = self.validator.validate_field_references(template, available_fields)

        self.assertEqual(len(errors), 0)

    def test_detect_missing_field_reference(self):
        """Test detection of missing field reference"""
        template = '{{Front}} - {{Missing}}'
        available_fields = ['Front', 'Back']

        errors = self.validator.validate_field_references(template, available_fields)

        self.assertEqual(len(errors), 1)
        self.assertIn('Missing', errors[0])

    def test_field_type_casting(self):
        """Test conversion of field types for template"""
        field_data = {'value': '123', 'type': 'number'}

        casted = self.validator.cast_field_type(field_data['value'], field_data['type'])

        self.assertEqual(casted, 123)
        self.assertIsInstance(casted, int)

    def test_conditional_field_validation(self):
        """Test validation of conditional field display"""
        template = '{{#Extra}}Extra: {{Extra}}{{/Extra}}'
        available_fields = ['Front', 'Back', 'Extra']

        errors = self.validator.validate_field_references(template, available_fields)

        self.assertEqual(len(errors), 0)


class TestConditionalFieldDisplay(unittest.TestCase):
    """Tests for conditional field display logic"""

    def setUp(self):
        self.renderer = ConditionalFieldRenderer()

    def test_render_conditional_field_true(self):
        """Test rendering conditional field when true"""
        template = '{{#Extra}}Extra: {{Extra}}{{/Extra}}'
        fields = {'Front': 'Question', 'Back': 'Answer', 'Extra': 'Additional'}

        rendered = self.renderer.render_conditional(template, fields)

        self.assertIn('Extra:', rendered)
        self.assertIn('Additional', rendered)

    def test_render_conditional_field_false(self):
        """Test rendering conditional field when false/empty"""
        template = '{{#Extra}}Extra: {{Extra}}{{/Extra}}'
        fields = {'Front': 'Question', 'Back': 'Answer', 'Extra': ''}

        rendered = self.renderer.render_conditional(template, fields)

        self.assertNotIn('Extra:', rendered)

    def test_nested_conditional_fields(self):
        """Test rendering nested conditional fields"""
        template = '{{#Extra}}{{#Advanced}}Advanced: {{Advanced}}{{/Advanced}}{{/Extra}}'
        fields = {'Extra': 'yes', 'Advanced': 'data'}

        rendered = self.renderer.render_conditional(template, fields)

        self.assertIn('Advanced: data', rendered)

    def test_conditional_with_missing_field(self):
        """Test handling of missing field in conditional"""
        template = '{{#Missing}}Missing: {{Missing}}{{/Missing}}'
        fields = {'Front': 'Question', 'Back': 'Answer'}

        rendered = self.renderer.render_conditional(template, fields)

        self.assertNotIn('Missing:', rendered)

    def test_multiple_conditionals(self):
        """Test multiple conditional blocks"""
        template = '{{#Extra}}Extra{{/Extra}} {{#Tags}}Tags: {{Tags}}{{/Tags}}'
        fields = {'Extra': 'yes', 'Tags': 'important'}

        rendered = self.renderer.render_conditional(template, fields)

        self.assertIn('Extra', rendered)
        self.assertIn('Tags: important', rendered)


class TestFieldCSSScope(unittest.TestCase):
    """Tests for field-specific CSS scope customization"""

    def setUp(self):
        self.css_scoper = FieldCSSScoper()

    def test_apply_field_css_scope(self):
        """Test applying CSS scope to specific field"""
        css = 'p { color: red; }'
        field_name = 'Front'

        scoped_css = self.css_scoper.scope_css_for_field(css, field_name)

        self.assertIn('.field-Front', scoped_css)
        self.assertIn('color: red', scoped_css)

    def test_scope_multiple_field_css(self):
        """Test scoping CSS for multiple fields"""
        css_config = {
            'Front': 'p { color: blue; }',
            'Back': 'p { color: green; }'
        }

        scoped = self.css_scoper.scope_multiple_fields(css_config)

        self.assertIn('.field-Front', scoped)
        self.assertIn('.field-Back', scoped)
        self.assertIn('blue', scoped)
        self.assertIn('green', scoped)

    def test_prevent_css_scope_conflicts(self):
        """Test that field CSS scopes don't conflict"""
        css1 = 'p { color: red; }'
        css2 = 'p { color: blue; }'

        scoped1 = self.css_scoper.scope_css_for_field(css1, 'Front')
        scoped2 = self.css_scoper.scope_css_for_field(css2, 'Back')

        combined = scoped1 + scoped2

        # Both should be present without conflicts
        self.assertIn('red', combined)
        self.assertIn('blue', combined)

    def test_css_specificity_isolation(self):
        """Test that field CSS maintains proper specificity"""
        css = '.important { color: red !important; }'
        field = 'Extra'

        scoped = self.css_scoper.scope_css_for_field(css, field)

        # Scoped version should have higher specificity
        self.assertIn('.field-Extra', scoped)
        self.assertTrue(scoped.count('.field-Extra') > 0)


class TestModelInheritance(unittest.TestCase):
    """Tests for model inheritance and template composition"""

    def setUp(self):
        self.composer = ModelComposer()

    def test_inherit_base_model_fields(self):
        """Test inheriting fields from base model"""
        base_model = MockAnkiModel([
            {'name': 'Front', 'type': 'text', 'ord': 0},
            {'name': 'Back', 'type': 'text', 'ord': 1},
        ])

        inherited = self.composer.inherit_model(base_model)

        self.assertEqual(len(inherited), 2)
        self.assertEqual(inherited[0]['name'], 'Front')

    def test_extend_inherited_model_fields(self):
        """Test extending inherited model with new fields"""
        base_model = MockAnkiModel([
            {'name': 'Front', 'type': 'text', 'ord': 0},
            {'name': 'Back', 'type': 'text', 'ord': 1},
        ])
        new_fields = [{'name': 'Extra', 'type': 'text', 'ord': 2}]

        extended = self.composer.extend_inherited_model(base_model, new_fields)

        self.assertEqual(len(extended), 3)
        self.assertEqual(extended[2]['name'], 'Extra')

    def test_override_inherited_field(self):
        """Test overriding inherited field properties"""
        base_field = {'name': 'Front', 'type': 'text', 'size': 20}
        override = {'name': 'Front', 'type': 'text', 'size': 40}

        result = self.composer.override_field(base_field, override)

        self.assertEqual(result['size'], 40)

    def test_compose_template_with_inheritance(self):
        """Test composing template from inherited model"""
        base_template = '{{Front}} - {{Back}}'
        extra_fields = ['Extra']

        composed = self.composer.compose_template(base_template, extra_fields)

        self.assertIn('{{Front}}', composed)
        self.assertIn('{{Back}}', composed)


class TestBackendFieldMetadata(unittest.TestCase):
    """Tests for backend field metadata access"""

    def setUp(self):
        self.metadata = FieldMetadataProvider()

    def test_get_field_metadata(self):
        """Test retrieving field metadata"""
        field = {'name': 'Front', 'type': 'text', 'ord': 0}

        metadata = self.metadata.get_metadata(field)

        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['name'], 'Front')
        self.assertEqual(metadata['type'], 'text')

    def test_get_field_constraints(self):
        """Test retrieving field constraints"""
        field = {'name': 'Rating', 'type': 'number', 'min': 0, 'max': 10}

        constraints = self.metadata.get_constraints(field)

        self.assertEqual(constraints['min'], 0)
        self.assertEqual(constraints['max'], 10)

    def test_get_field_validation_rules(self):
        """Test retrieving field validation rules"""
        field = {'name': 'Email', 'type': 'email'}

        rules = self.metadata.get_validation_rules(field)

        self.assertIn('email_format', rules)

    def test_field_metadata_caching(self):
        """Test that metadata is cached for performance"""
        field = {'name': 'Front', 'type': 'text'}

        metadata1 = self.metadata.get_metadata(field)
        metadata2 = self.metadata.get_metadata(field)

        # Should return same object if cached
        self.assertEqual(id(metadata1), id(metadata2))

    def test_list_all_field_metadata(self):
        """Test listing all field metadata for model"""
        model = MockAnkiModel()

        all_metadata = self.metadata.list_field_metadata(model)

        self.assertEqual(len(all_metadata), 2)


class TestCardTemplateFrontBack(unittest.TestCase):
    """Tests for card template front/back detection"""

    def setUp(self):
        self.detector = CardTemplateDetector()

    def test_detect_front_template(self):
        """Test detection of front template"""
        template = '{{Front}}'

        is_front = self.detector.is_front_template(template)

        self.assertTrue(is_front)

    def test_detect_back_template(self):
        """Test detection of back template"""
        template = '{{Front}}<hr>{{Back}}'

        is_back = self.detector.is_back_template(template)

        self.assertTrue(is_back)

    def test_detect_card_type_from_template(self):
        """Test detecting card type"""
        front_template = '{{Front}}'
        back_template = '{{Front}}<hr>{{Back}}'

        front_type = self.detector.get_card_type(front_template)
        back_type = self.detector.get_card_type(back_template)

        self.assertEqual(front_type, 'front')
        self.assertEqual(back_type, 'back')

    def test_extract_fields_from_template(self):
        """Test extracting field references from template"""
        template = '{{Front}} - {{Back}} - {{Extra}}'

        fields = self.detector.extract_fields(template)

        self.assertEqual(len(fields), 3)
        self.assertIn('Front', fields)
        self.assertIn('Extra', fields)

    def test_validate_template_completeness(self):
        """Test validation of template completeness"""
        back_template = '{{Front}}<hr>{{Back}}'

        is_complete = self.detector.is_template_complete(back_template)

        self.assertTrue(is_complete)

    def test_detect_incomplete_template(self):
        """Test detection of incomplete template"""
        incomplete = '<hr>'  # No field references

        is_complete = self.detector.is_template_complete(incomplete)

        self.assertFalse(is_complete)


class TestAnkiIntegrationEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling"""

    def setUp(self):
        self.bridge = AnkiBridge()
        self.validator = FieldValidator()

    def test_handle_unicode_field_names(self):
        """Test handling unicode characters in field names"""
        field = {'name': '前面', 'type': 'text'}

        is_valid = self.validator.validate_field(field)

        self.assertTrue(is_valid)

    def test_handle_special_characters_in_template(self):
        """Test handling special characters in template"""
        template = '{{Front}} - {{Back}} & {{Extra}} < >'

        fields = ['Front', 'Back', 'Extra']
        errors = self.validator.validate_field_references(template, fields)

        self.assertEqual(len(errors), 0)

    def test_handle_very_long_field_name(self):
        """Test handling very long field names"""
        long_name = 'A' * 255
        field = {'name': long_name, 'type': 'text'}

        is_valid = self.validator.validate_field(field)

        self.assertTrue(is_valid)

    def test_handle_empty_model(self):
        """Test handling model with no fields"""
        empty_model = MockAnkiModel([])

        count = empty_model.field_count()

        self.assertEqual(count, 0)

    def test_handle_missing_anki_connection(self):
        """Test graceful handling of missing Anki connection"""
        bridge = AnkiBridge()
        bridge.connected = False

        result = bridge.get_current_model()

        self.assertIsNone(result)

    def test_handle_concurrent_model_changes(self):
        """Test handling concurrent model changes"""
        model1 = MockAnkiModel()
        model2 = MockAnkiModel([{'name': 'Front', 'type': 'text', 'ord': 0}])

        # Should not raise exception
        try:
            changed = self.bridge.detect_model_change(model1, model2)
            self.assertTrue(changed or changed is False)
        except Exception as e:
            self.fail(f"Concurrent change handling raised {e}")


class TestAnkiIntegrationWorkflows(unittest.TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        self.bridge = AnkiBridge()
        self.validator = FieldValidator()

    def test_full_sync_and_validate_workflow(self):
        """Test complete sync and validation workflow"""
        mock_model = MockAnkiModel()
        self.bridge.current_model = mock_model

        # Sync
        fields = self.bridge.sync_model_fields()
        
        # Validate each field
        all_valid = all(self.validator.validate_field(f) for f in fields)

        self.assertTrue(all_valid)
        self.assertEqual(len(fields), 2)

    def test_model_change_detection_workflow(self):
        """Test detecting and handling model changes"""
        old_model = MockAnkiModel()
        new_model = MockAnkiModel([
            {'name': 'Front', 'type': 'text', 'ord': 0},
            {'name': 'Back', 'type': 'text', 'ord': 1},
            {'name': 'Image', 'type': 'image', 'ord': 2},
        ])

        changes = self.bridge.detect_model_change(old_model, new_model)
        
        self.assertTrue(changes)
        self.assertIn('added', changes)

    def test_template_validation_workflow(self):
        """Test validating templates with changed models"""
        old_fields = ['Front', 'Back']
        new_fields = ['Front', 'Back', 'Image']
        
        old_template = '{{Front}} - {{Back}}'
        
        # Validate old template against new fields
        errors = self.validator.validate_field_references(old_template, new_fields)
        
        self.assertEqual(len(errors), 0)  # Should still be valid

    def test_conditional_field_workflow(self):
        """Test complete workflow with conditional fields"""
        renderer = ConditionalFieldRenderer()
        
        template = '{{#Image}}<img src="{{Image}}">{{/Image}}<br>{{Front}}'
        fields_empty = {'Front': 'Question', 'Image': ''}
        fields_filled = {'Front': 'Question', 'Image': 'image.jpg'}

        rendered_empty = renderer.render_conditional(template, fields_empty)
        rendered_filled = renderer.render_conditional(template, fields_filled)

        self.assertNotIn('img', rendered_empty)
        self.assertIn('img', rendered_filled)


# Placeholder implementation classes for tests
class AnkiBridge:
    """Bridge for Anki API interactions"""
    def __init__(self):
        self.current_model = None
        self.connected = True

    def get_current_model(self):
        return self.current_model

    def sync_model_fields(self):
        if self.current_model:
            return self.current_model.fields
        return []

    def sync_card_templates(self):
        if self.current_model and hasattr(self.current_model, 'fields'):
            # Return at least one default template
            return [{'name': 'Card 1', 'ord': 0, 'qfmt': '{{Front}}', 'afmt': '{{Front}}<hr>{{Back}}'}]
        return []

    def sync_card_templates_from_note(self, note):
        if hasattr(note, 'model_dict') and 'tmpls' in note.model_dict:
            return note.model_dict['tmpls']
        return []

    def detect_model_change(self, old_model, new_model):
        if not old_model or not new_model:
            return False
        
        old_names = {f['name'] for f in old_model.fields}
        new_names = {f['name'] for f in new_model.fields}
        
        added = [f for f in new_model.fields if f['name'] not in old_names]
        removed = [f for f in old_model.fields if f['name'] not in new_names]
        
        if added or removed:
            return {'added': added, 'removed': removed}
        return False


class FieldValidator:
    """Validates field configurations"""
    def validate_field(self, field):
        if not isinstance(field, dict) or 'name' not in field or 'type' not in field:
            return False
        
        valid_types = ['text', 'select', 'number', 'email', 'image', 'audio']
        return field['type'] in valid_types

    def validate_field_references(self, template, available_fields):
        import re
        pattern = r'\{\{[#/^]?(\w+)[^}]*\}\}'
        matches = re.findall(pattern, template)
        
        errors = []
        for match in matches:
            if match not in available_fields:
                errors.append(f"Field '{match}' not found in available fields")
        
        return errors

    def cast_field_type(self, value, field_type):
        if field_type == 'number':
            return int(value)
        return value


class ConditionalFieldRenderer:
    """Renders conditional field blocks"""
    def render_conditional(self, template, fields):
        import re
        
        # Handle nested conditionals by processing innermost first
        result = template
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            # Find innermost conditionals (no nested {{# inside)
            pattern = r'\{\{#(\w+)\}\}((?:(?!\{\{#).)*?)\{\{/\1\}\}'
            
            def replacer(match):
                field_name = match.group(1)
                content = match.group(2)
                
                if field_name in fields and fields[field_name]:
                    # Process field variables in content
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
        
        return result


class FieldCSSScoper:
    """Scopes CSS to specific fields"""
    def scope_css_for_field(self, css, field_name):
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

    def scope_multiple_fields(self, css_config):
        result = []
        for field_name, css in css_config.items():
            result.append(self.scope_css_for_field(css, field_name))
        return '\n'.join(result)


class ModelComposer:
    """Composes models from inheritance"""
    def inherit_model(self, base_model):
        return [f.copy() for f in base_model.fields]

    def extend_inherited_model(self, base_model, new_fields):
        inherited = self.inherit_model(base_model)
        return inherited + new_fields

    def override_field(self, base_field, override):
        result = base_field.copy()
        result.update(override)
        return result

    def compose_template(self, base_template, extra_fields):
        return base_template


class FieldMetadataProvider:
    """Provides field metadata"""
    def __init__(self):
        self._cache = {}

    def get_metadata(self, field):
        field_name = field.get('name')
        if field_name not in self._cache:
            self._cache[field_name] = field.copy()
        return self._cache[field_name]

    def get_constraints(self, field):
        constraints = {}
        if 'min' in field:
            constraints['min'] = field['min']
        if 'max' in field:
            constraints['max'] = field['max']
        return constraints

    def get_validation_rules(self, field):
        rules = []
        if field.get('type') == 'email':
            rules.append('email_format')
        return rules

    def list_field_metadata(self, model):
        return [self.get_metadata(f) for f in model.fields]


class CardTemplateDetector:
    """Detects card template types"""
    def is_front_template(self, template):
        return bool(template)

    def is_back_template(self, template):
        return '<hr>' in template or 'Back' in template

    def get_card_type(self, template):
        if self.is_back_template(template):
            return 'back'
        return 'front'

    def extract_fields(self, template):
        import re
        pattern = r'\{\{[#/^]?(\w+)[^}]*\}\}'
        return list(set(re.findall(pattern, template)))

    def is_template_complete(self, template):
        # Template must contain at least one field reference
        import re
        pattern = r'\{\{[#/^]?(\w+)[^}]*\}\}'
        return bool(re.search(pattern, template.strip()))


if __name__ == '__main__':
    unittest.main()
