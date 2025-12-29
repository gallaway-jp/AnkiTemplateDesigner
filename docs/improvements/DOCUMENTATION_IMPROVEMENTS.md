# Documentation Improvement Plan

**Project:** Anki Template Designer  
**Current Documentation Grade:** B+ (70%)  
**Target Documentation Grade:** A- (90%)  
**Timeline:** 3 months

---

## Quick Summary

### What's Good ✅
- Module-level docstrings (95% coverage)
- Exception class documentation (excellent)
- Security documentation (comprehensive)
- Service container examples (perfect)
- Recent markdown documentation (testing, licenses)

### What Needs Work ⚠️
- Public method docstrings (70% → need 95%)
- Type hints coverage (65% → need 90%)
- Docstring style consistency (80% → need 100%)
- Usage examples (30% → need 60%)
- Complex algorithm comments

---

## Priority 1: Missing Docstrings (2 Weeks)

### Core Conversion Methods (Critical)

#### File: `ui/template_converter.py`

```python
@staticmethod
def components_to_html(components):
    """
    Convert visual components to Anki template HTML.
    
    Traverses the component tree and generates sanitized HTML with
    Anki field references using {{FieldName}} mustache syntax.
    
    Args:
        components (List[Component]): Visual components to convert
    
    Returns:
        str: Sanitized HTML template string ready for Anki
    
    Raises:
        ResourceLimitError: If component count exceeds MAX_COMPONENTS
        TemplateSecurityError: If dangerous HTML patterns detected
    
    Example:
        >>> from ui.components import TextFieldComponent, DividerComponent
        >>> components = [
        ...     TextFieldComponent("Front"),
        ...     DividerComponent(),
        ...     TextFieldComponent("Back")
        ... ]
        >>> html = TemplateConverter.components_to_html(components)
        >>> print(html)
        <div class="component-0">{{Front}}</div>
        <hr class="component-1">
        <div class="component-2">{{Back}}</div>
    
    Security:
        All output is sanitized using SecurityValidator to prevent XSS.
        Field names are validated before inclusion.
    
    See Also:
        components_to_css(): Generates corresponding CSS
        html_to_components(): Reverse conversion
    """
```

```python
@staticmethod
def components_to_css(components):
    """
    Generate CSS stylesheet from visual components.
    
    Creates CSS rules for each component with auto-generated selectors.
    Components are numbered sequentially (.component-0, .component-1, etc.).
    
    Args:
        components (List[Component]): Components to generate CSS for
    
    Returns:
        str: Complete CSS stylesheet string
    
    Example:
        >>> from ui.components import TextFieldComponent
        >>> comp = TextFieldComponent("Front")
        >>> comp.font_size = 24
        >>> comp.color = "#FF0000"
        >>> css = TemplateConverter.components_to_css([comp])
        >>> print(css)
        .component-0 {
            font-size: 24px;
            color: #FF0000;
        }
    
    See Also:
        Component.to_css(): Individual component CSS generation
    """
```

```python
@staticmethod
def html_to_components(html, css=""):
    """
    Parse HTML template into visual components.
    
    Attempts to reverse-engineer Anki template HTML back into the visual
    component representation. Best-effort conversion that may not preserve
    all original styling.
    
    Args:
        html (str): HTML template string
        css (str, optional): CSS stylesheet to parse. Defaults to "".
    
    Returns:
        List[Component]: List of parsed components
    
    Raises:
        TemplateValidationError: If HTML structure is invalid
        TemplateSecurityError: If dangerous patterns detected
    
    Example:
        >>> html = '<div>{{Front}}</div><hr><div>{{Back}}</div>'
        >>> components = TemplateConverter.html_to_components(html)
        >>> print(len(components))
        3
        >>> print(components[0].field_name)
        Front
    
    Notes:
        - Simple templates convert reliably
        - Complex nested structures may lose fidelity
        - Custom CSS classes might not fully restore
        - Always validates and sanitizes input
    
    See Also:
        components_to_html(): Forward conversion
    """
```

### UI Setup Methods

#### File: `ui/visual_builder.py`

```python
def setup_ui(self):
    """
    Initialize the visual builder user interface.
    
    Creates a three-panel layout:
    - Left: Component palette (draggable components)
    - Center: Template canvas (drop zone)
    - Right: Properties panel (component editing)
    
    Sets up drag-and-drop between palette and canvas,
    and synchronizes selection across all panels.
    
    Called once during widget initialization.
    """
```

#### File: `ui/properties_panel.py`

```python
def rebuild_ui(self):
    """
    Rebuild the properties panel for the current component.
    
    Dynamically generates appropriate controls based on the
    component type and its available properties. Clears existing
    controls and creates new ones.
    
    Property groups shown:
    - Field settings (for components with field_name)
    - Layout properties (width, height, margins, padding)
    - Text properties (font, color, alignment)
    - Style properties (background, borders)
    - Constraint properties (if use_constraints enabled)
    
    Called when:
    - Component selection changes
    - Component type changes
    - Constraint mode toggles
    """
```

#### File: `ui/component_tree.py`

```python
def rebuild_tree(self):
    """
    Rebuild the component tree from current component list.
    
    Clears the tree widget and recreates it from scratch,
    preserving the hierarchical structure of containers
    and their children.
    
    Called when:
    - Components are added or removed
    - Component hierarchy changes
    - Components are reordered
    """
```

---

## Priority 2: Component Class Documentation (1 Week)

### File: `ui/components.py`

```python
class Component:
    """
    Base class for all visual template components.
    
    Components are visual building blocks that can be placed on the template
    canvas and converted to HTML/CSS for use in Anki flashcards. They support
    two layout modes:
    
    1. Flow Layout: Traditional top-to-bottom stacking
    2. Constraint Layout: Android-style constraint-based positioning
    
    All components have visual properties (size, color, fonts) and can be
    styled independently. Container and Conditional components can have
    child components, forming a tree structure.
    
    Attributes:
        type (ComponentType): Component type (TEXT_FIELD, IMAGE_FIELD, etc.)
        field_name (str): Anki field name this component displays
        id (int): Unique identifier (set when added to canvas)
        
        # Visual Properties
        width (str): Width with unit ("100%", "200px", "auto")
        height (str): Height with unit
        margin_* (int): Margins in pixels (top, right, bottom, left)
        padding_* (int): Padding in pixels (top, right, bottom, left)
        
        # Text Properties
        font_family (str): CSS font family
        font_size (int): Font size in pixels
        font_weight (str): "normal", "bold", etc.
        color (str): Text color (hex or named)
        text_align (Alignment): Text alignment enum
        
        # Border Properties
        border_width (int): Border width in pixels
        border_style (str): "solid", "dashed", "dotted", etc.
        border_color (str): Border color
        border_radius (int): Corner radius in pixels
        
        # Constraint Properties
        use_constraints (bool): Use constraint layout vs flow layout
        constraints (List[dict]): List of constraint definitions
        constraint_horizontal_bias (float): Horizontal bias (0.0-1.0)
        constraint_vertical_bias (float): Vertical bias (0.0-1.0)
    
    Subclasses:
        TextFieldComponent: Displays text from an Anki field
        ImageFieldComponent: Displays images from a field
        HeadingComponent: Styled heading text (h1-h6)
        DividerComponent: Horizontal line separator
        ContainerComponent: Groups other components (can have children)
        ConditionalComponent: Conditionally shows content (can have children)
    
    Example:
        >>> # Create a styled text component
        >>> comp = TextFieldComponent("Question")
        >>> comp.font_size = 24
        >>> comp.color = "#333333"
        >>> comp.text_align = Alignment.CENTER
        >>> comp.margin_top = 20
        >>> 
        >>> # Convert to HTML
        >>> html = comp.to_html()
        >>> print(html)
        <div class="text-field">{{Question}}</div>
        >>> 
        >>> # Convert to CSS
        >>> css = comp.to_css(".component-0")
        >>> print(css)
        .component-0 {
            font-size: 24px;
            color: #333333;
            text-align: center;
            margin-top: 20px;
        }
    
    See Also:
        ComponentType: Enum of available component types
        TemplateConverter: Converts components to/from HTML/CSS
        ConstraintSet: Manages constraint-based positioning
    """
```

```python
class ComponentType(Enum):
    """
    Types of visual components available in the template designer.
    
    Attributes:
        TEXT_FIELD: Displays text from an Anki field ({{FieldName}})
        IMAGE_FIELD: Displays images from a field
        DIVIDER: Horizontal line separator (<hr>)
        CONTAINER: Groups other components (can have children)
        HEADING: Styled heading text (h1-h6)
        BUTTON: Interactive button (reserved for future use)
        CONDITIONAL: Shows content conditionally ({{#Field}}...{{/Field}})
    
    Example:
        >>> comp_type = ComponentType.TEXT_FIELD
        >>> print(comp_type.value)
        'text_field'
    """
```

```python
class Alignment(Enum):
    """
    Text alignment options for components.
    
    Attributes:
        LEFT: Align text to the left (default for LTR languages)
        CENTER: Center text horizontally
        RIGHT: Align text to the right
        JUSTIFY: Justify text (stretch to fill width)
    
    Example:
        >>> comp = TextFieldComponent("Front")
        >>> comp.text_align = Alignment.CENTER
    """
```

---

## Priority 3: Type Hints (1 Week)

### Files to Update

#### `ui/visual_builder.py`
```python
def setup_ui(self) -> None:
def get_components(self) -> List[Component]:
def set_components(self, components: List[Component]) -> None:
def clear(self) -> None:
```

#### `utils/template_utils.py`
```python
@staticmethod
def extract_fields(template_html: str) -> Set[str]:

@staticmethod
def validate_template(template_html: str) -> Tuple[bool, List[str]]:

@staticmethod
def get_template_info(template_dict: Dict[str, str]) -> Dict[str, Any]:
```

#### `ui/properties_panel.py`
```python
def set_component(self, component: Optional[Component]) -> None:
def rebuild_ui(self) -> None:
def _clear_widgets(self) -> None:
def _notify_change(self) -> None:
```

---

## Priority 4: Docstring Style Standardization (3 Days)

### Convert to Google Style

Current NumPy-style docstrings to convert:

```python
# BEFORE (NumPy style)
def validate_template(template_html):
    """
    Validate template syntax and security
    
    Parameters
    ----------
    template_html : str
        Template HTML string
    
    Returns
    -------
    tuple
        (is_valid, error_messages)
    """

# AFTER (Google style)
def validate_template(template_html: str) -> Tuple[bool, List[str]]:
    """
    Validate template syntax and security.
    
    Args:
        template_html (str): Template HTML string
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
```

---

## Priority 5: Complex Algorithm Comments (1 Week)

### Files to Document

#### `ui/constraints.py` - ConstraintResolver

```python
def _apply_constraint(self, comp_id: int, constraint: Constraint, component_map: dict):
    """
    Apply a single constraint to update component position.
    
    Modifies the position dictionary for the given component based on
    the constraint type and target. Supports both parent-relative and
    component-relative constraints.
    
    Constraint Types:
        - LEFT_TO_LEFT: Align left edges
        - LEFT_TO_RIGHT: Place left edge at target's right
        - RIGHT_TO_LEFT: Place right edge at target's left
        - RIGHT_TO_RIGHT: Align right edges
        - (Similar for TOP/BOTTOM)
        - CENTER_HORIZONTAL: Center horizontally in target
        - CENTER_VERTICAL: Center vertically in target
    
    Args:
        comp_id: ID of component being constrained
        constraint: Constraint to apply
        component_map: Map of IDs to components
    
    Example:
        Component A constrained LEFT_TO_LEFT of parent with margin=10:
        - A's left edge will be at parent.x + 10
        
        Component B constrained LEFT_TO_RIGHT of A with margin=5:
        - B's left edge will be at A.right + 5
    """
    # Determine target bounds (parent or another component)
    target_bounds = self._get_target_bounds(constraint)
    
    if constraint.constraint_type == ConstraintType.LEFT_TO_LEFT:
        # Align left edge to target's left edge + margin
        self.positions[comp_id]['x'] = target_bounds['x'] + constraint.margin
        
    elif constraint.constraint_type == ConstraintType.LEFT_TO_RIGHT:
        # Place left edge at target's right edge + margin
        self.positions[comp_id]['x'] = target_bounds['right'] + constraint.margin
    
    # ... (continue with inline comments for each case)
```

#### `ui/layout_strategies.py`

```python
class ConstraintLayoutStrategy(LayoutStrategy):
    """
    Android-style constraint-based layout strategy.
    
    Resolves component positions using a constraint resolution algorithm
    similar to Android's ConstraintLayout. Components define relationships
    to other components or to the parent container.
    
    Algorithm:
        1. Initialize all component positions to (0, 0)
        2. Iterate through components and apply constraints
        3. Handle centering and bias calculations
        4. Resolve any conflicts using priority rules
    
    Example:
        >>> strategy = ConstraintLayoutStrategy()
        >>> components = [comp1, comp2]  # with constraints defined
        >>> bounds = strategy.calculate_bounds(components, 800, 600)
        >>> print(bounds[id(comp1)])
        QRect(10, 10, 200, 50)
    
    See Also:
        FlowLayoutStrategy: Simpler top-to-bottom layout
        ConstraintResolver: Core constraint resolution logic
        Constraint: Individual constraint definition
    """
```

---

## Priority 6: Usage Examples (2 Weeks)

### Create EXAMPLES.md

```markdown
# Usage Examples

## Creating a Simple Template

```python
from ui.components import TextFieldComponent, DividerComponent
from ui.template_converter import TemplateConverter

# Create components
front = TextFieldComponent("Front")
front.font_size = 24
front.text_align = Alignment.CENTER

divider = DividerComponent()
divider.border_color = "#CCCCCC"

back = TextFieldComponent("Back")
back.font_size = 18

# Convert to HTML/CSS
components = [front, divider, back]
html = TemplateConverter.components_to_html(components)
css = TemplateConverter.components_to_css(components)

print(html)
# Output:
# <div class="component-0">{{Front}}</div>
# <hr class="component-1">
# <div class="component-2">{{Back}}</div>
```

## Using Constraints

```python
from ui.components import TextFieldComponent
from ui.constraints import Constraint, ConstraintType, ConstraintTarget

# Create two components
title = TextFieldComponent("Title")
title.id = 1

content = TextFieldComponent("Content")
content.id = 2

# Create constraints
constraints = [
    # Center title horizontally in parent
    Constraint(
        source_component_id=1,
        constraint_type=ConstraintType.CENTER_HORIZONTAL,
        target=ConstraintTarget.PARENT
    ),
    # Place title at top of parent
    Constraint(
        source_component_id=1,
        constraint_type=ConstraintType.TOP_TO_TOP,
        target=ConstraintTarget.PARENT,
        margin=20
    ),
    # Place content below title
    Constraint(
        source_component_id=2,
        constraint_type=ConstraintType.TOP_TO_BOTTOM,
        target=ConstraintTarget.COMPONENT,
        target_component_id=1,
        margin=10
    )
]

# Apply constraints
from ui.constraints import ConstraintSet, ConstraintResolver

constraint_set = ConstraintSet()
for c in constraints:
    constraint_set.add_constraint(c)

resolver = ConstraintResolver(800, 600)
positions = resolver.resolve([title, content], constraint_set)

print(positions[1])  # Title position
# {'x': 300, 'y': 20, 'width': 200, 'height': 30}
```

## Security Validation

```python
from utils.security import SecurityValidator
from utils.exceptions import TemplateSecurityError

# Valid HTML
html = '<div>{{Front}}</div>'
is_safe, warnings = SecurityValidator.validate_template_security(html)
print(is_safe)  # True

# Dangerous HTML
dangerous_html = '<div onclick="alert()">{{Front}}</div>'
try:
    sanitized = SecurityValidator.sanitize_html(dangerous_html)
    print(sanitized)
    # Output: '<div>{{Front}}</div>' (onclick removed)
except TemplateSecurityError as e:
    print(f"Security error: {e}")
```
```

---

## Automation Setup (1 Week)

### 1. Install Documentation Tools

```bash
pip install sphinx sphinx-rtd-theme pydocstyle interrogate
```

### 2. Configure Sphinx

```bash
cd docs
sphinx-quickstart
```

Edit `docs/conf.py`:
```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google-style docstrings
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
```

### 3. Add Pre-commit Hooks

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: [--convention=google, --add-ignore=D100,D104]
  
  - repo: https://github.com/econchick/interrogate
    rev: 1.5.0
    hooks:
      - id: interrogate
        args: [--fail-under=80, -vv, --ignore-init-module]
```

### 4. Add CI/CD Documentation Build

Add to `.github/workflows/docs.yml`:
```yaml
name: Documentation

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install sphinx sphinx-rtd-theme
          pip install -r requirements.txt
      - name: Build docs
        run: |
          cd docs
          make html
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

---

## Timeline

### Week 1-2: Critical Docstrings
- [ ] Add docstrings to `TemplateConverter` methods
- [ ] Add docstrings to `Component` class and subclasses
- [ ] Add docstrings to UI `setup_ui()` methods

### Week 3-4: Type Hints & Style
- [ ] Add type hints to `ui/` modules
- [ ] Add type hints to `utils/` modules
- [ ] Convert NumPy-style to Google-style docstrings

### Week 5-6: Examples & Comments
- [ ] Add inline comments to complex algorithms
- [ ] Create EXAMPLES.md
- [ ] Add usage examples to key classes

### Week 7-8: Automation & Architecture
- [ ] Set up Sphinx documentation generation
- [ ] Create ARCHITECTURE.md
- [ ] Add pre-commit hooks
- [ ] Set up CI/CD for docs

### Week 9-12: Polish & Review
- [ ] Review all documentation
- [ ] Run interrogate for coverage metrics
- [ ] Fix any remaining gaps
- [ ] Create CONTRIBUTING.md with doc standards

---

## Success Metrics

| Metric | Current | Target | Deadline |
|--------|---------|--------|----------|
| Public method docstrings | 70% | 95% | Week 4 |
| Type hint coverage | 65% | 90% | Week 4 |
| Docstring style consistency | 80% | 100% | Week 4 |
| Complex algorithm comments | 40% | 80% | Week 6 |
| Usage examples | 30% | 60% | Week 6 |
| Overall documentation score | 70% (B+) | 90% (A-) | Week 12 |

---

## Review Checklist

Before merging documentation changes, verify:

- [ ] All public methods have docstrings
- [ ] Docstrings follow Google style
- [ ] Type hints present for all public methods
- [ ] Complex algorithms have inline comments
- [ ] At least one example per major class
- [ ] No pydocstyle warnings
- [ ] Interrogate shows >80% coverage
- [ ] Sphinx builds without errors

---

## Maintenance

### Ongoing Documentation Requirements

1. **New Code:**
   - All new classes must have docstrings with examples
   - All new public methods must have full docstrings
   - All new modules must have module-level docstrings

2. **Code Changes:**
   - Update docstrings when method signatures change
   - Update examples when behavior changes
   - Update architecture docs for major refactors

3. **Review Process:**
   - PR review must check documentation quality
   - CI must pass pydocstyle checks
   - Documentation coverage must not decrease

4. **Quarterly:**
   - Review and update ARCHITECTURE.md
   - Review and update EXAMPLES.md
   - Audit documentation coverage metrics

---

**Next Action:** Start with Priority 1 - add docstrings to core conversion methods
