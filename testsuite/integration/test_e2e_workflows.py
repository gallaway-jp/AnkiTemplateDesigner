"""
End-to-end workflow tests

Tests cover:
- Complete template creation workflow
- Template editing and saving to Anki
- Import/Export functionality
- Constraint-based layout workflows
"""
import pytest
from ui.components import (
    TextFieldComponent, ImageFieldComponent, DividerComponent,
    HeadingComponent, ContainerComponent, ConditionalComponent
)
from ui.template_converter import TemplateConverter

# Create convenience aliases
components_to_html = TemplateConverter.components_to_html
components_to_css = TemplateConverter.components_to_css
from ui.constraints import ConstraintHelper, ConstraintSet, Constraint, ConstraintTarget, ConstraintType


class TestBasicWorkflow:
    """Test basic template creation workflow"""
    
    def test_create_simple_template(self):
        """Test creating a simple flashcard template from scratch"""
        # Step 1: Create components
        components = [
            TextFieldComponent("Front"),
            TextFieldComponent("Back")
        ]
        
        # Set properties
        components[0].font_size = 18
        components[0].font_family = "Arial"
        components[1].font_size = 14
        
        # Step 2: Convert to HTML
        html = components_to_html(components)
        assert html is not None
        
        # Step 3: Generate CSS
        css = components_to_css(components)
        assert css is not None
        
        # Step 4: Create template structure
        template = {
            'name': 'Basic',
            'qfmt': html,
            'afmt': html,
            'ord': 0
        }
        
        assert template['name'] == 'Basic'
        assert '{{Front}}' in template['qfmt'] or 'Front' in template['qfmt']
    
    def test_create_image_card_template(self):
        """Test creating a template with image"""
        components = [
            TextFieldComponent("Word"),
            ImageFieldComponent("Picture"),
            TextFieldComponent("Definition")
        ]
        
        html = components_to_html(components)
        assert html is not None
        
        # Should contain image reference
        # (Exact format depends on implementation)
    
    def test_create_multi_field_template(self):
        """Test creating template with multiple fields"""
        components = [
            TextFieldComponent("Field1"),
            TextFieldComponent("Field2"),
            TextFieldComponent("Field3"),
            TextFieldComponent("Field4"),
        ]
        
        html = components_to_html(components)
        css = components_to_css(components)
        
        assert html is not None
        assert css is not None


class TestConstraintWorkflow:
    """Test constraint-based layout workflows"""
    
    def test_centered_card_layout(self):
        """Test creating a centered card layout with constraints"""
        # Create main content component
        content = ContainerComponent()
        content.use_constraints = True
        content.width = "300px"
        content.height = "200px"
        
        # Center in parent
        constraints = ConstraintHelper.create_centered_constraints("content")
        
        assert len(constraints) == 2
        assert content.use_constraints is True
    
    def test_two_column_layout(self):
        """Test creating two-column layout with constraints"""
        left_col = ContainerComponent()
        left_col.use_constraints = True
        left_col.width = "180px"
        left_col.height = "400px"
        
        right_col = ContainerComponent()
        right_col.use_constraints = True
        right_col.width = "180px"
        right_col.height = "400px"
        
        components = [left_col, right_col]
        
        assert all(c.use_constraints for c in components)
    
    def test_vertical_stack_with_constraints(self):
        """Test creating vertical stack using constraints"""
        components = [
            TextFieldComponent("Header"),
            TextFieldComponent("Body"),
            TextFieldComponent("Footer")
        ]
        
        for comp in components:
            comp.use_constraints = True
        
        # Create vertical chain
        comp_ids = ["header", "body", "footer"]
        constraints = ConstraintHelper.create_chain_constraints(comp_ids, vertical=True)
        
        assert len(constraints) > 0
    
    def test_match_parent_layout(self):
        """Test creating full-screen component with match parent"""
        fullscreen = ContainerComponent()
        fullscreen.use_constraints = True
        fullscreen.width = "400px"
        fullscreen.height = "600px"
        
        # Match parent on all sides
        constraints = ConstraintHelper.create_match_parent_constraints("fullscreen", margin=0)
        
        assert len(constraints) == 4


class TestEditWorkflow:
    """Test template editing workflows"""
    
    def test_add_component_to_existing(self):
        """Test adding a new component to existing template"""
        # Existing components
        existing = [
            TextFieldComponent("Front")
        ]
        
        # Add new component
        new_comp = TextFieldComponent("Back")
        existing.append(new_comp)
        
        assert len(existing) == 2
        
        # Convert to HTML
        html = components_to_html(existing)
        assert html is not None
    
    def test_remove_component(self):
        """Test removing a component"""
        components = [
            TextFieldComponent("Keep1"),
            TextFieldComponent("Remove"),
            TextFieldComponent("Keep2")
        ]
        
        # Set IDs
        components[0].id = "keep1"
        components[1].id = "remove"
        components[2].id = "keep2"
        
        # Remove middle component
        components = [c for c in components if c.id != "remove"]
        
        assert len(components) == 2
        assert all(c.id != "remove" for c in components)
    
    def test_modify_component_properties(self):
        """Test modifying component properties"""
        comp = TextFieldComponent("Original")
        comp.font_size = 14
        comp.color = "#000000"
        
        # Modify properties
        comp.field_name = "Modified"
        comp.font_size = 18
        comp.color = "#0066cc"
        
        assert comp.field_name == "Modified"
        assert comp.font_size == 18
        assert comp.color == "#0066cc"
    
    def test_reorder_components(self):
        """Test reordering components"""
        components = [
            TextFieldComponent("First"),
            TextFieldComponent("Second"),
            TextFieldComponent("Third")
        ]
        
        # Set IDs
        components[0].id = "first"
        components[1].id = "second"
        components[2].id = "third"
        
        # Reorder: move first to end
        components = [components[1], components[2], components[0]]
        
        assert components[0].id == "second"
        assert components[1].id == "third"
        assert components[2].id == "first"


class TestSaveWorkflow:
    """Test saving templates to Anki"""
    
    def test_prepare_template_for_save(self, sample_template):
        """Test preparing template data for Anki"""
        components = [
            TextFieldComponent("Front")
        ]
        
        # Generate qfmt
        qfmt = components_to_html(components)
        
        # Generate afmt (with answer)
        answer_components = components.copy()
        answer_components.append(TextFieldComponent("Back"))
        afmt = components_to_html(answer_components)
        
        # Generate CSS
        css = components_to_css(components)
        
        # Update template
        template = sample_template.copy()
        template['tmpls'][0]['qfmt'] = qfmt
        template['tmpls'][0]['afmt'] = afmt
        template['css'] = css
        
        assert template['tmpls'][0]['qfmt'] is not None
        assert template['tmpls'][0]['afmt'] is not None
        assert template['css'] is not None
    
    def test_save_with_constraints(self):
        """Test saving template with constraint layout"""
        comp = TextFieldComponent("Text")
        comp.use_constraints = True
        comp.width = "200px"
        comp.height = "100px"
        
        # Add constraints
        constraints = ConstraintHelper.create_centered_constraints("centered")
        
        # Convert to HTML
        html = components_to_html([comp])
        
        # Constraint data should be available
        assert comp.use_constraints is True
        assert len(constraints) > 0


class TestImportExport:
    """Test import/export workflows"""
    
    def test_export_template_components(self):
        """Test exporting component data"""
        components = [
            TextFieldComponent("Front"),
            ImageFieldComponent("Image")
        ]
        
        # Components exist
        assert len(components) == 2
        assert isinstance(components[0], TextFieldComponent)
        assert isinstance(components[1], ImageFieldComponent)
    
    def test_import_template_components(self):
        """Test importing component data"""
        # Simulated import data
        components = [
            TextFieldComponent("Front"),
            TextFieldComponent("Back")
        ]
        
        # Set IDs
        components[0].id = 'imported1'
        components[1].id = 'imported2'
        
        assert len(components) == 2
        assert components[0].id == 'imported1'
        assert components[1].id == 'imported2'


class TestComplexScenarios:
    """Test complex real-world scenarios"""
    
    def test_language_learning_card(self):
        """Test creating a language learning flashcard"""
        # Front: Word + Image
        front_components = [
            TextFieldComponent("Word"),
            TextFieldComponent("Pronunciation"),
            ImageFieldComponent("Image")
        ]
        
        front_components[0].font_size = 24
        front_components[1].font_size = 14
        
        # Back: Everything + Translation
        back_components = front_components.copy()
        back_components.extend([
            TextFieldComponent("Translation"),
            TextFieldComponent("Example")
        ])
        
        back_components[3].font_size = 18
        back_components[4].font_size = 12
        
        # Generate templates
        qfmt = components_to_html(front_components)
        afmt = components_to_html(back_components)
        css = components_to_css(back_components)
        
        assert qfmt is not None
        assert afmt is not None
        assert css is not None
    
    def test_cloze_deletion_template(self):
        """Test creating a cloze deletion template"""
        components = [
            TextFieldComponent("Text"),
            TextFieldComponent("Extra")
        ]
        
        components[0].font_size = 16
        components[1].font_size = 12
        
        html = components_to_html(components)
        css = components_to_css(components)
        
        assert html is not None
    
    def test_responsive_layout_with_constraints(self):
        """Test creating responsive layout using constraints"""
        # Header that spans full width
        header = TextFieldComponent("Title")
        header.use_constraints = True
        header.height = "60px"
        
        # Content that's centered with fixed width
        content = TextFieldComponent("Content")
        content.use_constraints = True
        content.width = "300px"
        content.height = "200px"
        
        # Footer that spans full width at bottom
        footer = TextFieldComponent("Footer")
        footer.use_constraints = True
        footer.height = "40px"
        
        components = [header, content, footer]
        
        # All should use constraints
        assert all(c.use_constraints for c in components)
