"""Network Manager implementation for DBUS."""
import logging
from typing import Any

from dbus_next.aio.message_bus import MessageBus

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.dbus import DBus
from ..const import DBUS_NAME_NM, DBUS_OBJECT_SETTINGS
from ..interface import DBusInterface
from ..network.setting import NetworkSetting
from ..utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManagerSettings(DBusInterface):
    """Handle D-Bus interface for Network Manager Connection Settings Profile Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Settings.html
    """

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(bus, DBUS_NAME_NM, DBUS_OBJECT_SETTINGS)
        except DBusError:
            _LOGGER.warning("Can't connect to Network Manager Settings")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No Network Manager Settings support on the host. Local network functions have been disabled."
            )

    @dbus_connected
    async def add_connection(self, settings: Any) -> NetworkSetting:
        """Add new connection."""
        obj_con_setting = (
            await self.dbus.Settings.AddConnection(("a{sa{sv}}", settings))
        )[0]
        con_setting = NetworkSetting(obj_con_setting)
        await con_setting.connect(self.dbus.bus)
        return con_setting

    @dbus_connected
    async def reload_connections(self) -> bool:
        """Reload all local connection files."""
        return (await self.dbus.Settings.ReloadConnections())[0]
