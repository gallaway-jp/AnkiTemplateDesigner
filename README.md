# Anki Template Designer

A visual drag-and-drop template designer for [Anki](https://apps.ankiweb.net/) flashcards, powered by [GrapeJS](https://grapesjs.com/).

## Features

- **Visual Editor** – GrapeJS-based canvas with drag-and-drop components
- **Anki Components** – Dedicated blocks for `{{Field}}`, `{{cloze}}`, `{{hint:}}`, `{{type:}}`, conditionals, tags, and `{{FrontSide}}`
- **Front / Back Editing** – Toggle between card sides with independent state
- **Style Manager** – Typography, layout, spacing, background, and border controls
- **Layer Manager** – Tree view of the template DOM structure
- **Responsive Preview** – Desktop, tablet, and mobile device modes
- **Undo / Redo** – Full history via GrapeJS and Python backend
- **Export** – Get the generated HTML + CSS for use in Anki

## Project Structure

```
AnkiTemplateDesigner/
├── anki_template_designer/        # The Anki add-on package
│   ├── __init__.py                # Add-on entry point (hooks into Anki)
│   ├── config.json                # User-facing configuration
│   ├── manifest.json              # Anki add-on manifest
│   ├── meta.json                  # Anki add-on metadata
│   ├── core/                      # Data models & config schema
│   ├── gui/                       # Qt dialog & WebView bridge
│   │   ├── designer_dialog.py     # Main QDialog with QWebEngineView
│   │   └── webview_bridge.py      # QWebChannel Python↔JS bridge
│   ├── services/                  # Backend services
│   │   ├── template_service.py    # Template CRUD
│   │   ├── backup_manager.py      # Template backups
│   │   ├── undo_redo_manager.py   # History management
│   │   ├── config_service.py      # Configuration persistence
│   │   └── ...
│   ├── utils/                     # Logging, helpers
│   ├── web/                       # Frontend (loaded in QWebEngineView)
│   │   ├── index.html             # Main page – loads GrapeJS
│   │   ├── css/editor.css         # Theme & layout overrides
│   │   └── js/
│   │       ├── bridge.js          # QWebChannel bridge
│   │       ├── anki-components.js # Custom GrapeJS component types
│   │       ├── anki-blocks.js     # Draggable block definitions
│   │       └── editor.js          # Editor init & toolbar wiring
│   ├── templates/                 # Saved template files
│   └── tests/                     # Unit tests
├── pyproject.toml
├── requirements.txt
├── deploy_addon.ps1
├── LICENSE
└── README.md
```

## Development

### Prerequisites

- Python 3.9+
- Anki 2.1.50+ (for PyQt6 / QWebEngine)

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Running Tests

```bash
pytest anki_template_designer/tests/
```

### Deploying to Anki

```powershell
.\deploy_addon.ps1
```

This copies the `anki_template_designer/` package to your Anki add-ons directory.

## Technology

| Layer    | Technology                        |
|----------|-----------------------------------|
| Editor   | [GrapeJS](https://grapesjs.com/)  |
| Frontend | HTML / CSS / vanilla JS           |
| Bridge   | QWebChannel (Qt WebEngine)        |
| Backend  | Python / PyQt6                    |
| Host     | Anki 2.1 add-on system            |

## License

MIT
