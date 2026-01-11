"""
Anki Template Designer Add-on
Build and preview card templates for Anki Desktop and AnkiDroid

GrapeJS-based visual template builder with AnkiDroidJS API integration.
"""

# Only import when running within Anki environment
try:
    from aqt import mw, gui_hooks
    from aqt.utils import showInfo
    
    # Import and initialize only when Anki is fully loaded
    def on_profile_loaded():
        """Initialize add-on after profile is loaded."""
        try:
            from .hooks.menu import setup_menu
            setup_menu()
            print("[Template Designer] Addon initialized successfully")
        except Exception as e:
            showInfo(f"Template Designer initialization error: {str(e)}")
            print(f"[Template Designer] Initialization failed: {e}")
    
    # Wait for profile to load before initializing
    gui_hooks.profile_did_open.append(on_profile_loaded)
    
    __all__ = ['on_profile_loaded']
    
except ImportError:
    # Running in test environment or outside Anki
    print("[Template Designer] Running outside Anki environment")
    __all__ = []

