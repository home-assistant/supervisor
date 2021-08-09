"""Bus event system."""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, List

import attr

from .const import BusEvent
from .coresys import CoreSys, CoreSysAttributes

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Bus(CoreSysAttributes):
    """Handle Bus event system."""

    def __init__(self, coresys: CoreSys):
        """Initialize bus backend."""
        self.coresys = coresys
        self._listeners: Dict[BusEvent, List[EventListener]] = {}

    def register_event(
        self, event: BusEvent, callback: Callable[[Any], Awaitable[None]]
    ) -> EventListener:
        """Register callback for an event."""
        listener = EventListener(event, callback)
        self._listeners.setdefault(event, []).append(listener)
        return listener

    def fire_event(self, event: BusEvent, reference: Any) -> None:
        """Fire an event to the bus."""
        for listener in self._listeners.get(event, []):
            self.sys_create_task(listener.callback(reference))


@attr.s(slots=True, frozen=True)
class EventListener:
    """Event listener."""

    event_type: BusEvent = attr.ib()
    callback: Callable[[Any], Awaitable[None]] = attr.ib()
