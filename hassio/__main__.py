"""Main file for Hass.io."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import sys

from hassio import bootstrap

_LOGGER: logging.Logger = logging.getLogger(__name__)


def initialize_event_loop():
    """Attempt to use uvloop."""
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        pass

    return asyncio.get_event_loop()


# pylint: disable=invalid-name
if __name__ == "__main__":
    bootstrap.initialize_logging()

    # Init async event loop
    loop = initialize_event_loop()

    # Check if all information are available to setup Hass.io
    if not bootstrap.check_environment():
        sys.exit(1)

    # init executor pool
    executor = ThreadPoolExecutor(thread_name_prefix="SyncWorker")
    loop.set_default_executor(executor)

    _LOGGER.info("Initialize Hass.io setup")
    coresys = loop.run_until_complete(bootstrap.initialize_coresys())
    loop.run_until_complete(coresys.core.connect())

    bootstrap.supervisor_debugger(coresys)
    bootstrap.migrate_system_env(coresys)

    _LOGGER.info("Setup HassIO")
    loop.run_until_complete(coresys.core.setup())

    loop.call_soon_threadsafe(loop.create_task, coresys.core.start())
    loop.call_soon_threadsafe(bootstrap.reg_signal, loop)

    try:
        _LOGGER.info("Run Hass.io")
        loop.run_forever()
    finally:
        _LOGGER.info("Stopping Hass.io")
        loop.run_until_complete(coresys.core.stop())
        executor.shutdown(wait=False)
        loop.close()

    _LOGGER.info("Close Hass.io")
    sys.exit(0)
