"""Green board management."""

import asyncio
from collections.abc import Awaitable

from dbus_fast.aio.message_bus import MessageBus

from ....const import ATTR_ACTIVITY_LED, ATTR_POWER_LED, ATTR_USER_LED
from ...const import DBUS_ATTR_ACTIVITY_LED, DBUS_ATTR_POWER_LED, DBUS_ATTR_USER_LED
from ...interface import dbus_property
from ...utils import dbus_connected
from .const import BOARD_NAME_GREEN
from .interface import BoardProxy
from .validate import SCHEMA_GREEN_BOARD


class Green(BoardProxy):
    """Green board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_GREEN, SCHEMA_GREEN_BOARD)

    @property
    @dbus_property
    def activity_led(self) -> bool:
        """Get activity LED enabled."""
        return self.properties[DBUS_ATTR_ACTIVITY_LED]

    @dbus_connected
    def set_activity_led(self, enabled: bool) -> Awaitable[None]:
        """Enable/disable activity LED."""
        self._data[ATTR_ACTIVITY_LED] = enabled
        return self.connected_dbus.Boards.Green.set("activity_led", enabled)

    @property
    @dbus_property
    def power_led(self) -> bool:
        """Get power LED enabled."""
        return self.properties[DBUS_ATTR_POWER_LED]

    @dbus_connected
    def set_power_led(self, enabled: bool) -> Awaitable[None]:
        """Enable/disable power LED."""
        self._data[ATTR_POWER_LED] = enabled
        return self.connected_dbus.Boards.Green.set("power_led", enabled)

    @property
    @dbus_property
    def user_led(self) -> bool:
        """Get user LED enabled."""
        return self.properties[DBUS_ATTR_USER_LED]

    @dbus_connected
    def set_user_led(self, enabled: bool) -> Awaitable[None]:
        """Enable/disable disk LED."""
        self._data[ATTR_USER_LED] = enabled
        return self.connected_dbus.Boards.Green.set("user_led", enabled)

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

        # Set LEDs based on settings on connect
        await asyncio.gather(
            self.set_activity_led(self._data[ATTR_ACTIVITY_LED]),
            self.set_power_led(self._data[ATTR_POWER_LED]),
            self.set_user_led(self._data[ATTR_USER_LED]),
        )
