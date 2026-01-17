# Anki Template Designer

An Anki add-on for building and previewing card templates for both Anki Desktop and AnkiDroid with a powerful visual drag-and-drop builder.

## Features

- 🎨 **Visual Drag-and-Drop Builder** - Create templates without writing code
- 📝 Code Editor mode for advanced users
- 👁️ Live preview of templates
- 🖥️ Desktop template rendering simulation
- 📱 AnkiDroid template rendering simulation
- ⚡ Side-by-side comparison of both platforms
- 🔄 Auto-refresh on template changes
- 🎯 Component-based design with properties panel
- 📦 Pre-built components (text fields, images, dividers, headings)
- ✏️ Visual property editor (fonts, colors, spacing, alignment)
- 🔀 Import and edit existing templates
- 💾 Save directly to Anki
- ✨ **Phase 3 New Features:**
  - 📋 Template version history with one-click recovery
  - 💡 Context-sensitive inline tooltips on all controls
  - 🎯 Visual feedback for drag-and-drop operations
  - ⚙️ Fully customizable interface layout and toolbar

## Requirements

- Anki 2.1.45+
- AnkiJSApi add-on (for enhanced JavaScript support)

For detailed requirements, see [docs/user/REQUIREMENTS.md](docs/user/REQUIREMENTS.md).

## Installation

1. Download the add-on from AnkiWeb or clone this repository
2. Copy the folder to your Anki addons21 folder
3. Restart Anki

## Usage

For a complete guide, see the [Visual Builder Guide](docs/user/VISUAL_BUILDER_GUIDE.md) and [Quick Start](docs/user/QUICKSTART.md).

### Visual Builder Mode (Default)

1. Open a note type: Tools → Manage Note Types → Select a note type → Cards
2. Click "Template Designer" button
3. **Drag components** from the palette onto the canvas:
   - 📝 Text Field - Display note fields
   - 🖼️ Image Field - Display images
   - 📏 Divider - Add visual separators
   - 📌 Heading - Add formatted headings
   - 📦 Container - Group components
   - 🔀 Conditional - Show/hide based on field content
4. **Click on a component** to edit its properties in the right panel:
   - Change fonts, colors, sizes
   - Adjust spacing (margin/padding)
   - Set borders and backgrounds
   - Configure alignment
5. **Arrange components** by right-clicking:
   - Move up/down
   - Duplicate
   -├── editor_widget.py     # Code template editor widget
│   ├── visual_builder.py    # Visual drag-and-drop builder
│   ├── components.py        # Visual component classes
│   ├── properties_panel.py  # Component properties editor
│   └── template_converter.py # Convert between visual and code
6. View real-time previews for both Desktop and AnkiDroid
7. Switch to Code Editor mode if needed for advanced customization
8. Save your template back to Anki

### Code Editor Mode

1. Click "</> Code Editor" button at the top
2. Edit templates directly in HTML/CSS
3. Use tabs for Front Template, Back Template, and Styling
4. Switch back to Visual Builder to see the visual representation

## Project Structure

```
AnkiTemplateDesigner/
├── __init__.py              # Add-on entry point
├── manifest.json            # Add-on metadata
├── README.md                # This file
├── LICENSE                  # MIT license
├── pyproject.toml           # Project configuration
├── ui/                      # User interface components
├── renderers/               # Template rendering engines
├── services/                # Service layer
├── utils/                   # Utility modules
├── config/                  # Configuration and defaults
├── tests/                   # Test suite
├── scripts/                 # Build and development scripts
├── examples/                # Example templates
└── docs/                    # Documentation (see docs/README.md)
```

For detailed documentation structure, see [docs/README.md](docs/README.md).

## Development

For complete development setup and guidelines, see:
- [Development Guide](docs/developer/DEVELOPMENT.md)
- [Testing Guide](docs/developer/TESTING_GUIDE.md)
- [Phase 3 Feature Overview](docs/PHASE3-COMPLETION.md)
- [Phase 3 User Guide](docs/PHASE3-USER-GUIDE.md)

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python scripts/run_tests.py

# Build package
python scripts/build.py
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy .

# Linting
pylint ui/ utils/ renderers/

# Security scanning
bandit -r .
```

## Third-Party Software

This software uses the following open-source libraries:

### Runtime Dependencies
- **Anki** (AGPL v3) - Spaced repetition software platform
- **PyQt6** (GPL v3) - Qt bindings for Python GUI framework
- **PyQt6-WebEngine** (GPL v3) - Web rendering engine for PyQt6

### Development & Testing
- **pytest** (MIT) - Testing framework
- **pytest-qt** (MIT) - Qt testing support for pytest
- **pytest-cov** (MIT) - Code coverage plugin
- **coverage** (Apache 2.0) - Code coverage measurement
- **black** (MIT) - Code formatter
- **mypy** (MIT) - Static type checker
- **pylint** (GPL v2) - Code analyzer
- **bandit** (Apache 2.0) - Security issue scanner

For a complete list of dependencies and their licenses, see [docs/security/THIRD_PARTY_LICENSES.md](docs/security/THIRD_PARTY_LICENSES.md).

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### License Compatibility Note

This Anki add-on is released under the MIT License. However, it depends on:
- **Anki** (AGPL v3) - The host application
- **PyQt6** (GPL v3) - The GUI framework

When used as an Anki add-on (the intended deployment model), this is fully compatible with these licenses. The MIT license allows this software to be used with GPL/AGPL-licensed software.

For detailed license compliance information, see [docs/security/LICENSE_COMPLIANCE.md](docs/security/LICENSE_COMPLIANCE.md).

### Attribution

Copyright (c) 2025 Anki Template Designer Contributors

Special thanks to:
- Ankitects Pty Ltd for Anki
- Riverbank Computing Limited for PyQt6
- All open-source contributors

## Contributing

Contributions are welcome! Please see [docs/developer/DEVELOPMENT.md](docs/developer/DEVELOPMENT.md) for complete guidelines.

Quick checklist:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite: `python scripts/run_tests.py`
5. Submit a pull request

Please ensure:
- All tests pass
- Code is formatted with black
- Type hints are included
- Security scans pass
- New dependencies are compatible with MIT/GPL licenses

## Support

- Report bugs via GitHub Issues
- Security issues: See [docs/security/SECURITY.md](docs/security/SECURITY.md)
- License questions: See [docs/security/LICENSE_COMPLIANCE.md](docs/security/LICENSE_COMPLIANCE.md)
- Development setup: See [docs/developer/DEVELOPMENT.md](docs/developer/DEVELOPMENT.md)

## Documentation

Complete documentation is available in the [docs/](docs/) directory:
- 📚 [User Guide](docs/user/QUICKSTART.md)
- 💻 [Developer Guide](docs/developer/DEVELOPMENT.md)
- 🔒 [Security Policy](docs/security/SECURITY.md)
- 📊 [Analysis Reports](docs/analysis/)
- ✨ [Improvements](docs/improvements/)

See [docs/README.md](docs/README.md) for the complete documentation index.

## Changelog

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for project history and recent changes.

---

**Anki Template Designer** - Visual template builder for Anki flashcards  
Made with ❤️ for the Anki community
