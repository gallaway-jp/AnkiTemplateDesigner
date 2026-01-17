"""
Test Suite for Issue #47: User Onboarding System

Tests for onboarding manager, tutorial engine, guided tour, and template library.
Target: 30+ comprehensive tests covering all onboarding features.
"""

import unittest
from datetime import datetime
from services.onboarding_manager import (
    OnboardingManager,
    TutorialEngine,
    GuidedTourManager,
    TemplateLibraryManager,
    OnboardingProgress,
    OnboardingStatus,
    TutorialStepType,
    TutorialStep,
    TourHighlight,
    StarterTemplate,
    AchievementMilestone
)


class TestTutorialEngine(unittest.TestCase):
    """Test suite for TutorialEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = TutorialEngine()
    
    def test_initialization(self):
        """Test tutorial engine initializes with steps."""
        self.assertEqual(len(self.engine.tutorial_steps), 6)
        self.assertEqual(self.engine.current_step_index, 0)
    
    def test_get_current_step(self):
        """Test getting current step."""
        step = self.engine.get_current_step()
        self.assertIsNotNone(step)
        self.assertEqual(step.step_id, 'step_1')
    
    def test_advance_step(self):
        """Test advancing to next step."""
        initial_step = self.engine.get_current_step()
        advanced = self.engine.advance_step()
        
        self.assertTrue(advanced)
        next_step = self.engine.get_current_step()
        self.assertNotEqual(initial_step.step_id, next_step.step_id)
        self.assertEqual(next_step.step_id, 'step_2')
    
    def test_advance_to_last_step(self):
        """Test advancing through all steps."""
        for _ in range(5):
            self.assertTrue(self.engine.advance_step())
        
        # Try to advance past last step
        advanced = self.engine.advance_step()
        self.assertFalse(advanced)
    
    def test_validate_checkpoint(self):
        """Test checkpoint validation."""
        step = self.engine.get_current_step()
        
        # Validate correct checkpoint
        valid = self.engine.validate_checkpoint('component_placed')
        self.assertTrue(valid)
        self.assertIn('component_placed', self.engine.completed_checkpoints)
        
        # Invalid checkpoint should fail
        valid = self.engine.validate_checkpoint('wrong_checkpoint')
        self.assertFalse(valid)
    
    def test_is_complete(self):
        """Test tutorial completion detection."""
        self.assertFalse(self.engine.is_complete())
        
        # Advance to end
        for _ in range(5):
            self.engine.advance_step()
        
        self.assertTrue(self.engine.is_complete())
    
    def test_reset_tutorial(self):
        """Test resetting tutorial."""
        # Advance and validate
        self.engine.advance_step()
        self.engine.validate_checkpoint('property_changed')
        
        # Reset
        self.engine.reset_tutorial()
        self.assertEqual(self.engine.current_step_index, 0)
        self.assertEqual(len(self.engine.completed_checkpoints), 0)
    
    def test_step_structure(self):
        """Test tutorial step has all required fields."""
        step = self.engine.get_current_step()
        
        self.assertIsNotNone(step.step_id)
        self.assertIsNotNone(step.title)
        self.assertIsNotNone(step.description)
        self.assertIsNotNone(step.step_type)
        self.assertIsNotNone(step.instructions)
        self.assertIsNotNone(step.checkpoint_validation)
    
    def test_step_to_dict(self):
        """Test converting step to dictionary."""
        step = self.engine.get_current_step()
        step_dict = step.to_dict()
        
        self.assertEqual(step_dict['step_id'], step.step_id)
        self.assertEqual(step_dict['title'], step.title)
        self.assertEqual(step_dict['step_type'], step.step_type.value)


class TestGuidedTourManager(unittest.TestCase):
    """Test suite for GuidedTourManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = GuidedTourManager()
    
    def test_initialization(self):
        """Test tour manager initializes with highlights."""
        self.assertEqual(len(self.manager.tour_highlights), 6)
        self.assertFalse(self.manager.tour_active)
    
    def test_start_tour(self):
        """Test starting tour."""
        highlight = self.manager.start_tour()
        
        self.assertTrue(self.manager.tour_active)
        self.assertEqual(self.manager.current_highlight_index, 0)
        self.assertIsNotNone(highlight)
    
    def test_get_current_highlight(self):
        """Test getting current highlight."""
        self.manager.start_tour()
        highlight = self.manager.get_current_highlight()
        
        self.assertIsNotNone(highlight)
        self.assertEqual(highlight.element_id, 'component_library')
    
    def test_next_highlight(self):
        """Test moving to next highlight."""
        self.manager.start_tour()
        first_highlight = self.manager.get_current_highlight()
        
        advanced = self.manager.next_highlight()
        second_highlight = self.manager.get_current_highlight()
        
        self.assertTrue(advanced)
        self.assertNotEqual(first_highlight.element_id, second_highlight.element_id)
    
    def test_advance_through_all_highlights(self):
        """Test advancing through all tour highlights."""
        self.manager.start_tour()
        
        for _ in range(5):
            self.assertTrue(self.manager.next_highlight())
        
        # Try to advance past last highlight
        advanced = self.manager.next_highlight()
        self.assertFalse(advanced)
    
    def test_end_tour(self):
        """Test ending tour."""
        self.manager.start_tour()
        self.manager.next_highlight()
        
        self.manager.end_tour()
        
        self.assertFalse(self.manager.tour_active)
        self.assertEqual(self.manager.current_highlight_index, 0)
    
    def test_highlight_to_dict(self):
        """Test converting highlight to dictionary."""
        self.manager.start_tour()
        highlight = self.manager.get_current_highlight()
        highlight_dict = highlight.to_dict()
        
        self.assertEqual(highlight_dict['element_id'], highlight.element_id)
        self.assertEqual(highlight_dict['title'], highlight.title)
        self.assertEqual(highlight_dict['position'], highlight.position)


class TestTemplateLibraryManager(unittest.TestCase):
    """Test suite for TemplateLibraryManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.library = TemplateLibraryManager()
    
    def test_initialization(self):
        """Test library initializes with templates."""
        self.assertEqual(len(self.library.templates), 8)
    
    def test_get_all_templates(self):
        """Test getting all templates."""
        templates = self.library.get_all_templates()
        
        self.assertEqual(len(templates), 8)
        self.assertIsInstance(templates[0], StarterTemplate)
    
    def test_get_template_by_id(self):
        """Test getting template by ID."""
        template = self.library.get_template('simple_card')
        
        self.assertIsNotNone(template)
        self.assertEqual(template.template_id, 'simple_card')
        self.assertEqual(template.name, 'Simple Front/Back Card')
    
    def test_get_template_by_id_not_found(self):
        """Test getting non-existent template."""
        template = self.library.get_template('nonexistent')
        self.assertIsNone(template)
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        card_templates = self.library.get_templates_by_category('cards')
        
        self.assertGreater(len(card_templates), 0)
        for template in card_templates:
            self.assertEqual(template.category, 'cards')
    
    def test_get_templates_by_difficulty(self):
        """Test getting templates by difficulty."""
        beginner_templates = self.library.get_templates_by_difficulty('beginner')
        
        self.assertGreater(len(beginner_templates), 0)
        for template in beginner_templates:
            self.assertEqual(template.difficulty, 'beginner')
    
    def test_template_structure(self):
        """Test template has all required fields."""
        template = self.library.templates[0]
        
        self.assertIsNotNone(template.template_id)
        self.assertIsNotNone(template.name)
        self.assertIsNotNone(template.category)
        self.assertIsNotNone(template.html_content)
        self.assertIsNotNone(template.css_content)
        self.assertGreater(len(template.expected_fields), 0)
    
    def test_template_to_dict(self):
        """Test converting template to dictionary."""
        template = self.library.templates[0]
        template_dict = template.to_dict()
        
        self.assertEqual(template_dict['template_id'], template.template_id)
        self.assertEqual(template_dict['name'], template.name)
        self.assertEqual(template_dict['difficulty'], template.difficulty)


class TestOnboardingManager(unittest.TestCase):
    """Test suite for OnboardingManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = OnboardingManager()
        self.user_id = 'test_user'
    
    def test_initialization(self):
        """Test manager initializes correctly."""
        self.assertIsNotNone(self.manager.tutorial_engine)
        self.assertIsNotNone(self.manager.guided_tour_manager)
        self.assertIsNotNone(self.manager.template_library)
        self.assertEqual(len(self.manager.milestones), 5)
    
    def test_start_onboarding(self):
        """Test starting onboarding for new user."""
        progress = self.manager.start_onboarding(self.user_id)
        
        self.assertEqual(progress.user_id, self.user_id)
        self.assertEqual(progress.status, OnboardingStatus.NOT_STARTED)
        self.assertIsNotNone(progress.started_at)
        self.assertIn(self.user_id, self.manager.progress_tracking)
    
    def test_get_progress(self):
        """Test retrieving user progress."""
        self.manager.start_onboarding(self.user_id)
        progress = self.manager.get_progress(self.user_id)
        
        self.assertIsNotNone(progress)
        self.assertEqual(progress.user_id, self.user_id)
    
    def test_get_progress_nonexistent_user(self):
        """Test getting progress for non-existent user."""
        progress = self.manager.get_progress('nonexistent_user')
        self.assertIsNone(progress)
    
    def test_start_tutorial(self):
        """Test starting tutorial."""
        success, step = self.manager.start_tutorial(self.user_id)
        
        self.assertTrue(success)
        self.assertIsNotNone(step)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(progress.status, OnboardingStatus.IN_PROGRESS)
    
    def test_advance_tutorial(self):
        """Test advancing through tutorial."""
        self.manager.start_tutorial(self.user_id)
        
        success, step = self.manager.advance_tutorial(self.user_id)
        
        self.assertTrue(success)
        self.assertIsNotNone(step)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(len(progress.completed_steps), 1)
    
    def test_complete_tutorial(self):
        """Test completing full tutorial."""
        self.manager.start_tutorial(self.user_id)
        
        # Advance through all steps
        for _ in range(6):
            self.manager.advance_tutorial(self.user_id)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(progress.status, OnboardingStatus.TUTORIAL_COMPLETE)
    
    def test_validate_step_checkpoint(self):
        """Test validating step checkpoints."""
        self.manager.start_tutorial(self.user_id)
        
        valid = self.manager.validate_step_checkpoint(self.user_id, 'component_placed')
        self.assertTrue(valid)
    
    def test_skip_tutorial(self):
        """Test skipping tutorial."""
        success = self.manager.skip_tutorial(self.user_id)
        
        self.assertTrue(success)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(progress.status, OnboardingStatus.TUTORIAL_COMPLETE)
    
    def test_replay_tutorial(self):
        """Test replaying tutorial."""
        self.manager.start_tutorial(self.user_id)
        self.manager.advance_tutorial(self.user_id)
        
        success, step = self.manager.replay_tutorial(self.user_id)
        
        self.assertTrue(success)
        self.assertEqual(step.step_id, 'step_1')
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(len(progress.completed_steps), 0)
    
    def test_start_guided_tour(self):
        """Test starting guided tour."""
        highlight = self.manager.start_guided_tour(self.user_id)
        
        self.assertIsNotNone(highlight)
        self.assertTrue(self.manager.guided_tour_manager.tour_active)
    
    def test_next_tour_highlight(self):
        """Test moving through tour highlights."""
        self.manager.start_guided_tour(self.user_id)
        
        advanced, highlight = self.manager.next_tour_highlight(self.user_id)
        
        self.assertTrue(advanced)
        self.assertIsNotNone(highlight)
    
    def test_complete_guided_tour(self):
        """Test completing guided tour."""
        self.manager.start_guided_tour(self.user_id)
        
        # Advance through all highlights
        for _ in range(6):
            self.manager.next_tour_highlight(self.user_id)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertTrue(progress.tour_completed)
    
    def test_end_guided_tour(self):
        """Test ending guided tour."""
        self.manager.start_guided_tour(self.user_id)
        
        success = self.manager.end_guided_tour(self.user_id)
        
        self.assertTrue(success)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertTrue(progress.tour_completed)
    
    def test_view_template(self):
        """Test viewing template."""
        template = self.manager.view_template(self.user_id, 'simple_card')
        
        self.assertIsNotNone(template)
        self.assertEqual(template.template_id, 'simple_card')
        
        progress = self.manager.get_progress(self.user_id)
        self.assertIn('simple_card', progress.templates_viewed)
    
    def test_view_multiple_templates(self):
        """Test viewing multiple templates."""
        self.manager.view_template(self.user_id, 'simple_card')
        self.manager.view_template(self.user_id, 'cloze_deletion')
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(len(progress.templates_viewed), 2)
    
    def test_load_template(self):
        """Test loading template for editing."""
        success, template = self.manager.load_template(self.user_id, 'simple_card')
        
        self.assertTrue(success)
        self.assertIsNotNone(template)
        self.assertEqual(template.template_id, 'simple_card')
    
    def test_load_nonexistent_template(self):
        """Test loading non-existent template."""
        success, template = self.manager.load_template(self.user_id, 'nonexistent')
        
        self.assertFalse(success)
        self.assertIsNone(template)
    
    def test_mark_first_template_created(self):
        """Test marking first template creation."""
        self.manager.start_onboarding(self.user_id)
        success = self.manager.mark_first_template_created(self.user_id)
        
        self.assertTrue(success)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertTrue(progress.first_template_created)
    
    def test_fully_onboarded_status(self):
        """Test reaching fully onboarded status."""
        self.manager.start_onboarding(self.user_id)
        self.manager.end_guided_tour(self.user_id)
        self.manager.mark_first_template_created(self.user_id)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(progress.status, OnboardingStatus.FULLY_ONBOARDED)
    
    def test_get_milestones(self):
        """Test getting all milestones."""
        milestones = self.manager.get_milestones()
        
        self.assertEqual(len(milestones), 5)
        self.assertIsInstance(milestones[0], AchievementMilestone)
    
    def test_get_milestone_by_id(self):
        """Test getting milestone by ID."""
        milestone = self.manager.get_milestone('first_component')
        
        self.assertIsNotNone(milestone)
        self.assertEqual(milestone.milestone_id, 'first_component')
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        templates = self.manager.get_templates_by_category('cards')
        
        self.assertGreater(len(templates), 0)
        for template in templates:
            self.assertEqual(template.category, 'cards')
    
    def test_get_all_templates(self):
        """Test getting all templates."""
        templates = self.manager.get_all_templates()
        
        self.assertEqual(len(templates), 8)
    
    def test_get_progress_summary(self):
        """Test getting progress summary."""
        self.manager.start_tutorial(self.user_id)
        self.manager.advance_tutorial(self.user_id)
        
        summary = self.manager.get_progress_summary(self.user_id)
        
        self.assertEqual(summary['user_id'], self.user_id)
        self.assertIn('tutorial_progress', summary)
        self.assertIn('status', summary)
    
    def test_export_progress(self):
        """Test exporting progress."""
        self.manager.start_onboarding(self.user_id)
        self.manager.view_template(self.user_id, 'simple_card')
        
        progress_data = self.manager.export_progress(self.user_id)
        
        self.assertIsNotNone(progress_data)
        self.assertEqual(progress_data['user_id'], self.user_id)
        self.assertIn('simple_card', progress_data['templates_viewed'])
    
    def test_import_progress(self):
        """Test importing progress."""
        original_data = {
            'user_id': self.user_id,
            'status': 'in_progress',
            'completed_steps': ['step_1', 'step_2'],
            'current_step': 'step_3',
            'tour_completed': False,
            'templates_viewed': ['simple_card'],
            'first_template_created': False
        }
        
        success = self.manager.import_progress(self.user_id, original_data)
        
        self.assertTrue(success)
        
        progress = self.manager.get_progress(self.user_id)
        self.assertEqual(len(progress.completed_steps), 2)
        self.assertIn('simple_card', progress.templates_viewed)
    
    def test_milestone_to_dict(self):
        """Test converting milestone to dictionary."""
        milestone = self.manager.get_milestone('first_component')
        milestone_dict = milestone.to_dict()
        
        self.assertEqual(milestone_dict['milestone_id'], milestone.milestone_id)
        self.assertEqual(milestone_dict['name'], milestone.name)


class TestOnboardingDataClasses(unittest.TestCase):
    """Test suite for onboarding data classes."""
    
    def test_onboarding_progress_to_dict(self):
        """Test OnboardingProgress to_dict."""
        progress = OnboardingProgress(
            user_id='test_user',
            status=OnboardingStatus.IN_PROGRESS,
            completed_steps=['step_1'],
            started_at=datetime.now()
        )
        
        data = progress.to_dict()
        
        self.assertEqual(data['user_id'], 'test_user')
        self.assertEqual(data['status'], 'in_progress')
        self.assertEqual(len(data['completed_steps']), 1)
    
    def test_tutorial_step_to_dict(self):
        """Test TutorialStep to_dict."""
        step = TutorialStep(
            step_id='test_step',
            title='Test Step',
            description='Test description',
            step_type=TutorialStepType.COMPONENT_PLACEMENT,
            target_element='test_element',
            instructions='Test instructions',
            checkpoint_validation='test_checkpoint'
        )
        
        data = step.to_dict()
        
        self.assertEqual(data['step_id'], 'test_step')
        self.assertEqual(data['step_type'], 'component_placement')
    
    def test_tour_highlight_to_dict(self):
        """Test TourHighlight to_dict."""
        highlight = TourHighlight(
            element_id='test_element',
            title='Test',
            description='Test description',
            position='top'
        )
        
        data = highlight.to_dict()
        
        self.assertEqual(data['element_id'], 'test_element')
        self.assertEqual(data['position'], 'top')


if __name__ == '__main__':
    unittest.main()
