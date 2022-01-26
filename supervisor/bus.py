"""Bus event system."""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

import attr

from .const import BusEvent
from .coresys import CoreSys, CoreSysAttributes

_LOGGER: logging.Logger = logging.getLogger(__name__)


@attr.s(slots=True, frozen=True)
class EventListener:
    """Event listener."""

    event_type: BusEvent = attr.ib()
    callback: Callable[[Any], Awaitable[None]] = attr.ib()


class Bus(CoreSysAttributes):
    """Handle Bus event system."""

    def __init__(self, coresys: CoreSys):
        """Initialize bus backend."""
        self.coresys = coresys
        self._listeners: dict[BusEvent, list[EventListener]] = {}

    def register_event(
        self, event: BusEvent, callback: Callable[[Any], Awaitable[None]]
    ) -> EventListener:
        """Register callback for an event."""
        listener = EventListener(event, callback)
        self._listeners.setdefault(event, []).append(listener)
        return listener

    def fire_event(self, event: BusEvent, reference: Any) -> None:
        """Fire an event to the bus."""
        _LOGGER.debug("Fire event '%s' with '%s'", event, reference)
        for listener in self._listeners.get(event, []):
            self.sys_create_task(listener.callback(reference))

    def remove_listener(self, listener: EventListener) -> None:
        """Unregister an listener."""
        try:
            self._listeners[listener.event_type].remove(listener)
        except (ValueError, KeyError):
            _LOGGER.warning("Listener %s not registered", listener)
