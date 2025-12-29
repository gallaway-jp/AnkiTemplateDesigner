# Quick Start Guide

## Installation

### Method 1: From Release Package
1. Download the latest `.ankiaddon` file from releases
2. Open Anki
3. Go to **Tools → Add-ons → Install from file**
4. Select the downloaded `.ankiaddon` file
5. Click **OK** to confirm
6. Restart Anki

### Method 2: From Source (Development)
1. Clone or download this repository
2. Copy the entire `AnkiTemplateDesigner` folder to your Anki add-ons directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **macOS**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`
3. Restart Anki

## First Launch

### Opening the Template Designer

#### Option 1: From Tools Menu
1. Open Anki
2. Click **Tools → Template Designer**
3. The designer will open with the first available note type

#### Option 2: From Card Layout Screen
1. Open Anki
2. Go to **Tools → Manage Note Types**
3. Select a note type
4. Click **Cards**
5. Look for the **Template Designer** button
6. Click it to open the designer for that specific note type

## Using the Template Designer

### Interface Overview

The Template Designer window is divided into two main sections:

**Left Panel - Editor:**
- Card selector dropdown (switch between cards)
- Add/Remove card buttons
- Three tabs:
  - **Front Template**: HTML for the question side
  - **Back Template**: HTML for the answer side
  - **Styling**: CSS for both sides

**Right Panel - Preview:**
- Platform selector: Desktop | AnkiDroid | Both
- Theme selector: Light | Dark (for AnkiDroid)
- Refresh button
- Split preview panes showing rendered output

**Bottom Bar:**
- Save to Anki button
- Close button
- Front/Back toggle buttons

### Basic Workflow

1. **Select a Card**
   - Use the card dropdown to choose which card template to edit
   - If you have multiple cards in your note type, switch between them

2. **Edit the Template**
   - Click on the **Front Template** tab
   - Enter or modify your HTML
   - Click on the **Back Template** tab
   - Enter or modify your HTML
   - Click on the **Styling** tab
   - Add or modify CSS

3. **Preview Changes**
   - The preview updates automatically as you type (if auto-refresh is enabled)
   - Toggle between platforms to see how it looks on Desktop vs AnkiDroid
   - Switch between Light and Dark themes for AnkiDroid
   - Click Front/Back buttons to preview question or answer side

4. **Save Your Work**
   - Click **Save to Anki** to apply changes to your note type
   - Confirm the save dialog
   - Your templates are now updated in Anki!

## Example: Creating a Simple Card

### Step 1: Create a Basic Front Template
```html
<div class="question">
    {{Front}}
</div>
```

### Step 2: Create a Basic Back Template
```html
<div class="answer">
    {{FrontSide}}
    <hr>
    {{Back}}
</div>
```

### Step 3: Add Styling
```css
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    background-color: white;
    color: black;
    padding: 20px;
}

.question {
    font-weight: bold;
    color: #0066cc;
}

.answer {
    margin-top: 20px;
}

hr {
    border: none;
    border-top: 2px solid #ccc;
    margin: 15px 0;
}
```

### Step 4: Preview and Save
1. Check the preview in both Desktop and AnkiDroid modes
2. Toggle between Light and Dark themes
3. Click **Save to Anki** when satisfied

## Template Syntax

### Field Placeholders
- `{{FieldName}}` - Inserts the content of a field
- Example: `{{Front}}`, `{{Back}}`, `{{Extra}}`

### Conditional Fields
- `{{#FieldName}}...{{/FieldName}}` - Show content only if field has data
- `{{^FieldName}}...{{/FieldName}}` - Show content only if field is empty

Example:
```html
{{#Image}}
    <img src="{{Image}}" alt="Card Image">
{{/Image}}

{{^Image}}
    <p>No image available</p>
{{/Image}}
```

### Special Fields
- `{{FrontSide}}` - On back template, shows the front content
- `{{Tags}}` - Shows all tags for the note
- `{{Type}}` - Shows the note type name
- `{{Deck}}` - Shows the deck name

## Tips and Tricks

### 1. Use Platform-Specific Styles
```css
/* Desktop only - using night mode class */
.night_mode .card {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

/* General mobile-friendly styles */
@media (max-width: 600px) {
    .card {
        font-size: 16px;
        padding: 10px;
    }
}
```

### 2. Preview with Real Data
- The designer uses sample data by default
- If you have existing notes of the selected type, it will use one for preview
- This gives you a realistic view of how your templates will look

### 3. Test Both Sides
- Always check both Front and Back previews
- Use the Front/Back toggle buttons in the bottom bar
- Ensure `{{FrontSide}}` displays correctly on the back

### 4. Compare Platforms
- Use the "Both" option in platform selector
- Check how your template looks on Desktop vs AnkiDroid
- Test both Light and Dark themes for AnkiDroid

### 5. Organize Multiple Cards
- Use descriptive names for your cards
- The card selector shows all cards in the note type
- You can add new cards or remove existing ones

## Configuration

Access configuration via **Tools → Add-ons → Anki Template Designer → Config**

Available settings:
- `preview_width`: Width of preview window (default: 800)
- `preview_height`: Height of preview window (default: 600)
- `default_platform`: Platform to show first (desktop/ankidroid)
- `ankidroid_theme`: Default theme (light/dark)
- `show_both_platforms`: Show split view by default (true/false)
- `auto_refresh`: Auto-refresh on changes (true/false)

## Troubleshooting

### Preview Not Updating
- Click the Refresh button manually
- Check if auto_refresh is enabled in config
- Ensure your template has valid HTML syntax

### Save Button Not Working
- Verify you have permission to modify note types
- Check for validation errors in your template
- Ensure Anki is not in the middle of a sync

### Templates Look Different in Actual Anki
- The preview is a simulation and may not be 100% accurate
- Test your templates with actual cards after saving
- Some JavaScript features may behave differently

### AnkiDroid Preview Doesn't Match Device
- The AnkiDroid renderer is a simulation
- Actual devices may render slightly differently
- Use it as a guide, not an exact replica

## Next Steps

- Explore the example templates in `examples.py`
- Read [DEVELOPMENT.md](DEVELOPMENT.md) for advanced customization
- Check [CHANGELOG.md](CHANGELOG.md) for latest features
- Review Anki's official template documentation

## Getting Help

- Check the documentation files in this repository
- Review existing issues on the project page
- Create a new issue with your question or problem
- Include template code and screenshots when reporting issues

Happy template designing! 🎨
