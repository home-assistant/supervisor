"""Network Manager implementation for DBUS."""

import logging
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from ...exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from ..const import DBUS_NAME_NM, DBUS_OBJECT_SETTINGS
from ..interface import DBusInterface
from ..network.setting import NetworkSetting
from ..utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManagerSettings(DBusInterface):
    """Handle D-Bus interface for Network Manager Connection Settings Profile Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Settings.html
    """

    bus_name: str = DBUS_NAME_NM
    object_path: str = DBUS_OBJECT_SETTINGS

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to Network Manager Settings")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning(
                "No Network Manager Settings support on the host. Local network functions have been disabled."
            )

    @dbus_connected
    async def add_connection(self, settings: Any) -> NetworkSetting:
        """Add new connection."""
        obj_con_setting = await self.connected_dbus.Settings.call(
            "add_connection", settings
        )
        con_setting = NetworkSetting(obj_con_setting)
        await con_setting.connect(self.connected_dbus.bus)
        return con_setting

    @dbus_connected
    async def reload_connections(self) -> bool:
        """Reload all local connection files."""
        return await self.connected_dbus.Settings.call("reload_connections")
