"""
Template library with pre-built templates for common use cases.

Provides a collection of professionally designed templates that users
can import and customize for their needs.
"""

from typing import Dict, List, Optional
from .components import (
    Component, ComponentType, Alignment,
    TextFieldComponent, ImageFieldComponent, HeadingComponent,
    DividerComponent, ContainerComponent
)
from config.constants import UIDefaults, ComponentDefaults


class TemplateLibrary:
    """
    Collection of pre-built templates.
    
    Templates are organized by category and include common
    flashcard designs for various subjects.
    """
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get list of template categories."""
        return [
            "Language Learning",
            "Medical",
            "Science & Math",
            "General",
            "Minimalist",
            "Advanced"
        ]
    
    @staticmethod
    def get_templates_by_category(category: str) -> List[Dict]:
        """
        Get all templates in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of template metadata dicts
        """
        all_templates = TemplateLibrary.get_all_templates()
        return [t for t in all_templates if t['category'] == category]
    
    @staticmethod
    def get_all_templates() -> List[Dict]:
        """
        Get metadata for all available templates.
        
        Returns:
            List of dicts with template info
        """
        return [
            {
                'id': 'basic_text',
                'name': 'Basic Text Card',
                'category': 'General',
                'description': 'Simple front/back text card',
                'fields': ['Front', 'Back'],
                'preview': 'Basic card with question on front, answer on back'
            },
            {
                'id': 'vocabulary',
                'name': 'Vocabulary Card',
                'category': 'Language Learning',
                'description': 'Word, pronunciation, and definition',
                'fields': ['Word', 'Pronunciation', 'Definition', 'Example'],
                'preview': 'Language learning card with word, pronunciation, definition and example'
            },
            {
                'id': 'cloze_basic',
                'name': 'Basic Cloze',
                'category': 'General',
                'description': 'Fill-in-the-blank style card',
                'fields': ['Text', 'Extra'],
                'preview': 'Cloze deletion card for fill-in-the-blank practice'
            },
            {
                'id': 'image_occlusion',
                'name': 'Image Occlusion',
                'category': 'Medical',
                'description': 'Image with hidden labels',
                'fields': ['Image', 'Question', 'Answer'],
                'preview': 'Medical diagram with occluded labels'
            },
            {
                'id': 'formula',
                'name': 'Formula Card',
                'category': 'Science & Math',
                'description': 'Mathematical formula with explanation',
                'fields': ['Formula', 'Variables', 'Example', 'Notes'],
                'preview': 'Math/science formula with variables and examples'
            },
            {
                'id': 'minimal',
                'name': 'Minimal Card',
                'category': 'Minimalist',
                'description': 'Clean, distraction-free design',
                'fields': ['Question', 'Answer'],
                'preview': 'Ultra-minimal design with no visual clutter'
            },
            {
                'id': 'two_column',
                'name': 'Two Column',
                'category': 'Advanced',
                'description': 'Side-by-side comparison',
                'fields': ['Left', 'Right', 'Notes'],
                'preview': 'Two-column layout for comparisons'
            },
            {
                'id': 'medical_drug',
                'name': 'Drug Information',
                'category': 'Medical',
                'description': 'Medication details card',
                'fields': ['Drug', 'Class', 'Mechanism', 'Indications', 'Side Effects'],
                'preview': 'Comprehensive drug information card'
            },
            {
                'id': 'anatomy',
                'name': 'Anatomy Card',
                'category': 'Medical',
                'description': 'Anatomical structure details',
                'fields': ['Structure', 'Location', 'Function', 'Image'],
                'preview': 'Anatomy card with structure details and image'
            },
            {
                'id': 'language_sentence',
                'name': 'Sentence Practice',
                'category': 'Language Learning',
                'description': 'Full sentence translation',
                'fields': ['Native', 'Translation', 'Grammar Notes'],
                'preview': 'Sentence translation with grammar notes'
            }
        ]
    
    @staticmethod
    def create_template(template_id: str) -> Optional[Dict]:
        """
        Create a template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template dict with components, or None if not found
        """
        templates = {
            'basic_text': TemplateLibrary._create_basic_text(),
            'vocabulary': TemplateLibrary._create_vocabulary(),
            'cloze_basic': TemplateLibrary._create_cloze_basic(),
            'image_occlusion': TemplateLibrary._create_image_occlusion(),
            'formula': TemplateLibrary._create_formula(),
            'minimal': TemplateLibrary._create_minimal(),
            'two_column': TemplateLibrary._create_two_column(),
            'medical_drug': TemplateLibrary._create_medical_drug(),
            'anatomy': TemplateLibrary._create_anatomy(),
            'language_sentence': TemplateLibrary._create_language_sentence(),
        }
        
        return templates.get(template_id)
    
    @staticmethod
    def _create_basic_text() -> Dict:
        """Create basic text card template."""
        front = TextFieldComponent("Front")
        front.font_size = 24
        front.width = "350px"
        front.text_align = Alignment.CENTER
        
        back = TextFieldComponent("Back")
        back.font_size = 20
        
        return {
            'name': 'Basic Text Card',
            'front': [front],
            'back': [front, DividerComponent(), back],
            'css': '.card { font-family: Arial; text-align: center; padding: 20px; }'
        }
    
    @staticmethod
    def _create_vocabulary() -> Dict:
        """Create vocabulary card template."""
        word = HeadingComponent("Word", level=1)
        word.text_align = Alignment.CENTER
        
        pronunciation = TextFieldComponent("Pronunciation")
        pronunciation.font_size = 18
        pronunciation.color = "#666"
        pronunciation.text_align = Alignment.CENTER
        
        definition = TextFieldComponent("Definition")
        definition.font_size = 20
        definition.text_align = Alignment.LEFT
        
        example = TextFieldComponent("Example")
        example.font_size = 16
        example.color = "#888"
        example.text_align = Alignment.LEFT
        
        css = '''
.card {
    font-family: Georgia, serif;
    max-width: 500px;
    margin: 0 auto;
    padding: 30px;
}
.pronunciation { font-style: italic; margin-bottom: 20px; }
.example { padding: 10px; background: #f5f5f5; border-left: 3px solid #4CAF50; }
'''
        
        return {
            'name': 'Vocabulary Card',
            'front': [word, pronunciation],
            'back': [word, pronunciation, DividerComponent(), definition, example],
            'css': css
        }
    
    @staticmethod
    def _create_cloze_basic() -> Dict:
        """Create basic cloze deletion template."""
        text = TextFieldComponent("Text")
        text.font_size = 22
        text.text_align = Alignment.LEFT
        
        extra = TextFieldComponent("Extra")
        extra.font_size = 16
        extra.color = "#666"
        
        css = '''
.card {
    font-family: Arial;
    font-size: 20px;
    padding: 30px;
}
.cloze { font-weight: bold; color: #2196F3; }
.extra { margin-top: 20px; font-size: 14px; color: #666; }
'''
        
        return {
            'name': 'Basic Cloze',
            'front': [text],
            'back': [text, DividerComponent(), extra],
            'css': css
        }
    
    @staticmethod
    def _create_image_occlusion() -> Dict:
        """Create image occlusion template."""
        image = ImageFieldComponent("Image")
        
        question = TextFieldComponent("Question")
        question.font_size = 18
        question.text_align = Alignment.CENTER
        
        answer = TextFieldComponent("Answer")
        answer.font_size = 20
        answer.color = "#4CAF50"
        answer.text_align = Alignment.CENTER
        
        css = '''
.card {
    text-align: center;
    padding: 20px;
}
img { max-width: 100%; height: auto; border: 2px solid #ddd; }
.question { margin-top: 20px; font-weight: bold; }
.answer { margin-top: 10px; color: #4CAF50; }
'''
        
        return {
            'name': 'Image Occlusion',
            'front': [image, question],
            'back': [image, question, answer],
            'css': css
        }
    
    @staticmethod
    def _create_formula() -> Dict:
        """Create formula card template."""
        formula = HeadingComponent("Formula", level=2)
        formula.text_align = Alignment.CENTER
        
        variables = TextFieldComponent("Variables")
        variables.font_size = 18
        
        example = TextFieldComponent("Example")
        example.font_size = 18
        
        notes = TextFieldComponent("Notes")
        notes.font_size = 16
        notes.color = "#666"
        
        css = '''
.card {
    font-family: 'Courier New', monospace;
    max-width: 600px;
    margin: 0 auto;
    padding: 30px;
}
.formula { 
    font-size: 28px;
    background: #f0f0f0;
    padding: 20px;
    border-radius: 5px;
}
.variables { margin-top: 20px; line-height: 1.6; }
.example {
    margin-top: 15px;
    padding: 15px;
    background: #e3f2fd;
    border-left: 4px solid #2196F3;
}
'''
        
        return {
            'name': 'Formula Card',
            'front': [formula],
            'back': [formula, DividerComponent(), variables, example, notes],
            'css': css
        }
    
    @staticmethod
    def _create_minimal() -> Dict:
        """Create minimal card template."""
        question = TextFieldComponent("Question")
        question.font_size = 26
        question.text_align = Alignment.CENTER
        
        answer = TextFieldComponent("Answer")
        answer.font_size = 22
        answer.text_align = Alignment.CENTER
        
        css = '''
.card {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: white;
    color: #333;
    padding: 60px 40px;
    line-height: 1.5;
}
'''
        
        return {
            'name': 'Minimal Card',
            'front': [question],
            'back': [answer],
            'css': css
        }
    
    @staticmethod
    def _create_two_column() -> Dict:
        """Create two-column template."""
        left = TextFieldComponent("Left")
        left.width = "180px"
        
        right = TextFieldComponent("Right")
        right.width = "180px"
        
        notes = TextFieldComponent("Notes")
        notes.color = "#666"
        
        css = '''
.card {
    font-family: Arial;
    padding: 30px;
}
.two-column {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}
.column {
    flex: 1;
    padding: 15px;
    background: #f5f5f5;
    border-radius: 5px;
}
'''
        
        return {
            'name': 'Two Column',
            'front': [left, right],
            'back': [left, right, DividerComponent(), notes],
            'css': css
        }
    
    @staticmethod
    def _create_medical_drug() -> Dict:
        """Create medical drug information template."""
        drug = HeadingComponent("Drug", level=1)
        
        drug_class = TextFieldComponent("Class")
        drug_class.font_size = 18
        drug_class.color = "#1976D2"
        
        mechanism = TextFieldComponent("Mechanism")
        mechanism.font_size = 16
        
        indications = TextFieldComponent("Indications")
        indications.font_size = 16
        
        side_effects = TextFieldComponent("Side Effects")
        side_effects.font_size = 16
        side_effects.color = "#D32F2F"
        
        css = '''
.card {
    font-family: Arial;
    max-width: 600px;
    margin: 0 auto;
    padding: 30px;
    line-height: 1.6;
}
.drug-name { color: #1976D2; margin-bottom: 10px; }
.section { margin-bottom: 15px; padding: 10px; background: #f9f9f9; }
.side-effects { color: #D32F2F; }
'''
        
        return {
            'name': 'Drug Information',
            'front': [drug, drug_class],
            'back': [drug, drug_class, DividerComponent(), mechanism, indications, side_effects],
            'css': css
        }
    
    @staticmethod
    def _create_anatomy() -> Dict:
        """Create anatomy card template."""
        structure = HeadingComponent("Structure", level=1)
        
        location = TextFieldComponent("Location")
        location.font_size = 18
        
        function = TextFieldComponent("Function")
        function.font_size = 18
        
        image = ImageFieldComponent("Image")
        
        css = '''
.card {
    font-family: Arial;
    max-width: 600px;
    margin: 0 auto;
    padding: 30px;
}
.structure { color: #D32F2F; }
.location, .function {
    margin-bottom: 15px;
    padding: 10px;
    background: #f5f5f5;
    border-left: 3px solid #2196F3;
}
img { max-width: 100%; height: auto; border: 2px solid #ddd; margin-top: 20px; }
'''
        
        return {
            'name': 'Anatomy Card',
            'front': [structure],
            'back': [structure, DividerComponent(), location, function, image],
            'css': css
        }
    
    @staticmethod
    def _create_language_sentence() -> Dict:
        """Create language sentence practice template."""
        native = TextFieldComponent("Native")
        native.font_size = 22
        native.text_align = Alignment.CENTER
        
        translation = TextFieldComponent("Translation")
        translation.font_size = 20
        translation.color = "#4CAF50"
        translation.text_align = Alignment.CENTER
        
        grammar = TextFieldComponent("Grammar Notes")
        grammar.font_size = 16
        grammar.color = "#666"
        
        css = '''
.card {
    font-family: Arial;
    max-width: 600px;
    margin: 0 auto;
    padding: 40px;
    line-height: 1.8;
}
.native { font-weight: bold; margin-bottom: 30px; }
.translation { color: #4CAF50; margin-bottom: 20px; }
.grammar {
    padding: 15px;
    background: #fff3e0;
    border-left: 4px solid #ff9800;
    font-size: 14px;
}
'''
        
        return {
            'name': 'Sentence Practice',
            'front': [native],
            'back': [native, DividerComponent(), translation, grammar],
            'css': css
        }
