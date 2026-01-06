#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event-Driven Architecture Core
Observer pattern implementation for loose coupling
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import threading
from collections import defaultdict


class EventType(Enum):
    """Event types enumeration"""
    OPTIMIZATION_STARTED = "optimization_started"
    OPTIMIZATION_COMPLETED = "optimization_completed"
    OPTIMIZATION_FAILED = "optimization_failed"
    OPTIMIZER_STARTED = "optimizer_started"
    OPTIMIZER_COMPLETED = "optimizer_completed"
    BACKUP_STARTED = "backup_started"
    BACKUP_COMPLETED = "backup_completed"
    RESTORE_STARTED = "restore_started"
    RESTORE_COMPLETED = "restore_completed"
    SERVICE_DISABLED = "service_disabled"
    REGISTRY_CHANGED = "registry_changed"
    PROGRESS_UPDATE = "progress_update"
    ERROR_OCCURRED = "error_occurred"
    WARNING_OCCURRED = "warning_occurred"


@dataclass
class Event:
    """Base event class"""
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = datetime.now()


class EventHandler(ABC):
    """Abstract event handler interface"""
    
    @abstractmethod
    def handle(self, event: Event) -> None:
        """Handle an event"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: EventType) -> bool:
        """Check if handler can handle event type"""
        pass


class EventBus:
    """
    Event Bus implementation
    Central event dispatcher using Observer pattern
    Thread-safe implementation
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._callbacks: Dict[EventType, List[Callable[[Event], None]]] = defaultdict(list)
        self._lock = threading.RLock()
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe handler to event type"""
        with self._lock:
            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)
    
    def subscribe_callback(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Subscribe callback function to event type"""
        with self._lock:
            if callback not in self._callbacks[event_type]:
                self._callbacks[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe handler from event type"""
        with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
    
    def publish(self, event: Event) -> None:
        """
        Publish event to all subscribers
        Thread-safe event dispatching
        """
        with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Notify handlers
            handlers = self._handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    if handler.can_handle(event.event_type):
                        handler.handle(event)
                except Exception as e:
                    # Log error but don't stop event propagation
                    print(f"Error in event handler {handler.__class__.__name__}: {e}")
            
            # Notify callbacks
            callbacks = self._callbacks.get(event.event_type, [])
            for callback in callbacks:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def publish_sync(self, event: Event) -> None:
        """Publish event synchronously (blocking)"""
        self.publish(event)
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get event history"""
        with self._lock:
            if event_type:
                filtered = [e for e in self._event_history if e.event_type == event_type]
                return filtered[-limit:]
            return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        with self._lock:
            self._event_history.clear()
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get number of subscribers for event type"""
        with self._lock:
            return len(self._handlers[event_type]) + len(self._callbacks[event_type])


# Singleton instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get singleton EventBus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

