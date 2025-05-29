"""Main file for Supervisor."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
import sys

import zlib_fast

# Enable fast zlib before importing supervisor
zlib_fast.enable()

# pylint: disable=wrong-import-position
from supervisor import bootstrap  # noqa: E402
from supervisor.utils.blockbuster import BlockBusterManager  # noqa: E402
from supervisor.utils.logging import activate_log_queue_handler  # noqa: E402

# pylint: enable=wrong-import-position

_LOGGER: logging.Logger = logging.getLogger(__name__)

CONTAINER_OS_STARTUP_CHECK = Path("/run/os/startup-marker")


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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Check if all information are available to setup Supervisor
    bootstrap.check_environment()

    # init executor pool
    executor = ThreadPoolExecutor(thread_name_prefix="SyncWorker")
    loop.set_default_executor(executor)

    activate_log_queue_handler()

    _LOGGER.info("Initializing Supervisor setup")
    coresys = loop.run_until_complete(bootstrap.initialize_coresys())
    loop.set_debug(coresys.config.debug)
    if coresys.config.detect_blocking_io:
        BlockBusterManager.activate()
    loop.run_until_complete(coresys.core.connect())

    loop.run_until_complete(bootstrap.supervisor_debugger(coresys))

    # Signal health startup for container
    run_os_startup_check_cleanup()

    _LOGGER.info("Setting up Supervisor")
    loop.run_until_complete(coresys.core.setup())

    bootstrap.register_signal_handlers(loop, coresys)

    try:
        loop.run_until_complete(coresys.core.start())
    except Exception as err:  # pylint: disable=broad-except
        # Supervisor itself is running at this point, just something didn't
        # start as expected. Log with traceback to get more insights for
        # such cases.
        _LOGGER.critical("Supervisor start failed: %s", err, exc_info=True)

    try:
        _LOGGER.info("Running Supervisor")
        loop.run_forever()
    finally:
        loop.close()

    _LOGGER.info("Closing Supervisor")
    sys.exit(coresys.core.exit_code)
