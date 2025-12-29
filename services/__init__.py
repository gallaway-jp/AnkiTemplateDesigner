"""
Services package - Business logic and dependency injection
"""

from .service_container import ServiceContainer
from .template_service import TemplateService

__all__ = ['ServiceContainer', 'TemplateService']
