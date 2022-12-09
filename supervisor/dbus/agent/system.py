"""System object for OS-Agent."""

from ..const import DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_SYSTEM
from ..interface import DBusInterface
from ..utils import dbus_connected


class System(DBusInterface):
    """System object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_SYSTEM

    @dbus_connected
    async def schedule_wipe_device(self) -> None:
        """Schedule a factory reset on next system boot."""
        await self.dbus.System.call_schedule_wipe_device()
