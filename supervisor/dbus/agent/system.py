"""System object for OS-Agent."""

from ..const import DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_SYSTEM
from ..interface import DBusInterface
from ..utils import dbus_connected


class System(DBusInterface):
    """System object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_SYSTEM

    @dbus_connected
    async def schedule_wipe_device(self) -> bool:
        """Schedule a factory reset on next system boot."""
        return await self.connected_dbus.System.call("schedule_wipe_device")

    @dbus_connected
    async def migrate_docker_storage_driver(self, backend: str) -> None:
        """Migrate Docker storage driver."""
        await self.connected_dbus.System.call("migrate_docker_storage_driver", backend)

    @dbus_connected
    async def add_ssh_auth_key(self, key: str) -> None:
        """Append a public key to root's SSH authorized keys on the host.

        OS Agent writes the string verbatim to the authorized_keys file, so
        callers must validate it first.
        """
        await self.connected_dbus.System.call("add_ssh_auth_key", key)

    @dbus_connected
    async def clear_ssh_auth_keys(self) -> None:
        """Remove all of root's SSH authorized keys on the host."""
        await self.connected_dbus.System.call("clear_ssh_auth_keys")
