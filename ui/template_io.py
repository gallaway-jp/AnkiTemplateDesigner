"""
Template export and import functionality.

Allows saving templates to portable files and loading them back.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from .components import Component, ComponentType, Alignment
from utils.exceptions import TemplateLoadError, TemplateSaveError
from utils.logging_config import get_logger

logger = get_logger(__name__)


class TemplateExporter:
    """Handles exporting templates to portable formats."""
    
    FILE_EXTENSION = ".atd"  # Anki Template Designer format
    FILE_VERSION = "1.0"
    
    @staticmethod
    def export_template(components: List[Component], css: str, metadata: Optional[Dict] = None,
                       file_path: str = None) -> str:
        """
        Export template to a file.
        
        Args:
            components: List of components to export
            css: CSS styling
            metadata: Optional metadata (name, author, etc.)
            file_path: Path to save file (if None, returns JSON string)
            
        Returns:
            str: File path if saved, JSON string otherwise
            
        Raises:
            TemplateSaveError: If export fails
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.setdefault('version', TemplateExporter.FILE_VERSION)
            metadata.setdefault('created', datetime.now().isoformat())
            metadata.setdefault('name', 'Untitled Template')
            
            # Serialize components
            components_data = [TemplateExporter._serialize_component(c) for c in components]
            
            # Create export data
            export_data = {
                'metadata': metadata,
                'components': components_data,
                'css': css
            }
            
            # Convert to JSON
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            # Save to file if path provided
            if file_path:
                # Ensure proper extension
                if not file_path.endswith(TemplateExporter.FILE_EXTENSION):
                    file_path += TemplateExporter.FILE_EXTENSION
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                
                logger.info(f"Template exported to {file_path}")
                return file_path
            
            return json_str
            
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            raise TemplateSaveError(f"Export failed: {e}") from e
    
    @staticmethod
    def _serialize_component(component: Component) -> Dict:
        """
        Serialize a component to a dictionary.
        
        Args:
            component: Component to serialize
            
        Returns:
            Dict representation of component
        """
        data = {
            'type': component.type.value,
            'x': getattr(component, 'x', 0),
            'y': getattr(component, 'y', 0),
            'width': component.width,
            'height': component.height,
            'properties': {}
        }
        
        # Serialize type-specific properties
        if hasattr(component, 'field_name'):
            data['properties']['field_name'] = component.field_name
        
        if hasattr(component, 'font_family'):
            data['properties']['font_family'] = component.font_family
        
        if hasattr(component, 'font_size'):
            data['properties']['font_size'] = component.font_size
        
        if hasattr(component, 'text_color'):
            data['properties']['text_color'] = component.text_color
        
        if hasattr(component, 'background_color'):
            data['properties']['background_color'] = component.background_color
        
        if hasattr(component, 'alignment'):
            data['properties']['alignment'] = component.alignment.value if component.alignment else 'left'
        
        if hasattr(component, 'padding'):
            data['properties']['padding'] = component.padding
        
        if hasattr(component, 'margin'):
            data['properties']['margin'] = component.margin
        
        if hasattr(component, 'border_width'):
            data['properties']['border_width'] = component.border_width
        
        if hasattr(component, 'border_color'):
            data['properties']['border_color'] = component.border_color
        
        # Serialize children
        if hasattr(component, 'children') and component.children:
            data['children'] = [TemplateExporter._serialize_component(c) for c in component.children]
        
        return data


class TemplateImporter:
    """Handles importing templates from files."""
    
    @staticmethod
    def import_template(file_path: str) -> Dict:
        """
        Import template from a file.
        
        Args:
            file_path: Path to template file
            
        Returns:
            Dict with 'components', 'css', and 'metadata'
            
        Raises:
            TemplateLoadError: If import fails
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate format
            if 'metadata' not in data or 'components' not in data:
                raise TemplateLoadError("Invalid template file format")
            
            # Check version compatibility
            version = data['metadata'].get('version', '1.0')
            if not TemplateImporter._is_version_compatible(version):
                logger.warning(f"Template version {version} may not be fully compatible")
            
            # Deserialize components
            components = [TemplateImporter._deserialize_component(c) for c in data['components']]
            
            result = {
                'components': components,
                'css': data.get('css', ''),
                'metadata': data.get('metadata', {})
            }
            
            logger.info(f"Template imported from {file_path}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in template file: {e}")
            raise TemplateLoadError("File is not valid JSON") from e
        except FileNotFoundError:
            logger.error(f"Template file not found: {file_path}")
            raise TemplateLoadError("Template file not found")
        except Exception as e:
            logger.error(f"Failed to import template: {e}")
            raise TemplateLoadError(f"Import failed: {e}") from e
    
    @staticmethod
    def import_from_string(json_str: str) -> Dict:
        """
        Import template from JSON string.
        
        Args:
            json_str: JSON string containing template data
            
        Returns:
            Dict with 'components', 'css', and 'metadata'
            
        Raises:
            TemplateLoadError: If import fails
        """
        try:
            data = json.loads(json_str)
            
            components = [TemplateImporter._deserialize_component(c) for c in data['components']]
            
            return {
                'components': components,
                'css': data.get('css', ''),
                'metadata': data.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to import from string: {e}")
            raise TemplateLoadError(f"Import failed: {e}") from e
    
    @staticmethod
    def _deserialize_component(data: Dict) -> Component:
        """
        Deserialize a component from a dictionary.
        
        Args:
            data: Dict representation of component
            
        Returns:
            Component instance
        """
        from .components import (
            TextFieldComponent, ImageFieldComponent, HeadingComponent,
            DividerComponent, ContainerComponent, ConditionalComponent
        )
        
        # Get component type
        component_type = ComponentType(data['type'])
        
        # Create appropriate component type
        props = data.get('properties', {})
        field_name = props.get('field_name', '')
        
        if component_type == ComponentType.TEXT_FIELD:
            component = TextFieldComponent(field_name)
        elif component_type == ComponentType.IMAGE_FIELD:
            component = ImageFieldComponent(field_name)
        elif component_type == ComponentType.HEADING:
            component = HeadingComponent(field_name)
        elif component_type == ComponentType.DIVIDER:
            component = DividerComponent()
        elif component_type == ComponentType.CONTAINER:
            component = ContainerComponent()
        elif component_type == ComponentType.CONDITIONAL:
            component = ConditionalComponent(field_name)
        else:
            # Fallback to base component
            component = Component(component_type, field_name)
        
        # Set position (if attributes exist)
        if hasattr(component, 'x'):
            component.x = data.get('x', 0)
        if hasattr(component, 'y'):
            component.y = data.get('y', 0)
        
        # Set dimensions
        component.width = data.get('width', '100%')
        component.height = data.get('height', 'auto')
        
        # Restore properties
        props = data.get('properties', {})
        
        if 'field_name' in props:
            component.field_name = props['field_name']
        
        if 'font_family' in props:
            component.font_family = props['font_family']
        
        if 'font_size' in props:
            component.font_size = props['font_size']
        
        if 'text_color' in props:
            component.text_color = props['text_color']
        
        if 'background_color' in props:
            component.background_color = props['background_color']
        
        if 'alignment' in props:
            component.alignment = Alignment(props['alignment'])
        
        if 'padding' in props:
            component.padding = props['padding']
        
        if 'margin' in props:
            component.margin = props['margin']
        
        if 'border_width' in props:
            component.border_width = props['border_width']
        
        if 'border_color' in props:
            component.border_color = props['border_color']
        
        # Restore children
        if 'children' in data:
            component.children = [TemplateImporter._deserialize_component(c) for c in data['children']]
            for child in component.children:
                child.parent = component
        
        return component
    
    @staticmethod
    def _is_version_compatible(version: str) -> bool:
        """
        Check if template version is compatible.
        
        Args:
            version: Version string
            
        Returns:
            bool: True if compatible
        """
        # For now, accept version 1.x
        try:
            major = int(version.split('.')[0])
            return major == 1
        except (ValueError, IndexError):
            return False


class TemplateSharing:
    """
    Utilities for sharing templates between users.
    
    Provides functions for creating shareable template bundles
    and validating imported templates.
    """
    
    @staticmethod
    def create_template_bundle(templates: List[Dict], bundle_name: str, 
                               output_path: str) -> str:
        """
        Create a bundle of multiple templates.
        
        Args:
            templates: List of template dicts (each with components, css, metadata)
            bundle_name: Name of the bundle
            output_path: Path to save bundle file
            
        Returns:
            str: Path to created bundle
            
        Raises:
            TemplateSaveError: If bundle creation fails
        """
        try:
            bundle_data = {
                'bundle_name': bundle_name,
                'created': datetime.now().isoformat(),
                'template_count': len(templates),
                'templates': []
            }
            
            for template in templates:
                template_data = TemplateExporter.export_template(
                    template['components'],
                    template.get('css', ''),
                    template.get('metadata', {})
                )
                bundle_data['templates'].append(json.loads(template_data))
            
            # Save bundle
            bundle_path = output_path
            if not bundle_path.endswith('.atd-bundle'):
                bundle_path += '.atd-bundle'
            
            with open(bundle_path, 'w', encoding='utf-8') as f:
                json.dump(bundle_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Template bundle created: {bundle_path}")
            return bundle_path
            
        except Exception as e:
            logger.error(f"Failed to create bundle: {e}")
            raise TemplateSaveError(f"Bundle creation failed: {e}") from e
    
    @staticmethod
    def import_template_bundle(bundle_path: str) -> List[Dict]:
        """
        Import a bundle of templates.
        
        Args:
            bundle_path: Path to bundle file
            
        Returns:
            List of template dicts
            
        Raises:
            TemplateLoadError: If bundle import fails
        """
        try:
            with open(bundle_path, 'r', encoding='utf-8') as f:
                bundle_data = json.load(f)
            
            templates = []
            for template_data in bundle_data.get('templates', []):
                json_str = json.dumps(template_data)
                template = TemplateImporter.import_from_string(json_str)
                templates.append(template)
            
            logger.info(f"Imported {len(templates)} templates from bundle")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to import bundle: {e}")
            raise TemplateLoadError(f"Bundle import failed: {e}") from e
    
    @staticmethod
    def validate_template(template_data: Dict) -> bool:
        """
        Validate template data structure.
        
        Args:
            template_data: Template data to validate
            
        Returns:
            bool: True if valid
        """
        try:
            # Check required fields
            if 'metadata' not in template_data:
                return False
            
            if 'components' not in template_data:
                return False
            
            # Validate components
            for component_data in template_data['components']:
                if 'type' not in component_data:
                    return False
                
                # Check if type is valid
                try:
                    ComponentType(component_data['type'])
                except ValueError:
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Template validation failed: {e}")
            return False
