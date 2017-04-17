"""Tools file for HassIO."""
import asyncio
import json
import logging
import re
import socket

import aiohttp
import async_timeout

from .const import URL_HASSIO_VERSION, URL_HASSIO_VERSION_BETA

_LOGGER = logging.getLogger(__name__)

_RE_VERSION = re.compile(r"VERSION=(.*)")
_IMAGE_ARCH = re.compile(r".*/([a-z0-9]*)-hassio-supervisor")


async def fetch_current_versions(websession, beta=False):
    """Fetch current versions from github.

    Is a coroutine.
    """
    url = URL_HASSIO_VERSION_BETA if beta else URL_HASSIO_VERSION
    try:
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.get(url) as request:
                return await request.json(content_type=None)

    except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as err:
        _LOGGER.warning("Can't fetch versions from %s! %s", url, err)

    except json.JSONDecodeError as err:
        _LOGGER.warning("Can't parse versions from %s! %s", url, err)


def get_arch_from_image(image):
    """Return arch from hassio image name."""
    found = _IMAGE_ARCH.match(image)
    if found:
        return found.group(1)


def get_version_from_env(env_list):
    """Extract Version from ENV list."""
    for env in env_list:
        found = _RE_VERSION.match(env)
        if found:
            return found.group(1)

    _LOGGER.error("Can't find VERSION in env")
    return None


def get_local_ip(loop):
    """Retrieve local IP address.

    Need run inside executor.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Use Google Public DNS server to determine own IP
        sock.connect(('8.8.8.8', 80))

        return sock.getsockname()[0]
    except socket.error:
        return socket.gethostbyname(socket.gethostname())
    finally:
        sock.close()


def write_json_file(jsonfile, data):
    """Write a json file."""
    try:
        with open(jsonfile, 'w') as conf_file:
            conf_file.write(json.dumps(data))
    except OSError:
        return False

    return True


def read_json_file(jsonfile):
    """Read a json file and return a dict."""
    with open(jsonfile, 'r') as cfile:
        return json.loads(cfile.read())
