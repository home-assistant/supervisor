"""CGroup object for OS-Agent."""

from ..const import DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_CGROUP
from ..interface import DBusInterface
from ..utils import dbus_connected


class CGroup(DBusInterface):
    """CGroup object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_CGROUP

    @dbus_connected
    async def add_devices_allowed(self, container_id: str, permission: str) -> None:
        """Update cgroup devices and add new devices."""
        await self.connected_dbus.CGroup.call(
            "add_devices_allowed", container_id, permission
        )
