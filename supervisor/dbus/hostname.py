"""D-Bus interface for hostname."""

import logging

from dbus_fast.aio.message_bus import MessageBus

from ..exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from .const import (
    DBUS_ATTR_CHASSIS,
    DBUS_ATTR_DEPLOYMENT,
    DBUS_ATTR_KERNEL_RELEASE,
    DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME,
    DBUS_ATTR_STATIC_HOSTNAME,
    DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME,
    DBUS_IFACE_HOSTNAME,
    DBUS_NAME_HOSTNAME,
    DBUS_OBJECT_HOSTNAME,
)
from .interface import DBusInterfaceProxy, dbus_property
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Hostname(DBusInterfaceProxy):
    """Handle D-Bus interface for hostname/system.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.hostname1.html
    """

    name: str = DBUS_NAME_HOSTNAME
    bus_name: str = DBUS_NAME_HOSTNAME
    object_path: str = DBUS_OBJECT_HOSTNAME
    properties_interface: str = DBUS_IFACE_HOSTNAME

    async def connect(self, bus: MessageBus):
        """Connect to system's D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-hostname")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning(
                "No hostname support on the host. Hostname functions have been disabled."
            )

    @property
    @dbus_property
    def hostname(self) -> str | None:
        """Return local hostname."""
        return self.properties[DBUS_ATTR_STATIC_HOSTNAME]

    @property
    @dbus_property
    def chassis(self) -> str | None:
        """Return local chassis type."""
        return self.properties[DBUS_ATTR_CHASSIS]

    @property
    @dbus_property
    def deployment(self) -> str | None:
        """Return local deployment type."""
        return self.properties[DBUS_ATTR_DEPLOYMENT]

    @property
    @dbus_property
    def kernel(self) -> str | None:
        """Return local kernel version."""
        return self.properties[DBUS_ATTR_KERNEL_RELEASE]

    @property
    @dbus_property
    def operating_system(self) -> str | None:
        """Return local operating system."""
        return self.properties[DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME]

    @property
    @dbus_property
    def cpe(self) -> str | None:
        """Return local CPE."""
        return self.properties[DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME]

    @dbus_connected
    async def set_static_hostname(self, hostname: str) -> None:
        """Change local hostname."""
        await self.connected_dbus.call("set_static_hostname", hostname, False)
