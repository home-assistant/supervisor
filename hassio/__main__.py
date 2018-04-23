"""Main file for HassIO."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import sys

import hassio.bootstrap as bootstrap

_LOGGER = logging.getLogger(__name__)


def attempt_use_uvloop():
    """Attempt to use uvloop."""
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


# pylint: disable=invalid-name
if __name__ == "__main__":
    bootstrap.initialize_logging()
    attempt_use_uvloop()
    loop = asyncio.get_event_loop()

    if not bootstrap.check_environment():
        sys.exit(1)

    # init executor pool
    executor = ThreadPoolExecutor(thread_name_prefix="SyncWorker")
    loop.set_default_executor(executor)

    _LOGGER.info("Initialize Hassio setup")
    coresys = bootstrap.initialize_coresys(loop)

    bootstrap.migrate_system_env(coresys)

    _LOGGER.info("Setup HassIO")
    loop.run_until_complete(coresys.core.setup())

    loop.call_soon_threadsafe(loop.create_task, coresys.core.start())
    loop.call_soon_threadsafe(bootstrap.reg_signal, loop)

    try:
        _LOGGER.info("Run HassIO")
        loop.run_forever()
    finally:
        _LOGGER.info("Stopping HassIO")
        loop.run_until_complete(coresys.core.stop())
        executor.shutdown(wait=False)
        loop.close()

    _LOGGER.info("Close Hassio")
    sys.exit(0)
