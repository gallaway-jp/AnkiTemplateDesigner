"""
Custom exception hierarchy for Anki Template Designer

This module provides a structured exception hierarchy for better error handling
and clearer error messages throughout the application.
"""


class TemplateDesignerError(Exception):
    """
    Base exception for all Anki Template Designer errors.
    
    All custom exceptions in the application should inherit from this base class
    to allow for consistent error handling and categorization.
    """
    pass


class TemplateValidationError(TemplateDesignerError):
    """
    Raised when template validation fails.
    
    This includes syntax errors, structural issues, or semantic problems
    in template HTML or mustache syntax.
    
    Attributes:
        message (str): Error description
        field (str, optional): Field name that caused the error
        line_number (int, optional): Line number where error occurred
    """
    
    def __init__(self, message, field=None, line_number=None):
        """
        Initialize template validation error.
        
        Args:
            message: Detailed error description
            field: Field name that caused the error (optional)
            line_number: Line number in template where error occurred (optional)
        """
        self.message = message
        self.field = field
        self.line_number = line_number
        
        # Build detailed error message
        details = []
        if field:
            details.append(f"field='{field}'")
        if line_number:
            details.append(f"line={line_number}")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class TemplateSecurityError(TemplateDesignerError):
    """
    Raised when a security violation is detected in template content.
    
    This includes XSS attempts, dangerous HTML/CSS patterns, or attempts
    to bypass security restrictions.
    
    Attributes:
        message (str): Error description
        violation_type (str): Type of security violation
        dangerous_content (str, optional): The dangerous content that was detected
    """
    
    def __init__(self, message, violation_type=None, dangerous_content=None):
        """
        Initialize template security error.
        
        Args:
            message: Detailed error description
            violation_type: Type of security violation (e.g., 'xss', 'css_injection')
            dangerous_content: The dangerous content detected (truncated if long)
        """
        self.message = message
        self.violation_type = violation_type
        self.dangerous_content = dangerous_content
        
        # Build detailed error message
        details = []
        if violation_type:
            details.append(f"type={violation_type}")
        if dangerous_content:
            # Truncate long content for security logs
            truncated = dangerous_content[:50] + '...' if len(dangerous_content) > 50 else dangerous_content
            details.append(f"content='{truncated}'")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class TemplateSaveError(TemplateDesignerError):
    """
    Raised when saving a template to Anki fails.
    
    This could be due to database issues, permission problems, or
    conflicts with existing templates.
    
    Attributes:
        message (str): Error description
        template_id (int, optional): ID of template being saved
        note_type (str, optional): Note type name
    """
    
    def __init__(self, message, template_id=None, note_type=None):
        """
        Initialize template save error.
        
        Args:
            message: Detailed error description
            template_id: ID of template that failed to save
            note_type: Name of note type for the template
        """
        self.message = message
        self.template_id = template_id
        self.note_type = note_type
        
        # Build detailed error message
        details = []
        if template_id is not None:
            details.append(f"template_id={template_id}")
        if note_type:
            details.append(f"note_type='{note_type}'")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class TemplateLoadError(TemplateDesignerError):
    """
    Raised when loading a template from Anki fails.
    
    This could be due to missing templates, corrupted data, or
    incompatible template formats.
    
    Attributes:
        message (str): Error description
        template_id (int, optional): ID of template being loaded
        note_type (str, optional): Note type name
    """
    
    def __init__(self, message, template_id=None, note_type=None):
        """
        Initialize template load error.
        
        Args:
            message: Detailed error description
            template_id: ID of template that failed to load
            note_type: Name of note type for the template
        """
        self.message = message
        self.template_id = template_id
        self.note_type = note_type
        
        # Build detailed error message
        details = []
        if template_id is not None:
            details.append(f"template_id={template_id}")
        if note_type:
            details.append(f"note_type='{note_type}'")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class ResourceLimitError(TemplateDesignerError):
    """
    Raised when a resource limit is exceeded.
    
    This includes size limits for HTML/CSS, component count limits,
    or other resource constraints.
    
    Attributes:
        message (str): Error description
        resource_type (str): Type of resource that exceeded limit
        current_value (int, optional): Current value that exceeded limit
        limit_value (int, optional): Maximum allowed value
    """
    
    def __init__(self, message, resource_type=None, current_value=None, limit_value=None):
        """
        Initialize resource limit error.
        
        Args:
            message: Detailed error description
            resource_type: Type of resource (e.g., 'html_size', 'component_count')
            current_value: Actual value that exceeded the limit
            limit_value: Maximum allowed value
        """
        self.message = message
        self.resource_type = resource_type
        self.current_value = current_value
        self.limit_value = limit_value
        
        # Build detailed error message
        details = []
        if resource_type:
            details.append(f"resource={resource_type}")
        if current_value is not None and limit_value is not None:
            details.append(f"value={current_value}, limit={limit_value}")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class ComponentError(TemplateDesignerError):
    """
    Raised when a component operation fails.
    
    This includes invalid component configurations, constraint violations,
    or incompatible component combinations.
    
    Attributes:
        message (str): Error description
        component_type (str, optional): Type of component involved
        component_id (str, optional): ID of component if applicable
    """
    
    def __init__(self, message, component_type=None, component_id=None):
        """
        Initialize component error.
        
        Args:
            message: Detailed error description
            component_type: Type of component (e.g., 'TextFieldComponent')
            component_id: Unique identifier for the component
        """
        self.message = message
        self.component_type = component_type
        self.component_id = component_id
        
        # Build detailed error message
        details = []
        if component_type:
            details.append(f"type={component_type}")
        if component_id:
            details.append(f"id={component_id}")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class RenderError(TemplateDesignerError):
    """
    Raised when template rendering fails.
    
    This includes errors during HTML generation, CSS compilation,
    or preview rendering.
    
    Attributes:
        message (str): Error description
        renderer_type (str, optional): Type of renderer (e.g., 'Desktop', 'AnkiDroid')
        stage (str, optional): Rendering stage where error occurred
    """
    
    def __init__(self, message, renderer_type=None, stage=None):
        """
        Initialize render error.
        
        Args:
            message: Detailed error description
            renderer_type: Type of renderer that failed
            stage: Rendering stage (e.g., 'html_generation', 'css_compilation')
        """
        self.message = message
        self.renderer_type = renderer_type
        self.stage = stage
        
        # Build detailed error message
        details = []
        if renderer_type:
            details.append(f"renderer={renderer_type}")
        if stage:
            details.append(f"stage={stage}")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)


class ConstraintError(TemplateDesignerError):
    """
    Raised when constraint resolution fails.
    
    This includes circular dependencies, unsatisfiable constraints,
    or invalid constraint configurations.
    
    Attributes:
        message (str): Error description
        component_id (str, optional): Component with constraint problem
        constraint_type (str, optional): Type of constraint
    """
    
    def __init__(self, message, component_id=None, constraint_type=None):
        """
        Initialize constraint error.
        
        Args:
            message: Detailed error description
            component_id: ID of component with constraint issue
            constraint_type: Type of constraint (e.g., 'circular_dependency')
        """
        self.message = message
        self.component_id = component_id
        self.constraint_type = constraint_type
        
        # Build detailed error message
        details = []
        if component_id:
            details.append(f"component={component_id}")
        if constraint_type:
            details.append(f"type={constraint_type}")
        
        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"
        
        super().__init__(full_message)
