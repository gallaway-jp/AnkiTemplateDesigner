"""Event collection and tracking for analytics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
from threading import RLock
import uuid


@dataclass
class Event:
    """Represents a tracked event."""
    event_type: str
    timestamp: datetime
    event_id: str
    user_id: Optional[str]
    category: str
    data: Dict[str, Any]
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'event_id': self.event_id,
            'user_id': self.user_id,
            'category': self.category,
            'data': self.data,
            'duration_ms': self.duration_ms,
            'error': self.error,
            'metadata': self.metadata or {},
        }


class EventCollector:
    """Collects and buffers analytics events."""

    def __init__(self, batch_size: int = 100, user_id: Optional[str] = None):
        """Initialize event collector.
        
        Args:
            batch_size: Number of events to buffer before batch
            user_id: Optional user identifier
        """
        self.batch_size = batch_size
        self.user_id = user_id
        self.event_queue: deque = deque(maxlen=10000)
        self.lock = RLock()
        self.event_count = 0
        self.filters: Dict[str, bool] = {}
        self.sampling_rate = 1.0

    def track(
        self,
        event_type: str,
        category: str,
        data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track an event.
        
        Args:
            event_type: Type of event
            category: Event category
            data: Event data dictionary
            duration_ms: Optional duration in milliseconds
            error: Optional error message
            metadata: Optional metadata
            
        Returns:
            Event ID
        """
        with self.lock:
            # Check filter
            if event_type in self.filters and not self.filters[event_type]:
                return ""

            # Check sampling
            import random
            if random.random() > self.sampling_rate:
                return ""

            event_id = str(uuid.uuid4())
            event = Event(
                event_type=event_type,
                timestamp=datetime.now(),
                event_id=event_id,
                user_id=self.user_id,
                category=category,
                data=data or {},
                duration_ms=duration_ms,
                error=error,
                metadata=metadata,
            )

            self.event_queue.append(event)
            self.event_count += 1

            return event_id

    def batch_events(self, size: Optional[int] = None) -> List[Event]:
        """Get batch of events.
        
        Args:
            size: Batch size (default: self.batch_size)
            
        Returns:
            List of events
        """
        with self.lock:
            batch_size = size or self.batch_size
            batch = []

            while len(batch) < batch_size and self.event_queue:
                batch.append(self.event_queue.popleft())

            return batch

    def peek_events(self, size: int = 10) -> List[Event]:
        """Peek at events without removing them.
        
        Args:
            size: Number of events to peek
            
        Returns:
            List of events
        """
        with self.lock:
            return list(self.event_queue)[:size]

    def flush_events(self) -> int:
        """Get all remaining events and clear queue.
        
        Returns:
            Number of events flushed
        """
        with self.lock:
            count = len(self.event_queue)
            self.event_queue.clear()
            return count

    def get_event_count(self) -> int:
        """Get total events tracked.
        
        Returns:
            Event count
        """
        with self.lock:
            return self.event_count

    def get_queue_size(self) -> int:
        """Get current queue size.
        
        Returns:
            Queue size
        """
        with self.lock:
            return len(self.event_queue)

    def set_filter(self, event_type: str, enabled: bool) -> bool:
        """Enable/disable event type.
        
        Args:
            event_type: Event type to filter
            enabled: Whether to track this event type
            
        Returns:
            True if set successfully
        """
        with self.lock:
            self.filters[event_type] = enabled
            return True

    def get_filter(self, event_type: str) -> Optional[bool]:
        """Get filter status for event type.
        
        Args:
            event_type: Event type
            
        Returns:
            Filter status or None if not set
        """
        with self.lock:
            return self.filters.get(event_type)

    def set_sampling_rate(self, rate: float) -> bool:
        """Set event sampling rate.
        
        Args:
            rate: Sampling rate (0.0 to 1.0)
            
        Returns:
            True if set successfully
        """
        with self.lock:
            if 0.0 <= rate <= 1.0:
                self.sampling_rate = rate
                return True
            return False

    def get_sampling_rate(self) -> float:
        """Get current sampling rate.
        
        Returns:
            Sampling rate
        """
        with self.lock:
            return self.sampling_rate

    def clear(self) -> None:
        """Clear all events."""
        with self.lock:
            self.event_queue.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get collector statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            return {
                'total_events': self.event_count,
                'queue_size': len(self.event_queue),
                'batch_size': self.batch_size,
                'sampling_rate': self.sampling_rate,
                'filters_count': len(self.filters),
            }
