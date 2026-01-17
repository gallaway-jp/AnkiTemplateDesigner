"""
Issue #47: User Onboarding System

Comprehensive onboarding flow for new users to rapidly learn the application.
Features: Interactive tutorial, guided tour, templates library, progress tracking.

Architecture:
- OnboardingManager: Main orchestrator for onboarding flow
- TutorialStep: Individual tutorial step data model
- OnboardingProgress: User progress tracking
- TemplateLibrary: Pre-built starter templates
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json


class TutorialStepType(Enum):
    """Types of tutorial steps."""
    COMPONENT_PLACEMENT = "component_placement"
    PROPERTY_EDITING = "property_editing"
    PREVIEW_TESTING = "preview_testing"
    STYLING = "styling"
    TEMPLATE_SAVE = "template_save"
    EXPORT = "export"


class OnboardingStatus(Enum):
    """Onboarding completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TUTORIAL_COMPLETE = "tutorial_complete"
    FULLY_ONBOARDED = "fully_onboarded"


@dataclass
class TutorialStep:
    """Individual tutorial step."""
    step_id: str
    title: str
    description: str
    step_type: TutorialStepType
    target_element: str
    instructions: str
    checkpoint_validation: Optional[str]
    hint: Optional[str] = None
    video_url: Optional[str] = None
    duration_seconds: int = 60
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'step_id': self.step_id,
            'title': self.title,
            'description': self.description,
            'step_type': self.step_type.value,
            'target_element': self.target_element,
            'instructions': self.instructions,
            'checkpoint_validation': self.checkpoint_validation,
            'hint': self.hint,
            'video_url': self.video_url,
            'duration_seconds': self.duration_seconds
        }


@dataclass
class TourHighlight:
    """UI element highlight for guided tour."""
    element_id: str
    title: str
    description: str
    position: str  # 'top', 'bottom', 'left', 'right'
    action: Optional[str] = None  # Optional action to perform
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'element_id': self.element_id,
            'title': self.title,
            'description': self.description,
            'position': self.position,
            'action': self.action
        }


@dataclass
class StarterTemplate:
    """Pre-built starter template."""
    template_id: str
    name: str
    category: str  # 'cards', 'fields', 'styling'
    description: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    html_content: str
    css_content: str
    expected_fields: List[str]
    thumbnail_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'difficulty': self.difficulty,
            'html_content': self.html_content,
            'css_content': self.css_content,
            'expected_fields': self.expected_fields,
            'thumbnail_url': self.thumbnail_url
        }


@dataclass
class OnboardingProgress:
    """User onboarding progress tracking."""
    user_id: str
    status: OnboardingStatus
    completed_steps: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    tour_completed: bool = False
    templates_viewed: List[str] = field(default_factory=list)
    first_template_created: bool = False
    started_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    total_time_seconds: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'status': self.status.value,
            'completed_steps': self.completed_steps,
            'current_step': self.current_step,
            'tour_completed': self.tour_completed,
            'templates_viewed': self.templates_viewed,
            'first_template_created': self.first_template_created,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'total_time_seconds': self.total_time_seconds
        }


@dataclass
class AchievementMilestone:
    """Achievement milestone for motivation."""
    milestone_id: str
    name: str
    description: str
    trigger_condition: str
    icon: str
    reward_description: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'milestone_id': self.milestone_id,
            'name': self.name,
            'description': self.description,
            'trigger_condition': self.trigger_condition,
            'icon': self.icon,
            'reward_description': self.reward_description
        }


class TutorialEngine:
    """Manages tutorial progression and validation."""
    
    def __init__(self):
        """Initialize tutorial engine."""
        self.tutorial_steps = self._initialize_tutorial_steps()
        self.current_step_index = 0
        self.completed_checkpoints = []
    
    def _initialize_tutorial_steps(self) -> List[TutorialStep]:
        """Initialize default tutorial steps."""
        return [
            TutorialStep(
                step_id='step_1',
                title='Welcome to Template Designer',
                description='Learn the basics of creating Anki templates',
                step_type=TutorialStepType.COMPONENT_PLACEMENT,
                target_element='canvas_area',
                instructions='Create your first template by dragging components onto the canvas',
                checkpoint_validation='component_placed',
                hint='Start by adding a simple text field'
            ),
            TutorialStep(
                step_id='step_2',
                title='Edit Component Properties',
                description='Customize component behavior and appearance',
                step_type=TutorialStepType.PROPERTY_EDITING,
                target_element='properties_panel',
                instructions='Click a component to select it, then modify its properties in the panel on the right',
                checkpoint_validation='property_changed'
            ),
            TutorialStep(
                step_id='step_3',
                title='Preview Your Template',
                description='See how your template looks in action',
                step_type=TutorialStepType.PREVIEW_TESTING,
                target_element='preview_panel',
                instructions='Use the preview panel to test your template with sample data',
                checkpoint_validation='preview_opened'
            ),
            TutorialStep(
                step_id='step_4',
                title='Apply Custom Styling',
                description='Make your template unique with custom CSS',
                step_type=TutorialStepType.STYLING,
                target_element='style_editor',
                instructions='Add custom CSS to style your template components',
                checkpoint_validation='style_added'
            ),
            TutorialStep(
                step_id='step_5',
                title='Save Your Template',
                description='Save your template for future use',
                step_type=TutorialStepType.TEMPLATE_SAVE,
                target_element='save_button',
                instructions='Click the Save button to store your template',
                checkpoint_validation='template_saved'
            ),
            TutorialStep(
                step_id='step_6',
                title='Export and Share',
                description='Export your template to use in Anki',
                step_type=TutorialStepType.EXPORT,
                target_element='export_button',
                instructions='Export your template and import it into Anki',
                checkpoint_validation='template_exported'
            )
        ]
    
    def get_current_step(self) -> Optional[TutorialStep]:
        """Get current tutorial step."""
        if self.current_step_index < len(self.tutorial_steps):
            return self.tutorial_steps[self.current_step_index]
        return None
    
    def advance_step(self) -> bool:
        """Advance to next step."""
        if self.current_step_index < len(self.tutorial_steps) - 1:
            self.current_step_index += 1
            return True
        return False
    
    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """Validate that a checkpoint was reached."""
        step = self.get_current_step()
        if step and step.checkpoint_validation == checkpoint_id:
            self.completed_checkpoints.append(checkpoint_id)
            return True
        return False
    
    def is_complete(self) -> bool:
        """Check if tutorial is complete."""
        return self.current_step_index >= len(self.tutorial_steps) - 1
    
    def reset_tutorial(self) -> None:
        """Reset tutorial to beginning."""
        self.current_step_index = 0
        self.completed_checkpoints = []


class GuidedTourManager:
    """Manages the guided tour of UI elements."""
    
    def __init__(self):
        """Initialize guided tour manager."""
        self.tour_highlights = self._initialize_tour_highlights()
        self.current_highlight_index = 0
        self.tour_active = False
    
    def _initialize_tour_highlights(self) -> List[TourHighlight]:
        """Initialize tour highlights for key UI elements."""
        return [
            TourHighlight(
                element_id='component_library',
                title='Component Library',
                description='Drag and drop components from here to create your template',
                position='right'
            ),
            TourHighlight(
                element_id='canvas_area',
                title='Design Canvas',
                description='This is where you build your template layout',
                position='center'
            ),
            TourHighlight(
                element_id='properties_panel',
                title='Properties Panel',
                description='Configure the selected component here',
                position='left'
            ),
            TourHighlight(
                element_id='preview_panel',
                title='Live Preview',
                description='See real-time changes as you edit',
                position='left'
            ),
            TourHighlight(
                element_id='style_editor',
                title='Style Editor',
                description='Add custom CSS to style your components',
                position='right'
            ),
            TourHighlight(
                element_id='device_simulator',
                title='Device Testing',
                description='Test your template on different devices',
                position='bottom'
            )
        ]
    
    def start_tour(self) -> TourHighlight:
        """Start the guided tour."""
        self.tour_active = True
        self.current_highlight_index = 0
        return self.get_current_highlight()
    
    def get_current_highlight(self) -> Optional[TourHighlight]:
        """Get current tour highlight."""
        if self.current_highlight_index < len(self.tour_highlights):
            return self.tour_highlights[self.current_highlight_index]
        return None
    
    def next_highlight(self) -> bool:
        """Move to next highlight."""
        if self.current_highlight_index < len(self.tour_highlights) - 1:
            self.current_highlight_index += 1
            return True
        return False
    
    def end_tour(self) -> None:
        """End the guided tour."""
        self.tour_active = False
        self.current_highlight_index = 0


class TemplateLibraryManager:
    """Manages the starter templates library."""
    
    def __init__(self):
        """Initialize template library manager."""
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[StarterTemplate]:
        """Initialize pre-built starter templates."""
        return [
            StarterTemplate(
                template_id='simple_card',
                name='Simple Front/Back Card',
                category='cards',
                description='Classic front-back card template for basic memorization',
                difficulty='beginner',
                html_content='<div class="card">\n  <div class="front">{{Front}}</div>\n  <div class="back">{{Back}}</div>\n</div>',
                css_content='.card { background: white; padding: 20px; }\n.front { font-size: 24px; margin-bottom: 20px; }\n.back { color: #666; }',
                expected_fields=['Front', 'Back']
            ),
            StarterTemplate(
                template_id='multi_field_card',
                name='Multi-Field Card',
                category='cards',
                description='Template with multiple fields for complex information',
                difficulty='beginner',
                html_content='<div class="card">\n  <div class="title">{{Title}}</div>\n  <div class="content">{{Content}}</div>\n  <div class="extra">{{Extra}}</div>\n</div>',
                css_content='.card { padding: 20px; }\n.title { font-weight: bold; font-size: 18px; }\n.content { margin: 15px 0; }\n.extra { color: #999; font-size: 12px; }',
                expected_fields=['Title', 'Content', 'Extra']
            ),
            StarterTemplate(
                template_id='cloze_deletion',
                name='Cloze Deletion',
                category='cards',
                description='Template for cloze deletion type cards',
                difficulty='intermediate',
                html_content='<div class="card">\n  <div class="question">{{cloze:Text}}</div>\n  <div class="extra">{{Extra}}</div>\n</div>',
                css_content='.card { padding: 20px; }\n.cloze { color: blue; font-weight: bold; }\n.question { font-size: 20px; margin: 20px 0; }\n.extra { margin-top: 20px; color: #666; }',
                expected_fields=['Text', 'Extra']
            ),
            StarterTemplate(
                template_id='image_based',
                name='Image-Based Card',
                category='cards',
                description='Template for image-focused cards with labels',
                difficulty='intermediate',
                html_content='<div class="card">\n  <div class="image-container">{{Image}}</div>\n  <div class="labels">{{Labels}}</div>\n</div>',
                css_content='.card { padding: 20px; text-align: center; }\n.image-container { margin: 20px 0; }\nimg { max-width: 300px; max-height: 300px; }\n.labels { margin-top: 20px; color: #333; }',
                expected_fields=['Image', 'Labels']
            ),
            StarterTemplate(
                template_id='minimal_styling',
                name='Minimal Dark Theme',
                category='styling',
                description='Clean dark theme for comfortable study',
                difficulty='beginner',
                html_content='<div class="card">{{Front}}</div>',
                css_content=':root { --bg-color: #1e1e1e; --text-color: #ffffff; }\n.card { background: var(--bg-color); color: var(--text-color); padding: 20px; font-size: 24px; }',
                expected_fields=['Front']
            ),
            StarterTemplate(
                template_id='modern_card',
                name='Modern Card Design',
                category='styling',
                description='Contemporary card design with smooth animations',
                difficulty='advanced',
                html_content='<div class="card">\n  <div class="header">{{Title}}</div>\n  <div class="body">{{Content}}</div>\n  <div class="footer">{{Source}}</div>\n</div>',
                css_content='.card { border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease; }\n.header { padding: 15px; border-bottom: 2px solid #007bff; }\n.body { padding: 20px; }\n.footer { padding: 10px; background: #f8f9fa; }',
                expected_fields=['Title', 'Content', 'Source']
            ),
            StarterTemplate(
                template_id='bilingual_card',
                name='Bilingual Card',
                category='cards',
                description='Perfect for language learning with two languages',
                difficulty='intermediate',
                html_content='<div class="card">\n  <div class="language-1">{{Language1}}</div>\n  <div class="divider"></div>\n  <div class="language-2">{{Language2}}</div>\n</div>',
                css_content='.card { padding: 20px; }\n.language-1 { font-size: 22px; margin-bottom: 20px; }\n.divider { height: 1px; background: #ccc; margin: 20px 0; }\n.language-2 { font-size: 18px; color: #666; }',
                expected_fields=['Language1', 'Language2']
            ),
            StarterTemplate(
                template_id='quiz_card',
                name='Quiz with Multiple Choices',
                category='cards',
                description='Template for quiz-style cards with answer choices',
                difficulty='advanced',
                html_content='<div class="card">\n  <div class="question">{{Question}}</div>\n  <div class="choices">{{Choice1}}<br>{{Choice2}}<br>{{Choice3}}</div>\n  <div class="answer">{{Answer}}</div>\n</div>',
                css_content='.card { padding: 20px; }\n.question { font-weight: bold; margin-bottom: 20px; }\n.choices { background: #f5f5f5; padding: 15px; margin: 20px 0; }\n.answer { color: green; font-weight: bold; margin-top: 20px; }',
                expected_fields=['Question', 'Choice1', 'Choice2', 'Choice3', 'Answer']
            )
        ]
    
    def get_all_templates(self) -> List[StarterTemplate]:
        """Get all available templates."""
        return self.templates
    
    def get_templates_by_category(self, category: str) -> List[StarterTemplate]:
        """Get templates by category."""
        return [t for t in self.templates if t.category == category]
    
    def get_templates_by_difficulty(self, difficulty: str) -> List[StarterTemplate]:
        """Get templates by difficulty level."""
        return [t for t in self.templates if t.difficulty == difficulty]
    
    def get_template(self, template_id: str) -> Optional[StarterTemplate]:
        """Get template by ID."""
        for template in self.templates:
            if template.template_id == template_id:
                return template
        return None


class OnboardingManager:
    """Main orchestrator for user onboarding system."""
    
    def __init__(self):
        """Initialize onboarding manager."""
        self.progress_tracking = {}
        self.tutorial_engine = TutorialEngine()
        self.guided_tour_manager = GuidedTourManager()
        self.template_library = TemplateLibraryManager()
        self.milestones = self._initialize_milestones()
    
    def _initialize_milestones(self) -> List[AchievementMilestone]:
        """Initialize achievement milestones."""
        return [
            AchievementMilestone(
                milestone_id='first_component',
                name='Component Master',
                description='Place your first component on the canvas',
                trigger_condition='component_placed',
                icon='⭐',
                reward_description='Great start! You\'re on your way to building templates.'
            ),
            AchievementMilestone(
                milestone_id='first_template',
                name='Template Creator',
                description='Create and save your first template',
                trigger_condition='template_saved',
                icon='🎨',
                reward_description='Awesome! You created your first template.'
            ),
            AchievementMilestone(
                milestone_id='styling_expert',
                name='Styling Expert',
                description='Add custom CSS to your template',
                trigger_condition='style_added',
                icon='🎭',
                reward_description='Beautiful styling! You\'re becoming a pro.'
            ),
            AchievementMilestone(
                milestone_id='preview_master',
                name='Preview Master',
                description='Test your template in preview mode',
                trigger_condition='preview_opened',
                icon='👁️',
                reward_description='Perfect! Preview testing ensures quality templates.'
            ),
            AchievementMilestone(
                milestone_id='export_expert',
                name='Export Expert',
                description='Export your template for Anki use',
                trigger_condition='template_exported',
                icon='📦',
                reward_description='Done! Your template is ready to use in Anki.'
            )
        ]
    
    def start_onboarding(self, user_id: str) -> OnboardingProgress:
        """Start onboarding for a new user."""
        progress = OnboardingProgress(
            user_id=user_id,
            status=OnboardingStatus.NOT_STARTED,
            started_at=datetime.now(),
            last_updated=datetime.now()
        )
        self.progress_tracking[user_id] = progress
        return progress
    
    def get_progress(self, user_id: str) -> Optional[OnboardingProgress]:
        """Get user's onboarding progress."""
        return self.progress_tracking.get(user_id)
    
    def start_tutorial(self, user_id: str) -> Tuple[bool, Optional[TutorialStep]]:
        """Start the interactive tutorial."""
        progress = self.get_progress(user_id)
        if not progress:
            progress = self.start_onboarding(user_id)
        
        progress.status = OnboardingStatus.IN_PROGRESS
        progress.current_step = self.tutorial_engine.get_current_step().step_id
        progress.last_updated = datetime.now()
        
        return True, self.tutorial_engine.get_current_step()
    
    def advance_tutorial(self, user_id: str) -> Tuple[bool, Optional[TutorialStep]]:
        """Advance to next tutorial step."""
        progress = self.get_progress(user_id)
        if not progress:
            return False, None
        
        current_step = self.tutorial_engine.get_current_step()
        if current_step:
            progress.completed_steps.append(current_step.step_id)
        
        advanced = self.tutorial_engine.advance_step()
        next_step = self.tutorial_engine.get_current_step()
        
        if next_step:
            progress.current_step = next_step.step_id
        
        if self.tutorial_engine.is_complete():
            progress.status = OnboardingStatus.TUTORIAL_COMPLETE
        
        progress.last_updated = datetime.now()
        return advanced, next_step
    
    def validate_step_checkpoint(self, user_id: str, checkpoint_id: str) -> bool:
        """Validate that user completed a step checkpoint."""
        progress = self.get_progress(user_id)
        if not progress:
            return False
        
        valid = self.tutorial_engine.validate_checkpoint(checkpoint_id)
        if valid:
            progress.last_updated = datetime.now()
        
        return valid
    
    def start_guided_tour(self, user_id: str) -> TourHighlight:
        """Start the guided tour of UI elements."""
        progress = self.get_progress(user_id)
        if not progress:
            progress = self.start_onboarding(user_id)
        
        highlight = self.guided_tour_manager.start_tour()
        progress.last_updated = datetime.now()
        
        return highlight
    
    def next_tour_highlight(self, user_id: str) -> Tuple[bool, Optional[TourHighlight]]:
        """Move to next tour highlight."""
        progress = self.get_progress(user_id)
        if not progress:
            return False, None
        
        advanced = self.guided_tour_manager.next_highlight()
        highlight = self.guided_tour_manager.get_current_highlight()
        
        if not advanced:
            progress.tour_completed = True
        
        progress.last_updated = datetime.now()
        return advanced, highlight
    
    def end_guided_tour(self, user_id: str) -> bool:
        """End the guided tour."""
        progress = self.get_progress(user_id)
        if not progress:
            return False
        
        self.guided_tour_manager.end_tour()
        progress.tour_completed = True
        progress.last_updated = datetime.now()
        
        return True
    
    def view_template(self, user_id: str, template_id: str) -> Optional[StarterTemplate]:
        """View a starter template."""
        progress = self.get_progress(user_id)
        if not progress:
            progress = self.start_onboarding(user_id)
        
        template = self.template_library.get_template(template_id)
        if template and template_id not in progress.templates_viewed:
            progress.templates_viewed.append(template_id)
        
        progress.last_updated = datetime.now()
        return template
    
    def load_template(self, user_id: str, template_id: str) -> Tuple[bool, Optional[StarterTemplate]]:
        """Load a starter template for editing."""
        template = self.template_library.get_template(template_id)
        if not template:
            return False, None
        
        progress = self.get_progress(user_id)
        if not progress:
            progress = self.start_onboarding(user_id)
        
        progress.last_updated = datetime.now()
        return True, template
    
    def mark_first_template_created(self, user_id: str) -> bool:
        """Mark that user created their first template."""
        progress = self.get_progress(user_id)
        if not progress:
            return False
        
        progress.first_template_created = True
        progress.last_updated = datetime.now()
        
        # Check if fully onboarded
        if progress.tour_completed and progress.first_template_created:
            progress.status = OnboardingStatus.FULLY_ONBOARDED
        
        return True
    
    def get_milestones(self) -> List[AchievementMilestone]:
        """Get all achievement milestones."""
        return self.milestones
    
    def get_milestone(self, milestone_id: str) -> Optional[AchievementMilestone]:
        """Get milestone by ID."""
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                return milestone
        return None
    
    def get_templates_by_category(self, category: str) -> List[StarterTemplate]:
        """Get starter templates by category."""
        return self.template_library.get_templates_by_category(category)
    
    def get_all_templates(self) -> List[StarterTemplate]:
        """Get all starter templates."""
        return self.template_library.get_all_templates()
    
    def skip_tutorial(self, user_id: str) -> bool:
        """Skip the tutorial."""
        progress = self.get_progress(user_id)
        if not progress:
            progress = self.start_onboarding(user_id)
        
        self.tutorial_engine.reset_tutorial()
        progress.status = OnboardingStatus.TUTORIAL_COMPLETE
        progress.last_updated = datetime.now()
        
        return True
    
    def replay_tutorial(self, user_id: str) -> Tuple[bool, Optional[TutorialStep]]:
        """Replay the tutorial from the beginning."""
        progress = self.get_progress(user_id)
        if not progress:
            progress = self.start_onboarding(user_id)
        
        self.tutorial_engine.reset_tutorial()
        progress.status = OnboardingStatus.IN_PROGRESS
        progress.completed_steps = []
        progress.current_step = self.tutorial_engine.get_current_step().step_id
        progress.last_updated = datetime.now()
        
        return True, self.tutorial_engine.get_current_step()
    
    def get_progress_summary(self, user_id: str) -> Dict:
        """Get summary of user's onboarding progress."""
        progress = self.get_progress(user_id)
        if not progress:
            return {}
        
        return {
            'user_id': user_id,
            'status': progress.status.value,
            'tutorial_progress': f"{len(progress.completed_steps)}/6",
            'tour_completed': progress.tour_completed,
            'first_template_created': progress.first_template_created,
            'templates_viewed': len(progress.templates_viewed),
            'started_at': progress.started_at.isoformat() if progress.started_at else None,
            'is_fully_onboarded': progress.status == OnboardingStatus.FULLY_ONBOARDED
        }
    
    def export_progress(self, user_id: str) -> Optional[Dict]:
        """Export user's onboarding progress as JSON."""
        progress = self.get_progress(user_id)
        if not progress:
            return None
        
        return progress.to_dict()
    
    def import_progress(self, user_id: str, progress_data: Dict) -> bool:
        """Import user's onboarding progress from JSON."""
        try:
            progress = OnboardingProgress(
                user_id=user_id,
                status=OnboardingStatus(progress_data['status']),
                completed_steps=progress_data.get('completed_steps', []),
                current_step=progress_data.get('current_step'),
                tour_completed=progress_data.get('tour_completed', False),
                templates_viewed=progress_data.get('templates_viewed', []),
                first_template_created=progress_data.get('first_template_created', False)
            )
            self.progress_tracking[user_id] = progress
            return True
        except (KeyError, ValueError):
            return False
