"""Tests for template service."""

import pytest
import tempfile
import os
from anki_template_designer.services.template_service import TemplateService
from anki_template_designer.core.models import Template


@pytest.fixture
def temp_service():
    """Create a service with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield TemplateService(tmpdir)


class TestTemplateServiceCreation:
    """Tests for template creation."""
    
    def test_create_template(self, temp_service):
        """Test template creation."""
        template = temp_service.create_template("Test")
        assert template.name == "Test"
        assert temp_service.current_template == template
    
    def test_create_template_default_name(self, temp_service):
        """Test template creation with default name."""
        template = temp_service.create_template()
        assert template.name == "Untitled Template"
    
    def test_create_template_adds_to_cache(self, temp_service):
        """Test template is added to cache."""
        template = temp_service.create_template("Cached")
        assert template.id in temp_service._templates


class TestTemplateServicePersistence:
    """Tests for template saving and loading."""
    
    def test_save_template(self, temp_service):
        """Test template saving."""
        template = temp_service.create_template("Test")
        assert temp_service.save_template(template)
        
        # Check file exists
        file_path = temp_service._get_template_path(template.id)
        assert os.path.exists(file_path)
    
    def test_save_current_template(self, temp_service):
        """Test saving current template without argument."""
        temp_service.create_template("Current")
        assert temp_service.save_template()
    
    def test_save_no_template_returns_false(self, temp_service):
        """Test saving with no template returns False."""
        assert not temp_service.save_template()
    
    def test_save_and_load(self, temp_service):
        """Test save and load round-trip."""
        template = temp_service.create_template("Test")
        template.css = "body { color: red; }"
        
        assert temp_service.save_template(template)
        
        # Clear cache
        temp_service._templates.clear()
        temp_service._current_template = None
        
        # Load from disk
        loaded = temp_service.load_template(template.id)
        assert loaded is not None
        assert loaded.name == "Test"
        assert loaded.css == "body { color: red; }"
    
    def test_load_nonexistent_returns_none(self, temp_service):
        """Test loading nonexistent template returns None."""
        result = temp_service.load_template("nonexistent-id")
        assert result is None


class TestTemplateServiceListing:
    """Tests for template listing."""
    
    def test_list_templates(self, temp_service):
        """Test template listing."""
        temp_service.create_template("First")
        temp_service.save_template()
        
        temp_service.create_template("Second")
        temp_service.save_template()
        
        templates = temp_service.list_templates()
        assert len(templates) == 2
    
    def test_list_templates_sorted_by_date(self, temp_service):
        """Test templates are sorted by modified date."""
        t1 = temp_service.create_template("First")
        temp_service.save_template()
        
        import time
        time.sleep(0.01)  # Ensure different timestamp
        
        t2 = temp_service.create_template("Second")
        temp_service.save_template()
        
        templates = temp_service.list_templates()
        # Most recent first
        assert templates[0]["name"] == "Second"
    
    def test_list_empty_directory(self, temp_service):
        """Test listing with no templates."""
        templates = temp_service.list_templates()
        assert templates == []


class TestTemplateServiceDeletion:
    """Tests for template deletion."""
    
    def test_delete_template(self, temp_service):
        """Test template deletion."""
        template = temp_service.create_template("ToDelete")
        temp_service.save_template()
        
        assert temp_service.delete_template(template.id)
        assert temp_service.get_template(template.id) is None
    
    def test_delete_clears_current(self, temp_service):
        """Test deleting current template clears it."""
        template = temp_service.create_template("Current")
        temp_service.save_template()
        
        assert temp_service.current_template == template
        temp_service.delete_template(template.id)
        assert temp_service.current_template is None
    
    def test_delete_removes_file(self, temp_service):
        """Test deletion removes file from disk."""
        template = temp_service.create_template("ToDelete")
        temp_service.save_template()
        
        file_path = temp_service._get_template_path(template.id)
        assert os.path.exists(file_path)
        
        temp_service.delete_template(template.id)
        assert not os.path.exists(file_path)


class TestTemplateServiceRetrieval:
    """Tests for template retrieval."""
    
    def test_get_template_from_cache(self, temp_service):
        """Test getting template from cache."""
        template = temp_service.create_template("Cached")
        
        result = temp_service.get_template(template.id)
        assert result == template
    
    def test_get_template_from_disk(self, temp_service):
        """Test getting template loads from disk if not cached."""
        template = temp_service.create_template("OnDisk")
        temp_service.save_template()
        
        # Clear cache
        temp_service._templates.clear()
        
        result = temp_service.get_template(template.id)
        assert result is not None
        assert result.name == "OnDisk"
    
    def test_set_current_template(self, temp_service):
        """Test setting current template."""
        template = temp_service.create_template("Test")
        temp_service.save_template()
        
        temp_service._current_template = None
        
        assert temp_service.set_current_template(template.id)
        assert temp_service.current_template == template
    
    def test_set_current_nonexistent_returns_false(self, temp_service):
        """Test setting nonexistent template as current returns False."""
        assert not temp_service.set_current_template("nonexistent")


class TestTemplateServiceDuplication:
    """Tests for template duplication."""
    
    def test_duplicate_template(self, temp_service):
        """Test template duplication."""
        original = temp_service.create_template("Original")
        original.css = "body { color: blue; }"
        temp_service.save_template()
        
        duplicate = temp_service.duplicate_template(original.id)
        
        assert duplicate is not None
        assert duplicate.id != original.id
        assert duplicate.name == "Original (Copy)"
        assert duplicate.css == original.css
    
    def test_duplicate_with_custom_name(self, temp_service):
        """Test duplication with custom name."""
        original = temp_service.create_template("Original")
        temp_service.save_template()
        
        duplicate = temp_service.duplicate_template(original.id, "My Copy")
        
        assert duplicate.name == "My Copy"
    
    def test_duplicate_nonexistent_returns_none(self, temp_service):
        """Test duplicating nonexistent template returns None."""
        result = temp_service.duplicate_template("nonexistent")
        assert result is None


class TestTemplateServiceSecurity:
    """Security-related tests."""
    
    def test_path_traversal_prevention(self, temp_service):
        """Test path traversal is prevented."""
        # Attempt path traversal
        malicious_id = "../../../etc/passwd"
        safe_path = temp_service._get_template_path(malicious_id)
        
        # Should not contain path separators
        assert ".." not in safe_path
        assert safe_path.endswith(".json")
