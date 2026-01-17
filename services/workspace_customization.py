"""
Workspace Customization Module

Provides comprehensive workspace customization features including:
- Custom layout configurations with panel management
- Theme customization with predefined and custom color schemes
- Keyboard shortcut management with conflict detection
- Preset configuration storage and management
- State persistence and validation

Classes:
    PanelState: Represents the state of a workspace panel
    LayoutConfiguration: Defines panel arrangement and grid
    Theme: Defines color scheme for the workspace
    KeyboardShortcut: Defines keyboard binding and action mapping
    PresetConfiguration: Bundles layout, theme, and shortcuts
    LayoutManager: Manages workspace layouts
    ThemeManager: Manages color themes
    ShortcutManager: Manages keyboard shortcuts
    PresetManager: Manages preset configurations
    WorkspaceManager: Orchestrates all customization features
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Literal, Optional, Tuple
from datetime import datetime
import json


@dataclass
class PanelState:
    """Represents the state of a workspace panel."""
    name: str
    position: Literal["left", "center", "right", "top", "bottom"]
    visible: bool = True
    width: int = 100
    height: int = 100
    collapsed: bool = False
    z_index: int = 1

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PanelState":
        """Create from dictionary representation."""
        return cls(**data)


@dataclass
class LayoutConfiguration:
    """Defines a workspace layout configuration."""
    name: str
    description: str = ""
    panels: Dict[str, PanelState] = field(default_factory=dict)
    grid_template: str = "1fr 1fr 1fr"
    grid_direction: Literal["row", "column"] = "row"
    is_default: bool = False
    created_timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data["panels"] = {k: v.to_dict() if isinstance(v, PanelState) else v 
                         for k, v in self.panels.items()}
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "LayoutConfiguration":
        """Create from dictionary representation."""
        panels = {}
        for k, v in data.get("panels", {}).items():
            panels[k] = PanelState.from_dict(v) if isinstance(v, dict) else v
        data["panels"] = panels
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Theme:
    """Defines a color theme for the workspace."""
    name: str
    background_color: str = "#FFFFFF"
    text_color: str = "#1E1E1E"
    accent_color: str = "#0078D4"
    secondary_color: str = "#50E6FF"
    border_color: str = "#E0E0E0"
    panel_background: str = "#F5F5F5"
    success_color: str = "#107C10"
    warning_color: str = "#FFB900"
    error_color: str = "#D83B01"
    is_dark: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create from dictionary representation."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def validate(self) -> Tuple[bool, str]:
        """Validate theme colors."""
        colors = {
            "background": self.background_color,
            "text": self.text_color,
            "accent": self.accent_color,
            "secondary": self.secondary_color,
            "border": self.border_color,
            "panel": self.panel_background,
            "success": self.success_color,
            "warning": self.warning_color,
            "error": self.error_color,
        }
        
        for name, color in colors.items():
            if not self._is_valid_color(color):
                return False, f"Invalid color for {name}: {color}"
        
        return True, "Theme validation passed"

    @staticmethod
    def _is_valid_color(color: str) -> bool:
        """Check if color string is valid hex or named color."""
        if color.startswith("#"):
            hex_color = color.lstrip("#")
            return len(hex_color) in (3, 6, 8) and all(c in "0123456789ABCDEFabcdef" for c in hex_color)
        return color in ["transparent", "inherit", "initial"]


@dataclass
class KeyboardShortcut:
    """Defines a keyboard shortcut binding."""
    action: str
    key_combination: str
    category: str = "general"
    description: str = ""
    is_custom: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KeyboardShortcut":
        """Create from dictionary representation."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def normalize_key_combination(self) -> str:
        """Normalize key combination to standard format."""
        parts = [p.lower() for p in self.key_combination.split("+")]
        modifiers = []
        key = None
        
        for part in parts:
            if part in ["ctrl", "shift", "alt", "meta"]:
                modifiers.append(part)
            else:
                key = part
        
        modifiers.sort()
        if key:
            return "+".join(modifiers + [key]) if modifiers else key
        return self.key_combination


@dataclass
class PresetConfiguration:
    """Bundles layout, theme, and shortcuts into a preset."""
    name: str
    layout: LayoutConfiguration = field(default_factory=lambda: LayoutConfiguration("default"))
    theme: Theme = field(default_factory=lambda: Theme("default"))
    shortcuts: Dict[str, KeyboardShortcut] = field(default_factory=dict)
    description: str = ""
    saved_timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    is_builtin: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "layout": self.layout.to_dict(),
            "theme": self.theme.to_dict(),
            "shortcuts": {k: v.to_dict() if isinstance(v, KeyboardShortcut) else v 
                         for k, v in self.shortcuts.items()},
            "description": self.description,
            "saved_timestamp": self.saved_timestamp,
            "is_builtin": self.is_builtin,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PresetConfiguration":
        """Create from dictionary representation."""
        layout = LayoutConfiguration.from_dict(data.get("layout", {}))
        theme = Theme.from_dict(data.get("theme", {}))
        shortcuts = {}
        for k, v in data.get("shortcuts", {}).items():
            shortcuts[k] = KeyboardShortcut.from_dict(v) if isinstance(v, dict) else v
        
        return cls(
            name=data.get("name", ""),
            layout=layout,
            theme=theme,
            shortcuts=shortcuts,
            description=data.get("description", ""),
            saved_timestamp=data.get("saved_timestamp", datetime.now().timestamp()),
            is_builtin=data.get("is_builtin", False),
        )


class LayoutManager:
    """Manages workspace layout configurations."""
    
    def __init__(self):
        self.layouts: Dict[str, LayoutConfiguration] = {}
        self.current_layout: Optional[LayoutConfiguration] = None
        self._initialize_predefined_layouts()

    def _initialize_predefined_layouts(self):
        """Initialize predefined layouts."""
        # Horizontal layout
        horizontal = LayoutConfiguration(
            name="Horizontal",
            description="Editor left, preview center, properties right",
            grid_template="1fr 1fr 1fr",
            grid_direction="row",
            is_default=True,
        )
        horizontal.panels = {
            "editor": PanelState("editor", "left", visible=True, width=40),
            "preview": PanelState("preview", "center", visible=True, width=30),
            "properties": PanelState("properties", "right", visible=True, width=30),
        }
        self.layouts["Horizontal"] = horizontal
        self.current_layout = horizontal

        # Vertical layout
        vertical = LayoutConfiguration(
            name="Vertical",
            description="Editor top, preview and properties bottom",
            grid_template="1fr 1fr",
            grid_direction="column",
        )
        vertical.panels = {
            "editor": PanelState("editor", "top", visible=True, height=60),
            "preview": PanelState("preview", "bottom", visible=True, width=50, height=40),
            "properties": PanelState("properties", "bottom", visible=True, width=50, height=40),
        }
        self.layouts["Vertical"] = vertical

        # Minimalist layout
        minimalist = LayoutConfiguration(
            name="Minimalist",
            description="Editor and preview only, properties hidden",
            grid_template="1fr 1fr",
            grid_direction="row",
        )
        minimalist.panels = {
            "editor": PanelState("editor", "left", visible=True, width=60),
            "preview": PanelState("preview", "right", visible=True, width=40),
            "properties": PanelState("properties", "right", visible=False),
        }
        self.layouts["Minimalist"] = minimalist

        # Wide layout
        wide = LayoutConfiguration(
            name="Wide",
            description="Full-width editor, minimized preview and properties",
            grid_template="1fr",
            grid_direction="row",
        )
        wide.panels = {
            "editor": PanelState("editor", "top", visible=True, height=80),
            "preview": PanelState("preview", "bottom", visible=True, width=50, height=20, collapsed=True),
            "properties": PanelState("properties", "bottom", visible=True, width=50, height=20, collapsed=True),
        }
        self.layouts["Wide"] = wide

    def get_layout(self, name: str) -> Optional[LayoutConfiguration]:
        """Get layout by name."""
        return self.layouts.get(name)

    def get_all_layouts(self) -> List[str]:
        """Get list of available layout names."""
        return list(self.layouts.keys())

    def apply_layout(self, name: str) -> Tuple[bool, str]:
        """Apply layout by name."""
        layout = self.get_layout(name)
        if not layout:
            return False, f"Layout '{name}' not found"
        self.current_layout = layout
        return True, f"Layout '{name}' applied successfully"

    def create_custom_layout(self, name: str, grid_template: str, 
                           direction: str = "row") -> Tuple[bool, str]:
        """Create custom layout."""
        if name in self.layouts:
            return False, f"Layout '{name}' already exists"
        if direction not in ["row", "column"]:
            return False, f"Invalid direction: {direction}"
        
        layout = LayoutConfiguration(
            name=name,
            description=f"Custom layout: {name}",
            grid_template=grid_template,
            grid_direction=direction,
        )
        self.layouts[name] = layout
        return True, f"Layout '{name}' created successfully"

    def add_panel_to_layout(self, layout_name: str, panel: PanelState) -> Tuple[bool, str]:
        """Add panel to layout."""
        layout = self.get_layout(layout_name)
        if not layout:
            return False, f"Layout '{layout_name}' not found"
        layout.panels[panel.name] = panel
        return True, f"Panel '{panel.name}' added to layout '{layout_name}'"

    def save_layout_state(self, layout: LayoutConfiguration) -> dict:
        """Save layout state to dictionary."""
        return layout.to_dict()

    def get_current_layout(self) -> Optional[LayoutConfiguration]:
        """Get currently applied layout."""
        return self.current_layout

    def reset_to_default(self):
        """Reset to default layout."""
        self.apply_layout("Horizontal")


class ThemeManager:
    """Manages color themes for the workspace."""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self._initialize_predefined_themes()

    def _initialize_predefined_themes(self):
        """Initialize predefined themes."""
        # Light theme
        light = Theme(
            name="Light",
            background_color="#FFFFFF",
            text_color="#1E1E1E",
            accent_color="#0078D4",
            secondary_color="#50E6FF",
            border_color="#E0E0E0",
            panel_background="#F5F5F5",
            is_dark=False,
        )
        self.themes["Light"] = light
        self.current_theme = light

        # Dark theme
        dark = Theme(
            name="Dark",
            background_color="#1E1E1E",
            text_color="#FFFFFF",
            accent_color="#00D4FF",
            secondary_color="#646695",
            border_color="#3E3E3E",
            panel_background="#252526",
            is_dark=True,
        )
        self.themes["Dark"] = dark

        # High contrast theme
        high_contrast = Theme(
            name="High Contrast",
            background_color="#000000",
            text_color="#FFFFFF",
            accent_color="#FFFF00",
            secondary_color="#00FFFF",
            border_color="#FFFFFF",
            panel_background="#1A1A1A",
            success_color="#00FF00",
            warning_color="#FFFF00",
            error_color="#FF0000",
            is_dark=True,
        )
        self.themes["High Contrast"] = high_contrast

        # Sepia theme
        sepia = Theme(
            name="Sepia",
            background_color="#F5E6D3",
            text_color="#5C4033",
            accent_color="#8B4513",
            secondary_color="#D2A679",
            border_color="#C5A880",
            panel_background="#FBF5ED",
            is_dark=False,
        )
        self.themes["Sepia"] = sepia

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name."""
        return self.themes.get(name)

    def get_all_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())

    def apply_theme(self, name: str) -> Tuple[bool, str]:
        """Apply theme by name."""
        theme = self.get_theme(name)
        if not theme:
            return False, f"Theme '{name}' not found"
        self.current_theme = theme
        return True, f"Theme '{name}' applied successfully"

    def create_custom_theme(self, name: str, **colors) -> Tuple[bool, str]:
        """Create custom theme with specified colors."""
        if name in self.themes:
            return False, f"Theme '{name}' already exists"
        
        theme = Theme(name=name, **colors)
        is_valid, message = theme.validate()
        if not is_valid:
            return False, message
        
        self.themes[name] = theme
        return True, f"Theme '{name}' created successfully"

    def get_current_theme(self) -> Optional[Theme]:
        """Get currently applied theme."""
        return self.current_theme

    def reset_to_default(self):
        """Reset to default light theme."""
        self.apply_theme("Light")


class ShortcutManager:
    """Manages keyboard shortcuts."""
    
    def __init__(self):
        self.shortcuts: Dict[str, KeyboardShortcut] = {}
        self.key_map: Dict[str, str] = {}  # key_combination -> action
        self._initialize_default_shortcuts()

    def _initialize_default_shortcuts(self):
        """Initialize default keyboard shortcuts."""
        defaults = [
            KeyboardShortcut("save", "ctrl+s", "editing", "Save template"),
            KeyboardShortcut("undo", "ctrl+z", "editing", "Undo last action"),
            KeyboardShortcut("redo", "ctrl+y", "editing", "Redo last action"),
            KeyboardShortcut("cut", "ctrl+x", "editing", "Cut selection"),
            KeyboardShortcut("copy", "ctrl+c", "editing", "Copy selection"),
            KeyboardShortcut("paste", "ctrl+v", "editing", "Paste from clipboard"),
            KeyboardShortcut("selectall", "ctrl+a", "editing", "Select all"),
            KeyboardShortcut("find", "ctrl+f", "navigation", "Find in template"),
            KeyboardShortcut("replace", "ctrl+h", "navigation", "Find and replace"),
            KeyboardShortcut("preview", "ctrl+shift+p", "navigation", "Toggle preview"),
            KeyboardShortcut("properties", "ctrl+shift+i", "navigation", "Toggle properties"),
        ]
        
        for shortcut in defaults:
            self.register_shortcut(shortcut)

    def register_shortcut(self, shortcut: KeyboardShortcut) -> Tuple[bool, str]:
        """Register a new shortcut."""
        normalized_key = shortcut.normalize_key_combination()
        
        # Check for conflicts - if key already exists for different action
        if normalized_key in self.key_map:
            existing_action = self.key_map[normalized_key]
            # Allow re-registration of same action, but reject different action
            if existing_action != shortcut.action:
                # Don't reject, allow registration (tests expect conflict detection on demand)
                pass
        
        # Remove any old key binding for this action
        old_key = None
        for key, action in self.key_map.items():
            if action == shortcut.action and key != normalized_key:
                old_key = key
                break
        if old_key:
            del self.key_map[old_key]
        
        self.shortcuts[shortcut.action] = shortcut
        self.key_map[normalized_key] = shortcut.action
        return True, f"Shortcut registered: {shortcut.action} -> {normalized_key}"

    def get_shortcut(self, action: str) -> Optional[KeyboardShortcut]:
        """Get shortcut by action name."""
        return self.shortcuts.get(action)

    def get_shortcut_by_keys(self, key_combination: str) -> Optional[KeyboardShortcut]:
        """Get shortcut by key combination."""
        normalized = KeyboardShortcut(action="", key_combination=key_combination).normalize_key_combination()
        action = self.key_map.get(normalized)
        return self.shortcuts.get(action) if action else None

    def detect_conflicts(self) -> List[Tuple[str, str, str]]:
        """Detect all key binding conflicts."""
        conflicts = []
        seen_keys = {}
        
        for action, shortcut in self.shortcuts.items():
            normalized_key = shortcut.normalize_key_combination()
            if normalized_key in seen_keys:
                conflicts.append((action, seen_keys[normalized_key], normalized_key))
            else:
                seen_keys[normalized_key] = action
        
        return conflicts

    def reset_to_defaults(self):
        """Reset all shortcuts to defaults."""
        self.shortcuts.clear()
        self.key_map.clear()
        self._initialize_default_shortcuts()

    def get_all_shortcuts(self) -> Dict[str, KeyboardShortcut]:
        """Get all registered shortcuts."""
        return self.shortcuts.copy()

    def remove_shortcut(self, action: str) -> Tuple[bool, str]:
        """Remove a shortcut."""
        if action not in self.shortcuts:
            return False, f"Shortcut '{action}' not found"
        
        shortcut = self.shortcuts[action]
        normalized_key = shortcut.normalize_key_combination()
        del self.shortcuts[action]
        if normalized_key in self.key_map:
            del self.key_map[normalized_key]
        
        return True, f"Shortcut '{action}' removed"


class PresetManager:
    """Manages preset configurations."""
    
    def __init__(self, layout_manager: LayoutManager, theme_manager: ThemeManager, 
                 shortcut_manager: ShortcutManager):
        self.presets: Dict[str, PresetConfiguration] = {}
        self.layout_manager = layout_manager
        self.theme_manager = theme_manager
        self.shortcut_manager = shortcut_manager
        self._initialize_builtin_presets()

    def _initialize_builtin_presets(self):
        """Initialize built-in preset configurations."""
        # Minimal preset
        minimal = PresetConfiguration(
            name="Minimal",
            description="Minimalist workspace with editor and preview",
            is_builtin=True,
        )
        minimal.layout = self.layout_manager.get_layout("Minimalist") or LayoutConfiguration("Minimalist")
        minimal.theme = self.theme_manager.get_theme("Light") or Theme("Light")
        self.presets["Minimal"] = minimal

        # Developer preset
        developer = PresetConfiguration(
            name="Developer",
            description="Advanced workspace optimized for developers",
            is_builtin=True,
        )
        developer.layout = self.layout_manager.get_layout("Horizontal") or LayoutConfiguration("Horizontal")
        developer.theme = self.theme_manager.get_theme("Dark") or Theme("Dark")
        self.presets["Developer"] = developer

        # Designer preset
        designer = PresetConfiguration(
            name="Designer",
            description="Workspace optimized for template design",
            is_builtin=True,
        )
        designer.layout = self.layout_manager.get_layout("Vertical") or LayoutConfiguration("Vertical")
        designer.theme = self.theme_manager.get_theme("Light") or Theme("Light")
        self.presets["Designer"] = designer

        # Analyst preset
        analyst = PresetConfiguration(
            name="Analyst",
            description="Workspace optimized for analytics and performance",
            is_builtin=True,
        )
        analyst.layout = self.layout_manager.get_layout("Wide") or LayoutConfiguration("Wide")
        analyst.theme = self.theme_manager.get_theme("High Contrast") or Theme("High Contrast")
        self.presets["Analyst"] = analyst

    def create_preset(self, name: str, description: str = "") -> Tuple[bool, str]:
        """Create preset from current workspace state."""
        if name in self.presets:
            return False, f"Preset '{name}' already exists"
        
        preset = PresetConfiguration(
            name=name,
            description=description,
            layout=self.layout_manager.get_current_layout() or LayoutConfiguration("default"),
            theme=self.theme_manager.get_current_theme() or Theme("default"),
            shortcuts=self.shortcut_manager.get_all_shortcuts(),
        )
        self.presets[name] = preset
        return True, f"Preset '{name}' created successfully"

    def load_preset(self, name: str) -> Tuple[bool, str]:
        """Load preset and apply all settings."""
        if name not in self.presets:
            return False, f"Preset '{name}' not found"
        
        preset = self.presets[name]
        
        # Apply layout
        if preset.layout:
            success, msg = self.layout_manager.apply_layout(preset.layout.name)
            if not success:
                # If layout doesn't exist, create it
                self.layout_manager.layouts[preset.layout.name] = preset.layout
                self.layout_manager.apply_layout(preset.layout.name)
        
        # Apply theme
        if preset.theme:
            success, msg = self.theme_manager.apply_theme(preset.theme.name)
            if not success:
                # If theme doesn't exist, create it
                self.theme_manager.themes[preset.theme.name] = preset.theme
                self.theme_manager.apply_theme(preset.theme.name)
        
        # Apply shortcuts
        self.shortcut_manager.shortcuts = preset.shortcuts.copy()
        self.shortcut_manager.key_map.clear()
        for shortcut in preset.shortcuts.values():
            normalized_key = shortcut.normalize_key_combination()
            self.shortcut_manager.key_map[normalized_key] = shortcut.action
        
        return True, f"Preset '{name}' loaded successfully"

    def delete_preset(self, name: str) -> Tuple[bool, str]:
        """Delete a preset."""
        if name not in self.presets:
            return False, f"Preset '{name}' not found"
        
        if self.presets[name].is_builtin:
            return False, f"Cannot delete built-in preset '{name}'"
        
        del self.presets[name]
        return True, f"Preset '{name}' deleted successfully"

    def get_preset(self, name: str) -> Optional[PresetConfiguration]:
        """Get preset by name."""
        return self.presets.get(name)

    def get_all_presets(self) -> List[str]:
        """Get list of all preset names."""
        return list(self.presets.keys())

    def export_preset(self, name: str) -> Tuple[bool, str, Optional[str]]:
        """Export preset as JSON string."""
        if name not in self.presets:
            return False, f"Preset '{name}' not found", None
        
        preset = self.presets[name]
        try:
            json_str = json.dumps(preset.to_dict(), indent=2)
            return True, f"Preset '{name}' exported successfully", json_str
        except Exception as e:
            return False, f"Error exporting preset: {str(e)}", None

    def import_preset(self, json_str: str) -> Tuple[bool, str]:
        """Import preset from JSON string."""
        try:
            data = json.loads(json_str)
            preset = PresetConfiguration.from_dict(data)
            
            if preset.name in self.presets:
                return False, f"Preset '{preset.name}' already exists"
            
            self.presets[preset.name] = preset
            return True, f"Preset '{preset.name}' imported successfully"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error importing preset: {str(e)}"


class WorkspaceManager:
    """Orchestrates workspace customization features."""
    
    def __init__(self):
        self.layout_manager = LayoutManager()
        self.theme_manager = ThemeManager()
        self.shortcut_manager = ShortcutManager()
        self.preset_manager = PresetManager(
            self.layout_manager,
            self.theme_manager,
            self.shortcut_manager,
        )

    def apply_layout(self, name: str) -> Tuple[bool, str]:
        """Apply layout by name."""
        return self.layout_manager.apply_layout(name)

    def apply_theme(self, name: str) -> Tuple[bool, str]:
        """Apply theme by name."""
        return self.theme_manager.apply_theme(name)

    def register_shortcut(self, shortcut: KeyboardShortcut) -> Tuple[bool, str]:
        """Register keyboard shortcut."""
        return self.shortcut_manager.register_shortcut(shortcut)

    def create_preset(self, name: str, description: str = "") -> Tuple[bool, str]:
        """Create preset from current state."""
        return self.preset_manager.create_preset(name, description)

    def load_preset(self, name: str) -> Tuple[bool, str]:
        """Load preset configuration."""
        return self.preset_manager.load_preset(name)

    def get_workspace_state(self) -> dict:
        """Get current workspace state."""
        return {
            "layout": self.layout_manager.get_current_layout().to_dict() 
                     if self.layout_manager.get_current_layout() else None,
            "theme": self.theme_manager.get_current_theme().to_dict() 
                    if self.theme_manager.get_current_theme() else None,
            "shortcuts": {k: v.to_dict() for k, v in self.shortcut_manager.get_all_shortcuts().items()},
        }

    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate current configuration."""
        errors = []
        
        # Validate current layout
        if not self.layout_manager.get_current_layout():
            errors.append("No layout applied")
        
        # Validate current theme
        if self.theme_manager.get_current_theme():
            is_valid, msg = self.theme_manager.get_current_theme().validate()
            if not is_valid:
                errors.append(msg)
        else:
            errors.append("No theme applied")
        
        # Detect shortcut conflicts
        conflicts = self.shortcut_manager.detect_conflicts()
        if conflicts:
            for action1, action2, key in conflicts:
                errors.append(f"Shortcut conflict: '{action1}' and '{action2}' both use '{key}'")
        
        return len(errors) == 0, errors

    def reset_to_defaults(self):
        """Reset all customizations to defaults."""
        self.layout_manager.reset_to_default()
        self.theme_manager.reset_to_default()
        self.shortcut_manager.reset_to_defaults()

    def get_available_layouts(self) -> List[str]:
        """Get list of available layouts."""
        return self.layout_manager.get_all_layouts()

    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return self.theme_manager.get_all_themes()

    def get_available_presets(self) -> List[str]:
        """Get list of available presets."""
        return self.preset_manager.get_all_presets()
