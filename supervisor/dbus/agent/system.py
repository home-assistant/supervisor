"""System object for OS-Agent."""

from dbus_next.aio.message_bus import MessageBus

from ...utils.dbus import DBus
from ..const import DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_SYSTEM
from ..interface import DBusInterface
from ..utils import dbus_connected


class System(DBusInterface):
    """System object for OS Agent."""

    async def connect(self, bus: MessageBus) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(bus, DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_SYSTEM)

    @dbus_connected
    async def schedule_wipe_device(self) -> None:
        """Schedule a factory reset on next system boot."""
        await self.dbus.System.call_schedule_wipe_device()
