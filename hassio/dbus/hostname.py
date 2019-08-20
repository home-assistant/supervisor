"""D-Bus interface for hostname."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER = logging.getLogger(__name__)


class Hostname(DBusInterface):
    """Handle D-Bus interface for hostname/system."""

    dbus_name = "org.freedesktop.hostname1"
    dbus_path = "/org/freedesktop/hostname1"
    dbus_interface = "org.freedesktop.hostname1"
    interface_property = [
        "StaticHostname",
        "Chassis",
        "Deployment",
        "KernelRelease",
        "OperatingSystemPrettyName",
        "OperatingSystemCPEName",
    ]

    @dbus_connected
    def set_static_hostname(self, hostname: str):
        """Change local hostname."""
        return self.interface.call_setstatichostname(hostname, False)
