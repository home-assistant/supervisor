"""Main file for HassIO."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
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
    executor = ThreadPoolExecutor(thread_name_prefix="SyncWorker")
    loop.set_default_executor(executor)

    _LOGGER.info("Initialize Hassio setup")
    config = bootstrap.initialize_system_data()
    hassio = core.HassIO(loop, config)

    bootstrap.migrate_system_env(config)

    _LOGGER.info("Run Hassio setup")
    loop.run_until_complete(hassio.setup())

    _LOGGER.info("Start Hassio task")
    loop.call_soon_threadsafe(loop.create_task, hassio.start())
    loop.call_soon_threadsafe(bootstrap.reg_signal, loop, hassio)

    _LOGGER.info("Run Hassio loop")
    loop.run_forever()

    _LOGGER.info("Cleanup system")
    executor.shutdown(wait=False)
    loop.close()

    _LOGGER.info("Close Hassio")
    sys.exit(hassio.exit_code)
