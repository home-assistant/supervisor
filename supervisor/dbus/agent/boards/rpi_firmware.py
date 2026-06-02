"""Raspberry Pi firmware management."""

from collections.abc import Awaitable

from ...const import (
    DBUS_ATTR_BLOCKED_REASON,
    DBUS_ATTR_CURRENT_VERSION,
    DBUS_ATTR_LATEST_VERSION,
    DBUS_ATTR_UPDATE_AVAILABLE,
    DBUS_ATTR_UPDATE_BLOCKED,
    DBUS_ATTR_UPDATE_PENDING,
    DBUS_IFACE_HAOS_BOARDS_RPI_FIRMWARE,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS_BOARDS_RPI_FIRMWARE,
)
from ...interface import DBusInterfaceProxy, dbus_property
from ...utils import dbus_connected


class RPiFirmware(DBusInterfaceProxy):
    """Raspberry Pi firmware proxy.

    The os-agent registers `io.hass.os.Boards.RaspberryPi.Firmware` whenever
    the host is a Raspberry Pi 4 / 5 or a Yellow (CM4 / CM5). It is a standalone
    D-Bus object, not a board: all properties are read-only and the single
    `Update` method bundles bootloader + (where present) VL805 firmware updates.
    """

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_BOARDS_RPI_FIRMWARE
    properties_interface: str = DBUS_IFACE_HAOS_BOARDS_RPI_FIRMWARE
    sync_properties: bool = True

    @property
    @dbus_property
    def current_version(self) -> str | None:
        """Composite installed firmware version string."""
        return self.properties[DBUS_ATTR_CURRENT_VERSION]

    @property
    @dbus_property
    def latest_version(self) -> str | None:
        """Composite available firmware version string."""
        return self.properties[DBUS_ATTR_LATEST_VERSION]

    @property
    @dbus_property
    def update_available(self) -> bool:
        """Return True if a newer firmware (bootloader EEPROM or VL805) is available."""
        return self.properties[DBUS_ATTR_UPDATE_AVAILABLE]

    @property
    @dbus_property
    def update_blocked(self) -> bool:
        """Return True if the current boot device does not support an update."""
        return self.properties[DBUS_ATTR_UPDATE_BLOCKED]

    @property
    @dbus_property
    def update_pending(self) -> bool:
        """Return True if an update was applied and a reboot is still pending."""
        return self.properties[DBUS_ATTR_UPDATE_PENDING]

    @property
    @dbus_property
    def blocked_reason(self) -> str | None:
        """Blocked reason; None when not blocked.

        Currently, the only emitted value is `unsupported_boot_device`. It is
        used universally whenever the OS Agent reports `update_blocked`,
        even though the actual cause varies (e.g. CM4 without self-update
        enabled, or USB/NVMe boot device). Treat this as a coarse "the update
        cannot be applied here" signal rather than a precise diagnosis;
        more specific values may be introduced in the future.
        """
        return self.properties[DBUS_ATTR_BLOCKED_REASON] or None

    @dbus_connected
    def update_firmware(self) -> Awaitable[None]:
        """Apply the bundled firmware (bootloader EEPROM and VL805 where present) update."""
        return self.connected_dbus.Boards.RaspberryPi.Firmware.call("update")
