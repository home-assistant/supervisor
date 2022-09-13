"""CGroup object for OS-Agent."""

from dbus_next.aio.message_bus import MessageBus

from ...utils.dbus import DBus
from ..const import DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_CGROUP
from ..interface import DBusInterface
from ..utils import dbus_connected


class CGroup(DBusInterface):
    """CGroup object for OS Agent."""

    async def connect(self, bus: MessageBus) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(bus, DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_CGROUP)

    @dbus_connected
    async def add_devices_allowed(self, container_id: str, permission: str) -> None:
        """Update cgroup devices and add new devices."""
        await self.dbus.CGroup.call_add_devices_allowed(container_id, permission)
