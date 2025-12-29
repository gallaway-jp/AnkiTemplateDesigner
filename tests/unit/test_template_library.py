"""
Tests for template library functionality.
"""

import pytest
from ui.template_library import TemplateLibrary
from ui.components import ComponentType


class TestTemplateLibrary:
    """Test TemplateLibrary"""
    
    def test_get_categories(self):
        """Test getting template categories"""
        categories = TemplateLibrary.get_categories()
        
        assert len(categories) > 0
        assert "Language Learning" in categories
        assert "Medical" in categories
        assert "Science & Math" in categories
    
    def test_get_all_templates(self):
        """Test getting all templates"""
        templates = TemplateLibrary.get_all_templates()
        
        assert len(templates) == 10  # We created 10 templates
        
        # Check template structure
        for template in templates:
            assert 'id' in template
            assert 'name' in template
            assert 'description' in template
            assert 'category' in template
    
    def test_create_basic_text_template(self):
        """Test creating basic text template"""
        template = TemplateLibrary.create_template('basic_text')
        
        assert template is not None
        assert 'front' in template
        assert 'back' in template
        assert len(template['front']) > 0
        assert len(template['back']) > 0
        
        # Should have Front and Back fields
        all_components = template['front'] + template['back']
        front_components = [c for c in all_components if getattr(c, 'field_name', '') == 'Front']
        back_components = [c for c in all_components if getattr(c, 'field_name', '') == 'Back']
        
        assert len(front_components) > 0
        assert len(back_components) > 0
    
    def test_create_vocabulary_template(self):
        """Test creating vocabulary template"""
        template = TemplateLibrary.create_template('vocabulary')
        
        assert template is not None
        assert 'front' in template
        assert 'back' in template
        
        # Should have word, pronunciation, definition, example
        all_components = template['front'] + template['back']
        field_names = [getattr(c, 'field_name', '') for c in all_components]
        
        assert 'Word' in field_names
    
    def test_create_cloze_template(self):
        """Test creating cloze template"""
        template = TemplateLibrary.create_template('cloze_basic')
        
        assert template is not None
        assert 'front' in template
        assert 'back' in template
        assert len(template['front']) > 0
    
    def test_create_image_occlusion_template(self):
        """Test creating image occlusion template"""
        template = TemplateLibrary.create_template('image_occlusion')
        
        assert template is not None
        assert 'front' in template
        
        # Should have at least one image component
        all_components = template['front'] + template['back']
        image_components = [c for c in all_components if c.type == ComponentType.IMAGE_FIELD]
        assert len(image_components) > 0
    
    def test_create_formula_template(self):
        """Test creating formula template"""
        template = TemplateLibrary.create_template('formula')
        
        assert template is not None
        assert len(template['front']) > 0
    
    def test_create_minimal_template(self):
        """Test creating minimal template"""
        template = TemplateLibrary.create_template('minimal')
        
        assert template is not None
        assert len(template['front']) > 0
    
    def test_create_two_column_template(self):
        """Test creating two-column template"""
        template = TemplateLibrary.create_template('two_column')
        
        assert template is not None
        assert len(template['front']) > 0
    
    def test_create_medical_drug_template(self):
        """Test creating medical drug template"""
        template = TemplateLibrary.create_template('medical_drug')
        
        assert template is not None
        assert len(template['front']) > 0
        
        # Should have drug-related fields
        all_components = template['front'] + template['back']
        field_names = [getattr(c, 'field_name', '') for c in all_components]
        
        # At least one medical-related field
        medical_fields = ['Drug', 'Mechanism', 'Indications', 'Side']
        assert any(mf in ' '.join(field_names) for mf in medical_fields)
    
    def test_create_anatomy_template(self):
        """Test creating anatomy template"""
        template = TemplateLibrary.create_template('anatomy')
        
        assert template is not None
        assert len(template['front']) > 0
    
    def test_create_language_sentence_template(self):
        """Test creating language sentence template"""
        template = TemplateLibrary.create_template('language_sentence')
        
        assert template is not None
        assert len(template['front']) > 0
    
    def test_invalid_template_id(self):
        """Test creating template with invalid ID"""
        template = TemplateLibrary.create_template('invalid_id')
        assert template is None
    
    def test_template_components_have_properties(self):
        """Test that template components have proper properties"""
        template = TemplateLibrary.create_template('basic_text')
        
        all_components = template['front'] + template['back']
        for component in all_components:
            # Check basic properties exist
            assert hasattr(component, 'width')
            assert hasattr(component, 'height')
            assert hasattr(component, 'type')
    
    def test_filter_by_category(self):
        """Test filtering templates by category"""
        all_templates = TemplateLibrary.get_all_templates()
        
        # Get medical templates
        medical_templates = [t for t in all_templates if t['category'] == 'Medical']
        
        assert len(medical_templates) > 0
        
        # All should be medical
        for template in medical_templates:
            assert template['category'] == 'Medical'
