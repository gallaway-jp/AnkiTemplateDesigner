# User Guide - Anki Template Designer v2.0.0

**Version**: 2.0.0 (Production Release)  
**Last Updated**: January 2026  
**Status**: Complete & Tested

---

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Creating Templates](#creating-templates)
4. [Editing Templates](#editing-templates)
5. [Using Blocks](#using-blocks)
6. [Preview & Testing](#preview--testing)
7. [Saving & Exporting](#saving--exporting)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Tips & Tricks](#tips--tricks)
10. [FAQ](#faq)
11. [Support](#support)

---

## 🚀 Getting Started

### Launch the Application

**From Anki**:
1. Open Anki
2. Go to Tools menu
3. Select "Anki Template Designer"
4. Window opens with editor ready

**Standalone** (Portable version):
- Double-click `AnkiTemplateDesigner.exe` (Windows)
- Double-click `AnkiTemplateDesigner.app` (macOS)
- Run `./AnkiTemplateDesigner` (Linux)

### First Time Setup

**Step 1: Select Anki Data**
- Application automatically detects your Anki installation
- If not found, select Anki folder manually
- Click "Connect"

**Step 2: Select Note Type**
- Choose note type from dropdown
- View available fields

**Step 3: Start Editing**
- Template editor opens with current template
- Make changes in editor
- Preview updates in real-time

---

## 🎨 Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────┐
│  Anki Template Designer v2.0.0                  │
├──────────────┬─────────────────┬────────────────┤
│   Models     │   Components    │   Properties   │
│   Dropdown   │     Palette     │     Panel      │
├──────────────┴──────┬──────────┴────────────────┤
│                                                  │
│      Template Editor (HTML/CSS)                 │
│      - Syntax highlighting                      │
│      - Real-time validation                     │
│      - Auto-complete                            │
│                                                  │
├──────────────────────────────────────────────────┤
│      Live Preview                              │
│      - Real-time rendering                      │
│      - Field interpolation                      │
│      - CSS styling applied                      │
├──────────────────────────────────────────────────┤
│ [Undo] [Redo] [Save] [Export] [Settings] [Help] │
└──────────────────────────────────────────────────┘
```

### Panel Description

**Models Panel** (Top Left)
- Dropdown to select note type
- Shows current model name
- Displays field list
- Edit model settings

**Components Palette** (Top Center)
- Reusable template components
- Drag to editor
- Double-click to insert
- Categories: Text, Cards, Formatting, Media

**Properties Panel** (Top Right)
- Component properties when selected
- Edit styles inline
- Remove components
- View component hierarchy

**Template Editor** (Main Area)
- HTML and CSS editing
- Syntax highlighting
- Real-time validation
- Handlebars support (`{{Front}}`, `{{Back}}`)

**Live Preview** (Bottom)
- Real-time rendering
- Sample field values
- CSS styling applied
- Responsive design preview

---

## ✏️ Creating Templates

### Create New Template from Scratch

**Step 1: Basic Structure**
```html
<div class="card">
  <div class="front">
    {{Front}}
  </div>
  <div class="back">
    {{Back}}
  </div>
</div>
```

**Step 2: Add Styling**
```css
.card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
}

.front {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.back {
  font-size: 18px;
  color: #333;
}
```

**Step 3: Preview**
- Preview updates in real-time
- See styled template with sample data
- Check responsiveness

**Step 4: Customize**
- Add more fields: `{{Extra}}`, `{{Image}}`
- Adjust colors and fonts
- Add media placeholders

### Using Template Components

**Text Component**
- Drag from palette
- Insert field reference: `{{FieldName}}`
- Format text: bold, italic, size

**Image Component**
- Drag from palette
- Insert image field: `<img src="{{Image}}" />`
- Set size and alignment

**Card Component**
- Pre-styled card container
- Responsive design
- Border and shadow styling

**Formatting Component**
- Headers, paragraphs, lists
- Pre-styled elements
- Consistent spacing

### Clone Existing Template

**Step 1: Select Template**
- Open Models dropdown
- Select note type
- View current template

**Step 2: Save As**
- Click "Save As..."
- Enter new name
- Click "Save"

**Step 3: Modify**
- Edit clone template
- Original remains unchanged
- Test changes in preview

---

## 🎯 Editing Templates

### Edit Field References

**Basic Syntax**:
```html
<!-- Show field content -->
{{Front}}

<!-- Conditional display -->
{{#Extra}}
  <div>{{Extra}}</div>
{{/Extra}}

<!-- Format with CSS class -->
<span class="answer">{{Back}}</span>
```

### Add Conditional Blocks

**Syntax**:
```html
<!-- If field has content -->
{{#ImageUrl}}
  <img src="{{ImageUrl}}" />
{{/ImageUrl}}

<!-- If field is empty -->
{{^Example}}
  <p>No example provided</p>
{{/Example}}
```

### Apply Custom Styles

**CSS Example**:
```css
/* Main container */
.card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
}

/* Question styling */
.question {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 30px;
  border-bottom: 2px solid rgba(255,255,255,0.3);
  padding-bottom: 20px;
}

/* Answer styling */
.answer {
  font-size: 20px;
  line-height: 1.6;
  opacity: 0.95;
}

/* Responsive */
@media (max-width: 600px) {
  .card {
    padding: 15px;
  }
  .question {
    font-size: 18px;
  }
}
```

### Validation

- **Real-time**: HTML/CSS validated as you type
- **Warnings**: Displayed in editor margin
- **Errors**: Shown in preview
- **Auto-fix**: Suggestions provided

---

## 🧩 Using Blocks

### What Are Blocks?

Blocks are pre-designed, reusable template components that combine HTML + CSS for common patterns.

### Available Blocks

**Text Blocks**:
- Heading (H1, H2, H3)
- Paragraph
- List (ordered, unordered)
- Quote

**Card Blocks**:
- Basic card
- Gradient card
- Outlined card
- Shadow card

**Layout Blocks**:
- Two-column
- Three-column
- Centered
- Responsive grid

**Content Blocks**:
- Image
- Video
- Audio
- File attachment

### Insert Blocks

**Drag & Drop**:
1. Find block in Components Palette
2. Drag to editor at desired position
3. Release to insert

**Double-Click**:
1. Find block in Components Palette
2. Double-click to insert at cursor
3. Block appears with default styling

**Search**:
1. Type block name in search box
2. Select from results
3. Click to insert

### Customize Blocks

**Edit Properties**:
1. Click block in editor
2. Properties panel appears on right
3. Modify: colors, sizes, text
4. Changes apply in real-time

**Override Styles**:
```css
/* Override default block styling */
.card-gradient {
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
}
```

**Remove Block**:
1. Click block
2. Press Delete key
3. Block removed, content preserved

---

## 👁️ Preview & Testing

### Live Preview

**Automatic Updates**:
- Preview updates as you type
- Shows styled result
- Displays sample field values
- Updates in real-time

**Sample Data**:
- Default sample values shown
- Edit samples in Preview panel
- Test with different field values
- See responsive behavior

### Responsive Testing

**Device Sizes**:
- Toggle responsive mode
- Test: Mobile, Tablet, Desktop
- View at different sizes
- Check text wrapping

**Dark Mode**:
- Enable dark mode toggle
- Test contrast and readability
- Check colors in dark theme
- Adjust if needed

### Field Interpolation

**Test Fields**:
1. Preview panel shows sample values
2. Click "Edit Samples"
3. Modify field values
4. See preview update instantly

**Special Characters**:
- Test with: accented characters, emoji
- Unicode: ñ, é, 中文, 🎉
- HTML entities: &lt;, &gt;, &amp;

---

## 💾 Saving & Exporting

### Save to Anki

**Click Save**:
1. Click "Save" button (or Ctrl+S)
2. Template saves to Anki immediately
3. Status: "Saved successfully"
4. Use in next study session

**Auto-save**:
- Disabled by default
- Enable in Settings
- Saves every 5 minutes
- Prevents data loss

### Export Template

**Export as HTML**:
1. Click "Export" button
2. Choose format: HTML, ZIP, JSON
3. Select save location
4. File downloads

**Export Options**:
- HTML only (template code)
- ZIP (with CSS and resources)
- JSON (portable format)
- Share with others

**Export Formats**:

**HTML**:
```html
<!-- Standalone HTML file -->
<!-- Includes all CSS -->
<!-- Ready to use as template -->
```

**ZIP**:
```
template.zip
├── index.html
├── styles.css
├── assets/
│   ├── images/
│   └── fonts/
└── manifest.json
```

**JSON**:
```json
{
  "name": "My Template",
  "version": "1.0",
  "fields": ["Front", "Back"],
  "template": "...",
  "styles": "..."
}
```

### Share Templates

**Share via Link**:
1. Export as ZIP
2. Upload to cloud storage (Dropbox, Google Drive)
3. Share link with others
4. Others import via "Import" button

**Share in Community**:
1. Export template
2. Create GitHub Gist
3. Post in Anki forums
4. Community can use template

---

## ⌨️ Keyboard Shortcuts

| Action | Windows | macOS | Linux |
|--------|---------|-------|-------|
| Save | Ctrl+S | Cmd+S | Ctrl+S |
| Undo | Ctrl+Z | Cmd+Z | Ctrl+Z |
| Redo | Ctrl+Y | Cmd+Shift+Z | Ctrl+Y |
| Find | Ctrl+F | Cmd+F | Ctrl+F |
| Replace | Ctrl+H | Cmd+H | Ctrl+H |
| Cut | Ctrl+X | Cmd+X | Ctrl+X |
| Copy | Ctrl+C | Cmd+C | Ctrl+C |
| Paste | Ctrl+V | Cmd+V | Ctrl+V |
| Select All | Ctrl+A | Cmd+A | Ctrl+A |
| Zoom In | Ctrl+Plus | Cmd+Plus | Ctrl+Plus |
| Zoom Out | Ctrl+Minus | Cmd+Minus | Ctrl+Minus |
| Full Screen | F11 | Cmd+Ctrl+F | F11 |
| Help | F1 | F1 | F1 |

---

## 💡 Tips & Tricks

### Performance Tips

1. **Reduce Preview Updates**
   - Disable real-time preview for large templates
   - Update preview on demand with F5
   - Improves editor responsiveness

2. **Optimize CSS**
   - Use classes over inline styles
   - Minimize selectors depth
   - Remove unused styles
   - Pre-load fonts

3. **Large Projects**
   - Break templates into components
   - Use external stylesheets
   - Test in preview, not live Anki

### Design Tips

1. **Typography**
   - Use system fonts (faster loading)
   - Limit to 2-3 font sizes
   - Maintain contrast ratio >4.5:1
   - Use line-height: 1.5-1.8

2. **Color Schemes**
   - Use 3-5 main colors
   - Test in light and dark modes
   - Use accessible colors
   - Check colorblind-safe palettes

3. **Responsive Design**
   - Mobile-first approach
   - Test at 320px, 768px, 1200px
   - Use flexible units (%, em, rem)
   - Avoid fixed widths

### Productivity Tips

1. **Use Components Palette**
   - Build from blocks, not scratch
   - Faster template creation
   - Consistent styling
   - Easy modifications

2. **Save Variations**
   - Keep multiple versions
   - Test before deploying
   - Easy rollback if needed
   - Compare versions

3. **Backup Templates**
   - Export regularly
   - Store in cloud
   - Version control in Git
   - Share with team

---

## ❓ FAQ

**Q: Can I use images in templates?**  
A: Yes! Use `<img src="{{ImageField}}" />` to display images from fields.

**Q: Are my templates synced to AnkiWeb?**  
A: Yes, templates are saved with your Anki data and sync with AnkiWeb.

**Q: Can I undo all changes?**  
A: Yes, use Ctrl+Z or the Undo button. History tracks 100 actions.

**Q: Can I export template for sharing?**  
A: Yes, click Export. Choose HTML, ZIP, or JSON format.

**Q: Can I use JavaScript in templates?**  
A: Limited. Basic JavaScript works, but advanced features are restricted for security.

**Q: How do I test before saving?**  
A: Use Live Preview. It shows real-time rendering with sample data.

**Q: Can I revert to original template?**  
A: Yes, open "Template Info" in Anki to view original, then restore.

**Q: What if my template breaks Anki?**  
A: Anki has built-in safeguards. Worst case, revert template in Anki settings.

**Q: Can I use CSS Grid/Flexbox?**  
A: Yes! Both are fully supported. Test responsiveness in preview.

**Q: How do I make dark mode compatible?**  
A: Use CSS variables. Anki automatically switches colors in dark mode.

---

## 📞 Support & Resources

**Documentation**: https://github.com/gallaway-jp/AnkiTemplateDesigner/wiki  
**Issues**: https://github.com/gallaway-jp/AnkiTemplateDesigner/issues  
**Discussions**: https://github.com/gallaway-jp/AnkiTemplateDesigner/discussions

**Video Tutorials**: Coming soon  
**Community Forum**: Anki forums (coming soon)

---

*User Guide v2.0.0 - January 2026*
