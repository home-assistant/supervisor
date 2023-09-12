"""Green board management."""

import asyncio

from ...const import DBUS_ATTR_ACTIVITY_LED, DBUS_ATTR_POWER_LED, DBUS_ATTR_USER_LED
from ...interface import dbus_property
from .const import BOARD_NAME_GREEN
from .interface import BoardProxy


class Green(BoardProxy):
    """Green board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_GREEN)

    @property
    @dbus_property
    def activity_led(self) -> bool:
        """Get activity LED enabled."""
        return self.properties[DBUS_ATTR_ACTIVITY_LED]

    @activity_led.setter
    def activity_led(self, enabled: bool) -> None:
        """Enable/disable activity LED."""
        asyncio.create_task(self.dbus.Boards.Green.set_activity_led(enabled))

    @property
    @dbus_property
    def power_led(self) -> bool:
        """Get power LED enabled."""
        return self.properties[DBUS_ATTR_POWER_LED]

    @power_led.setter
    def power_led(self, enabled: bool) -> None:
        """Enable/disable power LED."""
        asyncio.create_task(self.dbus.Boards.Green.set_power_led(enabled))

    @property
    @dbus_property
    def user_led(self) -> bool:
        """Get user LED enabled."""
        return self.properties[DBUS_ATTR_USER_LED]

    @user_led.setter
    def user_led(self, enabled: bool) -> None:
        """Enable/disable disk LED."""
        asyncio.create_task(self.dbus.Boards.Green.set_user_led(enabled))
