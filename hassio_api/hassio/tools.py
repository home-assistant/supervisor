"""Tools file for HassIO."""
import logging
import re

import async_timeout

from .const import URL_SUPERVISOR_VERSION

_LOGGER = logging.getLogger(__name__)

_RE_VERSION = re.compile(r"VERSION=(.*)")
_RE_IMAGE = re.compile(r"(.*):(.*)")


async def fetch_current_versions(websession):
    """Fetch current versions from github."""
    try:
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.get(URL_SUPERVISOR_VERSION) as request:
                return await request.json()

    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.warning("Can't fetch versions from github! %s", err)


def get_version_from_env(env_list):
    """Extract Version from ENV list."""
    for env in env_list:
        found = _RE_VERSION.match(env)
        if found:
            return found.group(1)

    _LOGGER.error("Can't find VERSION in env")
    return None

def extract_image_name(image):
    """Extract image name and tag from docker attrs."""
    data = _RE_IMAGE.match(image)
    if not data:
        _LOGGER.error("Invalid docker information: %s", image)
        return (None, None)

    return (data.group(1), data.group(2))
