"""
Issue #48: Documentation System

In-app help system for self-service learning and reference.
Features: Help dialog, tooltips, context menu, documentation browser, searchable knowledge base.

Architecture:
- DocumentationSystem: Main manager for all documentation
- HelpArticle: Individual help article data model
- Tooltip: UI tooltip data model
- DocumentationBrowser: Full documentation viewer
- SearchEngine: Full-text search functionality
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import re


class ArticleCategory(Enum):
    """Documentation article categories."""
    GETTING_STARTED = "getting_started"
    COMPONENTS = "components"
    PROPERTIES = "properties"
    STYLING = "styling"
    PREVIEW = "preview"
    EXPORT = "export"
    TROUBLESHOOTING = "troubleshooting"
    ADVANCED = "advanced"
    TIPS = "tips"


class TooltipTrigger(Enum):
    """Tooltip trigger types."""
    HOVER = "hover"
    CLICK = "click"
    FOCUS = "focus"


@dataclass
class HelpArticle:
    """Individual help documentation article."""
    article_id: str
    title: str
    category: ArticleCategory
    content: str
    short_description: str
    keywords: List[str]
    related_articles: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    view_count: int = 0
    helpful_votes: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'article_id': self.article_id,
            'title': self.title,
            'category': self.category.value,
            'content': self.content,
            'short_description': self.short_description,
            'keywords': self.keywords,
            'related_articles': self.related_articles,
            'code_examples': self.code_examples,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'view_count': self.view_count,
            'helpful_votes': self.helpful_votes
        }


@dataclass
class Tooltip:
    """UI tooltip definition."""
    tooltip_id: str
    element_id: str
    title: str
    content: str
    trigger: TooltipTrigger
    position: str  # 'top', 'bottom', 'left', 'right', 'auto'
    delay_ms: int = 300
    max_width_px: int = 300
    persistent: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'tooltip_id': self.tooltip_id,
            'element_id': self.element_id,
            'title': self.title,
            'content': self.content,
            'trigger': self.trigger.value,
            'position': self.position,
            'delay_ms': self.delay_ms,
            'max_width_px': self.max_width_px,
            'persistent': self.persistent
        }


@dataclass
class ContextMenuAction:
    """Context menu action for help."""
    action_id: str
    label: str
    icon: str
    action_type: str  # 'view_help', 'search', 'open_docs'
    target: Optional[str] = None  # article_id or search query
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'action_id': self.action_id,
            'label': self.label,
            'icon': self.icon,
            'action_type': self.action_type,
            'target': self.target
        }


@dataclass
class SearchResult:
    """Search result from documentation."""
    article_id: str
    title: str
    excerpt: str
    category: str
    relevance_score: float
    match_positions: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'article_id': self.article_id,
            'title': self.title,
            'excerpt': self.excerpt,
            'category': self.category,
            'relevance_score': self.relevance_score,
            'match_positions': self.match_positions
        }


class SearchEngine:
    """Full-text search engine for documentation."""
    
    def __init__(self, articles: List[HelpArticle]):
        """Initialize search engine with articles."""
        self.articles = articles
        self.build_index()
    
    def build_index(self):
        """Build search index from articles."""
        self.index = {}
        for article in self.articles:
            # Index title
            self._index_text(article.article_id, article.title, weight=2.0)
            # Index content
            self._index_text(article.article_id, article.content, weight=1.0)
            # Index keywords
            for keyword in article.keywords:
                self._index_text(article.article_id, keyword, weight=1.5)
    
    def _index_text(self, article_id: str, text: str, weight: float = 1.0):
        """Index text for an article."""
        words = re.findall(r'\b\w+\b', text.lower())
        for word in set(words):  # Use set to avoid duplicates
            if word not in self.index:
                self.index[word] = []
            self.index[word].append((article_id, weight))
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search documentation by query."""
        query_words = re.findall(r'\b\w+\b', query.lower())
        scores = {}
        
        # Score articles by matching words
        for word in query_words:
            if word in self.index:
                for article_id, weight in self.index[word]:
                    if article_id not in scores:
                        scores[article_id] = 0
                    scores[article_id] += weight
        
        # Create search results
        results = []
        for article_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]:
            article = self._get_article(article_id)
            if article:
                excerpt = self._extract_excerpt(article.content, query_words)
                results.append(SearchResult(
                    article_id=article_id,
                    title=article.title,
                    excerpt=excerpt,
                    category=article.category.value,
                    relevance_score=score / max(scores.values()) if scores else 0
                ))
        
        return results
    
    def _get_article(self, article_id: str) -> Optional[HelpArticle]:
        """Get article by ID."""
        for article in self.articles:
            if article.article_id == article_id:
                return article
        return None
    
    def _extract_excerpt(self, text: str, keywords: List[str], length: int = 150) -> str:
        """Extract relevant excerpt from text."""
        text_lower = text.lower()
        
        # Find position of first keyword
        first_pos = len(text)
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1 and pos < first_pos:
                first_pos = pos
        
        # Extract excerpt around keyword
        start = max(0, first_pos - 50)
        end = min(len(text), start + length)
        
        excerpt = text[start:end].strip()
        if start > 0:
            excerpt = '...' + excerpt
        if end < len(text):
            excerpt = excerpt + '...'
        
        return excerpt


class DocumentationBrowser:
    """Full-featured documentation browser."""
    
    def __init__(self, articles: List[HelpArticle]):
        """Initialize documentation browser."""
        self.articles = articles
        self.search_engine = SearchEngine(articles)
        self.current_article = None
        self.article_history = []
        self.bookmarks = []
    
    def get_article(self, article_id: str) -> Optional[HelpArticle]:
        """Get article by ID and track view."""
        article = None
        for a in self.articles:
            if a.article_id == article_id:
                article = a
                break
        
        if article:
            article.view_count += 1
            self.current_article = article
            self.article_history.append(article_id)
            return article
        
        return None
    
    def get_articles_by_category(self, category: ArticleCategory) -> List[HelpArticle]:
        """Get all articles in a category."""
        return [a for a in self.articles if a.category == category]
    
    def get_all_categories(self) -> List[ArticleCategory]:
        """Get all article categories."""
        return list(set(a.category for a in self.articles))
    
    def get_table_of_contents(self) -> Dict[str, List[str]]:
        """Get table of contents organized by category."""
        toc = {}
        for category in self.get_all_categories():
            articles = self.get_articles_by_category(category)
            toc[category.value] = [a.title for a in articles]
        return toc
    
    def search(self, query: str) -> List[SearchResult]:
        """Search articles."""
        return self.search_engine.search(query)
    
    def add_bookmark(self, article_id: str) -> bool:
        """Add article to bookmarks."""
        if article_id not in self.bookmarks:
            self.bookmarks.append(article_id)
            return True
        return False
    
    def remove_bookmark(self, article_id: str) -> bool:
        """Remove article from bookmarks."""
        if article_id in self.bookmarks:
            self.bookmarks.remove(article_id)
            return True
        return False
    
    def get_bookmarks(self) -> List[HelpArticle]:
        """Get all bookmarked articles."""
        bookmarked = []
        for article_id in self.bookmarks:
            article = self.get_article(article_id)
            if article:
                bookmarked.append(article)
        return bookmarked
    
    def get_recent_articles(self, limit: int = 5) -> List[HelpArticle]:
        """Get recently viewed articles."""
        recent_ids = list(dict.fromkeys(reversed(self.article_history)))[:limit]
        recent = []
        for article_id in recent_ids:
            article = self.get_article(article_id)
            if article:
                recent.append(article)
        return recent
    
    def mark_helpful(self, article_id: str) -> bool:
        """Mark article as helpful."""
        for article in self.articles:
            if article.article_id == article_id:
                article.helpful_votes += 1
                return True
        return False


class TooltipManager:
    """Manages UI tooltips."""
    
    def __init__(self):
        """Initialize tooltip manager."""
        self.tooltips = {}
        self.active_tooltips = []
        self._initialize_default_tooltips()
    
    def _initialize_default_tooltips(self):
        """Initialize default tooltips for common UI elements."""
        default_tooltips = [
            Tooltip(
                tooltip_id='component_library_tooltip',
                element_id='component_library',
                title='Component Library',
                content='Drag and drop components from here to design your template.',
                trigger=TooltipTrigger.HOVER,
                position='right',
                delay_ms=500
            ),
            Tooltip(
                tooltip_id='canvas_tooltip',
                element_id='canvas_area',
                title='Design Canvas',
                content='This is where you build your template layout. Click to select components.',
                trigger=TooltipTrigger.HOVER,
                position='top',
                delay_ms=500
            ),
            Tooltip(
                tooltip_id='properties_tooltip',
                element_id='properties_panel',
                title='Properties Panel',
                content='Configure the selected component here. Change colors, sizes, and other properties.',
                trigger=TooltipTrigger.HOVER,
                position='left',
                delay_ms=500
            ),
            Tooltip(
                tooltip_id='preview_tooltip',
                element_id='preview_panel',
                title='Live Preview',
                content='See real-time changes as you edit your template.',
                trigger=TooltipTrigger.HOVER,
                position='left',
                delay_ms=500
            ),
            Tooltip(
                tooltip_id='style_editor_tooltip',
                element_id='style_editor',
                title='Style Editor',
                content='Add custom CSS to style your components. Full CSS support available.',
                trigger=TooltipTrigger.HOVER,
                position='right',
                delay_ms=500
            ),
            Tooltip(
                tooltip_id='export_tooltip',
                element_id='export_button',
                title='Export Template',
                content='Export your template to use in Anki. Supports multiple formats.',
                trigger=TooltipTrigger.HOVER,
                position='top',
                delay_ms=500
            ),
        ]
        
        for tooltip in default_tooltips:
            self.register_tooltip(tooltip)
    
    def register_tooltip(self, tooltip: Tooltip) -> bool:
        """Register a new tooltip."""
        if tooltip.tooltip_id not in self.tooltips:
            self.tooltips[tooltip.tooltip_id] = tooltip
            return True
        return False
    
    def get_tooltip(self, tooltip_id: str) -> Optional[Tooltip]:
        """Get tooltip by ID."""
        return self.tooltips.get(tooltip_id)
    
    def get_tooltips_for_element(self, element_id: str) -> List[Tooltip]:
        """Get all tooltips for an element."""
        return [t for t in self.tooltips.values() if t.element_id == element_id]
    
    def show_tooltip(self, tooltip_id: str) -> bool:
        """Show a tooltip."""
        if tooltip_id in self.tooltips and tooltip_id not in self.active_tooltips:
            self.active_tooltips.append(tooltip_id)
            return True
        return False
    
    def hide_tooltip(self, tooltip_id: str) -> bool:
        """Hide a tooltip."""
        if tooltip_id in self.active_tooltips:
            self.active_tooltips.remove(tooltip_id)
            return True
        return False
    
    def get_all_tooltips(self) -> List[Tooltip]:
        """Get all tooltips."""
        return list(self.tooltips.values())


class ContextMenuManager:
    """Manages context menu (right-click) actions."""
    
    def __init__(self):
        """Initialize context menu manager."""
        self.actions = {}
        self._initialize_default_actions()
    
    def _initialize_default_actions(self):
        """Initialize default context menu actions."""
        default_actions = [
            ContextMenuAction(
                action_id='help_component',
                label='Learn About This',
                icon='help',
                action_type='view_help',
                target='components'
            ),
            ContextMenuAction(
                action_id='search_help',
                label='Search Documentation',
                icon='search',
                action_type='search',
                target=None
            ),
            ContextMenuAction(
                action_id='open_docs',
                label='Open Documentation',
                icon='book',
                action_type='open_docs',
                target=None
            ),
        ]
        
        for action in default_actions:
            self.register_action(action)
    
    def register_action(self, action: ContextMenuAction) -> bool:
        """Register context menu action."""
        if action.action_id not in self.actions:
            self.actions[action.action_id] = action
            return True
        return False
    
    def get_action(self, action_id: str) -> Optional[ContextMenuAction]:
        """Get action by ID."""
        return self.actions.get(action_id)
    
    def get_all_actions(self) -> List[ContextMenuAction]:
        """Get all context menu actions."""
        return list(self.actions.values())


class DocumentationSystem:
    """Main documentation system manager."""
    
    def __init__(self):
        """Initialize documentation system."""
        self.articles = self._initialize_articles()
        self.browser = DocumentationBrowser(self.articles)
        self.tooltip_manager = TooltipManager()
        self.context_menu_manager = ContextMenuManager()
        self.user_preferences = {}
    
    def _initialize_articles(self) -> List[HelpArticle]:
        """Initialize default help articles."""
        return [
            HelpArticle(
                article_id='getting_started_1',
                title='Getting Started with Template Designer',
                category=ArticleCategory.GETTING_STARTED,
                content='''Welcome to Template Designer! This guide will help you create your first Anki template.

1. Open Template Designer from Anki
2. Start with a blank template or choose a starter template
3. Add components to your template using the component library
4. Customize properties in the properties panel
5. Preview your template to see how it looks
6. Export your template when satisfied

Template Designer supports all Anki template features including field references, conditionals, and custom styling.

For more details, see related articles on components and styling.''',
                short_description='Learn how to create your first template in 5 minutes',
                keywords=['getting_started', 'first_template', 'beginner', 'tutorial'],
                related_articles=['components_1', 'properties_1', 'preview_1']
            ),
            HelpArticle(
                article_id='components_1',
                title='Understanding Components',
                category=ArticleCategory.COMPONENTS,
                content='''Components are the building blocks of your Anki template.

Available Components:
- Text Field: Display a text value from your note
- Rich Text Field: Display formatted text with images and links
- Button: Interactive button for actions
- List: Display a list of items
- Checkbox: Toggle option
- Image: Display images from your notes
- Code Block: Display code with syntax highlighting

To add a component:
1. Open the Component Library
2. Drag your desired component to the canvas
3. Drop it in the position you want
4. Adjust its properties in the Properties Panel

Each component has specific properties you can customize. Use the preview to see changes in real-time.''',
                short_description='Learn about available components and how to use them',
                keywords=['components', 'building_blocks', 'fields', 'layout'],
                related_articles=['properties_1', 'styling_1']
            ),
            HelpArticle(
                article_id='properties_1',
                title='Component Properties Guide',
                category=ArticleCategory.PROPERTIES,
                content='''Every component has properties you can customize.

Common Properties:
- Position: X and Y coordinates on the canvas
- Size: Width and height of the component
- Font: Font family, size, and color
- Background: Background color or image
- Border: Border style, width, and color
- Padding: Space inside the component
- Margin: Space around the component
- Opacity: Transparency level (0-100%)
- Z-Index: Layer order (higher appears on top)

To modify properties:
1. Select a component on the canvas
2. Look at the Properties Panel on the right
3. Change values to customize the appearance
4. See changes instantly in the preview

Hold Shift while dragging to constrain proportions.
Double-click values to enter custom CSS.''',
                short_description='Master component properties for precise control',
                keywords=['properties', 'customization', 'styling', 'layout'],
                related_articles=['components_1', 'styling_1']
            ),
            HelpArticle(
                article_id='styling_1',
                title='Custom CSS and Styling',
                category=ArticleCategory.STYLING,
                content='''Template Designer supports full CSS customization.

How to Add Custom CSS:
1. Click the "Style Editor" tab
2. Write your CSS code
3. Changes apply instantly in preview

CSS Tips:
- Use color names, hex (#FFF), RGB (255,255,255)
- Font families: Arial, Verdana, Georgia, monospace
- Use flexbox for responsive layouts
- CSS variables work for theming

Example CSS:
```css
.my-component {
  background: linear-gradient(45deg, #fff, #eee);
  border-radius: 8px;
  padding: 20px;
  font-size: 16px;
}
```

Anki Template Variables:
- {{field_name}}: Display card field
- {{type:field_name}}: Check if field exists
- #conditional_field ... /conditional_field

For more Anki syntax, see Anki documentation.''',
                short_description='Create beautiful custom styling with CSS',
                keywords=['css', 'styling', 'custom', 'design', 'colors'],
                related_articles=['components_1', 'preview_1', 'export_1']
            ),
            HelpArticle(
                article_id='preview_1',
                title='Using the Preview Panel',
                category=ArticleCategory.PREVIEW,
                content='''The Preview Panel shows how your template looks with real data.

Features:
- Real-time rendering as you edit
- Sample data for testing
- Device simulation options
- Performance metrics
- Responsive layout testing

How to Preview:
1. Create your template
2. Click the Preview tab
3. Scroll through preview to see all elements
4. Test interactions
5. Check different screen sizes

Preview Best Practices:
- Always preview before exporting
- Test with long and short field values
- Check with different fonts and colors
- Verify links and buttons work
- Test on different devices if possible

If preview doesn't update, try:
1. Check browser console for errors
2. Validate CSS syntax
3. Check template syntax

The preview matches Anki's rendering engine for accuracy.''',
                short_description='Preview and test your template design',
                keywords=['preview', 'testing', 'preview_panel', 'rendering'],
                related_articles=['components_1', 'styling_1', 'troubleshooting_1']
            ),
            HelpArticle(
                article_id='export_1',
                title='Exporting Your Template',
                category=ArticleCategory.EXPORT,
                content='''Export your completed template to use in Anki.

Export Options:
- Export to Anki: Direct import to active deck
- Export as File: Save .apkg for sharing
- Export as JSON: Save template data for backup
- Copy to Clipboard: Quick sharing via chat

Steps to Export:
1. Finalize your template design
2. Test in preview thoroughly
3. Click Export button
4. Choose your export format
5. Follow prompts to complete export

After Export:
- Template automatically appears in Anki
- Create test cards to verify
- Make adjustments if needed
- Re-export if changes required

Export Troubleshooting:
- Ensure template validates successfully
- Check for syntax errors
- Verify all fields are correct
- Test with sample data
- Check Anki is running (for direct export)

Sharing Templates:
- Export as file and share .apkg
- Share JSON for others to import
- Include instructions for your template
- Document any special requirements''',
                short_description='Export your template for use in Anki',
                keywords=['export', 'sharing', 'save', 'apkg', 'backup'],
                related_articles=['styling_1', 'preview_1']
            ),
            HelpArticle(
                article_id='troubleshooting_1',
                title='Common Issues and Solutions',
                category=ArticleCategory.TROUBLESHOOTING,
                content='''Quick solutions to common problems.

Issue: Preview not updating
Solution: Refresh browser (Ctrl+R), check console for errors

Issue: CSS not applying
Solution: Check CSS syntax, verify selectors, use browser DevTools

Issue: Field not displaying
Solution: Check field name spelling, verify field exists in note type

Issue: Layout looks wrong on mobile
Solution: Test responsive design, check viewport settings, use mobile emulator

Issue: Can't export template
Solution: Validate template, check Anki running, clear cache

Issue: Performance is slow
Solution: Simplify CSS, reduce image sizes, profile with DevTools

Need More Help?
- Check documentation for your feature
- Search documentation index
- Look for similar templates
- Check Anki community forums
- Post on template designer support

Getting Support:
- Open help dialog (F1)
- Right-click for context help
- Search documentation
- Check tutorials and guides''',
                short_description='Solutions to common template design issues',
                keywords=['troubleshooting', 'problems', 'errors', 'help', 'fix'],
                related_articles=['components_1', 'styling_1', 'preview_1']
            ),
            HelpArticle(
                article_id='tips_1',
                title='Tips and Tricks for Power Users',
                category=ArticleCategory.TIPS,
                content='''Advanced techniques to level up your template skills.

Design Tips:
- Use grid for consistent alignment
- Create reusable component groups
- Use CSS variables for consistency
- Test across different note types
- Keep templates maintainable

Performance Tips:
- Minimize CSS and JavaScript
- Optimize image sizes
- Cache static resources
- Use efficient selectors
- Profile with DevTools

Workflow Tips:
- Use keyboard shortcuts for speed
- Save templates frequently
- Comment your CSS
- Version control your templates
- Build component library

Style Tips:
- Use consistent color schemes
- Follow typography guidelines
- Respect user preferences (dark mode)
- Ensure sufficient contrast
- Test with different zoom levels

Advanced Features:
- Custom JavaScript in templates
- Variable substitution
- Conditional rendering
- Template inheritance
- Plugin integration

Learning Resources:
- Built-in tutorials
- Anki template documentation
- CSS reference guides
- Community templates
- Video tutorials''',
                short_description='Advanced techniques and productivity tips',
                keywords=['tips', 'tricks', 'advanced', 'power_user', 'optimization'],
                related_articles=['components_1', 'styling_1', 'export_1']
            ),
        ]
    
    def search(self, query: str) -> List[SearchResult]:
        """Search documentation."""
        return self.browser.search(query)
    
    def get_article(self, article_id: str) -> Optional[HelpArticle]:
        """Get article by ID."""
        return self.browser.get_article(article_id)
    
    def get_articles_by_category(self, category: ArticleCategory) -> List[HelpArticle]:
        """Get articles by category."""
        return self.browser.get_articles_by_category(category)
    
    def get_all_articles(self) -> List[HelpArticle]:
        """Get all articles."""
        return self.articles
    
    def get_table_of_contents(self) -> Dict[str, List[str]]:
        """Get table of contents."""
        return self.browser.get_table_of_contents()
    
    def get_tooltips_for_element(self, element_id: str) -> List[Tooltip]:
        """Get tooltips for UI element."""
        return self.tooltip_manager.get_tooltips_for_element(element_id)
    
    def register_tooltip(self, tooltip: Tooltip) -> bool:
        """Register custom tooltip."""
        return self.tooltip_manager.register_tooltip(tooltip)
    
    def show_tooltip(self, tooltip_id: str) -> bool:
        """Show tooltip."""
        return self.tooltip_manager.show_tooltip(tooltip_id)
    
    def hide_tooltip(self, tooltip_id: str) -> bool:
        """Hide tooltip."""
        return self.tooltip_manager.hide_tooltip(tooltip_id)
    
    def get_context_menu_actions(self) -> List[ContextMenuAction]:
        """Get context menu actions."""
        return self.context_menu_manager.get_all_actions()
    
    def add_bookmark(self, article_id: str) -> bool:
        """Add article to bookmarks."""
        return self.browser.add_bookmark(article_id)
    
    def remove_bookmark(self, article_id: str) -> bool:
        """Remove article from bookmarks."""
        return self.browser.remove_bookmark(article_id)
    
    def get_bookmarks(self) -> List[HelpArticle]:
        """Get bookmarked articles."""
        return self.browser.get_bookmarks()
    
    def mark_article_helpful(self, article_id: str) -> bool:
        """Mark article as helpful."""
        return self.browser.mark_helpful(article_id)
    
    def get_recent_articles(self, limit: int = 5) -> List[HelpArticle]:
        """Get recently viewed articles."""
        return self.browser.get_recent_articles(limit)
    
    def export_article(self, article_id: str) -> Optional[Dict]:
        """Export article as JSON."""
        article = self.get_article(article_id)
        return article.to_dict() if article else None
    
    def get_documentation_stats(self) -> Dict:
        """Get documentation statistics."""
        total_articles = len(self.articles)
        total_views = sum(a.view_count for a in self.articles)
        total_helpful = sum(a.helpful_votes for a in self.articles)
        categories = len(self.browser.get_all_categories())
        
        return {
            'total_articles': total_articles,
            'total_views': total_views,
            'total_helpful_votes': total_helpful,
            'total_categories': categories,
            'bookmarks': len(self.browser.bookmarks),
            'most_viewed': max((a.title, a.view_count) for a in self.articles),
            'most_helpful': max((a.title, a.helpful_votes) for a in self.articles)
        }
