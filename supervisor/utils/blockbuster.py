"""Activate and deactivate blockbuster for finding blocking I/O."""

import logging

from blockbuster import BlockBuster

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BlockBusterManager:
    """Manage BlockBuster instance."""

    _instance: BlockBuster | None = None

    @classmethod
    def is_enabled(cls):
        """Return true if blockbuster detection is enabled."""
        if cls._instance is None:
            return False
        for _, fn in cls._instance.functions.items():
            return fn.activated
        return False

    @classmethod
    def activate(cls):
        """Activate blockbuster detection."""
        _LOGGER.info("Activating BlockBuster blocking I/O detection")
        if cls._instance is None:
            cls._instance = BlockBuster()
        cls._instance.activate()

    @classmethod
    def deactivate(cls):
        """Deactivate blockbuster detection."""
        _LOGGER.info("Deactivating BlockBuster blocking I/O detection")
        if cls._instance:
            cls._instance.deactivate()
