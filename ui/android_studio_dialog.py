"""
Main template designer dialog - Android Studio style
Features Component Tree | Design Surface | Properties Panel layout
"""

from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QMessageBox, Qt, QTabWidget, QLabel,
    QToolBar, QAction, QComboBox, QWidget
)
from aqt import mw
from aqt.utils import showInfo

from .base_dialog import BaseTemplateDialog
from .component_tree import ComponentTree
from .design_surface import DesignSurface
from .properties_panel import PropertiesPanel
from .editor_widget import EditorWidget
from .preview_widget import PreviewWidget
from .template_converter import TemplateConverter
from .components import Component
from services import ServiceContainer
from typing import Optional, List, Dict, Any


class AndroidStudioDesignerDialog(BaseTemplateDialog):
    """
    Main dialog for template designer with Android Studio-style layout.
    
    Layout:
    ┌────────────────────────────────────────────────────────────────┐
    │  Toolbar: [Mode: Design ▼] [Save] [Preview] [Settings]        │
    ├──────────┬──────────────────────────┬──────────────────────────┤
    │          │                          │                          │
    │Component │     Design Surface       │   Properties Panel       │
    │  Tree    │                          │                          │
    │          │  [Zoom, Pan, Grid]       │   - Selected Component   │
    │  • Text  │                          │   - Layout               │
    │  • Image │  ┌────────────────────┐  │   - Text                 │
    │  • Div   │  │  Component 1       │  │   - Spacing              │
    │          │  └────────────────────┘  │   - Background           │
    │          │  ┌────────────────────┐  │                          │
    │          │  │  Component 2       │  │                          │
    │          │  └────────────────────┘  │                          │
    │          │                          │                          │
    └──────────┴──────────────────────────┴──────────────────────────┘
    """
    
    def __init__(
        self,
        services: ServiceContainer,
        parent: Optional[QDialog] = None,
        note_type: Optional[Dict[str, Any]] = None
    ):
        # Current mode: 'design', 'code', 'split'
        self.current_mode = 'design'
        
        # Initialize parent (will call setup_ui and load_note_type)
        super().__init__(services, parent, note_type)
    
    def setup_ui(self):
        """Setup the dialog UI with Android Studio-style layout"""
        self.setWindowTitle("Anki Template Designer - Visual Editor")
        
        # Larger window for better experience
        width = self.config.get('window_width', 1600)
        height = self.config.get('window_height', 900)
        self.resize(width, height)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top toolbar
        self.create_toolbar(layout)
        
        # Main content area with 3-panel layout
        self.create_main_content(layout)
        
        # Bottom status bar (optional)
        self.create_status_bar(layout)
    
    def create_toolbar(self, parent_layout):
        """Create top toolbar with mode switcher and actions"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Note type selector
        toolbar.addWidget(QLabel("Note Type:"))
        
        self.note_type_combo = QComboBox()
        self.note_type_combo.setMinimumWidth(200)
        
        # Populate with available note types
        note_types = mw.col.models.all_names_and_ids()
        for nt in note_types:
            self.note_type_combo.addItem(nt.name, nt.id)
        
        # Set current note type if one is already loaded, or auto-select first
        if self.note_type:
            current_name = self.note_type.get('name', '')
            index = self.note_type_combo.findText(current_name)
            if index >= 0:
                self.note_type_combo.setCurrentIndex(index)
        elif note_types:
            # Auto-select first note type if none is loaded
            self.note_type_combo.setCurrentIndex(0)
            # Manually trigger the change since setting index doesn't always trigger signal
            first_id = self.note_type_combo.itemData(0)
            self.note_type = mw.col.models.get(first_id)
            # Update status
            if hasattr(self, 'status_label') and self.note_type:
                self.status_label.setText(f"Loaded: {self.note_type['name']}")
        
        self.note_type_combo.currentIndexChanged.connect(self.on_note_type_changed)
        toolbar.addWidget(self.note_type_combo)
        
        toolbar.addSeparator()
        
        # Mode switcher
        toolbar.addWidget(QLabel("Mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Design", "Code", "Split"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        toolbar.addWidget(self.mode_combo)
        
        toolbar.addSeparator()
        
        # Side switcher (Front/Back)
        toolbar.addWidget(QLabel("Side:"))
        
        self.side_combo = QComboBox()
        self.side_combo.addItems(["Front", "Back"])
        self.side_combo.currentTextChanged.connect(self.on_side_changed)
        toolbar.addWidget(self.side_combo)
        
        toolbar.addSeparator()
        
        # Actions
        save_action = QAction("Save to Anki", self)
        save_action.triggered.connect(self.save_to_anki)
        toolbar.addAction(save_action)
        
        preview_action = QAction("Refresh Preview", self)
        preview_action.triggered.connect(self.refresh_preview)
        toolbar.addAction(preview_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        self.toolbar = toolbar
        parent_layout.addWidget(toolbar)
    
    def on_note_type_changed(self, index: int):
        """Handle note type selection change"""
        if index >= 0:
            note_type_id = self.note_type_combo.itemData(index)
            self.note_type = mw.col.models.get(note_type_id)
            self.load_note_type()
            # Update status
            if self.note_type:
                self.status_label.setText(f"Loaded: {self.note_type['name']}")
            else:
                self.status_label.setText("Ready")
    
    def create_main_content(self, parent_layout):
        """Create main 3-panel layout: Component Tree | Design Surface | Properties"""
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Component Palette + Tree (stacked vertically)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Component Palette at top
        from .visual_builder import ComponentPalette
        self.component_palette = ComponentPalette()
        self.component_palette.setMaximumHeight(300)
        # Connect palette to add components
        self.component_palette.component_list.itemDoubleClicked.connect(self.on_palette_item_double_clicked)
        left_layout.addWidget(self.component_palette)
        
        # Component Tree below
        self.component_tree = ComponentTree(
            on_selection_change=self.on_tree_selection_changed,
            on_structure_change=self.on_structure_changed
        )
        left_layout.addWidget(self.component_tree)
        
        left_panel.setMinimumWidth(200)
        left_panel.setMaximumWidth(350)
        self.main_splitter.addWidget(left_panel)
        
        # Center panel: Design Surface or Code Editor
        self.center_stack = QTabWidget()
        self.center_stack.setTabsClosable(False)
        
        # Design Surface
        self.design_surface = DesignSurface(
            on_selection_change=self.on_surface_selection_changed
        )
        self.center_stack.addTab(self.design_surface, "Design")
        
        # Code Editor
        self.code_editor = EditorWidget(on_change_callback=self.on_code_changed)
        self.center_stack.addTab(self.code_editor, "Code")
        
        # Preview
        self.preview_widget = PreviewWidget()
        self.preview_widget.set_renderers(self.desktop_renderer, self.ankidroid_renderer)
        self.center_stack.addTab(self.preview_widget, "Preview")
        
        self.main_splitter.addWidget(self.center_stack)
        
        # Right panel: Properties
        self.properties_panel = PropertiesPanel(on_change=self.on_property_changed)
        self.properties_panel.setMinimumWidth(250)
        self.properties_panel.setMaximumWidth(400)
        self.main_splitter.addWidget(self.properties_panel)
        
        # Set initial splitter sizes: 20% tree, 55% center, 25% properties
        total_width = self.width()
        self.main_splitter.setSizes([
            int(total_width * 0.20),
            int(total_width * 0.55),
            int(total_width * 0.25)
        ])
        
        parent_layout.addWidget(self.main_splitter)
    
    def create_status_bar(self, parent_layout):
        """Create bottom status bar"""
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background: #f0f0f0;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Component count
        self.component_count_label = QLabel("Components: 0")
        self.component_count_label.setStyleSheet("padding: 5px; background: #f0f0f0;")
        status_layout.addWidget(self.component_count_label)
        
        parent_layout.addLayout(status_layout)
    
    def on_mode_changed(self, mode: str):
        """Handle mode change"""
        self.current_mode = mode.lower()
        
        if self.current_mode == 'design':
            self.center_stack.setCurrentIndex(0)  # Design Surface
        elif self.current_mode == 'code':
            # Sync design to code before showing
            self.sync_design_to_code()
            self.center_stack.setCurrentIndex(1)  # Code Editor
        elif self.current_mode == 'split':
            # Show both (would need custom split view widget)
            self.center_stack.setCurrentIndex(0)  # For now, show design
    
    def on_side_changed(self, side: str = None):
        """Handle front/back side change"""
        if side is not None:
            self.set_side(side.lower())
    
    def on_tree_selection_changed(self, component: Optional[Component]):
        """Handle component selection from tree"""
        # Update design surface selection
        self.design_surface.select_component(component)
        
        # Update properties panel
        self.properties_panel.set_component(component)
    
    def on_surface_selection_changed(self, component: Optional[Component]):
        """Handle component selection from design surface"""
        # Update component tree selection
        self.component_tree.select_component(component)
        
        # Update properties panel
        self.properties_panel.set_component(component)
    
    def on_structure_changed(self):
        """Handle structure change from tree"""
        # Update design surface
        components = self.component_tree.get_components()
        self.design_surface.set_components(components)
        
        # Update component count
        self.component_count_label.setText(f"Components: {len(components)}")
        
        # Update preview
        self.sync_design_to_code()
        self.refresh_preview()
    
    def on_note_type_changed(self, index):
        """Handle note type selection change"""
        if index < 0:
            return
        
        # Get selected note type ID
        note_type_id = self.note_type_combo.itemData(index)
        
        # Load the note type
        self.note_type = mw.col.models.get(note_type_id)
        
        # Reload templates
        self.load_note_type()
        
        # Update status
        if self.note_type:
            self.status_label.setText(f"Loaded: {self.note_type['name']}")
    
    def on_property_changed(self):
        """Handle property change"""
        # Refresh design surface to show changes
        self.design_surface.canvas.update()
        
        # Update preview
        self.sync_design_to_code()
        self.refresh_preview()
    
    def on_palette_item_double_clicked(self, item):
        """Handle double-click on palette item - adds new component"""
        from .components import (
            ComponentType, TextFieldComponent, ImageFieldComponent,
            DividerComponent, HeadingComponent, ContainerComponent,
            ConditionalComponent
        )
        
        # Get component type from item data
        comp_type = item.data(Qt.ItemDataRole.UserRole)
        
        # Create new component based on type
        new_component = None
        if comp_type == ComponentType.TEXT_FIELD:
            new_component = TextFieldComponent(field_name="Field")
        elif comp_type == ComponentType.IMAGE_FIELD:
            new_component = ImageFieldComponent(field_name="Image")
        elif comp_type == ComponentType.DIVIDER:
            new_component = DividerComponent()
        elif comp_type == ComponentType.HEADING:
            new_component = HeadingComponent(field_name="Title")
        elif comp_type == ComponentType.CONTAINER:
            new_component = ContainerComponent()
        elif comp_type == ComponentType.CONDITIONAL:
            new_component = ConditionalComponent(field_name="Field")
        
        if new_component:
            # Add to components list
            components = self.component_tree.get_components()
            components.append(new_component)
            
            # Update tree and surface
            self.component_tree.set_components(components)
            self.design_surface.set_components(components)
            self.component_count_label.setText(f"Components: {len(components)}")
            
            # Select the new component
            self.component_tree.select_component(new_component)
            self.design_surface.select_component(new_component)
            
            # Update preview
            self.sync_design_to_code()
            self.refresh_preview()
    
        # Check if note type is loaded
        if not self.note_type:
            showInfo("Please select a note type first")
            return
        
        # Sync design to code before saving
        self.sync_design_to_code()
        
        # Confirm save
        reply = QMessageBox.question(
            self,
            "Save Templates",
            f"Save changes to note type '{self.note_type['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Use the proper Anki API to save
                mw.col.models.update_dict(self.note_type)
                showInfo("Templates saved successfully!")
                self.status_label.setText("Saved to Anki")
            except Exception as e:
                showInfo(f"Error saving templates: {str(e)}")
                self.status_label.setText(f"Error: {str(e)}")
    
    def on_code_changed(self):
        """Handle code editor change"""
        self.refresh_preview()
    
    def sync_design_to_code(self):
        """Sync design surface components to code editor"""
        components = self.component_tree.get_components()
        
        if not components:
            return
        
        # Convert components to HTML/CSS
        html = TemplateConverter.components_to_html(components)
        css = TemplateConverter.components_to_css(components)
        
        # Update code editor
        templates = self.code_editor.templates
        if templates and len(templates) > 0:
            current_idx = self.code_editor.current_card_index
            template = templates[current_idx]
            
            # Update the appropriate side
            if self.current_side == 'front':
                template['qfmt'] = html
            else:
                template['afmt'] = html
            
            # Update CSS in note type (not in template)
            if self.note_type:
                self.note_type['css'] = css
            
            # Reload the template in editor to show changes
            self.code_editor.load_template(current_idx)
    
    def sync_code_to_design(self):
        """Sync code editor to design surface components"""
        templates = self.code_editor.templates
        if not templates:
            return
        
        current_idx = self.code_editor.current_card_index
        template = templates[current_idx]
        
        # Get HTML for current side
        if self.current_side == 'front':
            html = template.get('qfmt', '')
        else:
            html = template.get('afmt', '')
        
        # Get CSS from note type (not template)
        css = self.note_type.get('css', '') if self.note_type else ''
        
        # Convert HTML/CSS to components
        components = TemplateConverter.html_to_components(html, css)
        
        # Update component tree and design surface
        self.component_tree.set_components(components)
        self.design_surface.set_components(components)
        self.component_count_label.setText(f"Components: {len(components)}")
    
    def load_note_type(self):
        """Load templates from note type"""
        if not self.note_type:
            return
        
        # Pass note type to editor for CSS access
        self.code_editor.note_type = self.note_type
        
        # Get templates
        templates = self.note_type.get('tmpls', [])
        
        if templates:
            # Store templates in editor
            self.code_editor.set_templates(templates)
            
            # Load current template
            if len(templates) > 0:
                self.code_editor.load_template(0)
            
            # Sync to design view
            self.sync_code_to_design()
        
        # Update status
        if hasattr(self, 'status_label') and self.note_type:
            self.status_label.setText(f"Loaded: {self.note_type['name']}")
        elif hasattr(self, 'status_label'):
            self.status_label.setText("Ready")
    
    def load_current_side(self):
        """Load the current side (front/back) into design view"""
        self.sync_code_to_design()
        self.refresh_preview()
    
    def sync_to_preview(self) -> None:
        """Refresh the preview (implements base class abstract method)"""
        templates = self.code_editor.templates
        if templates:
            template = templates[0]
            note = self.get_sample_note()
            self.preview_widget.set_template(template, note=note, side=self.current_side)
            self.preview_widget.refresh_preview(side=self.current_side)
    
    def refresh_preview(self):
        """Refresh the preview (convenience method)"""
        self.sync_to_preview()
    
    def get_sample_note(self):
        """Get a sample note for preview"""
        if not self.note_type:
            return None
        
        # Try to find an existing note of this type
        note_ids = mw.col.find_notes(f'"note:{self.note_type["name"]}"')
        
        if note_ids:
            note = mw.col.get_note(note_ids[0])
            return note
        
        return None
    
    def get_templates_to_save(self) -> List[Dict[str, Any]]:
        """Get templates to save (implements base class abstract method)"""
        if hasattr(self, 'code_editor') and self.code_editor:
            return self.code_editor.templates if self.code_editor.templates else []
        return []
    
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        showInfo("Settings dialog not yet implemented")
    
    def closeEvent(self, event):
        """Handle dialog close"""
        # Check if there are unsaved changes
        # For now, just close
        event.accept()
