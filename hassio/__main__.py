"""Main file for HassIO."""
import asyncio
import logging
import signal

import hassio.bootstrap as bootstrap
import hassio.core as core

_LOGGER = logging.getLogger(__name__)


# pylint: disable=invalid-name
if __name__ == "__main__":
    bootstrap.initialize_logging()

    if not bootstrap.check_environment():
        exit(1)

    loop = asyncio.get_event_loop()
    hassio = core.HassIO(loop)

    _LOGGER.info("Run Hassio setup")
    loop.run_until_complete(hassio.setup())

    _LOGGER.info("Start Hassio task")
    loop.call_soon_threadsafe(asyncio.ensure_future, hassio.start(), loop)

    try:
        loop.add_signal_handler(
            signal.SIGTERM, lambda: loop.create_task(hassio.stop()))
    except ValueError:
        _LOGGER.warning("Could not bind to SIGTERM")

    loop.run_forever()
    loop.close()
    _LOGGER.info("Close Hassio")
