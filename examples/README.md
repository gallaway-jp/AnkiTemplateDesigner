# Example Templates

This directory contains example templates and usage demonstrations for the Anki Template Designer.

## examples.py

Demonstrates how to programmatically create Anki templates using the Template Designer API.

**Usage:**
```python
from examples import examples
```

## Examples Included

The examples demonstrate:

1. **Basic Component Usage** - Creating simple text and image components
2. **Layout Strategies** - Using different layout algorithms (constraint, flow, grid)
3. **Styling** - Applying CSS styles to components
4. **Complex Templates** - Building multi-component card templates
5. **AnkiDroid Compatibility** - Creating templates that work on both desktop and mobile

## Running Examples

```python
# Import the examples module
from examples import examples

# Access specific examples
basic_template = examples.create_basic_template()
complex_template = examples.create_complex_template()
```

## Creating Your Own Templates

For a complete guide on creating custom templates, see:
- [Visual Builder Guide](../docs/user/VISUAL_BUILDER_GUIDE.md)
- [Development Guide](../docs/developer/DEVELOPMENT.md)

## API Documentation

Key classes and methods:
- `Component` - Base component class
- `TemplateConverter` - Converts components to HTML/CSS
- `LayoutStrategy` - Layout algorithm classes

For detailed API documentation, run:
```bash
python -m pydoc ui.components
python -m pydoc ui.template_converter
python -m pydoc ui.layout_strategies
```
