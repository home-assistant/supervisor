"""System object for OS-Agent."""

from ...utils.gdbus import DBus
from ..const import DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_SYSTEM
from ..interface import DBusInterface
from ..utils import dbus_connected


class System(DBusInterface):
    """System object for OS Agent."""

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_SYSTEM)

    @dbus_connected
    async def schedule_wipe_device(self) -> bool:
        """Schedule a factory reset on next system boot."""
        return (await self.dbus.ScheduleWipeDevice())[0]
