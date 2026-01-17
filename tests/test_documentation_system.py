"""
Test Suite for Issue #48: Documentation System

Tests for documentation manager, articles, tooltips, context menu, search engine.
Target: 25+ comprehensive tests covering all documentation features.
"""

import unittest
from services.documentation_system import (
    DocumentationSystem,
    HelpArticle,
    Tooltip,
    ContextMenuAction,
    TooltipManager,
    ContextMenuManager,
    DocumentationBrowser,
    SearchEngine,
    ArticleCategory,
    TooltipTrigger,
    SearchResult
)


class TestHelpArticle(unittest.TestCase):
    """Test suite for HelpArticle data class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.article = HelpArticle(
            article_id='test_article',
            title='Test Article',
            category=ArticleCategory.GETTING_STARTED,
            content='Test content here',
            short_description='Test description',
            keywords=['test', 'article']
        )
    
    def test_article_creation(self):
        """Test creating help article."""
        self.assertEqual(self.article.article_id, 'test_article')
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.category, ArticleCategory.GETTING_STARTED)
    
    def test_article_view_count(self):
        """Test view count tracking."""
        self.assertEqual(self.article.view_count, 0)
        self.article.view_count += 1
        self.assertEqual(self.article.view_count, 1)
    
    def test_article_helpful_votes(self):
        """Test helpful votes tracking."""
        self.assertEqual(self.article.helpful_votes, 0)
        self.article.helpful_votes += 1
        self.assertEqual(self.article.helpful_votes, 1)
    
    def test_article_to_dict(self):
        """Test converting article to dictionary."""
        article_dict = self.article.to_dict()
        
        self.assertEqual(article_dict['article_id'], 'test_article')
        self.assertEqual(article_dict['title'], 'Test Article')
        self.assertEqual(article_dict['category'], 'getting_started')
        self.assertIsInstance(article_dict['keywords'], list)


class TestTooltip(unittest.TestCase):
    """Test suite for Tooltip."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tooltip = Tooltip(
            tooltip_id='test_tooltip',
            element_id='button_1',
            title='Test Tooltip',
            content='Tooltip content',
            trigger=TooltipTrigger.HOVER,
            position='top'
        )
    
    def test_tooltip_creation(self):
        """Test creating tooltip."""
        self.assertEqual(self.tooltip.tooltip_id, 'test_tooltip')
        self.assertEqual(self.tooltip.element_id, 'button_1')
        self.assertEqual(self.tooltip.trigger, TooltipTrigger.HOVER)
    
    def test_tooltip_defaults(self):
        """Test tooltip default values."""
        self.assertEqual(self.tooltip.delay_ms, 300)
        self.assertEqual(self.tooltip.max_width_px, 300)
        self.assertFalse(self.tooltip.persistent)
    
    def test_tooltip_to_dict(self):
        """Test converting tooltip to dictionary."""
        tooltip_dict = self.tooltip.to_dict()
        
        self.assertEqual(tooltip_dict['tooltip_id'], 'test_tooltip')
        self.assertEqual(tooltip_dict['trigger'], 'hover')
        self.assertEqual(tooltip_dict['position'], 'top')


class TestSearchEngine(unittest.TestCase):
    """Test suite for SearchEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.articles = [
            HelpArticle(
                article_id='article_1',
                title='Getting Started Guide',
                category=ArticleCategory.GETTING_STARTED,
                content='Learn how to get started with the application',
                short_description='Start here',
                keywords=['start', 'begin', 'new']
            ),
            HelpArticle(
                article_id='article_2',
                title='Advanced Styling',
                category=ArticleCategory.STYLING,
                content='Learn advanced CSS techniques for styling',
                short_description='Advanced styling',
                keywords=['css', 'styling', 'advanced']
            )
        ]
        self.search_engine = SearchEngine(self.articles)
    
    def test_search_engine_initialization(self):
        """Test search engine initializes with articles."""
        self.assertIsNotNone(self.search_engine.index)
        self.assertGreater(len(self.search_engine.index), 0)
    
    def test_search_by_keyword(self):
        """Test searching by keyword."""
        results = self.search_engine.search('styling')
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].article_id, 'article_2')
    
    def test_search_by_title(self):
        """Test searching by title."""
        results = self.search_engine.search('Getting Started')
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].title, 'Getting Started Guide')
    
    def test_search_results_structure(self):
        """Test search result structure."""
        results = self.search_engine.search('start')
        
        self.assertGreater(len(results), 0)
        result = results[0]
        self.assertIsInstance(result, SearchResult)
        self.assertIsNotNone(result.title)
        self.assertIsNotNone(result.excerpt)
        self.assertGreaterEqual(result.relevance_score, 0)
    
    def test_search_returns_limited_results(self):
        """Test search respects result limit."""
        results = self.search_engine.search('advanced', limit=1)
        self.assertEqual(len(results), 1)
    
    def test_search_no_matches(self):
        """Test search with no matches."""
        results = self.search_engine.search('nonexistent_keyword_xyz')
        self.assertEqual(len(results), 0)


class TestTooltipManager(unittest.TestCase):
    """Test suite for TooltipManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TooltipManager()
    
    def test_initialization(self):
        """Test tooltip manager initializes with default tooltips."""
        self.assertGreater(len(self.manager.tooltips), 0)
    
    def test_register_tooltip(self):
        """Test registering new tooltip."""
        tooltip = Tooltip(
            tooltip_id='custom_tooltip',
            element_id='custom_element',
            title='Custom',
            content='Custom tooltip',
            trigger=TooltipTrigger.CLICK,
            position='right'
        )
        
        success = self.manager.register_tooltip(tooltip)
        self.assertTrue(success)
        self.assertIn('custom_tooltip', self.manager.tooltips)
    
    def test_register_duplicate_tooltip(self):
        """Test registering duplicate tooltip."""
        tooltip1 = Tooltip(
            tooltip_id='dup_tooltip',
            element_id='element_1',
            title='First',
            content='First tooltip',
            trigger=TooltipTrigger.HOVER,
            position='top'
        )
        tooltip2 = Tooltip(
            tooltip_id='dup_tooltip',
            element_id='element_2',
            title='Second',
            content='Second tooltip',
            trigger=TooltipTrigger.HOVER,
            position='top'
        )
        
        self.manager.register_tooltip(tooltip1)
        success = self.manager.register_tooltip(tooltip2)
        
        self.assertFalse(success)
    
    def test_get_tooltip(self):
        """Test getting tooltip by ID."""
        tooltip = self.manager.get_tooltip('component_library_tooltip')
        
        self.assertIsNotNone(tooltip)
        self.assertEqual(tooltip.element_id, 'component_library')
    
    def test_get_tooltips_for_element(self):
        """Test getting tooltips for element."""
        tooltips = self.manager.get_tooltips_for_element('component_library')
        
        self.assertGreater(len(tooltips), 0)
        for tooltip in tooltips:
            self.assertEqual(tooltip.element_id, 'component_library')
    
    def test_show_tooltip(self):
        """Test showing tooltip."""
        success = self.manager.show_tooltip('component_library_tooltip')
        
        self.assertTrue(success)
        self.assertIn('component_library_tooltip', self.manager.active_tooltips)
    
    def test_hide_tooltip(self):
        """Test hiding tooltip."""
        self.manager.show_tooltip('component_library_tooltip')
        success = self.manager.hide_tooltip('component_library_tooltip')
        
        self.assertTrue(success)
        self.assertNotIn('component_library_tooltip', self.manager.active_tooltips)
    
    def test_get_all_tooltips(self):
        """Test getting all tooltips."""
        tooltips = self.manager.get_all_tooltips()
        
        self.assertIsInstance(tooltips, list)
        self.assertGreater(len(tooltips), 0)


class TestContextMenuManager(unittest.TestCase):
    """Test suite for ContextMenuManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ContextMenuManager()
    
    def test_initialization(self):
        """Test context menu manager initializes with default actions."""
        self.assertGreater(len(self.manager.actions), 0)
    
    def test_register_action(self):
        """Test registering context menu action."""
        action = ContextMenuAction(
            action_id='custom_action',
            label='Custom Action',
            icon='star',
            action_type='custom',
            target='custom_target'
        )
        
        success = self.manager.register_action(action)
        self.assertTrue(success)
        self.assertIn('custom_action', self.manager.actions)
    
    def test_get_action(self):
        """Test getting action by ID."""
        action = self.manager.get_action('help_component')
        
        self.assertIsNotNone(action)
        self.assertEqual(action.label, 'Learn About This')
    
    def test_get_all_actions(self):
        """Test getting all actions."""
        actions = self.manager.get_all_actions()
        
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)


class TestDocumentationBrowser(unittest.TestCase):
    """Test suite for DocumentationBrowser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.articles = [
            HelpArticle(
                article_id='article_1',
                title='First Article',
                category=ArticleCategory.GETTING_STARTED,
                content='First content',
                short_description='First',
                keywords=['first']
            ),
            HelpArticle(
                article_id='article_2',
                title='Second Article',
                category=ArticleCategory.STYLING,
                content='Second content',
                short_description='Second',
                keywords=['second']
            )
        ]
        self.browser = DocumentationBrowser(self.articles)
    
    def test_get_article(self):
        """Test getting article."""
        article = self.browser.get_article('article_1')
        
        self.assertIsNotNone(article)
        self.assertEqual(article.title, 'First Article')
    
    def test_view_count_incremented(self):
        """Test view count incremented when article viewed."""
        self.browser.get_article('article_1')
        article = self.browser.get_article('article_1')
        
        self.assertEqual(article.view_count, 2)
    
    def test_get_articles_by_category(self):
        """Test getting articles by category."""
        articles = self.browser.get_articles_by_category(ArticleCategory.STYLING)
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].article_id, 'article_2')
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        categories = self.browser.get_all_categories()
        
        self.assertIn(ArticleCategory.GETTING_STARTED, categories)
        self.assertIn(ArticleCategory.STYLING, categories)
    
    def test_get_table_of_contents(self):
        """Test getting table of contents."""
        toc = self.browser.get_table_of_contents()
        
        self.assertIsInstance(toc, dict)
        self.assertIn('getting_started', toc)
        self.assertIn('styling', toc)
    
    def test_add_bookmark(self):
        """Test adding bookmark."""
        success = self.browser.add_bookmark('article_1')
        
        self.assertTrue(success)
        self.assertIn('article_1', self.browser.bookmarks)
    
    def test_remove_bookmark(self):
        """Test removing bookmark."""
        self.browser.add_bookmark('article_1')
        success = self.browser.remove_bookmark('article_1')
        
        self.assertTrue(success)
        self.assertNotIn('article_1', self.browser.bookmarks)
    
    def test_get_bookmarks(self):
        """Test getting bookmarked articles."""
        self.browser.add_bookmark('article_1')
        self.browser.add_bookmark('article_2')
        
        bookmarks = self.browser.get_bookmarks()
        
        self.assertEqual(len(bookmarks), 2)
    
    def test_get_recent_articles(self):
        """Test getting recent articles."""
        self.browser.get_article('article_1')
        self.browser.get_article('article_2')
        
        recent = self.browser.get_recent_articles(limit=2)
        
        self.assertEqual(len(recent), 2)
    
    def test_mark_helpful(self):
        """Test marking article as helpful."""
        success = self.browser.mark_helpful('article_1')
        
        self.assertTrue(success)
        article = self.browser.get_article('article_1')
        self.assertEqual(article.helpful_votes, 1)


class TestDocumentationSystem(unittest.TestCase):
    """Test suite for DocumentationSystem."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.system = DocumentationSystem()
    
    def test_initialization(self):
        """Test system initializes correctly."""
        self.assertIsNotNone(self.system.articles)
        self.assertIsNotNone(self.system.browser)
        self.assertIsNotNone(self.system.tooltip_manager)
        self.assertIsNotNone(self.system.context_menu_manager)
        self.assertGreater(len(self.system.articles), 0)
    
    def test_search_documentation(self):
        """Test searching documentation."""
        results = self.system.search('template')
        
        self.assertGreater(len(results), 0)
    
    def test_get_article(self):
        """Test getting article."""
        article = self.system.get_article('getting_started_1')
        
        self.assertIsNotNone(article)
        self.assertEqual(article.title, 'Getting Started with Template Designer')
    
    def test_get_articles_by_category(self):
        """Test getting articles by category."""
        articles = self.system.get_articles_by_category(ArticleCategory.STYLING)
        
        self.assertGreater(len(articles), 0)
        for article in articles:
            self.assertEqual(article.category, ArticleCategory.STYLING)
    
    def test_get_all_articles(self):
        """Test getting all articles."""
        articles = self.system.get_all_articles()
        
        self.assertGreater(len(articles), 0)
    
    def test_get_table_of_contents(self):
        """Test getting table of contents."""
        toc = self.system.get_table_of_contents()
        
        self.assertIsInstance(toc, dict)
        self.assertGreater(len(toc), 0)
    
    def test_get_tooltips_for_element(self):
        """Test getting tooltips for element."""
        tooltips = self.system.get_tooltips_for_element('canvas_area')
        
        self.assertGreater(len(tooltips), 0)
    
    def test_register_custom_tooltip(self):
        """Test registering custom tooltip."""
        tooltip = Tooltip(
            tooltip_id='custom_tooltip',
            element_id='custom_element',
            title='Custom',
            content='Custom tooltip',
            trigger=TooltipTrigger.CLICK,
            position='left'
        )
        
        success = self.system.register_tooltip(tooltip)
        self.assertTrue(success)
    
    def test_show_hide_tooltip(self):
        """Test showing and hiding tooltips."""
        self.assertTrue(self.system.show_tooltip('canvas_tooltip'))
        self.assertTrue(self.system.hide_tooltip('canvas_tooltip'))
    
    def test_get_context_menu_actions(self):
        """Test getting context menu actions."""
        actions = self.system.get_context_menu_actions()
        
        self.assertGreater(len(actions), 0)
    
    def test_bookmark_operations(self):
        """Test bookmark operations."""
        self.assertTrue(self.system.add_bookmark('getting_started_1'))
        bookmarks = self.system.get_bookmarks()
        self.assertGreater(len(bookmarks), 0)
    
    def test_mark_article_helpful(self):
        """Test marking article helpful."""
        success = self.system.mark_article_helpful('getting_started_1')
        
        self.assertTrue(success)
        article = self.system.get_article('getting_started_1')
        self.assertGreater(article.helpful_votes, 0)
    
    def test_get_recent_articles(self):
        """Test getting recent articles."""
        self.system.get_article('getting_started_1')
        self.system.get_article('components_1')
        
        recent = self.system.get_recent_articles(limit=2)
        self.assertGreater(len(recent), 0)
    
    def test_export_article(self):
        """Test exporting article."""
        article_dict = self.system.export_article('getting_started_1')
        
        self.assertIsNotNone(article_dict)
        self.assertEqual(article_dict['article_id'], 'getting_started_1')
    
    def test_documentation_stats(self):
        """Test documentation statistics."""
        stats = self.system.get_documentation_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_articles', stats)
        self.assertIn('total_views', stats)
        self.assertIn('total_helpful_votes', stats)
        self.assertIn('total_categories', stats)


if __name__ == '__main__':
    unittest.main()
