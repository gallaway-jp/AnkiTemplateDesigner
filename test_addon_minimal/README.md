# Minimal UI Test Addon

A bare-bones Anki addon for testing basic UI functionality.

## Features

- Simple dialog window with basic Qt widgets
- Text input field
- Submit button
- Message box feedback

## Installation

1. Copy this folder to your Anki add-ons directory
2. Restart Anki
3. Go to Tools menu → "Open UI Test"

## What It Tests

- Basic QDialog creation and display
- QVBoxLayout and widget arrangement
- QLineEdit input field
- QPushButton with signal connection
- QMessageBox dialogs
- Menu integration via gui_hooks

## Directory Structure

```
test_addon_minimal/
├── __init__.py        # Main addon code
├── manifest.json      # Addon metadata
└── README.md          # This file
```

## Troubleshooting

- If the menu item doesn't appear, check the Anki console for errors
- Verify Python version compatibility with your Anki installation
- Check that manifest.json is properly formatted
