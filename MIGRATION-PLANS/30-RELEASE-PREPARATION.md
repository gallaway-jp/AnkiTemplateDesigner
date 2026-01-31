# Plan 30: Release Preparation

## Objective
Prepare the final release of the Anki Template Designer with all legacy code removed and documentation finalized.

---

## Prerequisites
- [ ] Plans 01-29 completed and tested
- [ ] All legacy code removed
- [ ] All documentation cleaned up
- [ ] All tests passing

---

## Step 30.1: Final Code Audit

### Task
Perform comprehensive final audit of the codebase.

### Security Audit Checklist

| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded credentials | [ ] | |
| Input validation on all user inputs | [ ] | |
| XSS prevention in WebView | [ ] | |
| Path traversal prevention | [ ] | |
| Safe JSON parsing | [ ] | |
| No eval/exec usage | [ ] | |
| Content-Security-Policy set | [ ] | |
| HTTPS for any external calls | [ ] | |

### Performance Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Lazy loading implemented | [ ] | |
| No memory leaks | [ ] | |
| Cache working correctly | [ ] | |
| Response times <100ms for 95% operations | [ ] | |
| Bundle size <200KB gzipped | [ ] | |

### Code Quality Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Type hints throughout | [ ] | |
| Docstrings on all public methods | [ ] | |
| No TODO comments remaining | [ ] | |
| No debug code remaining | [ ] | |
| Consistent code style | [ ] | |
| SOLID principles followed | [ ] | |

---

## Step 30.2: Update Version Numbers

### Task
Update version numbers across all files.

### Files to Update

**anki_template_designer/__init__.py**:
```python
__version__ = "2.0.0"
```

**anki_template_designer/manifest.json**:
```json
{
    "version": "2.0.0",
    "mod": [CURRENT_TIMESTAMP]
}
```

**anki_template_designer/meta.json**:
```json
{
    "mod": [CURRENT_TIMESTAMP]
}
```

**package.json** (if web assets have one):
```json
{
    "version": "2.0.0"
}
```

**README.md**:
- Update version badge
- Update changelog link
- Update feature list

---

## Step 30.3: Finalize Documentation

### Task
Ensure all documentation is complete and accurate.

### Required Documentation Files

| File | Status | Description |
|------|--------|-------------|
| README.md | [ ] | Main project README |
| CHANGELOG.md | [ ] | Version history |
| LICENSE | [ ] | License file |
| INSTALLATION.md | [ ] | Installation guide |
| USER-GUIDE.md | [ ] | User documentation |
| CONTRIBUTING.md | [ ] | Contribution guidelines |
| SECURITY.md | [ ] | Security policy |

### README.md Template

```markdown
# Anki Template Designer

Visual drag-and-drop template designer for Anki flashcards.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Anki](https://img.shields.io/badge/Anki-2.1.50%2B-green)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🎨 Visual drag-and-drop template editor
- 📱 Live preview for desktop and mobile
- 🔧 Component-based design system
- 💾 Template import/export
- 🔄 Undo/redo support
- ⚡ Performance optimized
- 🔒 Secure design

## Installation

1. Download the latest release
2. Open Anki
3. Go to Tools → Add-ons → Install from file
4. Select the downloaded .ankiaddon file
5. Restart Anki

## Usage

1. Open Tools → Template Designer
2. Create a new template or open existing
3. Drag components from sidebar to canvas
4. Edit properties in the right panel
5. Save and apply to note types

## Requirements

- Anki 2.1.50 or later
- Windows, macOS, or Linux

## Documentation

- [Installation Guide](INSTALLATION.md)
- [User Guide](USER-GUIDE.md)
- [Changelog](CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [Report Issues](https://github.com/yourusername/AnkiTemplateDesigner/issues)
- [Discussions](https://github.com/yourusername/AnkiTemplateDesigner/discussions)
```

### CHANGELOG.md Update

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-XX-XX

### Added
- Complete rewrite with new architecture
- Performance optimization engine
- Backup and recovery system
- Plugin architecture
- Analytics system
- Cloud storage support (optional)

### Changed
- Migrated to new codebase structure
- Improved UI/UX
- Better error handling
- Enhanced security

### Removed
- Legacy code
- Deprecated features
- Unused dependencies

### Fixed
- All known issues from 1.x
- Performance bottlenecks
- Memory leaks
```

---

## Step 30.4: Create Release Package

### Task
Build the release package for distribution.

### Build Steps

```powershell
# Create clean build directory
$buildDir = "build/anki_template_designer"
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $buildDir

# Copy addon files
Copy-Item -Recurse anki_template_designer/* $buildDir/

# Remove development files
Remove-Item -Recurse -Force "$buildDir/__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$buildDir/tests" -ErrorAction SilentlyContinue
Get-ChildItem -Recurse $buildDir -Filter "*.pyc" | Remove-Item
Get-ChildItem -Recurse $buildDir -Filter ".DS_Store" | Remove-Item

# Create .ankiaddon package
$version = "2.0.0"
$outputFile = "dist/anki_template_designer_v$version.ankiaddon"
New-Item -ItemType Directory -Force dist

# Package as zip with .ankiaddon extension
Compress-Archive -Path "$buildDir/*" -DestinationPath $outputFile -Force

Write-Host "Package created: $outputFile"
```

### Package Verification

```powershell
# Verify package contents
$tempDir = "verify_temp"
Expand-Archive -Path $outputFile -DestinationPath $tempDir -Force

# Check required files
$requiredFiles = @(
    "__init__.py",
    "manifest.json",
    "config.json",
    "meta.json",
    "web/index.html"
)

foreach ($file in $requiredFiles) {
    if (Test-Path "$tempDir/$file") {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file MISSING" -ForegroundColor Red
    }
}

Remove-Item -Recurse -Force $tempDir
```

---

## Step 30.5: Test Release Package

### Task
Test the release package in a clean Anki installation.

### Test Procedure

1. [ ] Install fresh Anki (or use clean profile)
2. [ ] Install .ankiaddon package via Tools → Add-ons → Install from file
3. [ ] Restart Anki
4. [ ] Verify addon appears in add-ons list
5. [ ] Open Template Designer
6. [ ] Test all major features:
   - [ ] Create new template
   - [ ] Add components
   - [ ] Edit properties
   - [ ] Save template
   - [ ] Load template
   - [ ] Export template
   - [ ] Undo/redo
   - [ ] Preview

### Compatibility Testing

| Platform | Anki Version | Status |
|----------|--------------|--------|
| Windows 10/11 | 2.1.50+ | [ ] |
| macOS 12+ | 2.1.50+ | [ ] |
| Linux (Ubuntu) | 2.1.50+ | [ ] |

---

## Step 30.6: Create GitHub Release

### Task
Create and publish the GitHub release.

### Release Checklist

1. [ ] Create release tag:
   ```bash
   git tag -a v2.0.0 -m "Release version 2.0.0"
   git push origin v2.0.0
   ```

2. [ ] Go to GitHub → Releases → Draft new release

3. [ ] Fill in release information:
   - **Tag**: v2.0.0
   - **Title**: Anki Template Designer v2.0.0
   - **Description**: (see template below)

4. [ ] Upload release assets:
   - anki_template_designer_v2.0.0.ankiaddon
   - Source code (auto-generated)

5. [ ] Publish release

### Release Description Template

```markdown
# Anki Template Designer v2.0.0

## What's New

🎉 Complete rewrite of the Anki Template Designer with improved architecture, performance, and features.

### Highlights

- **New UI**: Modern, responsive interface with three-panel layout
- **Performance**: Sub-100ms response times for 95% of operations
- **Security**: Enhanced security with input validation and CSP
- **Plugin System**: Extensible architecture for custom components
- **Backup System**: Automatic backups with recovery options

### Installation

1. Download `anki_template_designer_v2.0.0.ankiaddon`
2. Open Anki
3. Go to Tools → Add-ons → Install from file
4. Select the downloaded file
5. Restart Anki

### Requirements

- Anki 2.1.50 or later

### Documentation

See the [User Guide](USER-GUIDE.md) for detailed instructions.

### Known Issues

- None at this time

### Feedback

Please report any issues on the [Issues page](https://github.com/yourusername/AnkiTemplateDesigner/issues).
```

---

## Step 30.7: Post-Release Tasks

### Task
Complete post-release activities.

### Checklist

1. [ ] Announce on Anki forums
2. [ ] Update AnkiWeb addon page (if applicable)
3. [ ] Monitor issue tracker for bug reports
4. [ ] Respond to user feedback
5. [ ] Plan next version based on feedback

### Monitoring

Set up alerts for:
- New issues opened
- Support requests
- Error reports

---

## User Testing Checklist

### Final Verification

1. [ ] Fresh install works
2. [ ] Upgrade from previous version works (if applicable)
3. [ ] All documented features work
4. [ ] No error messages in Anki console
5. [ ] Performance targets met
6. [ ] User guide accurate

---

## Success Criteria

- [ ] Release package created successfully
- [ ] All tests pass
- [ ] Documentation complete
- [ ] GitHub release published
- [ ] Installation verified on all platforms

---

## Project Complete! 🎉

Congratulations on completing the migration to the new codebase!

### Summary of What Was Accomplished

1. ✅ New clean codebase based on test_addon_minimal
2. ✅ All features from ISSUE-54 through ISSUE-59 implemented
3. ✅ Comprehensive security review
4. ✅ Performance optimization
5. ✅ Full test coverage
6. ✅ Complete documentation
7. ✅ All legacy code removed
8. ✅ Release package published

### Maintenance Notes

For future development:
- Follow the established patterns in the codebase
- Add tests for any new features
- Update documentation as needed
- Maintain backward compatibility where possible
- Continue security reviews

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
