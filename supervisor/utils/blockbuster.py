"""Activate and deactivate blockbuster for finding blocking I/O."""

from functools import cache
import logging

from blockbuster import BlockBuster

_LOGGER: logging.Logger = logging.getLogger(__name__)


@cache
def _get_blockbuster() -> BlockBuster:
    """Get blockbuster instance."""
    return BlockBuster()


def blockbuster_enabled() -> bool:
    """Return true if blockbuster detection is enabled."""
    blockbuster = _get_blockbuster()
    # We activate all or none so just check the first one
    for _, fn in blockbuster.functions.items():
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
