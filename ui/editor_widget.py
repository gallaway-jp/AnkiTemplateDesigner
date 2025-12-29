"""
Editor widget for editing templates
"""

from aqt.qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPlainTextEdit, QLabel, QPushButton, QComboBox
)
from aqt.theme import theme_manager
from .syntax_highlighter import HTMLHighlighter, CSSHighlighter, HighlighterTheme


class EditorWidget(QWidget):
    """Widget for editing card templates"""
    
    def __init__(self, parent=None, on_change_callback=None):
        super().__init__(parent)
        self.on_change_callback = on_change_callback
        self.current_card_index = 0
        self.templates = []
        self.note_type = None  # Store note type for CSS access
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Card selector
        card_selector = QHBoxLayout()
        card_selector.addWidget(QLabel("Card:"))
        self.card_combo = QComboBox()
        self.card_combo.currentIndexChanged.connect(self.on_card_changed)
        card_selector.addWidget(self.card_combo)
        card_selector.addStretch()
        
        # Add/Remove card buttons
        self.add_card_btn = QPushButton("Add Card")
        self.add_card_btn.clicked.connect(self.add_card)
        card_selector.addWidget(self.add_card_btn)
        
        self.remove_card_btn = QPushButton("Remove Card")
        self.remove_card_btn.clicked.connect(self.remove_card)
        card_selector.addWidget(self.remove_card_btn)
        
        layout.addLayout(card_selector)
        
        # Template tabs
        self.tabs = QTabWidget()
        
        # Front template
        self.front_editor = QPlainTextEdit()
        self.front_editor.setPlaceholderText("Enter front template HTML here...")
        self.front_editor.textChanged.connect(self.on_template_changed)
        self.tabs.addTab(self.front_editor, "Front Template")
        
        # Add syntax highlighting
        self.front_highlighter = HTMLHighlighter(self.front_editor.document())
        
        # Back template
        self.back_editor = QPlainTextEdit()
        self.back_editor.setPlaceholderText("Enter back template HTML here...")
        self.back_editor.textChanged.connect(self.on_template_changed)
        self.tabs.addTab(self.back_editor, "Back Template")
        
        # Add syntax highlighting
        self.back_highlighter = HTMLHighlighter(self.back_editor.document())
        
        # Styling
        self.style_editor = QPlainTextEdit()
        self.style_editor.setPlaceholderText("Enter CSS styling here...")
        self.style_editor.textChanged.connect(self.on_template_changed)
        self.tabs.addTab(self.style_editor, "Styling")
        
        # Add syntax highlighting
        self.style_highlighter = CSSHighlighter(self.style_editor.document())
        
        layout.addWidget(self.tabs)
        
        # Action buttons
        actions = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Template")
        self.save_btn.clicked.connect(self.save_template)
        actions.addWidget(self.save_btn)
        
        self.revert_btn = QPushButton("Revert Changes")
        self.revert_btn.clicked.connect(self.revert_changes)
        actions.addWidget(self.revert_btn)
        
        actions.addStretch()
        layout.addLayout(actions)
    
    def set_templates(self, templates):
        """Set the templates to edit"""
        self.templates = templates
        self.card_combo.clear()
        
        for i, template in enumerate(templates):
            name = template.get('name', f'Card {i + 1}')
            self.card_combo.addItem(name)
        
        if templates:
            self.current_card_index = 0
            self.load_template(0)
    
    def load_template(self, index):
        """Load a template into the editors"""
        if not self.templates or index >= len(self.templates):
            return
        
        template = self.templates[index]
        
        # Block signals to prevent triggering change callback
        self.front_editor.blockSignals(True)
        self.back_editor.blockSignals(True)
        self.style_editor.blockSignals(True)
        
        self.front_editor.setPlainText(template.get('qfmt', ''))
        self.back_editor.setPlainText(template.get('afmt', ''))
        
        # CSS comes from note type, not template
        if self.note_type:
            self.style_editor.setPlainText(self.note_type.get('css', ''))
        else:
            self.style_editor.setPlainText('')
        
        self.front_editor.blockSignals(False)
        self.back_editor.blockSignals(False)
        self.style_editor.blockSignals(False)
    
    def on_card_changed(self, index):
        """Handle card selection change"""
        self.current_card_index = index
        self.load_template(index)
    
    def on_template_changed(self):
        """Handle template text change"""
        if self.on_change_callback:
            template = self.get_current_template()
            self.on_change_callback(template)
    
    def get_current_template(self):
        """Get the current template as a dictionary"""
        if not self.templates:
            return {}
        
        return {
            'name': self.card_combo.currentText(),
            'qfmt': self.front_editor.toPlainText(),
            'afmt': self.back_editor.toPlainText(),
            'css': self.style_editor.toPlainText()
        }
    
    def save_template(self):
        """Save the current template"""
        if self.templates and self.current_card_index < len(self.templates):
            template = self.templates[self.current_card_index]
            template['qfmt'] = self.front_editor.toPlainText()
            template['afmt'] = self.back_editor.toPlainText()
            # CSS is saved to note type, not template
            if self.note_type:
                self.note_type['css'] = self.style_editor.toPlainText()
    
    def revert_changes(self):
        """Revert changes to the current template"""
        self.load_template(self.current_card_index)
    
    def add_card(self):
        """Add a new card template"""
        new_template = {
            'name': f'Card {len(self.templates) + 1}',
            'qfmt': '',
            'afmt': '',
            'css': ''
        }
        self.templates.append(new_template)
        self.card_combo.addItem(new_template['name'])
        self.card_combo.setCurrentIndex(len(self.templates) - 1)
    
    def remove_card(self):
        """Remove the current card template"""
        if len(self.templates) <= 1:
            return  # Don't allow removing the last template
        
        index = self.current_card_index
        self.templates.pop(index)
        self.card_combo.removeItem(index)
        
        if index >= len(self.templates):
            index = len(self.templates) - 1
        
        self.current_card_index = index
        self.load_template(index)
