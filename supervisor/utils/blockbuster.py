"""Activate and deactivate blockbuster for finding blocking I/O."""

import logging

from blockbuster import BlockBuster as _BlockBuster

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BlockBuster:
    _instance: _BlockBuster | None = None

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
            cls._instance = _BlockBuster()
        cls._instance.activate()

    @classmethod
    def deactivate(cls):
        """Deactivate blockbuster detection."""
        _LOGGER.info("Deactivating BlockBuster blocking I/O detection")
        if cls._instance:
            cls._instance.deactivate()

import logging

from blockbuster import BlockBuster

_LOGGER: logging.Logger = logging.getLogger(__name__)
_blockbuster: BlockBuster | None = None


def _get_blockbuster() -> BlockBuster:
    # pylint: disable=global-statement
    global _blockbuster  # noqa: PLW0603
    if _blockbuster is None:
        _blockbuster = BlockBuster()
    return _blockbuster


def blockbuster_enabled() -> bool:
    """Return true if blockbuster detection is enabled."""
    if _blockbuster is None:
        return False

    # We activate all or none so just check the first one
    for _, fn in _blockbuster.functions.items():
        return fn.activated
    return False


def activate_blockbuster() -> None:
    """Activate blockbuster detection."""
    _LOGGER.info("Activating BlockBuster blocking I/O detection")
    _get_blockbuster().activate()


def deactivate_blockbuster() -> None:
    """Deactivate blockbuster detection."""
    _LOGGER.info("Deactivating BlockBuster blocking I/O detection")
    _get_blockbuster().deactivate()
