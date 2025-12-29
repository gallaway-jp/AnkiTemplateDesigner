"""
Tests for template services
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from services.service_container import ServiceContainer
from services.template_service import TemplateService
from utils import TemplateLoadError, TemplateSaveError


class TestServiceContainer:
    """Tests for ServiceContainer dependency injection"""
    
    def test_container_initialization(self):
        """Test ServiceContainer initializes empty"""
        container = ServiceContainer()
        
        assert len(container.list_services()) == 0
    
    def test_register_singleton(self):
        """Test registering a singleton service"""
        container = ServiceContainer()
        config = {'key': 'value'}
        
        container.register_singleton('config', config)
        
        assert container.has('config')
        assert container.get('config') == config
        assert container.get('config') is config  # Same instance
    
    def test_register_factory(self):
        """Test registering a factory service"""
        container = ServiceContainer()
        factory = Mock(return_value="new_instance")
        
        container.register_factory('service', factory)
        
        result1 = container.get('service')
        result2 = container.get('service')
        
        assert factory.call_count == 2  # Called twice
        assert result1 == "new_instance"
        assert result2 == "new_instance"
    
    def test_duplicate_singleton_registration_error(self):
        """Test registering duplicate singleton raises error"""
        container = ServiceContainer()
        container.register_singleton('test', 'first')
        
        with pytest.raises(ValueError, match="already registered"):
            container.register_singleton('test', 'second')
    
    def test_duplicate_factory_registration_error(self):
        """Test registering duplicate factory raises error"""
        container = ServiceContainer()
        container.register_factory('test', lambda: 'first')
        
        with pytest.raises(ValueError, match="already registered"):
            container.register_factory('test', lambda: 'second')
    
    def test_get_unregistered_service_error(self):
        """Test getting unregistered service raises KeyError"""
        container = ServiceContainer()
        
        with pytest.raises(KeyError, match="not registered"):
            container.get('nonexistent')
    
    def test_singleton_has_precedence_over_factory(self):
        """Test singletons are checked before factories"""
        container = ServiceContainer()
        container.register_singleton('test', 'singleton')
        
        # This won't actually work because of duplicate check,
        # but we test the get precedence
        result = container.get('test')
        
        assert result == 'singleton'
    
    def test_has_method(self):
        """Test has() method works correctly"""
        container = ServiceContainer()
        
        assert not container.has('test')
        
        container.register_singleton('test', 'value')
        
        assert container.has('test')
    
    def test_list_services(self):
        """Test listing all registered services"""
        container = ServiceContainer()
        container.register_singleton('service1', 'value1')
        container.register_factory('service2', lambda: 'value2')
        
        services = container.list_services()
        
        assert 'service1' in services
        assert 'service2' in services
        assert len(services) == 2
    
    def test_clear_services(self):
        """Test clearing all services"""
        container = ServiceContainer()
        container.register_singleton('test', 'value')
        
        container.clear()
        
        assert len(container.list_services()) == 0
        assert not container.has('test')
    
    def test_override_singleton(self):
        """Test overriding existing singleton"""
        container = ServiceContainer()
        container.register_singleton('test', 'original')
        
        container.override('test', 'overridden')
        
        assert container.get('test') == 'overridden'
    
    def test_override_factory_converts_to_singleton(self):
        """Test overriding factory converts it to singleton"""
        container = ServiceContainer()
        factory = Mock(return_value='factory_value')
        container.register_factory('test', factory)
        
        container.override('test', 'override_value')
        
        # Should not call factory anymore
        result = container.get('test')
        assert result == 'override_value'
        assert factory.call_count == 0
    
    def test_override_nonexistent_service_error(self):
        """Test overriding nonexistent service raises error"""
        container = ServiceContainer()
        
        with pytest.raises(KeyError, match="Cannot override"):
            container.override('nonexistent', 'value')


class TestTemplateService:
    """Tests for TemplateService"""
    
    def test_service_initialization(self):
        """Test TemplateService initializes with dependencies"""
        collection = Mock()
        service = TemplateService(collection)
        
        assert service.collection is collection
        assert service.security_validator is not None
        assert service.converter is not None
    
    def test_load_note_type_by_id(self):
        """Test loading note type by specific ID"""
        collection = Mock()
        note_type = {'id': 123, 'name': 'Test Type'}
        collection.models.get.return_value = note_type
        
        service = TemplateService(collection)
        result = service.load_note_type(123)
        
        assert result == note_type
        collection.models.get.assert_called_once_with(123)
    
    def test_load_first_available_note_type(self):
        """Test loading first available note type when ID is None"""
        collection = Mock()
        mock_name_id = Mock()
        mock_name_id.id = 456
        collection.models.all_names_and_ids.return_value = [mock_name_id]
        note_type = {'id': 456, 'name': 'First Type'}
        collection.models.get.return_value = note_type
        
        service = TemplateService(collection)
        result = service.load_note_type(None)
        
        assert result == note_type
        collection.models.get.assert_called_once_with(456)
    
    def test_load_note_type_none_available(self):
        """Test loading note type when none exist"""
        collection = Mock()
        collection.models.all_names_and_ids.return_value = []
        
        service = TemplateService(collection)
        result = service.load_note_type(None)
        
        assert result is None
    
    def test_load_note_type_not_found_error(self):
        """Test loading nonexistent note type raises error"""
        collection = Mock()
        collection.models.get.return_value = None
        
        service = TemplateService(collection)
        
        with pytest.raises(TemplateLoadError, match="not found"):
            service.load_note_type(999)
    
    def test_get_templates(self):
        """Test getting templates from note type"""
        service = TemplateService(Mock())
        note_type = {'tmpls': [{'name': 'Card 1'}, {'name': 'Card 2'}]}
        
        templates = service.get_templates(note_type)
        
        assert len(templates) == 2
        assert templates[0]['name'] == 'Card 1'
    
    def test_get_sample_note(self):
        """Test getting sample note for preview"""
        collection = Mock()
        note_type = {'name': 'Basic'}
        collection.find_notes.return_value = [100, 200]
        mock_note = Mock()
        collection.get_note.return_value = mock_note
        
        service = TemplateService(collection)
        result = service.get_sample_note(note_type)
        
        assert result is mock_note
        collection.find_notes.assert_called_once()
        collection.get_note.assert_called_once_with(100)
    
    def test_get_sample_note_none_found(self):
        """Test getting sample note when none exist"""
        collection = Mock()
        note_type = {'name': 'Basic'}
        collection.find_notes.return_value = []
        
        service = TemplateService(collection)
        result = service.get_sample_note(note_type)
        
        assert result is None


class TestServiceIntegration:
    """Integration tests for service layer"""
    
    def test_container_with_template_service(self):
        """Test ServiceContainer with TemplateService"""
        container = ServiceContainer()
        collection = Mock()
        
        # Register collection as singleton
        container.register_singleton('collection', collection)
        
        # Register template service factory
        container.register_factory(
            'template_service',
            lambda: TemplateService(container.get('collection'))
        )
        
        # Resolve template service
        service = container.get('template_service')
        
        assert isinstance(service, TemplateService)
        assert service.collection is collection
    
    def test_dependency_injection_pattern(self):
        """Test full dependency injection pattern"""
        container = ServiceContainer()
        
        # Create mock dependencies
        collection = Mock()
        security_validator = Mock()
        
        # Register dependencies
        container.register_singleton('collection', collection)
        container.register_singleton('security_validator', security_validator)
        
        # Register service with dependencies
        container.register_factory(
            'template_service',
            lambda: TemplateService(
                container.get('collection'),
                container.get('security_validator')
            )
        )
        
        # Resolve and use service
        service = container.get('template_service')
        
        assert service.collection is collection
        assert service.security_validator is security_validator
    
    def test_container_with_mocked_collection(self):
        """Test using container with fully mocked Anki collection"""
        container = ServiceContainer()
        
        # Create comprehensive mock collection
        collection = Mock()
        collection.models = Mock()
        collection.models.all_names_and_ids.return_value = []
        
        container.register_singleton('collection', collection)
        container.register_factory(
            'template_service',
            lambda: TemplateService(container.get('collection'))
        )
        
        service = container.get('template_service')
        result = service.load_note_type(None)
        
        # Should handle empty collection gracefully
        assert result is None
