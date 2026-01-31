# Plan 01: Foundation & Project Structure

## Objective
Establish the new clean addon structure based on `test_addon_minimal` pattern.

---

## Pre-Implementation Checklist

- [ ] Backup current project (git commit)
- [ ] Read this plan completely
- [ ] Understand the target structure

---

## Step 1.1: Create New Addon Directory Structure

### Task
Create the new clean addon folder structure that will eventually replace all legacy code.

### Implementation

Create the following directory structure:

```
anki_template_designer/
├── __init__.py           # Main addon entry point
├── manifest.json         # Addon metadata
├── config.json           # Default configuration
├── meta.json             # Anki addon metadata
├── core/
│   └── __init__.py
├── gui/
│   └── __init__.py
├── services/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── web/
│   └── index.html        # Main UI (from test_addon_minimal)
└── tests/
    └── __init__.py
```

### Quality Checks

#### Security
- [ ] Directory structure doesn't expose sensitive paths
- [ ] No hardcoded credentials in initial files

#### Performance
- [ ] Minimal initial imports (lazy loading strategy)

#### Best Practices
- [ ] Follow Python package conventions
- [ ] Use `__init__.py` for proper module structure

#### Maintainability
- [ ] Clear, logical folder organization
- [ ] Each folder has single responsibility

#### Documentation
- [ ] Add module docstrings to all `__init__.py` files

#### Testing
- [ ] Structure supports test discovery
- [ ] Tests folder mirrors source structure

#### Accessibility
- [ ] N/A for this step

#### Scalability
- [ ] Structure can accommodate future modules

#### Compatibility
- [ ] Works with Python 3.9+ (Anki requirement)
- [ ] Cross-platform paths

#### Error Handling
- [ ] N/A for this step

#### Complexity
- [ ] Simple, flat where possible

#### Architecture
- [ ] Clean separation of concerns
- [ ] Follows layered architecture pattern

#### License
- [ ] N/A for this step

#### Specification
- [ ] Aligns with addon requirements

---

## Step 1.2: Create Initial `__init__.py` Files

### Task
Create minimal `__init__.py` files for each package.

### Implementation

**anki_template_designer/__init__.py**
```python
"""
Anki Template Designer Add-on

A visual template designer for creating Anki flashcard templates.
Uses GrapeJS for drag-and-drop template building.

Author: [Your Name]
License: MIT
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "[Your Name]"

# Lazy imports - only load when needed
__all__ = []
```

**anki_template_designer/core/__init__.py**
```python
"""
Core module for template processing and data models.

Contains:
- Template parser
- Template generator
- Data models
"""
```

**anki_template_designer/gui/__init__.py**
```python
"""
GUI module for Qt-based user interface components.

Contains:
- Main designer dialog
- WebView integration
- Qt widgets
"""
```

**anki_template_designer/services/__init__.py**
```python
"""
Services module for business logic and external integrations.

Contains:
- Template service
- Backup service
- Analytics service
"""
```

**anki_template_designer/utils/__init__.py**
```python
"""
Utilities module for shared helper functions.

Contains:
- Logging utilities
- Configuration helpers
- Common utilities
"""
```

**anki_template_designer/tests/__init__.py**
```python
"""
Test suite for Anki Template Designer.
"""
```

### Quality Checks

#### Security
- [ ] No sensitive imports or data exposure

#### Performance
- [ ] Uses lazy loading pattern
- [ ] No heavy imports at module level

#### Best Practices
- [ ] Proper docstrings
- [ ] `__all__` defined where needed

#### Maintainability
- [ ] Clear module descriptions
- [ ] Consistent style

#### Documentation
- [ ] Module-level docstrings present
- [ ] Author and version info in main module

#### Testing
- [ ] Test package properly initialized

#### Accessibility
- [ ] N/A

#### Scalability
- [ ] Can add new submodules easily

#### Compatibility
- [ ] Python 3.9+ compatible syntax

#### Error Handling
- [ ] N/A for this step

#### Complexity
- [ ] Minimal, focused files

#### Architecture
- [ ] Clean module boundaries

#### License
- [ ] License specified in main module

#### Specification
- [ ] Matches addon structure requirements

---

## Step 1.3: Create manifest.json

### Task
Create the Anki addon manifest file.

### Implementation

**anki_template_designer/manifest.json**
```json
{
    "name": "Anki Template Designer",
    "package": "anki_template_designer",
    "version": "2.0.0",
    "author": "[Your Name]",
    "homepage": "https://github.com/yourusername/AnkiTemplateDesigner",
    "conflicts": [],
    "min_point_version": 50,
    "mod": 1706745600
}
```

### Quality Checks

#### Security
- [ ] No sensitive data in manifest

#### Performance
- [ ] N/A

#### Best Practices
- [ ] Valid JSON format
- [ ] All required fields present

#### Maintainability
- [ ] Version follows semver

#### Documentation
- [ ] Homepage URL provided

#### Testing
- [ ] JSON validates correctly

#### Accessibility
- [ ] N/A

#### Scalability
- [ ] N/A

#### Compatibility
- [ ] min_point_version set appropriately for Anki 2.1.50+

#### Error Handling
- [ ] N/A

#### Complexity
- [ ] Simple, flat structure

#### Architecture
- [ ] Follows Anki addon manifest spec

#### License
- [ ] N/A (license in separate file)

#### Specification
- [ ] Matches Anki addon requirements

---

## Step 1.4: Create config.json

### Task
Create the default configuration file.

### Implementation

**anki_template_designer/config.json**
```json
{
    "debugLogging": false,
    "logLevel": "INFO",
    "autoSave": true,
    "autoSaveIntervalSeconds": 30,
    "theme": "system",
    "windowSize": {
        "width": 1200,
        "height": 800
    },
    "recentTemplates": [],
    "maxRecentTemplates": 10
}
```

### Quality Checks

#### Security
- [ ] No sensitive defaults
- [ ] Logging level appropriate for production

#### Performance
- [ ] Reasonable auto-save interval
- [ ] Window size within normal bounds

#### Best Practices
- [ ] Sensible defaults
- [ ] Clear option names

#### Maintainability
- [ ] Easy to understand options
- [ ] Grouped logically

#### Documentation
- [ ] Options are self-documenting

#### Testing
- [ ] JSON validates correctly

#### Accessibility
- [ ] Theme option supports system preference

#### Scalability
- [ ] Can add more options

#### Compatibility
- [ ] Works across platforms

#### Error Handling
- [ ] Fallback values are safe

#### Complexity
- [ ] Simple structure

#### Architecture
- [ ] Configuration separate from code

#### License
- [ ] N/A

#### Specification
- [ ] Matches expected configuration options

---

## Step 1.5: Create meta.json

### Task
Create the Anki meta.json file.

### Implementation

**anki_template_designer/meta.json**
```json
{
    "name": "Anki Template Designer",
    "mod": 1706745600,
    "min_point_version": 50,
    "max_point_version": 999,
    "branch_index": 0,
    "disabled": false
}
```

### Quality Checks

#### Security
- [ ] No sensitive data

#### Performance
- [ ] N/A

#### Best Practices
- [ ] All required fields

#### Maintainability
- [ ] Version constraints appropriate

#### Documentation
- [ ] N/A

#### Testing
- [ ] JSON validates

#### Accessibility
- [ ] N/A

#### Scalability
- [ ] N/A

#### Compatibility
- [ ] max_point_version allows future Anki versions

#### Error Handling
- [ ] N/A

#### Complexity
- [ ] Minimal

#### Architecture
- [ ] Follows Anki spec

#### License
- [ ] N/A

#### Specification
- [ ] Matches Anki requirements

---

## User Testing Checklist

After completing all steps:

### Automated Tests
```bash
# From project root
python -m pytest anki_template_designer/tests/ -v
```

### Manual Verification

1. [ ] All directories created correctly
2. [ ] All `__init__.py` files have proper docstrings
3. [ ] `manifest.json` is valid JSON
4. [ ] `config.json` is valid JSON
5. [ ] `meta.json` is valid JSON
6. [ ] No Python syntax errors in any file

### Structure Verification
```bash
# Verify structure (PowerShell)
Get-ChildItem -Recurse anki_template_designer | Where-Object { $_.Extension -eq ".py" -or $_.Extension -eq ".json" }
```

---

## Success Criteria

- [ ] All 5 steps completed
- [ ] All quality checks pass
- [ ] All user tests pass
- [ ] No errors when importing main package

---

## Next Step

After successful completion, proceed to [02-CORE-ADDON-ENTRY.md](02-CORE-ADDON-ENTRY.md).

---

## Notes/Issues

_Document any issues encountered during implementation here:_

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
