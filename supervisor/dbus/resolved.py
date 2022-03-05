"""D-Bus interface for systemd-resolved."""
import logging

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.dbus import DBus
from .const import DBUS_NAME_RESOLVED, DBUS_OBJECT_RESOLVED
from .interface import DBusInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Resolved(DBusInterface):
    """Handle D-Bus interface for systemd-resolved."""

    name = DBUS_NAME_RESOLVED

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_RESOLVED, DBUS_OBJECT_RESOLVED)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-resolved.")
        except DBusInterfaceError:
            _LOGGER.warning(
                "Host has no systemd-resolved support. DNS will not work correctly."
            )
