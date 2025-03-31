"""Yellow board management."""

import asyncio
from collections.abc import Awaitable

from dbus_fast.aio.message_bus import MessageBus

from ....const import ATTR_DISK_LED, ATTR_HEARTBEAT_LED, ATTR_POWER_LED
from ...const import DBUS_ATTR_DISK_LED, DBUS_ATTR_HEARTBEAT_LED, DBUS_ATTR_POWER_LED
from ...interface import dbus_property
from ...utils import dbus_connected
from .const import BOARD_NAME_YELLOW
from .interface import BoardProxy
from .validate import SCHEMA_YELLOW_BOARD


class Yellow(BoardProxy):
    """Yellow board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_YELLOW, SCHEMA_YELLOW_BOARD)

    @property
    @dbus_property
    def heartbeat_led(self) -> bool:
        """Get heartbeat LED enabled."""
        return self.properties[DBUS_ATTR_HEARTBEAT_LED]

    @dbus_connected
    def set_heartbeat_led(self, enabled: bool) -> Awaitable[None]:
        """Enable/disable heartbeat LED."""
        self._data[ATTR_HEARTBEAT_LED] = enabled
        return self.connected_dbus.Boards.Yellow.set("heartbeat_led", enabled)

    @property
    @dbus_property
    def power_led(self) -> bool:
        """Get power LED enabled."""
        return self.properties[DBUS_ATTR_POWER_LED]

    @dbus_connected
    def set_power_led(self, enabled: bool) -> Awaitable[None]:
        """Enable/disable power LED."""
        self._data[ATTR_POWER_LED] = enabled
        return self.connected_dbus.Boards.Yellow.set("power_led", enabled)

    @property
    @dbus_property
    def disk_led(self) -> bool:
        """Get disk LED enabled."""
        return self.properties[DBUS_ATTR_DISK_LED]

    @dbus_connected
    def set_disk_led(self, enabled: bool) -> Awaitable[None]:
        """Enable/disable disk LED."""
        self._data[ATTR_DISK_LED] = enabled
        return self.connected_dbus.Boards.Yellow.set("disk_led", enabled)

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

        # Set LEDs based on settings on connect
        await asyncio.gather(
            self.set_disk_led(self._data[ATTR_DISK_LED]),
            self.set_heartbeat_led(self._data[ATTR_HEARTBEAT_LED]),
            self.set_power_led(self._data[ATTR_POWER_LED]),
        )
