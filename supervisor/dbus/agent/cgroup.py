"""CGroup object for OS-Agent."""

from ...utils.gdbus import DBus
from ..const import DBUS_NAME_HAOS_CGROUP, DBUS_OBJECT_HAOS_CGROUP
from ..interface import DBusInterface
from ..utils import dbus_connected


class CGroup(DBusInterface):
    """CGroup object for OS Agent."""

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_HAOS_CGROUP, DBUS_OBJECT_HAOS_CGROUP)

    @dbus_connected
    async def add_devices_allowed(self, container_id: str, permission: str) -> bool:
        """Update cgroup devices and add new devices."""
        return await self.dbus.AddDevicesAllowed(container_id, permission)[0]
