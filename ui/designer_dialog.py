"""
Main template designer dialog
"""

from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QMessageBox, Qt, QTabWidget, QLabel,
    QFileDialog, QMenu, QToolBar
)
from aqt import mw
from aqt.utils import showInfo

from .base_dialog import BaseTemplateDialog
from .editor_widget import EditorWidget
from .preview_widget import PreviewWidget
from .visual_builder import VisualTemplateBuilder
from .template_converter import TemplateConverter
from .commands import CommandHistory
from .shortcuts import ShortcutManager, ShortcutAction
from .template_library import TemplateLibrary
from .template_io import TemplateExporter, TemplateImporter
from .recent_templates import RecentTemplatesMenuManager
from .progress_indicators import TaskRunner
from services import ServiceContainer
from typing import Optional, Dict, Any, List
from pathlib import Path


class TemplateDesignerDialog(BaseTemplateDialog):
    """Main dialog for template designer"""
    
    def __init__(
        self,
        services: ServiceContainer,
        parent: Optional[QDialog] = None,
        note_type: Optional[Dict[str, Any]] = None
    ):
        # Current mode: 'visual', 'code'
        self.current_mode = 'visual'
        
        # Track if preview is detached
        self.preview_detached = False
        self.detached_preview_window = None
        
        # Command history for undo/redo
        self.command_history = CommandHistory()
        
        # Keyboard shortcuts manager
        self.shortcut_manager = ShortcutManager(self)
        
        # Recent templates manager
        self.recent_templates_manager = None  # Initialized in setup_ui
        
        # Current file path for save/load
        self.current_file_path = None
        
        # Initialize parent (will call setup_ui and load_note_type)
        super().__init__(services, parent, note_type)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Anki Template Designer")
        
        # Get size from config - larger default to show everything
        width = self.config.get('preview_width', 1600)
        height = self.config.get('preview_height', 900)
        self.resize(width, height)
        
        layout = QVBoxLayout(self)
        
        # Add menu bar
        self._setup_menu_bar(layout)
        
        # Mode selector at top
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("<b>Edit Mode:</b>"))
        
        self.visual_mode_btn = QPushButton("Visual Builder")
        self.visual_mode_btn.setCheckable(True)
        self.visual_mode_btn.setChecked(True)
        self.visual_mode_btn.clicked.connect(lambda: self.set_mode('visual'))
        mode_layout.addWidget(self.visual_mode_btn)
        
        self.code_mode_btn = QPushButton("Code Editor")
        self.code_mode_btn.setCheckable(True)
        self.code_mode_btn.clicked.connect(lambda: self.set_mode('code'))
        mode_layout.addWidget(self.code_mode_btn)
        
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Main splitter (editor on left, preview on right)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tabbed editor area
        self.editor_tabs = QTabWidget()
        
        # Visual builder
        self.visual_builder = VisualTemplateBuilder(on_change_callback=self.on_visual_change)
        self.editor_tabs.addTab(self.visual_builder, "Visual Builder")
        
        # Code editor
        self.editor = EditorWidget(on_change_callback=self.on_template_change)
        self.editor_tabs.addTab(self.editor, "Code Editor")
        
        self.main_splitter.addWidget(self.editor_tabs)
        
        # Preview widget
        self.preview = PreviewWidget()
        self.preview.set_renderers(self.desktop_renderer, self.ankidroid_renderer)
        self.main_splitter.addWidget(self.preview)
        
        # Set initial splitter sizes (50% editor, 50% preview)
        self.main_splitter.setSizes([int(width * 0.5), int(width * 0.5)])
        
        layout.addWidget(self.main_splitter)
        
        # Bottom buttons
        buttons = QHBoxLayout()
        
        self.save_btn = QPushButton("Save to Anki")
        self.save_btn.clicked.connect(self.save_to_anki)
        buttons.addWidget(self.save_btn)
        
        self.detach_btn = QPushButton("Detach Preview")
        self.detach_btn.clicked.connect(self.toggle_preview_detach)
        buttons.addWidget(self.detach_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        buttons.addWidget(self.close_btn)
        
        buttons.addStretch()
        
        # Side selector
        self.front_btn = QPushButton("Front")
        self.front_btn.setCheckable(True)
        self.front_btn.setChecked(True)
        self.front_btn.clicked.connect(lambda: self.set_side('front'))
        buttons.addWidget(self.front_btn)
        
        self.back_btn = QPushButton("Back")
        self.back_btn.setCheckable(True)
        self.back_btn.clicked.connect(lambda: self.set_side('back'))
        buttons.addWidget(self.back_btn)
        
        layout.addLayout(buttons)
        
        # Start in visual mode
        self.editor_tabs.setCurrentWidget(self.visual_builder)
        
        # Setup keyboard shortcuts after UI is ready
        self._setup_keyboard_shortcuts()
    
    def set_mode(self, mode):
        """Switch between visual and code modes"""
        if mode == self.current_mode:
            return
        
        # Sync data before switching
        if self.current_mode == 'visual':
            # Convert visual to code
            self.sync_visual_to_code()
        else:
            # Convert code to visual
            self.sync_code_to_visual()
        
        self.current_mode = mode
        
        # Update button states
        self.visual_mode_btn.setChecked(mode == 'visual')
        self.code_mode_btn.setChecked(mode == 'code')
        
        # Switch tab
        if mode == 'visual':
            self.editor_tabs.setCurrentWidget(self.visual_builder)
        else:
            self.editor_tabs.setCurrentWidget(self.editor)
    
    def sync_visual_to_code(self):
        """Sync visual builder to code editor"""
        try:
            components = self.visual_builder.get_components()
            if not components:
                return
                
            # Get current template from editor
            idx = self.editor.current_card_index
            if idx >= len(self.editor.templates):
                return
                
            current_template = self.editor.templates[idx]
            
            # Generate HTML and CSS from components
            html = TemplateConverter.components_to_html(components)
            css = TemplateConverter.components_to_css(components)
            
            # Update the template in the templates list
            if self.current_side == 'front':
                current_template['qfmt'] = html
            else:
                current_template['afmt'] = html
            current_template['css'] = css
            
            # Force editor to reload to show updated content
            self.editor.blockSignals(True)
            self.editor.load_template(idx)
            self.editor.blockSignals(False)
        except ValueError as e:
            self.handle_validation_error(e)
        except Exception as e:
            self.handle_error(e, "sync to code editor")
    
    def sync_code_to_visual(self):
        """Sync code editor to visual builder"""
        try:
            template = self.editor.get_current_template()
            if template:
                # Convert HTML to components
                html = template.get('qfmt' if self.current_side == 'front' else 'afmt', '')
                css = template.get('css', '')
                
                components = TemplateConverter.html_to_components(html, css)
                self.visual_builder.set_components(components)
        except ValueError as e:
            self.handle_validation_error(e)
        except Exception as e:
            self.handle_error(e, "parse template HTML")
    
    def on_note_type_loaded(self) -> None:
        """Hook called after note type is loaded"""
        templates = self.note_type.get('tmpls', [])
        self.editor.set_templates(templates)
        
        # Load first template into visual builder
        if templates:
            template = templates[0]
            html = template.get('qfmt', '')
            css = template.get('css', '')
            
            components = TemplateConverter.html_to_components(html, css)
            self.visual_builder.set_components(components)
            
            # Show initial preview
            self.on_template_change(template)
        
        # Sync to code editor immediately to keep in sync
        self.sync_visual_to_code()
    
    def on_visual_change(self):
        """Handle visual builder change"""
        if self.config.get('auto_refresh', True):
            try:
                self.sync_to_preview()
            except ValueError as e:
                self.handle_validation_error(e)
            except Exception as e:
                self.handle_error(e, "update preview")
    
    def on_template_change(self, template):
        """Handle template change in editor"""
        if self.config.get('auto_refresh', True):
            try:
                self.sync_to_preview()
            except ValueError as e:
                self.handle_validation_error(e)
            except Exception as e:
                self.handle_error(e, "update preview")
    
    def sync_to_preview(self) -> None:
        """Update the preview with current template (implements base class abstract method)"""
        # Get a sample note for preview
        sample_note = self.get_sample_note()
        
        # Get current template
        if self.current_mode == 'visual':
            try:
                components = self.visual_builder.get_components()
                if components:
                    template_dict = TemplateConverter.create_template_dict(components, self.current_side)
                    self.preview.set_template(template_dict, sample_note, side=self.current_side)
            except Exception as e:
                import logging
                logging.error(f"Error in visual preview: {e}")
        else:
            template = self.editor.get_current_template()
            if template:
                self.preview.set_template(template, sample_note, side=self.current_side)
    
    def get_templates_to_save(self) -> List[Dict[str, Any]]:
        """Get templates to save (implements base class abstract method)"""
        # Sync visual to code if in visual mode
        if self.current_mode == 'visual':
            self.sync_visual_to_code()
        
        # Get templates from editor
        return self.editor.templates
    
    def on_side_changed(self) -> None:
        """Override base class hook for side changes"""
        # Update button states
        self.front_btn.setChecked(self.current_side == 'front')
        self.back_btn.setChecked(self.current_side == 'back')
        
        # Reload visual builder with the correct side's template
        if self.current_mode == 'visual':
            template = self.editor.get_current_template()
            if template:
                html = template.get('qfmt' if self.current_side == 'front' else 'afmt', '')
                css = template.get('css', '')
                components = TemplateConverter.html_to_components(html, css)
                self.visual_builder.set_components(components)
        
        # Update preview
        self.sync_to_preview()
    
    def toggle_preview_detach(self):
        """Toggle preview between attached and detached"""
        if self.preview_detached:
            self.reattach_preview()
        else:
            self.detach_preview()
    
    def detach_preview(self):
        """Detach preview to separate window"""
        # Create detached window
        self.detached_preview_window = QDialog(self)
        self.detached_preview_window.setWindowTitle("Template Preview")
        self.detached_preview_window.resize(900, 700)
        
        layout = QVBoxLayout(self.detached_preview_window)
        
        # Move preview widget to new window
        self.main_splitter.widget(1).setParent(None)
        layout.addWidget(self.preview)
        
        # Update button
        self.detach_btn.setText("Reattach Preview")
        self.preview_detached = True
        
        # Show the window
        self.detached_preview_window.show()
        
        # Connect close event
        self.detached_preview_window.finished.connect(self.on_detached_preview_close)
    
    def reattach_preview(self):
        """Reattach preview to main window"""
        if self.detached_preview_window:
            # Move preview back to main splitter
            self.preview.setParent(None)
            self.main_splitter.addWidget(self.preview)
            
            # Close detached window
            self.detached_preview_window.close()
            self.detached_preview_window = None
            
            # Update button
            self.detach_btn.setText("Detach Preview")
            self.preview_detached = False
            
            # Restore splitter sizes
            width = self.width()
            self.main_splitter.setSizes([int(width * 0.5), int(width * 0.5)])
    
    def on_detached_preview_close(self):
        """Handle detached preview window close"""
        # Auto-reattach when user closes the detached window
        if self.preview_detached:
            self.reattach_preview()
    
    def closeEvent(self, event):
        """Handle dialog close"""
        # Close detached preview if open
        if self.detached_preview_window:
            self.detached_preview_window.close()
        
        # Check if there are unsaved changes
        # For now, just close
        event.accept()
    
    def _setup_menu_bar(self, layout):
        """Setup menu bar with File and Edit menus"""
        from PyQt6.QtWidgets import QMenuBar
        
        menubar = QMenuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New template
        new_action = file_menu.addAction("&New Template")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_template)
        
        # Open template
        open_action = file_menu.addAction("&Open Template...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_template)
        
        # Recent templates submenu
        self.recent_templates_manager = RecentTemplatesMenuManager()
        self.recent_templates_manager.setup_menu(file_menu)
        self.recent_templates_manager.connect_template_selected(self._on_recent_template_selected)
        
        file_menu.addSeparator()
        
        # Save template
        save_action = file_menu.addAction("&Save Template")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_template)
        
        # Save template as
        save_as_action = file_menu.addAction("Save Template &As...")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._on_save_template_as)
        
        file_menu.addSeparator()
        
        # Export template
        export_action = file_menu.addAction("&Export Template...")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_template)
        
        # Import template
        import_action = file_menu.addAction("&Import Template...")
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._on_import_template)
        
        file_menu.addSeparator()
        
        # Template library
        library_action = file_menu.addAction("Template &Library...")
        library_action.triggered.connect(self._on_show_template_library)
        
        file_menu.addSeparator()
        
        # Close
        close_action = file_menu.addAction("&Close")
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo
        self.undo_action = edit_menu.addAction("&Undo")
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._on_undo)
        self.undo_action.setEnabled(False)
        
        # Redo
        self.redo_action = edit_menu.addAction("&Redo")
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._on_redo)
        self.redo_action.setEnabled(False)
        
        edit_menu.addSeparator()
        
        # Find
        find_action = edit_menu.addAction("&Find Component...")
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self._on_find_component)
        
        layout.addWidget(menubar)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Register main actions
        self.shortcut_manager.register_action(ShortcutAction.SAVE, self._on_save_template)
        self.shortcut_manager.register_action(ShortcutAction.UNDO, self._on_undo)
        self.shortcut_manager.register_action(ShortcutAction.REDO, self._on_redo)
        self.shortcut_manager.register_action(ShortcutAction.EXPORT, self._on_export_template)
        self.shortcut_manager.register_action(ShortcutAction.IMPORT, self._on_import_template)
        
        # Update undo/redo action states
        self.command_history.can_undo_changed.connect(self.undo_action.setEnabled)
        self.command_history.can_redo_changed.connect(self.redo_action.setEnabled)
    
    def _on_new_template(self):
        """Create a new template"""
        # Ask to save current if modified
        # For now, just clear the visual builder
        self.visual_builder.clear()
        self.current_file_path = None
        self.setWindowTitle("Anki Template Designer - New Template")
    
    def _on_open_template(self):
        """Open a template file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Template",
            "",
            "Template Files (*.atd);;All Files (*)"
        )
        
        if file_path:
            self._load_template_file(file_path)
    
    def _on_recent_template_selected(self, file_path: str):
        """Handle recent template selection"""
        self._load_template_file(file_path)
    
    def _load_template_file(self, file_path: str):
        """Load a template from file"""
        try:
            importer = TemplateImporter()
            components = importer.import_template(file_path)
            
            self.visual_builder.set_components(components)
            self.current_file_path = file_path
            
            # Add to recent templates
            self.recent_templates_manager.add_template(file_path)
            
            # Update window title
            self.setWindowTitle(f"Anki Template Designer - {Path(file_path).name}")
            
            showInfo(f"Template loaded from {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to load template: {str(e)}"
            )
    
    def _on_save_template(self):
        """Save current template"""
        if self.current_file_path:
            self._save_template_to_file(self.current_file_path)
        else:
            self._on_save_template_as()
    
    def _on_save_template_as(self):
        """Save template as new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Template",
            "",
            "Template Files (*.atd);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.atd'):
                file_path += '.atd'
            
            self._save_template_to_file(file_path)
    
    def _save_template_to_file(self, file_path: str):
        """Save template to file"""
        try:
            components = self.visual_builder.get_components()
            
            exporter = TemplateExporter()
            exporter.export_template(components, file_path)
            
            self.current_file_path = file_path
            
            # Add to recent templates
            self.recent_templates_manager.add_template(file_path)
            
            # Update window title
            self.setWindowTitle(f"Anki Template Designer - {Path(file_path).name}")
            
            showInfo(f"Template saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save template: {str(e)}"
            )
    
    def _on_export_template(self):
        """Export template to .atd file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Template",
            "",
            "Anki Template Designer (*.atd);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.atd'):
                file_path += '.atd'
            
            self._save_template_to_file(file_path)
    
    def _on_import_template(self):
        """Import template from .atd file"""
        self._on_open_template()
    
    def _on_show_template_library(self):
        """Show template library dialog"""
        from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QPushButton, QComboBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Template Library")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Category filter
        category_combo = QComboBox()
        category_combo.addItem("All Categories")
        category_combo.addItems(TemplateLibrary.get_categories())
        layout.addWidget(category_combo)
        
        # Template list
        template_list = QListWidget()
        
        def update_template_list():
            template_list.clear()
            category = category_combo.currentText()
            
            if category == "All Categories":
                templates = TemplateLibrary.get_all_templates()
            else:
                templates = [t for t in TemplateLibrary.get_all_templates() 
                           if t['category'] == category]
            
            for template in templates:
                item = QListWidgetItem(
                    f"{template['name']} - {template['description']}"
                )
                item.setData(Qt.ItemDataRole.UserRole, template['id'])
                template_list.addItem(item)
        
        category_combo.currentTextChanged.connect(update_template_list)
        update_template_list()
        
        layout.addWidget(template_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        use_btn = QPushButton("Use Template")
        def on_use_template():
            current_item = template_list.currentItem()
            if current_item:
                template_id = current_item.data(Qt.ItemDataRole.UserRole)
                components = TemplateLibrary.create_template(template_id)
                self.visual_builder.set_components(components)
                dialog.accept()
        
        use_btn.clicked.connect(on_use_template)
        button_layout.addWidget(use_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _on_undo(self):
        """Undo last command"""
        if self.command_history.can_undo():
            self.command_history.undo()
            # Refresh visual builder
            self.on_visual_change()
    
    def _on_redo(self):
        """Redo last undone command"""
        if self.command_history.can_redo():
            self.command_history.redo()
            # Refresh visual builder
            self.on_visual_change()
    
    def _on_find_component(self):
        """Open find component dialog"""
        # This will be implemented when component search is integrated
        showInfo("Component search not yet implemented in this dialog")
