"""Green board management."""

import asyncio

from dbus_fast.aio.message_bus import MessageBus

from ....const import ATTR_ACTIVITY_LED, ATTR_POWER_LED, ATTR_USER_LED
from ...const import DBUS_ATTR_ACTIVITY_LED, DBUS_ATTR_POWER_LED, DBUS_ATTR_USER_LED
from ...interface import dbus_property
from .const import BOARD_NAME_GREEN
from .interface import BoardProxy
from .validate import SCHEMA_GREEN_BOARD


class Green(BoardProxy):
    """Green board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_GREEN, SCHEMA_GREEN_BOARD)
        self._activity_led_task: asyncio.Task | None = None
        self._power_led_task: asyncio.Task | None = None
        self._user_led_task: asyncio.Task | None = None

    @property
    @dbus_property
    def activity_led(self) -> bool:
        """Get activity LED enabled."""
        return self.properties[DBUS_ATTR_ACTIVITY_LED]

    @activity_led.setter
    def activity_led(self, enabled: bool) -> None:
        """Enable/disable activity LED."""
        self._data[ATTR_ACTIVITY_LED] = enabled
        self._activity_led_task = asyncio.create_task(
            self.dbus.Boards.Green.set_activity_led(enabled)
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
            self.dbus.Boards.Green.set_power_led(enabled)
        )

    @property
    @dbus_property
    def user_led(self) -> bool:
        """Get user LED enabled."""
        return self.properties[DBUS_ATTR_USER_LED]

    @user_led.setter
    def user_led(self, enabled: bool) -> None:
        """Enable/disable disk LED."""
        self._data[ATTR_USER_LED] = enabled
        self._user_led_task = asyncio.create_task(
            self.dbus.Boards.Green.set_user_led(enabled)
        )

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

        # Set LEDs based on settings on connect
        self.activity_led = self._data[ATTR_ACTIVITY_LED]
        self.power_led = self._data[ATTR_POWER_LED]
        self.user_led = self._data[ATTR_USER_LED]
