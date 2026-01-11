"""AnkiDroidJS API service for behavior integration.

This module provides access to the verified AnkiDroidJS API v0.0.4 methods
and generates JavaScript code for attaching behaviors to template components.
"""

from typing import List, Dict, Any, Optional


class AnkiJSApiService:
    """Service for AnkiDroidJS API integration.
    
    Provides list of available API methods and generates JavaScript code
    for attaching behaviors to template components.
    """
    
    # Verified AnkiDroidJS API v0.0.4 methods from ANKIJSAPI-VERIFICATION.md
    BEHAVIORS = [
        # Card Information
        {"category": "Card Info", "name": "getCardId", "description": "Get current card ID"},
        {"category": "Card Info", "name": "getCardNid", "description": "Get note ID"},
        {"category": "Card Info", "name": "getCardDeck", "description": "Get deck name"},
        {"category": "Card Info", "name": "getCardType", "description": "Get card type (0=new, 1=learning, 2=review, 3=relearning)"},
        {"category": "Card Info", "name": "getCardQueue", "description": "Get card queue state"},
        {"category": "Card Info", "name": "getCardMod", "description": "Get modification timestamp"},
        {"category": "Card Info", "name": "getCardReps", "description": "Get review count"},
        {"category": "Card Info", "name": "getCardLapses", "description": "Get lapse count"},
        {"category": "Card Info", "name": "getCardLeft", "description": "Get remaining learning steps"},
        {"category": "Card Info", "name": "getCardDue", "description": "Get due date/position"},
        {"category": "Card Info", "name": "getCardInterval", "description": "Get current interval"},
        {"category": "Card Info", "name": "getCardFactor", "description": "Get ease factor"},
        
        # Tags
        {"category": "Tags", "name": "getTags", "description": "Get all note tags as array"},
        {"category": "Tags", "name": "getCardFlag", "description": "Get flag value (0-4)"},
        {"category": "Tags", "name": "getCardMark", "description": "Get marked status (boolean)"},
        
        # Deck and Collection
        {"category": "Deck", "name": "getNewCardCountToday", "description": "Get new cards reviewed today"},
        {"category": "Deck", "name": "getStudiedCountToday", "description": "Get cards studied today"},
        {"category": "Deck", "name": "getTotalNewCountToday", "description": "Get total new cards scheduled today"},
        {"category": "Deck", "name": "getTotalReviewCountToday", "description": "Get total reviews scheduled today"},
        {"category": "Deck", "name": "getDeckName", "description": "Get current deck name"},
        
        # Time and Timers
        {"category": "Time", "name": "getTimeTaken", "description": "Get time taken on current card (seconds)"},
        {"category": "Time", "name": "getTimeLimit", "description": "Get time limit for current card"},
        
        # Note Type
        {"category": "Note Type", "name": "getNoteType", "description": "Get note type ID"},
        {"category": "Note Type", "name": "isNormalPriority", "description": "Check if card is normal priority"},
        
        # UI Actions
        {"category": "Actions", "name": "showAnswer", "description": "Reveal card answer"},
        {"category": "Actions", "name": "buttonAnswerEase1", "description": "Answer 'Again'"},
        {"category": "Actions", "name": "buttonAnswerEase2", "description": "Answer 'Hard'"},
        {"category": "Actions", "name": "buttonAnswerEase3", "description": "Answer 'Good'"},
        {"category": "Actions", "name": "buttonAnswerEase4", "description": "Answer 'Easy'"},
        {"category": "Actions", "name": "replayAudio", "description": "Replay audio"},
        {"category": "Actions", "name": "toggleFlag", "description": "Toggle flag state (cycles 0-4)"},
        {"category": "Actions", "name": "toggleMark", "description": "Toggle marked state"},
        {"category": "Actions", "name": "buryCard", "description": "Bury current card"},
        {"category": "Actions", "name": "buryNote", "description": "Bury all cards in note"},
        {"category": "Actions", "name": "suspendCard", "description": "Suspend current card"},
        {"category": "Actions", "name": "suspendNote", "description": "Suspend all cards in note"},
        {"category": "Actions", "name": "addTagToCard", "description": "Add tag to current card", "params": ["tag"]},
        {"category": "Actions", "name": "removeTagFromCard", "description": "Remove tag from current card", "params": ["tag"]},
        {"category": "Actions", "name": "addFlagToCard", "description": "Set flag (1-4)", "params": ["flag"]},
        {"category": "Actions", "name": "removeFlagFromCard", "description": "Remove flag (set to 0)"},
        {"category": "Actions", "name": "markCard", "description": "Mark current card"},
        {"category": "Actions", "name": "unmarkCard", "description": "Unmark current card"},
        
        # Navigation
        {"category": "Navigation", "name": "undo", "description": "Undo last action"},
        {"category": "Navigation", "name": "redo", "description": "Redo last undone action"},
        
        # TTS
        {"category": "TTS", "name": "ankiTtsSpeak", "description": "Speak text with TTS", "params": ["text", "lang", "pitch", "speed"]},
        {"category": "TTS", "name": "ankiTtsIsSpeaking", "description": "Check if TTS is currently speaking"},
        {"category": "TTS", "name": "ankiTtsStop", "description": "Stop TTS playback"},
        
        # Device
        {"category": "Device", "name": "isDisplayingAnswer", "description": "Check if answer is showing"},
        {"category": "Device", "name": "isTopbarShown", "description": "Check if top bar is visible"},
        
        # Toast Messages
        {"category": "Toast", "name": "ankiShowToast", "description": "Show toast message", "params": ["message"]},
        {"category": "Toast", "name": "ankiShowLongToast", "description": "Show long toast message", "params": ["message"]},
        
        # Custom Actions
        {"category": "Custom", "name": "searchCard", "description": "Search for cards", "params": ["query"]},
        {"category": "Custom", "name": "previewCard", "description": "Preview card", "params": ["cardId"]},
        {"category": "Custom", "name": "editCard", "description": "Edit current card"},
    ]
    
    def get_available_behaviors(self) -> List[Dict[str, Any]]:
        """Get list of all available AnkiDroidJS API behaviors.
        
        Returns:
            List of behavior dictionaries with name, category, description, and optional params
        """
        return self.BEHAVIORS
    
    def get_behaviors_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get behaviors grouped by category.
        
        Returns:
            Dictionary mapping category names to lists of behaviors
        """
        categories = {}
        for behavior in self.BEHAVIORS:
            category = behavior["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(behavior)
        return categories
    
    def generate_behavior_js(
        self,
        action: str,
        trigger: str = "click",
        target_selector: str = "",
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate JavaScript code for attaching a behavior to an element.
        
        Args:
            action: AnkiDroidJS API method name (e.g., 'showAnswer', 'toggleFlag')
            trigger: Event trigger (e.g., 'click', 'dblclick', 'keydown')
            target_selector: CSS selector for target element (empty for current element)
            params: Optional parameters to pass to the API method
            
        Returns:
            JavaScript code as string
        """
        params = params or {}
        
        # Build parameter string
        param_str = ""
        if params:
            param_list = [f"'{v}'" if isinstance(v, str) else str(v) for v in params.values()]
            param_str = ", " + ", ".join(param_list)
        
        # Generate event listener code
        selector = target_selector or "this"
        
        js_code = f"""
// Attach {action} behavior on {trigger}
(function() {{
    const element = {f'document.querySelector("{target_selector}")' if target_selector else 'this'};
    if (element) {{
        element.addEventListener('{trigger}', function(event) {{
            event.preventDefault();
            if (typeof AnkiDroidJS !== 'undefined') {{
                AnkiDroidJS.init().then(function(api) {{
                    api.{action}({param_str.lstrip(', ')});
                }});
            }}
        }});
    }}
}})();
""".strip()
        
        return js_code
    
    def validate_behavior(self, action: str) -> bool:
        """Check if an action is a valid AnkiDroidJS API method.
        
        Args:
            action: Method name to validate
            
        Returns:
            True if action exists in BEHAVIORS list
        """
        return any(b["name"] == action for b in self.BEHAVIORS)
    
    def get_behavior_info(self, action: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific behavior.
        
        Args:
            action: Method name to look up
            
        Returns:
            Behavior dictionary or None if not found
        """
        for behavior in self.BEHAVIORS:
            if behavior["name"] == action:
                return behavior
        return None
