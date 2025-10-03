"""
Event system for CatGen - enables decoupled communication between components
"""

from typing import Callable, Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger('catgen.events')


class EventType(Enum):
    """All possible events in the application"""
    # Cat events
    CAT_ADDED = "cat_added"
    CAT_UPDATED = "cat_updated"
    CAT_DELETED = "cat_deleted"
    CAT_VALIDATED = "cat_validated"
    
    # Breeding events
    LITTER_GENERATED = "litter_generated"
    LITTER_SAVED = "litter_saved"
    BREEDING_STARTED = "breeding_started"
    
    # Registry events
    REGISTRY_LOADED = "registry_loaded"
    REGISTRY_SAVED = "registry_saved"
    REGISTRY_CLEARED = "registry_cleared"
    REGISTRY_MODIFIED = "registry_modified"
    
    # Gene events
    GENE_ADDED = "gene_added"
    GENE_MODIFIED = "gene_modified"
    GENE_DELETED = "gene_deleted"
    GENES_RELOADED = "genes_reloaded"
    
    # UI events
    SELECTION_CHANGED = "selection_changed"
    FILTER_APPLIED = "filter_applied"
    TAB_CHANGED = "tab_changed"
    
    # System events
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"
    CACHE_INVALIDATED = "cache_invalidated"


@dataclass
class Event:
    """Event data container"""
    event_type: EventType
    data: Any
    timestamp: datetime
    source: Optional[str] = None
    
    def __repr__(self):
        return f"Event({self.event_type.value}, source={self.source}, time={self.timestamp})"


class EventBus:
    """
    Centralized event management system
    Implements the Observer pattern for loose coupling between components
    """
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._enabled = True
        
    def subscribe(self, event_type: EventType, callback: Callable, priority: int = 0):
        """
        Subscribe to an event type
        
        Args:
            event_type: The event to listen for
            callback: Function to call when event occurs (receives Event object)
            priority: Higher priority callbacks are called first (default 0)
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append((priority, callback))
        # Sort by priority (highest first)
        self._listeners[event_type].sort(key=lambda x: x[0], reverse=True)
        
        logger.debug(f"Subscribed to {event_type.value}: {callback.__name__}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Remove a callback from an event type"""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                (p, cb) for p, cb in self._listeners[event_type] 
                if cb != callback
            ]
            logger.debug(f"Unsubscribed from {event_type.value}: {callback.__name__}")
    
    def emit(self, event_type: EventType, data: Any = None, source: str = None):
        """
        Emit an event to all subscribers
        
        Args:
            event_type: The event to emit
            data: Data to pass to listeners
            source: Optional identifier of what emitted the event
        """
        if not self._enabled:
            return
        
        event = Event(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        logger.debug(f"Emitting event: {event}")
        
        # Call all listeners
        if event_type in self._listeners:
            for priority, callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(
                        f"Error in event listener {callback.__name__} "
                        f"for {event_type.value}: {e}",
                        exc_info=True
                    )
    
    def clear_listeners(self, event_type: Optional[EventType] = None):
        """Clear all listeners for an event type, or all listeners if None"""
        if event_type is None:
            self._listeners.clear()
            logger.info("Cleared all event listeners")
        else:
            self._listeners[event_type] = []
            logger.info(f"Cleared listeners for {event_type.value}")
    
    def get_history(self, event_type: Optional[EventType] = None, 
                    limit: int = 100) -> List[Event]:
        """Get recent event history"""
        if event_type is None:
            return self._event_history[-limit:]
        else:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
    
    def enable(self):
        """Enable event emission"""
        self._enabled = True
        logger.info("Event bus enabled")
    
    def disable(self):
        """Temporarily disable event emission (useful for batch operations)"""
        self._enabled = False
        logger.info("Event bus disabled")
    
    def __repr__(self):
        total_listeners = sum(len(listeners) for listeners in self._listeners.values())
        return f"EventBus(listeners={total_listeners}, history={len(self._event_history)})"


# Global event bus instance
_event_bus = None

def get_event_bus() -> EventBus:
    """Get the global event bus instance (singleton pattern)"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus():
    """Reset the global event bus (mainly for testing)"""
    global _event_bus
    _event_bus = EventBus()