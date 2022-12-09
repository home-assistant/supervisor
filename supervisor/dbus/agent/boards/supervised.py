"""Supervised board management."""

from .const import BOARD_NAME_SUPERVISED
from .interface import BoardProxy


class Supervised(BoardProxy):
    """Supervised board manager object."""

    def __init__(self) -> None:
        """Initialize properties."""
        super().__init__(BOARD_NAME_SUPERVISED)
        self.sync_properties: bool = False
