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
            # aiohttp's FileResponse reaches os.sendfile via
            # asyncio/unix_events.py:_sock_sendfile_native_impl on a
            # non-blocking socket. Blockbuster only whitelists the
            # base_events.sendfile entry point, so allow this caller too.
            # Fixed upstream by https://github.com/cbornet/blockbuster/pull/58
            # (issue https://github.com/cbornet/blockbuster/issues/57) — drop
            # this workaround once blockbuster is bumped to a version that
            # includes the fix.
            cls._instance.functions["os.sendfile"].can_block_in(
                "asyncio/unix_events.py", "_sock_sendfile_native_impl"
            )
        cls._instance.activate()

    @classmethod
    def deactivate(cls):
        """Deactivate blockbuster detection."""
        _LOGGER.info("Deactivating BlockBuster blocking I/O detection")
        if cls._instance:
            cls._instance.deactivate()
