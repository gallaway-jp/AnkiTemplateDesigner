# Changelog

All notable changes to the Anki Template Designer add-on will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Keyboard shortcuts for visual builder
- Template library/gallery with pre-built templates
- Export/import templates feature
- Live device preview for actual AnkiDroid devices
- Field autocomplete in code editor
- Undo/redo functionality in visual builder
- Template history/version control
- Custom renderer plugin system
- Nested container support in visual builder
- Multi-column layouts

## [0.2.0] - 2025-12-28

### Added - Visual Template Builder 🎨

#### Major Features
- **Visual Drag-and-Drop Builder** - Create templates without writing code
- **Component Palette** - Library of pre-built components
- **Properties Panel** - Visual editor for component properties
- **Template Converter** - Convert between visual components and HTML/CSS
- **Dual Mode Support** - Switch between Visual and Code modes

#### Component Types
- 📝 **Text Field Component** - Display note fields with full styling control
- 🖼️ **Image Field Component** - Display images with sizing options
- 📏 **Divider Component** - Horizontal separators
- 📌 **Heading Component** - Formatted headings (h1-h6)
- 📦 **Container Component** - Group and organize components
- 🔀 **Conditional Component** - Show/hide based on field content

#### Visual Properties Editor
- Font selection (family, size, weight, style)
- Color pickers for text and background
- Spacing controls (margin and padding with TRBL inputs)
- Border and border radius controls
- Text alignment options (left, center, right, justify)
- Width and height settings
- Background color with transparency support

#### User Experience
- Drag components from palette onto canvas
- Click to select and edit component properties
- Right-click context menu (delete, duplicate, move up/down)
- Visual feedback for selected components
- Empty state guidance
- Real-time preview updates from visual changes
- Import existing templates and edit visually

#### Documentation
- VISUAL_BUILDER_GUIDE.md - Comprehensive visual builder guide
- Updated README with visual builder instructions
- Updated QUICKSTART with visual workflow

### Changed
- Dialog layout now includes mode selector at top
- Editor area now uses tabs for Visual Builder and Code Editor
- Default mode is now Visual Builder
- Increased default window size to 1400x800
- Preview panel now updates from both visual and code changes

### Technical
- New component system with base class and specialized components
- Properties panel with form-based editing
- Template converter for bidirectional HTML/CSS conversion
- Component-to-HTML rendering engine
- Component-to-CSS generation
- HTML-to-components parser for importing existing templates
- Canvas widget with drag-and-drop support

## [0.1.0] - 2025-12-28

### Added
- Initial release of Anki Template Designer
- Main template designer dialog with split view
- Template editor widget with tabs for Front, Back, and Styling
- Preview widget with platform selector (Desktop/AnkiDroid/Both)
- Desktop template renderer simulating Anki Desktop card rendering
- AnkiDroid template renderer with light/dark theme support
- Base renderer with template processing logic
- Template utilities for validation and field extraction
- Style utilities for CSS processing
- Configuration system with customizable settings
- Multi-card support (add/remove cards)
- Real-time preview updates
- Sample data generation for preview
- Integration with Anki's card layout screen
- Menu item in Tools menu
- Comprehensive documentation (README, DEVELOPMENT, REQUIREMENTS)
- Example templates for testing
- Build script for creating .ankiaddon packages
- MIT License

### Features
- ✅ Side-by-side Desktop and AnkiDroid preview
- ✅ Theme support (light/dark) for AnkiDroid
- ✅ Platform-specific CSS rendering
- ✅ Template validation
- ✅ Field extraction from templates
- ✅ Conditional field support ({{#Field}} and {{^Field}})
- ✅ FrontSide support for back templates
- ✅ CSS minification and optimization
- ✅ Save templates back to Anki
- ✅ Auto-refresh on template changes
- ✅ Configurable preview dimensions

### Technical Details
- Minimum Anki version: 2.1.45
- Compatible with PyQt5 and PyQt6
- Modular architecture with separation of concerns
- Object-oriented design with base classes
- Comprehensive error handling
- Configuration persistence

### Known Limitations
- No syntax highlighting in editor
- Basic template validation (more comprehensive validation planned)
- No live device preview
- Preview uses sample data when no notes exist
- Limited AnkiDroid simulation (visual only, not functional)

## Development Notes

### Version 0.1.0 Development
This initial version establishes the foundation for the add-on with:
1. Core architecture (UI, Renderers, Utilities)
2. Basic template editing and preview
3. Platform-specific rendering simulation
4. Integration with Anki's note type system

### Design Decisions
- **Modular Architecture**: Separated concerns into UI, renderers, and utilities
- **Base Renderer Pattern**: Abstract base class allows easy addition of new renderers
- **Configuration System**: JSON-based configuration for user customization
- **Qt-based UI**: Leverages Anki's Qt framework for consistency
- **Platform Simulation**: CSS-based rendering rather than actual platform execution

### Future Direction
The add-on is designed to be extensible, with planned features including:
- Plugin system for custom renderers
- Template sharing/marketplace
- Advanced editing features
- Better AnkiDroid integration
- Performance optimizations

---

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for contribution guidelines.

## Support

For issues, feature requests, or questions:
1. Check existing issues on the project repository
2. Review documentation in README.md and DEVELOPMENT.md
3. Create a new issue with detailed information

## Acknowledgments

- Anki and AnkiDroid development teams
- AnkiJSApi add-on for inspiration
- Community contributors and testers
