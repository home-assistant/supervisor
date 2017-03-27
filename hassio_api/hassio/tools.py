"""Tools file for HassIO."""
import logging

import async_timeout

from .const import URL_SUPERVISOR_VERSION

_LOGGER = logging.getLogger(__name__)


async def fetch_current_versions(websession):
    """Fetch current versions from github."""
    try:
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.get(URL_SUPERVISOR_VERSION) as request:
                return await request.json()

    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.warning("Can't fetch versions from github! %s", err)
