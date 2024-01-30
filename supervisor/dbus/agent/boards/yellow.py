"""Yellow board management."""

import asyncio

from dbus_fast.aio.message_bus import MessageBus

from ....const import ATTR_DISK_LED, ATTR_HEARTBEAT_LED, ATTR_POWER_LED
from ...const import DBUS_ATTR_DISK_LED, DBUS_ATTR_HEARTBEAT_LED, DBUS_ATTR_POWER_LED
from ...interface import dbus_property
from .const import BOARD_NAME_YELLOW
from .interface import BoardProxy
from .validate import SCHEMA_YELLOW_BOARD


class Yellow(BoardProxy):
    """Yellow board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_YELLOW, SCHEMA_YELLOW_BOARD)
        self._heartbeat_led_task: asyncio.Task | None = None
        self._power_led_task: asyncio.Task | None = None
        self._disk_led_task: asyncio.Task | None = None

    @property
    @dbus_property
    def heartbeat_led(self) -> bool:
        """Get heartbeat LED enabled."""
        return self.properties[DBUS_ATTR_HEARTBEAT_LED]

    @heartbeat_led.setter
    def heartbeat_led(self, enabled: bool) -> None:
        """Enable/disable heartbeat LED."""
        self._data[ATTR_HEARTBEAT_LED] = enabled
        self._heartbeat_led_task = asyncio.create_task(
            self.dbus.Boards.Yellow.set_heartbeat_led(enabled)
        )

    @property
    @dbus_property
    def power_led(self) -> bool:
        """Get power LED enabled."""
        return self.properties[DBUS_ATTR_POWER_LED]

    @power_led.setter
    def power_led(self, enabled: bool) -> None:
        """Enable/disable power LED."""
        self._data[ATTR_POWER_LED] = enabled
        self._power_led_task = asyncio.create_task(
            self.dbus.Boards.Yellow.set_power_led(enabled)
        )

    @property
    @dbus_property
    def disk_led(self) -> bool:
        """Get disk LED enabled."""
        return self.properties[DBUS_ATTR_DISK_LED]

    @disk_led.setter
    def disk_led(self, enabled: bool) -> None:
        """Enable/disable disk LED."""
        self._data[ATTR_DISK_LED] = enabled
        self._disk_led_task = asyncio.create_task(
            self.dbus.Boards.Yellow.set_disk_led(enabled)
        )

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

        # Set LEDs based on settings on connect
        self.disk_led = self._data[ATTR_DISK_LED]
        self.heartbeat_led = self._data[ATTR_HEARTBEAT_LED]
        self.power_led = self._data[ATTR_POWER_LED]
