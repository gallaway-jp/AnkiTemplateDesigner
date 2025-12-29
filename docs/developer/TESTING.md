# Testing Checklist for Anki Template Designer

## Pre-Installation Testing

### Environment Check
- [ ] Anki version 2.1.45 or higher installed
- [ ] Python 3.9+ available (bundled with Anki)
- [ ] No conflicting add-ons installed
- [ ] Sufficient disk space for add-on

## Installation Testing

### Fresh Installation
- [ ] Install from .ankiaddon file
- [ ] Add-on appears in add-ons list
- [ ] No error messages during installation
- [ ] Anki restarts successfully
- [ ] Menu item appears under Tools

### Development Installation
- [ ] Symlink created correctly
- [ ] Add-on loads without errors
- [ ] Changes reflect after Anki restart
- [ ] No import errors in console

## UI Testing

### Main Dialog
- [ ] Dialog opens from Tools menu
- [ ] Dialog opens from Card Layout screen
- [ ] Window resizes properly
- [ ] Splitter works (drag to resize)
- [ ] All buttons visible and clickable
- [ ] Close button works
- [ ] Dialog remembers size/position

### Editor Widget
- [ ] Card selector dropdown works
- [ ] Can switch between cards
- [ ] Front template tab displays
- [ ] Back template tab displays
- [ ] Styling tab displays
- [ ] Text editing works in all tabs
- [ ] Add card button works
- [ ] Remove card button works
- [ ] Can't remove last card
- [ ] Save template button works
- [ ] Revert changes button works

### Preview Widget
- [ ] Desktop preview displays
- [ ] AnkiDroid preview displays
- [ ] Platform selector works (Desktop/AnkiDroid/Both)
- [ ] Theme selector works (Light/Dark)
- [ ] Refresh button updates preview
- [ ] Split view shows both platforms
- [ ] Preview updates on text change (if auto-refresh enabled)
- [ ] Front/Back toggle works

## Renderer Testing

### Desktop Renderer
- [ ] Renders basic template
- [ ] Field substitution works
- [ ] {{FrontSide}} on back template works
- [ ] Conditional fields work ({{#Field}})
- [ ] Negative conditionals work ({{^Field}})
- [ ] CSS applies correctly
- [ ] Night mode CSS present
- [ ] Images display properly
- [ ] Lists render correctly
- [ ] Links are styled

### AnkiDroid Renderer
- [ ] Renders basic template
- [ ] Light theme applies
- [ ] Dark theme applies
- [ ] Mobile viewport meta tag present
- [ ] Touch-friendly sizing
- [ ] Material Design colors used
- [ ] Roboto font family applied
- [ ] Responsive styles work
- [ ] Images display properly
- [ ] Code blocks styled correctly

### Template Processing
- [ ] Simple field {{Field}} works
- [ ] Multiple fields work
- [ ] Special fields work ({{Tags}}, {{Type}})
- [ ] Nested conditionals work
- [ ] Empty field handled correctly
- [ ] Whitespace preserved in templates
- [ ] HTML entities handled
- [ ] Special characters work

## Functionality Testing

### Template Operations
- [ ] Load existing note type templates
- [ ] Edit front template
- [ ] Edit back template
- [ ] Edit CSS styling
- [ ] Preview changes in real-time
- [ ] Save changes to Anki
- [ ] Save confirmation dialog appears
- [ ] Templates persist after save
- [ ] Can revert unsaved changes

### Multi-Card Support
- [ ] Load note type with multiple cards
- [ ] Switch between cards
- [ ] Edit different cards independently
- [ ] Add new card to note type
- [ ] Remove card from note type
- [ ] Card names display correctly
- [ ] Each card has own templates

### Data Handling
- [ ] Uses actual note data when available
- [ ] Falls back to sample data
- [ ] Sample data displays correctly
- [ ] Field names extracted correctly
- [ ] Missing fields handled gracefully

## Validation Testing

### Template Validation
- [ ] Valid templates pass validation
- [ ] Invalid syntax detected
- [ ] Unclosed conditionals detected
- [ ] Mismatched tags detected
- [ ] Empty field references detected
- [ ] Error messages are clear
- [ ] Validation runs on save

### CSS Validation
- [ ] Valid CSS passes
- [ ] Unclosed braces detected
- [ ] Syntax errors reported
- [ ] Comments handled
- [ ] Minification works
- [ ] Color extraction works

## Configuration Testing

### Settings
- [ ] Config file loads
- [ ] Default values work
- [ ] preview_width setting applies
- [ ] preview_height setting applies
- [ ] default_platform setting applies
- [ ] ankidroid_theme setting applies
- [ ] show_both_platforms setting applies
- [ ] auto_refresh setting applies
- [ ] Config changes persist
- [ ] Invalid config handled gracefully

### User Preferences
- [ ] Window size remembered
- [ ] Last platform remembered
- [ ] Theme preference saved
- [ ] Auto-refresh preference saved

## Integration Testing

### Anki Integration
- [ ] Accesses Anki collection
- [ ] Reads note types correctly
- [ ] Writes note types correctly
- [ ] Works with different note types
- [ ] Handles empty note types
- [ ] Works with cloze deletions
- [ ] Compatible with other add-ons
- [ ] No conflicts with AnkiWeb sync

### AnkiJSApi Integration
- [ ] Works when AnkiJSApi installed
- [ ] Works when AnkiJSApi not installed
- [ ] JavaScript API accessible
- [ ] Enhanced features available

## Cross-Platform Testing

### Windows
- [ ] Installs correctly
- [ ] UI renders properly
- [ ] File paths work
- [ ] Keyboard shortcuts work
- [ ] No platform-specific errors

### macOS
- [ ] Installs correctly
- [ ] UI follows macOS conventions
- [ ] File paths work
- [ ] Retina display support
- [ ] No platform-specific errors

### Linux
- [ ] Installs correctly
- [ ] UI renders properly
- [ ] File paths work
- [ ] Different DEs supported
- [ ] No platform-specific errors

## Performance Testing

### Loading
- [ ] Dialog opens quickly (<1s)
- [ ] Templates load quickly
- [ ] Large templates handled
- [ ] Multiple cards load efficiently

### Preview Rendering
- [ ] Preview updates smoothly
- [ ] No lag with typing
- [ ] Large CSS files handled
- [ ] Complex templates render
- [ ] Both previews update efficiently

### Memory Usage
- [ ] No memory leaks
- [ ] Multiple opens/closes stable
- [ ] Large note types handled
- [ ] Preview cleanup on close

## Error Handling

### Graceful Failures
- [ ] Missing note type handled
- [ ] Invalid template syntax handled
- [ ] CSS errors non-blocking
- [ ] File permission errors caught
- [ ] Network errors handled (if any)
- [ ] User-friendly error messages
- [ ] Errors logged appropriately

### Edge Cases
- [ ] Empty templates handled
- [ ] Templates with only whitespace
- [ ] Very long templates
- [ ] Special characters in field names
- [ ] Unicode handling
- [ ] Templates with scripts
- [ ] Malformed HTML/CSS

## Compatibility Testing

### Anki Versions
- [ ] Works on Anki 2.1.45
- [ ] Works on Anki 2.1.50+
- [ ] Works on latest Anki version
- [ ] Min version check enforced

### Note Types
- [ ] Basic note type
- [ ] Basic (and reversed)
- [ ] Cloze note type
- [ ] Custom note types
- [ ] Note types with many fields
- [ ] Note types with special chars

## Documentation Testing

### README
- [ ] Installation instructions clear
- [ ] Features listed accurately
- [ ] Usage examples work
- [ ] Links functional
- [ ] Screenshots current (if any)

### QUICKSTART
- [ ] Steps easy to follow
- [ ] Examples work
- [ ] Code snippets correct
- [ ] Tips helpful

### Code Documentation
- [ ] Docstrings present
- [ ] Function signatures clear
- [ ] Comments helpful
- [ ] Type hints (if any)

## Build Testing

### Package Creation
- [ ] build.py runs without errors
- [ ] .ankiaddon file created
- [ ] Correct files included
- [ ] No unwanted files included
- [ ] Package size reasonable
- [ ] Version number correct

### Installation from Package
- [ ] Package installs in Anki
- [ ] All files extracted
- [ ] Permissions correct
- [ ] No installation errors

## Security Testing

### Input Validation
- [ ] Template input sanitized
- [ ] CSS input validated
- [ ] No script injection possible
- [ ] File paths validated

### Data Safety
- [ ] No data loss on error
- [ ] Backups recommended (docs)
- [ ] Save operation atomic
- [ ] No corruption of collection

## Accessibility Testing

### UI Accessibility
- [ ] Keyboard navigation works
- [ ] Tab order logical
- [ ] Focus indicators visible
- [ ] Labels present
- [ ] Tooltips helpful
- [ ] High contrast support

## Regression Testing

### After Changes
- [ ] Previous features still work
- [ ] No new errors introduced
- [ ] Performance not degraded
- [ ] Config compatibility maintained
- [ ] Data format compatible

## User Acceptance Testing

### Workflow Testing
- [ ] Create new template workflow smooth
- [ ] Edit existing template intuitive
- [ ] Preview useful
- [ ] Save process clear
- [ ] Overall UX positive

### Real-World Scenarios
- [ ] Language learning cards
- [ ] Medical terminology cards
- [ ] Math/Science cards with formulas
- [ ] Image-heavy cards
- [ ] Audio cards (if supported)

## Final Checklist

- [ ] All critical features work
- [ ] No blocking bugs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Build process works
- [ ] Ready for release

---

## Testing Notes

### High Priority
- Core template editing and saving
- Preview rendering accuracy
- No data loss or corruption
- Anki integration stability

### Medium Priority
- UI polish and responsiveness
- Configuration options
- Validation accuracy
- Error messages clarity

### Low Priority
- Performance optimization
- Edge case handling
- Cosmetic issues
- Nice-to-have features

## Bug Reporting Template

When reporting bugs, include:
1. Anki version
2. Operating system
3. Add-on version
4. Steps to reproduce
5. Expected behavior
6. Actual behavior
7. Error messages (if any)
8. Screenshots (if applicable)

---

**Version**: 0.1.0  
**Last Updated**: 2025-12-28
