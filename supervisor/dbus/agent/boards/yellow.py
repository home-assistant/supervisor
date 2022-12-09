"""Yellow board management."""

import asyncio

from ...const import DBUS_ATTR_DISK_LED, DBUS_ATTR_HEARTBEAT_LED, DBUS_ATTR_POWER_LED
from ...interface import dbus_property
from .const import BOARD_NAME_YELLOW
from .interface import BoardProxy


class Yellow(BoardProxy):
    """Yellow board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_YELLOW)

    @property
    @dbus_property
    def heartbeat_led(self) -> bool:
        """Get heartbeat LED enabled."""
        return self.properties[DBUS_ATTR_HEARTBEAT_LED]

    @heartbeat_led.setter
    def heartbeat_led(self, enabled: bool) -> None:
        """Enable/disable heartbeat LED."""
        asyncio.create_task(self.dbus.Boards.Yellow.set_heartbeat_led(enabled))

    @property
    @dbus_property
    def power_led(self) -> bool:
        """Get power LED enabled."""
        return self.properties[DBUS_ATTR_POWER_LED]

    @power_led.setter
    def power_led(self, enabled: bool) -> None:
        """Enable/disable power LED."""
        asyncio.create_task(self.dbus.Boards.Yellow.set_power_led(enabled))

    @property
    @dbus_property
    def disk_led(self) -> bool:
        """Get disk LED enabled."""
        return self.properties[DBUS_ATTR_DISK_LED]

    @disk_led.setter
    def disk_led(self, enabled: bool) -> None:
        """Enable/disable disk LED."""
        asyncio.create_task(self.dbus.Boards.Yellow.set_disk_led(enabled))
