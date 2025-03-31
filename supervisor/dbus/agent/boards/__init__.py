"""Board management for OS Agent."""

import logging
from typing import cast

from dbus_fast.aio.message_bus import MessageBus

from ....exceptions import BoardInvalidError, DBusInterfaceError, DBusServiceUnkownError
from ...const import (
    DBUS_ATTR_BOARD,
    DBUS_IFACE_HAOS_BOARDS,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS_BOARDS,
)
from ...interface import DBusInterfaceProxy, dbus_property
from .const import BOARD_NAME_GREEN, BOARD_NAME_SUPERVISED, BOARD_NAME_YELLOW
from .green import Green
from .interface import BoardProxy
from .supervised import Supervised
from .yellow import Yellow

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BoardManager(DBusInterfaceProxy):
    """Board manager object."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_BOARDS
    properties_interface: str = DBUS_IFACE_HAOS_BOARDS
    sync_properties: bool = False

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__()

        self._board_proxy: BoardProxy | None = None

    @property
    @dbus_property
    def board(self) -> str:
        """Get board name."""
        return self.properties[DBUS_ATTR_BOARD]

    @property
    def green(self) -> Green:
        """Get Green board."""
        if self.board != BOARD_NAME_GREEN:
            raise BoardInvalidError("Green board is not in use", _LOGGER.error)

        return cast(Green, self._board_proxy)

    @property
    def supervised(self) -> Supervised:
        """Get Supervised board."""
        if self.board != BOARD_NAME_SUPERVISED:
            raise BoardInvalidError("Supervised board is not in use", _LOGGER.error)

        return cast(Supervised, self._board_proxy)

    @property
    def yellow(self) -> Yellow:
        """Get Yellow board."""
        if self.board != BOARD_NAME_YELLOW:
            raise BoardInvalidError("Yellow board is not in use", _LOGGER.error)

        return cast(Yellow, self._board_proxy)

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

        if self.board == BOARD_NAME_YELLOW:
            self._board_proxy = await Yellow().load_config()
        elif self.board == BOARD_NAME_GREEN:
            self._board_proxy = await Green().load_config()
        elif self.board == BOARD_NAME_SUPERVISED:
            self._board_proxy = await Supervised().load_config()
        else:
            return

        try:
            await self._board_proxy.connect(bus)
        except (DBusServiceUnkownError, DBusInterfaceError) as ex:
            _LOGGER.warning("OS-Agent board support initialization failed: %s", ex)
