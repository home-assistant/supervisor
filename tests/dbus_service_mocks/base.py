"""Baseclass for a dbus service mock."""

import asyncio
from functools import wraps
from typing import Any

from dbus_fast import Message
from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.service import ServiceInterface, method


class DBusServiceMock(ServiceInterface):
    """Base dbus service mock."""

    object_path: str
    interface: str
    bus: MessageBus | None = None

    def __init__(self):
        """Initialize dbus service mock."""
        super().__init__(self.interface)

    def export(self, bus: MessageBus) -> "DBusServiceMock":
        """Export object onto bus."""
        self.bus = bus
        bus.export(self.object_path, self)
        return self

    async def ping(self, *, sleep: bool = True):
        """Ping object to check for signals."""
        await self.bus.call(
            Message(
                destination=self.bus.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path=self.object_path,
                member="Ping",
            )
        )
        # This is called to force dbus to process messages for the object
        # So in general we sleep(0) after to clear the new task
        if sleep:
            await asyncio.sleep(0)


def dbus_method(name: str = None, disabled: bool = False, track_obj_path: bool = False):
    """Make DBus method with call tracking.

    Identical to dbus_fast.service.method wrapper except all calls to it are tracked.
    Can then test that methods with no output were called or the right arguments were
    used if the output is static.
    """
    orig_decorator = method(name=name, disabled=disabled)

    def decorator(func):
        calls: list[list[Any]] = []

        @wraps(func)
        def track_calls(self: DBusServiceMock, *args):
            if track_obj_path:
                calls.append((self.object_path, *args))
            else:
                calls.append(args)
            return func(self, *args)

        wrapped = orig_decorator(track_calls)
        wrapped.__dict__["calls"] = calls

        return wrapped

    return decorator
