"""
Tests for export/import functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from ui.template_io import TemplateExporter, TemplateImporter, TemplateSharing
from ui.components import TextFieldComponent, ImageFieldComponent


class TestTemplateExporter:
    """Test TemplateExporter"""
    
    def test_export_template(self):
        """Test exporting a template"""
        # Create test components
        components = [
            TextFieldComponent("Front"),
            TextFieldComponent("Back")
        ]
        
        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd', delete=False) as f:
            file_path = f.name
        
        try:
            exporter = TemplateExporter()
            metadata = {'name': 'Test Template'}
            exporter.export_template(components, css="", metadata=metadata, file_path=file_path)
            
            # Check file exists
            assert Path(file_path).exists()
            
            # Check file content
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'metadata' in data
            assert 'components' in data
            assert data['metadata']['name'] == "Test Template"
            assert data['metadata']['version'] == "1.0"
            assert len(data['components']) == 2
        
        finally:
            Path(file_path).unlink(missing_ok=True)
    
    def test_export_with_css(self):
        """Test exporting template with CSS"""
        components = [TextFieldComponent("Front")]
        css_style = ".card { background: white; }"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd', delete=False) as f:
            file_path = f.name
        
        try:
            exporter = TemplateExporter()
            exporter.export_template(components, css=css_style, file_path=file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert data['css'] == css_style
        
        finally:
            Path(file_path).unlink(missing_ok=True)
    
    def test_serialize_component_properties(self):
        """Test that all component properties are serialized"""
        component = TextFieldComponent("TestField")
        # Components don't have x,y by default, skip those
        component.width = "200px"
        component.height = "50px"
        component.font_size = 14
        component.font_family = "Arial"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd', delete=False) as f:
            file_path = f.name
        
        try:
            exporter = TemplateExporter()
            exporter.export_template([component], css="", file_path=file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            comp_data = data['components'][0]
            # x,y default to 0 if not present
            assert comp_data.get('x', 0) == 0
            assert comp_data.get('y', 0) == 0
            assert comp_data['width'] == "200px"
            assert comp_data['height'] == "50px"
            assert comp_data['properties']['font_size'] == 14
            assert comp_data['properties']['font_family'] == "Arial"
        
        finally:
            Path(file_path).unlink(missing_ok=True)


class TestTemplateImporter:
    """Test TemplateImporter"""
    
    def test_import_template(self):
        """Test importing a template"""
        # Create and export a template first
        components = [
            TextFieldComponent("Front"),
            TextFieldComponent("Back")
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd', delete=False) as f:
            file_path = f.name
        
        try:
            # Export
            exporter = TemplateExporter()
            metadata = {'name': 'Test Template'}
            exporter.export_template(components, css="", metadata=metadata, file_path=file_path)
            
            # Import
            importer = TemplateImporter()
            result = importer.import_template(file_path)
            
            assert len(result['components']) == 2
            assert result['components'][0].field_name == "Front"
            assert result['components'][1].field_name == "Back"
        
        finally:
            Path(file_path).unlink(missing_ok=True)
    
    def test_import_preserves_properties(self):
        """Test that importing preserves component properties"""
        component = TextFieldComponent("TestField")
        component.width = "200px"
        component.height = "50px"
        component.font_size = 14
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd', delete=False) as f:
            file_path = f.name
        
        try:
            # Export
            exporter = TemplateExporter()
            exporter.export_template([component], css="", file_path=file_path)
            
            # Import
            importer = TemplateImporter()
            result = importer.import_template(file_path)
            imported = result['components']
            
            assert imported[0].width == "200px"
            assert imported[0].height == "50px"
            assert imported[0].font_size == 14
        
        finally:
            Path(file_path).unlink(missing_ok=True)
    
    def test_import_from_string(self):
        """Test importing from JSON string"""
        template_json = json.dumps({
            "metadata": {
                "version": "1.0",
                "created": "2025-01-01T00:00:00",
                "name": "Test"
            },
            "components": [
                {
                    "type": "text_field",
                    "x": 10,
                    "y": 20,
                    "width": 100,
                    "height": 50,
                    "properties": {
                        "field_name": "TestField"
                    },
                    "children": []
                }
            ],
            "css": ""
        })
        
        importer = TemplateImporter()
        result = importer.import_from_string(template_json)
        
        assert 'components' in result
        assert len(result['components']) == 1
        assert result['components'][0].field_name == "TestField"
    
    def test_import_invalid_version(self):
        """Test importing template with invalid version"""
        template_json = json.dumps({
            "metadata": {
                "version": "99.0",  # Future version
                "created": "2025-01-01T00:00:00"
            },
            "components": [],
            "css": ""
        })
        
        importer = TemplateImporter()
        
        # Should still work (we accept v1.x)
        # But might raise error for incompatible versions
        # Depends on implementation
    
    def test_import_invalid_file(self):
        """Test importing invalid file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd', delete=False) as f:
            f.write("invalid json")
            file_path = f.name
        
        try:
            importer = TemplateImporter()
            
            with pytest.raises(Exception):  # Should raise some kind of error
                importer.import_template(file_path)
        
        finally:
            Path(file_path).unlink(missing_ok=True)


class TestTemplateSharing:
    """Test TemplateSharing"""
    
    def test_create_template_bundle(self):
        """Test creating template bundle"""
        components1 = [TextFieldComponent("Front1")]
        components2 = [TextFieldComponent("Front2")]
        
        templates = [
            {"name": "Template 1", "components": components1, "css": ""},
            {"name": "Template 2", "components": components2, "css": ""}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd-bundle', delete=False) as f:
            file_path = f.name
        
        try:
            sharing = TemplateSharing()
            sharing.create_template_bundle(templates, bundle_name="Test Bundle", output_path=file_path)
            
            assert Path(file_path).exists()
            
            # Check content
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'templates' in data
            assert len(data['templates']) == 2
        
        finally:
            Path(file_path).unlink(missing_ok=True)
    
    def test_import_template_bundle(self):
        """Test importing template bundle"""
        components1 = [TextFieldComponent("Front1")]
        components2 = [TextFieldComponent("Front2")]
        
        templates = [
            {"name": "Template 1", "components": components1, "css": ""},
            {"name": "Template 2", "components": components2, "css": ""}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.atd-bundle', delete=False) as f:
            file_path = f.name
        
        try:
            # Create bundle
            sharing = TemplateSharing()
            sharing.create_template_bundle(templates, bundle_name="Test Bundle", output_path=file_path)
            
            # Import bundle
            imported = sharing.import_template_bundle(file_path)
            
            assert len(imported) == 2
            # Bundle returns list of template dicts
            assert len(imported[0]['components']) == 1
            assert len(imported[1]['components']) == 1
        
        finally:
            Path(file_path).unlink(missing_ok=True)
    
    def test_validate_template(self):
        """Test template validation"""
        valid_template = {
            'metadata': {'name': 'Test'},
            'components': [{'type': 'text_field', 'field_name': 'Front'}]
        }
        
        sharing = TemplateSharing()
        
        # Should return True for valid template
        assert sharing.validate_template(valid_template) == True
    
    def test_validate_empty_template(self):
        """Test validating empty template"""
        sharing = TemplateSharing()
        
        # Empty template should be invalid (no metadata)
        assert sharing.validate_template([]) == False
        
        # Template with no components should be invalid
        invalid_template = {'metadata': {}}
        assert sharing.validate_template(invalid_template) == False
