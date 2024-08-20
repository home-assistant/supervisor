"""Supervised board management."""

from typing import Any

from supervisor.dbus.utils import dbus_connected

from .const import BOARD_NAME_SUPERVISED
from .interface import BoardProxy


class Supervised(BoardProxy):
    """Supervised board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_SUPERVISED)
        self.sync_properties: bool = False

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Do nothing as there are no properties.

        Currently unused, avoid using the Properties interface to avoid a bug in
        Go D-Bus, see: https://github.com/home-assistant/os-agent/issues/206
        """
