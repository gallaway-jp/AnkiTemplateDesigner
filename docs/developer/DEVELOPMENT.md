# Development Notes

## Architecture

The add-on is structured into several key components:

### 1. UI Layer (`ui/`)
- **designer_dialog.py**: Main dialog that orchestrates the entire interface
- **editor_widget.py**: Template editor with tabs for front/back/styling
- **preview_widget.py**: Split preview showing Desktop and AnkiDroid rendering

### 2. Renderer Layer (`renderers/`)
- **base_renderer.py**: Abstract base class with shared template logic
- **desktop_renderer.py**: Simulates Anki Desktop card rendering
- **ankidroid_renderer.py**: Simulates AnkiDroid card rendering with theme support

### 3. Utilities (`utils/`)
- **template_utils.py**: Template validation and processing
- **style_utils.py**: CSS validation and manipulation

## Key Features

### Template Editing
- Multi-card support (add/remove cards)
- Separate editors for front, back, and styling
- Real-time preview updates

### Preview Rendering
- Side-by-side Desktop and AnkiDroid previews
- Theme support (light/dark) for AnkiDroid
- Platform-specific CSS injection
- Sample data for preview when no notes exist

### AnkiDroid Simulation
The AnkiDroid renderer attempts to simulate the mobile viewing experience:
- Mobile-optimized typography (Roboto font family)
- Touch-friendly sizing (min 48px touch targets)
- Responsive viewport meta tag
- Material Design inspired light/dark themes
- Platform-specific CSS variables

### Desktop Simulation
The Desktop renderer simulates the desktop Anki experience:
- Desktop typography (Arial)
- Night mode support
- Standard Anki Desktop card wrapper styles

## Integration with AnkiJSApi

The add-on assumes AnkiJSApi is installed and can leverage its JavaScript capabilities:
- Enhanced JavaScript execution in templates
- Additional APIs for card interaction
- Better cross-platform compatibility

## Future Enhancements

### Planned Features
1. **Syntax Highlighting**: Add code editor with HTML/CSS syntax highlighting
2. **Template Library**: Pre-built template gallery
3. **Export/Import**: Share templates with other users
4. **Live Device Preview**: Connect to actual AnkiDroid device
5. **Template Validation**: More comprehensive error checking
6. **Field Autocomplete**: Suggest available fields while typing
7. **CSS Preprocessor**: Support for SASS/LESS
8. **Responsive Preview**: Different screen sizes
9. **Accessibility Checker**: Ensure templates are accessible
10. **Version Control**: Track template changes over time

### Technical Improvements
1. **Better Template Parser**: More robust Mustache/Handlebars parsing
2. **Performance**: Optimize preview rendering
3. **Testing**: Add unit tests for renderers
4. **Documentation**: API documentation for custom renderers
5. **Plugin System**: Allow custom renderer plugins

## Development Workflow

### Testing the Add-on
1. Copy the entire folder to Anki's `addons21` directory
2. Restart Anki
3. Access via Tools → Template Designer

### Building for Distribution
```bash
python build.py
```

This creates a `.ankiaddon` file ready for distribution.

### File Structure
```
AnkiTemplateDesigner/
├── __init__.py              # Package entry point
├── template_designer.py     # Main add-on logic and menu setup
├── manifest.json            # Add-on metadata
├── config.json              # Default settings
├── config.md                # Settings documentation
├── ui/                      # User interface components
│   ├── __init__.py
│   ├── designer_dialog.py
│   ├── preview_widget.py
│   └── editor_widget.py
├── renderers/               # Template renderers
│   ├── __init__.py
│   ├── base_renderer.py
│   ├── desktop_renderer.py
│   └── ankidroid_renderer.py
└── utils/                   # Utility functions
    ├── __init__.py
    ├── template_utils.py
    └── style_utils.py
```

## Contributing

When contributing to this project:
1. Follow the existing code structure
2. Add docstrings to all functions
3. Update this documentation for significant changes
4. Test with both Desktop and AnkiDroid renderers
5. Ensure compatibility with Anki 2.1.45+
