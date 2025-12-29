"""
Anki Template Designer Add-on
Build and preview card templates for Anki Desktop and AnkiDroid
"""

# Only import when running within Anki environment
# Tests will import modules directly
try:
    from aqt import mw
    from aqt.utils import showInfo
    
    # Import and initialize only when Anki is fully loaded
    def on_profile_loaded():
        """Initialize add-on after profile is loaded"""
        try:
            from .template_designer import init_addon
            init_addon()
        except Exception as e:
            showInfo(f"Template Designer initialization error: {str(e)}")
    
    # Wait for profile to load before initializing
    from aqt import gui_hooks
    gui_hooks.profile_did_open.append(on_profile_loaded)
    
    __all__ = ['on_profile_loaded']
except ImportError:
    # Running in test environment or outside Anki
    __all__ = []

