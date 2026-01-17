"""
Issue #53: Panel Synchronization System

Keeps UI panels synchronized with application state changes,
ensuring consistency and live updates across all interfaces.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
from datetime import datetime
import hashlib


class SyncEvent(Enum):
    """Types of synchronization events."""
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"
    COMPONENT_MODIFIED = "component_modified"
    PROPERTY_CHANGED = "property_changed"
    SELECTION_CHANGED = "selection_changed"
    CANVAS_UPDATED = "canvas_updated"
    PANEL_VISIBILITY = "panel_visibility"
    THEME_CHANGED = "theme_changed"
    UNDO_REDO = "undo_redo"


class PanelType(Enum):
    """Types of UI panels."""
    PROPERTIES = "properties"
    HIERARCHY = "hierarchy"
    CANVAS = "canvas"
    HISTORY = "history"
    LIBRARY = "library"
    PREVIEW = "preview"
    SETTINGS = "settings"


@dataclass
class PanelState:
    """State of a UI panel."""
    panel_type: PanelType = PanelType.PROPERTIES
    visible: bool = True
    focused: bool = False
    position: Dict[str, int] = field(default_factory=dict)
    size: Dict[str, int] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    dirty: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'panel_type': self.panel_type.value,
            'visible': self.visible,
            'focused': self.focused,
            'position': self.position,
            'size': self.size,
            'data': self.data,
            'last_updated': self.last_updated.isoformat(),
            'dirty': self.dirty
        }


@dataclass
class SyncMessage:
    """A synchronization message."""
    event_type: SyncEvent = SyncEvent.COMPONENT_MODIFIED
    source_panel: PanelType = PanelType.CANVAS
    affected_panels: List[PanelType] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    is_critical: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type.value,
            'source_panel': self.source_panel.value,
            'affected_panels': [p.value for p in self.affected_panels],
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'is_critical': self.is_critical
        }


class PanelSyncManager:
    """
    Manages synchronization of UI panels with application state,
    ensuring all panels reflect current state and stay in sync.
    """

    def __init__(self):
        """Initialize panel synchronization manager."""
        self.panel_states: Dict[PanelType, PanelState] = {}
        self.listeners: Dict[PanelType, List[Callable]] = {}
        self.sync_queue: List[SyncMessage] = []
        self.max_queue_size = 100
        self.is_syncing = False
        self.sync_throttle_ms = 50
        self.last_sync_time = datetime.now()
        self.consistency_checks_enabled = True
        self.state_cache: Dict[str, str] = {}
        self.conflict_resolution_mode = "merge"  # merge, replace, manual
        self.pending_updates: Dict[PanelType, Dict[str, Any]] = {}

        # Initialize default panel states
        for panel_type in PanelType:
            self.panel_states[panel_type] = PanelState(panel_type=panel_type)
            self.listeners[panel_type] = []

    def register_panel(self, panel_type: PanelType, initial_data: Dict[str, Any] = None) -> bool:
        """
        Register a new panel for synchronization.
        
        Args:
            panel_type: Type of panel
            initial_data: Initial panel data
            
        Returns:
            True if successful
        """
        if panel_type in self.panel_states:
            return False

        self.panel_states[panel_type] = PanelState(
            panel_type=panel_type,
            data=initial_data or {}
        )
        self.listeners[panel_type] = []
        
        return True

    def unregister_panel(self, panel_type: PanelType) -> bool:
        """
        Unregister a panel from synchronization.
        
        Args:
            panel_type: Type of panel
            
        Returns:
            True if successful
        """
        if panel_type not in self.panel_states:
            return False

        del self.panel_states[panel_type]
        del self.listeners[panel_type]
        
        return True

    def update_panel_state(self, panel_type: PanelType, data: Dict[str, Any], 
                          source: str = "unknown") -> bool:
        """
        Update state of a panel.
        
        Args:
            panel_type: Type of panel to update
            data: New panel data
            source: Source of update
            
        Returns:
            True if successful
        """
        if panel_type not in self.panel_states:
            return False

        panel = self.panel_states[panel_type]
        
        # Check for changes
        if self._has_changes(panel.data, data):
            panel.data = data
            panel.last_updated = datetime.now()
            panel.dirty = True
            
            # Queue synchronization message
            affected = self._determine_affected_panels(panel_type, data)
            message = SyncMessage(
                event_type=SyncEvent.PANEL_VISIBILITY,
                source_panel=panel_type,
                affected_panels=affected,
                data=data
            )
            
            self._queue_sync_message(message)
            return True

        return False

    def sync_component_change(self, component_id: str, changes: Dict[str, Any], 
                             panel_type: PanelType) -> None:
        """
        Synchronize component changes across panels.
        
        Args:
            component_id: Component that changed
            changes: Changes made
            panel_type: Panel that initiated change
        """
        # Determine affected panels
        affected = self._determine_affected_panels(panel_type, changes)
        
        # Create synchronization message
        message = SyncMessage(
            event_type=SyncEvent.COMPONENT_MODIFIED,
            source_panel=panel_type,
            affected_panels=affected,
            data={
                'component_id': component_id,
                'changes': changes
            }
        )
        
        self._queue_sync_message(message)
        self._process_sync_queue()

    def sync_selection_change(self, selected_ids: List[str], panel_type: PanelType) -> None:
        """
        Synchronize selection changes across panels.
        
        Args:
            selected_ids: IDs of selected items
            panel_type: Panel that initiated change
        """
        affected = [p for p in PanelType if p != panel_type]
        
        message = SyncMessage(
            event_type=SyncEvent.SELECTION_CHANGED,
            source_panel=panel_type,
            affected_panels=affected,
            data={'selected_ids': selected_ids}
        )
        
        self._queue_sync_message(message)
        self._process_sync_queue()

    def set_panel_visibility(self, panel_type: PanelType, visible: bool) -> bool:
        """
        Set panel visibility and synchronize.
        
        Args:
            panel_type: Panel type
            visible: Visibility state
            
        Returns:
            True if changed
        """
        if panel_type not in self.panel_states:
            return False

        panel = self.panel_states[panel_type]
        if panel.visible == visible:
            return False

        panel.visible = visible
        panel.dirty = True

        message = SyncMessage(
            event_type=SyncEvent.PANEL_VISIBILITY,
            source_panel=panel_type,
            affected_panels=[PanelType.SETTINGS],
            data={'panel': panel_type.value, 'visible': visible},
            is_critical=False
        )

        self._queue_sync_message(message)
        self._notify_listeners(panel_type, message.to_dict())
        
        return True

    def set_panel_focus(self, panel_type: PanelType) -> bool:
        """
        Set focus to a panel.
        
        Args:
            panel_type: Panel to focus
            
        Returns:
            True if successful
        """
        # Remove focus from all panels
        for panel in self.panel_states.values():
            if panel.focused:
                panel.focused = False

        # Set focus on target panel
        if panel_type in self.panel_states:
            self.panel_states[panel_type].focused = True
            
            message = SyncMessage(
                event_type=SyncEvent.PANEL_VISIBILITY,
                source_panel=panel_type,
                data={'focused': True}
            )
            
            self._notify_listeners(panel_type, message.to_dict())
            return True

        return False

    def check_consistency(self) -> Dict[str, bool]:
        """
        Check consistency of all panel states.
        
        Returns:
            Dictionary of consistency checks
        """
        results = {}
        
        # Check if all panels have current data
        for panel_type, panel in self.panel_states.items():
            is_consistent = not panel.dirty
            results[panel_type.value] = is_consistent

        return results

    def resolve_conflict(self, panel_type: PanelType, remote_data: Dict[str, Any],
                        local_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve conflict between local and remote panel state.
        
        Args:
            panel_type: Panel with conflict
            remote_data: Remote state
            local_data: Local state
            
        Returns:
            Resolved state
        """
        if self.conflict_resolution_mode == "replace":
            return remote_data
        elif self.conflict_resolution_mode == "merge":
            return self._merge_states(local_data, remote_data)
        else:  # manual
            return local_data  # User will resolve manually

    def _merge_states(self, local: Dict[str, Any], remote: Dict[str, Any]) -> Dict[str, Any]:
        """Merge local and remote states intelligently."""
        merged = local.copy()
        
        for key, remote_value in remote.items():
            if key not in merged:
                merged[key] = remote_value
            elif isinstance(remote_value, dict) and isinstance(merged[key], dict):
                merged[key] = self._merge_states(merged[key], remote_value)
            else:
                # Remote takes precedence
                merged[key] = remote_value

        return merged

    def _determine_affected_panels(self, source: PanelType, 
                                  data: Dict[str, Any]) -> List[PanelType]:
        """Determine which panels are affected by a change."""
        affected = []

        # Component changes affect multiple panels
        if 'component_id' in data:
            affected = [PanelType.PROPERTIES, PanelType.HIERARCHY, 
                       PanelType.CANVAS, PanelType.PREVIEW]

        # Selection affects most panels
        elif 'selected_ids' in data:
            affected = [PanelType.PROPERTIES, PanelType.HIERARCHY, 
                       PanelType.CANVAS, PanelType.PREVIEW]

        # Remove source panel from affected list
        affected = [p for p in affected if p != source]

        return affected

    def _queue_sync_message(self, message: SyncMessage) -> None:
        """Queue a synchronization message."""
        self.sync_queue.append(message)

        # Limit queue size
        if len(self.sync_queue) > self.max_queue_size:
            self.sync_queue = self.sync_queue[-self.max_queue_size:]

    def _process_sync_queue(self) -> None:
        """Process queued synchronization messages."""
        if self.is_syncing or len(self.sync_queue) == 0:
            return

        # Check throttle
        elapsed = (datetime.now() - self.last_sync_time).total_seconds() * 1000
        if elapsed < self.sync_throttle_ms:
            return

        self.is_syncing = True

        try:
            # Process messages
            while self.sync_queue:
                message = self.sync_queue.pop(0)
                self._distribute_sync_message(message)

            # Run consistency check
            if self.consistency_checks_enabled:
                self.check_consistency()

        finally:
            self.is_syncing = False
            self.last_sync_time = datetime.now()

    def _distribute_sync_message(self, message: SyncMessage) -> None:
        """Distribute sync message to affected panels."""
        message_dict = message.to_dict()

        # Notify source panel
        self._notify_listeners(message.source_panel, message_dict)

        # Notify affected panels
        for panel_type in message.affected_panels:
            self._notify_listeners(panel_type, message_dict)

            # Update panel state if needed
            if panel_type in self.panel_states:
                self.pending_updates[panel_type] = message.data

    def _notify_listeners(self, panel_type: PanelType, message_data: Dict[str, Any]) -> None:
        """Notify all listeners of a panel."""
        if panel_type not in self.listeners:
            return

        for listener in self.listeners[panel_type]:
            try:
                listener(message_data)
            except Exception:
                pass

    def _has_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Check if data has changed."""
        return self._compute_hash(old_data) != self._compute_hash(new_data)

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute hash of data for change detection."""
        import json
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception:
            return ""

    def add_listener(self, panel_type: PanelType, listener: Callable) -> None:
        """Add event listener for panel."""
        if panel_type not in self.listeners:
            self.listeners[panel_type] = []

        if listener not in self.listeners[panel_type]:
            self.listeners[panel_type].append(listener)

    def remove_listener(self, panel_type: PanelType, listener: Callable) -> None:
        """Remove event listener from panel."""
        if panel_type in self.listeners and listener in self.listeners[panel_type]:
            self.listeners[panel_type].remove(listener)

    def get_panel_state(self, panel_type: PanelType) -> Optional[PanelState]:
        """Get current state of a panel."""
        return self.panel_states.get(panel_type)

    def get_all_panel_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all panels."""
        return {
            panel_type.value: panel.to_dict()
            for panel_type, panel in self.panel_states.items()
        }

    def reset_panel(self, panel_type: PanelType) -> bool:
        """Reset panel to default state."""
        if panel_type not in self.panel_states:
            return False

        self.panel_states[panel_type] = PanelState(panel_type=panel_type)
        
        message = SyncMessage(
            event_type=SyncEvent.PANEL_VISIBILITY,
            source_panel=panel_type,
            data={'reset': True}
        )
        
        self._notify_listeners(panel_type, message.to_dict())
        return True

    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics."""
        dirty_panels = sum(1 for p in self.panel_states.values() if p.dirty)
        
        return {
            'total_panels': len(self.panel_states),
            'dirty_panels': dirty_panels,
            'queue_size': len(self.sync_queue),
            'is_syncing': self.is_syncing,
            'consistency_ok': all(self.check_consistency().values())
        }

    def force_full_sync(self) -> None:
        """Force full synchronization of all panels."""
        for panel_type, panel in self.panel_states.items():
            if panel.dirty:
                message = SyncMessage(
                    event_type=SyncEvent.CANVAS_UPDATED,
                    source_panel=panel_type,
                    data=panel.data,
                    is_critical=True
                )
                self._queue_sync_message(message)

        self._process_sync_queue()

    def clear_sync_queue(self) -> int:
        """Clear all pending sync messages."""
        count = len(self.sync_queue)
        self.sync_queue.clear()
        return count

    def set_throttle_ms(self, ms: int) -> None:
        """Set synchronization throttle time in milliseconds."""
        self.sync_throttle_ms = max(0, ms)

    def enable_consistency_checks(self, enabled: bool) -> None:
        """Enable or disable consistency checking."""
        self.consistency_checks_enabled = enabled

    def get_pending_updates(self, panel_type: PanelType) -> Dict[str, Any]:
        """Get pending updates for a panel."""
        updates = self.pending_updates.get(panel_type, {})
        if panel_type in self.pending_updates:
            del self.pending_updates[panel_type]
        return updates
