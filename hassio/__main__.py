"""Main file for HassIO."""
import asyncio
import logging
import sys

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
    loop.call_soon_threadsafe(loop.create_task, hassio.start())
    loop.call_soon_threadsafe(bootstrap.reg_signal, loop, hassio)

    loop.run_forever()
    loop.close()

    _LOGGER.info("Close Hassio")
    sys.exit(hassio.exit_code)
