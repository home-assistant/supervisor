"""Tools file for HassIO."""
import asyncio
from contextlib import suppress
from datetime import datetime
import json
import logging
import socket
import re

import aiohttp
import async_timeout
import voluptuous as vol
from voluptuous.humanize import humanize_error

_LOGGER = logging.getLogger(__name__)

FREEGEOIP_URL = "https://freegeoip.io/json/"

RE_STRING = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")


def get_local_ip(loop):
    """Retrieve local IP address.

    Return a future.
    """
    def local_ip():
        """Return local ip."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Use Google Public DNS server to determine own IP
            sock.connect(('8.8.8.8', 80))

            return sock.getsockname()[0]
        except socket.error:
            return socket.gethostbyname(socket.gethostname())
        finally:
            sock.close()

    return loop.run_in_executor(None, local_ip)


def write_json_file(jsonfile, data):
    """Write a json file."""
    try:
        json_str = json.dumps(data, indent=2)
        with jsonfile.open('w') as conf_file:
            conf_file.write(json_str)
    except (OSError, json.JSONDecodeError):
        return False

    return True


def read_json_file(jsonfile):
    """Read a json file and return a dict."""
    with jsonfile.open('r') as cfile:
        return json.loads(cfile.read())


async def fetch_timezone(websession):
    """Read timezone from freegeoip."""
    data = {}
    with suppress(aiohttp.ClientError, asyncio.TimeoutError,
                  json.JSONDecodeError, KeyError):
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.get(FREEGEOIP_URL) as request:
                data = await request.json()

    return data.get('time_zone', 'UTC')


def convert_to_ascii(raw):
    """Convert binary to ascii and remove colors."""
    return RE_STRING.sub("", raw.decode())


class JsonConfig(object):
    """Hass core object for handle it."""

    def __init__(self, json_file, schema):
        """Initialize hass object."""
        self._file = json_file
        self._schema = schema
        self._data = {}

        # init or load data
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

        # validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse %s -> %s",
                          self._file, humanize_error(self._data, ex))

    def save(self):
        """Store data to config file."""
        # validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse data -> %s",
                          humanize_error(self._data, ex))
            return False

        # write
        if not write_json_file(self._file, self._data):
            _LOGGER.error("Can't store config in %s", self._file)
            return False
        return True


class AsyncThrottle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period.
    """
    def __init__(self, delta):
        """Initialize async throttle."""
        self.throttle_period = delta
        self.time_of_last_call = datetime.min

    def __call__(self, method):
        """Throttle function"""
        async def wrapper(*args, **kwargs):
            """Throttle function wrapper"""
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return await method(*args, **kwargs)

        return wrapper
