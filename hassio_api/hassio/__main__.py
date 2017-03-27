"""Main file for HassIO."""
import asyncio
import logging

import hassio.bootstrap as bootstrap
import hassio.core as core

_LOGGER = logging.getLogger(__name__)


if __name__ == "__main__":
    bootstrap.initialize_logging()

    if not bootstrap.check_environment():
        exit(1)

    loop = asyncio.get_event_loop()
    _LOGGER.info("Start Hassio task")
    loop.create_task(core.run_hassio(loop))

    loop.run_forever()
    _LOGGER.info("Close Hassio")
