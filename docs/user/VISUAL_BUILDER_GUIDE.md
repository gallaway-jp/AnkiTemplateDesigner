# Visual Builder Guide

## Overview

The Visual Builder is a drag-and-drop interface that lets you create Anki card templates without writing any HTML or CSS code. This guide will help you get started.

## Interface Layout

The Visual Builder is divided into three main sections:

```
┌─────────────────────────────────────────────────────────────┐
│  🎨 Visual Builder    </> Code Editor                       │
├───────────┬─────────────────────────┬────────────────────────┤
│           │                         │                        │
│ Component │      Canvas             │   Properties Panel     │
│ Palette   │                         │                        │
│           │  Drag components here   │   • Field Name         │
│ 📝 Text   │                         │   • Layout             │
│ 🖼️ Image  │  ┌──────────────────┐  │   • Spacing           │
│ 📏 Divider│  │  Component 1     │  │   • Text              │
│ 📌 Heading│  └──────────────────┘  │   • Background        │
│ 📦 Box    │                         │   • Border            │
│ 🔀 If/Then│  ┌──────────────────┐  │                        │
│           │  │  Component 2     │  │                        │
│           │  └──────────────────┘  │                        │
│           │                         │                        │
└───────────┴─────────────────────────┴────────────────────────┘
```

## Getting Started

### Step 1: Open Visual Builder

1. In Anki, go to **Tools → Template Designer**
2. The Visual Builder opens by default
3. You'll see three panels: Palette, Canvas, and Properties

### Step 2: Add Your First Component

1. **Drag** a component from the left palette onto the canvas
2. For example, drag "📝 Text Field" to the canvas
3. The component appears on the canvas
4. It's automatically selected (highlighted in blue)

### Step 3: Configure the Component

1. With the component selected, look at the **Properties Panel** on the right
2. Change the **Field Name** to match your note field (e.g., "Front", "Back", "Question")
3. Adjust visual properties:
   - **Font**: Choose font family and size
   - **Colors**: Text and background colors
   - **Spacing**: Margin (outside) and padding (inside)
   - **Alignment**: Left, center, right, justify

### Step 4: Add More Components

Build your template by adding more components:

1. **Text Field** - For displaying note content
2. **Image Field** - For showing images
3. **Divider** - For visual separation (horizontal line)
4. **Heading** - For titles and headers
5. **Container** - For grouping components together
6. **Conditional** - For showing content only when a field has data

### Step 5: Arrange Components

Right-click on any component to:
- **Move Up** - Move component earlier in the template
- **Move Down** - Move component later in the template
- **Duplicate** - Create a copy of the component
- **Delete** - Remove the component

### Step 6: Preview Your Template

The right side shows live previews:
- **Platform Selector**: Choose Desktop, AnkiDroid, or Both
- **Theme Selector**: Light or Dark theme (for AnkiDroid)
- **Front/Back Toggle**: Switch between question and answer sides

### Step 7: Save Your Work

1. Click **Save to Anki** at the bottom
2. Confirm the save dialog
3. Your template is now saved to your note type!

## Component Types Explained

### 📝 Text Field

Displays content from a note field.

**Properties:**
- Field Name: Which note field to display (e.g., "Front", "Back")
- Show Label: Display a label above the field
- All standard text/layout properties

**Example Use:** Main question or answer text

### 🖼️ Image Field

Displays an image from a note field.

**Properties:**
- Field Name: Which field contains the image
- Max Width/Height: Limit image size
- Object Fit: How image scales (contain, cover, etc.)

**Example Use:** Picture for vocabulary cards, diagrams

### 📏 Divider

A horizontal line to separate sections.

**Properties:**
- Height: Thickness of the line
- Color: Line color (via background color)
- Margin: Space above and below

**Example Use:** Separator between question and answer

### 📌 Heading

A formatted heading for emphasis.

**Properties:**
- Level: h1, h2, h3, etc. (determines default size)
- Field Name: What text to display
- All text formatting options

**Example Use:** Card title, category labels

### 📦 Container

A box for grouping other components.

**Properties:**
- Layout direction: Vertical or horizontal
- Background: Container color
- All spacing and border options

**Example Use:** Grouping related information, creating colored boxes

### 🔀 Conditional

Shows content only if a field has data (or is empty).

**Properties:**
- Field Name: Which field to check
- Invert: Show when field is empty instead
- Children: Components to show/hide

**Example Use:** Optional hints, extra information

## Tips and Tricks

### Creating Consistent Spacing

Use margins to create breathing room:
- Top/Bottom margins: 10-20px between components
- Left/Right margins: 0px (usually)

### Color Coding

Use background colors to highlight important information:
- Light yellow (#fffacd) for hints
- Light blue (#e3f2fd) for examples
- Light green (#e8f5e9) for definitions

### Responsive Design

Keep these in mind for mobile (AnkiDroid):
- Use percentage widths (100%, 90%) instead of pixels
- Font sizes 16px+ are easier to read on phones
- Adequate padding (10-15px) for touch targets

### Font Hierarchy

Create visual hierarchy with font sizes:
- Headings: 24-28px
- Main content: 18-20px
- Secondary content: 14-16px

### Alignment Best Practices

- **Center**: Good for short text, images, headings
- **Left**: Better for longer text, paragraphs
- **Justify**: For formal, book-like appearance

## Common Template Patterns

### Basic Flashcard

1. Text Field (Front) - Center aligned, 20px font
2. Divider - 2px, light gray
3. Text Field (Back) - Center aligned, 18px font

### Image Vocabulary Card

1. Heading (Word) - Bold, 24px
2. Image Field (Picture) - Max height 300px
3. Divider
4. Text Field (Definition) - Left aligned
5. Conditional (Example sentence)

### Q&A with Hint

1. Text Field (Question) - Bold, 20px
2. Conditional (Hint) - Light background, small font
3. Divider
4. Text Field (Answer)
5. Conditional (Explanation) - Light background

## Switching to Code Mode

If you need more control:

1. Click **</> Code Editor** at the top
2. Your visual components are converted to HTML/CSS
3. Edit the code directly
4. Switch back to Visual Builder to see changes visually

**Note:** Complex code may not convert perfectly back to visual mode. The converter does its best but some manual adjustments may be needed.

## Keyboard Shortcuts

- **Delete**: Remove selected component
- **Ctrl+D**: Duplicate selected component (when implemented)
- **Ctrl+S**: Save template

## Troubleshooting

### Component doesn't show content

- Check that the **Field Name** matches exactly with your note fields
- Field names are case-sensitive

### Preview looks different than actual card

- Preview is a simulation - test with real cards
- Some JavaScript features may not work in preview
- AnkiDroid preview is approximate

### Can't find a field name

Available fields depend on your note type. To see all fields:
1. Go to Tools → Manage Note Types
2. Select your note type
3. Click "Fields"

### Colors not showing

- Make sure color is in hex format: #RRGGBB
- Use "transparent" for no background
- Try the color picker button

## Advanced Features

### Nested Conditionals

You can place conditionals inside containers to create complex logic:
1. Add a Container
2. Drag components into it
3. Wrap the container in a Conditional

### Multi-column Layout

Use multiple containers with flex layout:
1. Add a Container
2. Set flex direction to "row"
3. Add child containers for each column

### Custom Field Labels

Enable "Show Label" on Text Fields to add descriptive labels above fields.

## Getting Help

- Check component properties carefully
- Try the preview to see changes immediately
- Switch to Code Mode to see generated HTML/CSS
- Restart with a simple template and build up

Happy template building! 🎨
