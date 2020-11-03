"""Main file for Supervisor."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
import sys

from supervisor import bootstrap

_LOGGER: logging.Logger = logging.getLogger(__name__)

CONTAINER_OS_STARTUP_CHECK = Path("/os/overlay/supervisor.startup")


def run_os_startup_check_cleanup() -> None:
    """Cleanup OS startup check."""
    if not CONTAINER_OS_STARTUP_CHECK.exists():
        return

    try:
        CONTAINER_OS_STARTUP_CHECK.unlink()
    except OSError as err:
        _LOGGER.warning("Not able to remove the startup health file: %s", err)


# pylint: disable=invalid-name
if __name__ == "__main__":
    bootstrap.initialize_logging()

    # Init async event loop
    loop = asyncio.get_event_loop()

    # Check if all information are available to setup Supervisor
    bootstrap.check_environment()

    # init executor pool
    executor = ThreadPoolExecutor(thread_name_prefix="SyncWorker")
    loop.set_default_executor(executor)

    _LOGGER.info("Initializing Supervisor setup")
    coresys = loop.run_until_complete(bootstrap.initialize_coresys())
    loop.run_until_complete(coresys.core.connect())

    bootstrap.supervisor_debugger(coresys)
    bootstrap.migrate_system_env(coresys)

    # Signal health startup for container
    run_os_startup_check_cleanup()

    _LOGGER.info("Setting up Supervisor")
    loop.run_until_complete(coresys.core.setup())

    loop.call_soon_threadsafe(loop.create_task, coresys.core.start())
    loop.call_soon_threadsafe(bootstrap.reg_signal, loop, coresys)

    try:
        _LOGGER.info("Running Supervisor")
        loop.run_forever()
    finally:
        loop.close()

    _LOGGER.info("Closing Supervisor")
    sys.exit(0)
