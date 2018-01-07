"""HassIO docker utilitys."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=protected-access
def docker_process(method):
    """Wrap function with only run once."""
    async def wrap_api(api, *args, **kwargs):
        """Return api wrapper."""
        if api.lock.locked():
            _LOGGER.error(
                "Can't excute %s while a task is in progress", method.__name__)
            return False

        async with api.lock:
            return await method(api, *args, **kwargs)

    return wrap_api
