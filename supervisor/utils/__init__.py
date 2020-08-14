"""Tools file for Supervisor."""
import asyncio
from datetime import datetime
from ipaddress import IPv4Address
import logging
import re
import socket
from typing import Optional

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_STRING: re.Pattern = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")
RE_URL: re.Pattern = re.compile(r"(\w+:\/\/)(.*\.\w+)(.*)")


def convert_to_ascii(raw: bytes) -> str:
    """Convert binary to ascii and remove colors."""
    return RE_STRING.sub("", raw.decode())


def process_lock(method):
    """Wrap function with only run once."""

    async def wrap_api(api, *args, **kwargs):
        """Return api wrapper."""
        if api.lock.locked():
            _LOGGER.error(
                "Can't execute %s while a task is in progress", method.__name__
            )
            return False

        async with api.lock:
            return await method(api, *args, **kwargs)

    return wrap_api


class AsyncThrottle:
    """A class for throttling the execution of tasks.

    Decorator that prevents a function from being called more than once every
    time period with blocking.
    """

    def __init__(self, delta):
        """Initialize async throttle."""
        self.throttle_period = delta
        self.time_of_last_call = datetime.min
        self.synchronize: Optional[asyncio.Lock] = None

    def __call__(self, method):
        """Throttle function."""

        async def wrapper(*args, **kwargs):
            """Throttle function wrapper."""
            if not self.synchronize:
                self.synchronize = asyncio.Lock()

            async with self.synchronize:
                now = datetime.now()
                time_since_last_call = now - self.time_of_last_call

                if time_since_last_call > self.throttle_period:
                    self.time_of_last_call = now
                    return await method(*args, **kwargs)

        return wrapper


class AsyncCallFilter:
    """A class for throttling the execution of tasks, with a filter.

    Decorator that prevents a function from being called more than once every
    time period.
    """

    def __init__(self, delta):
        """Initialize async throttle."""
        self.throttle_period = delta
        self.time_of_last_call = datetime.min

    def __call__(self, method):
        """Throttle function."""

        async def wrapper(*args, **kwargs):
            """Throttle function wrapper."""
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return await method(*args, **kwargs)

        return wrapper


def check_port(address: IPv4Address, port: int) -> bool:
    """Check if port is mapped."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        result = sock.connect_ex((str(address), port))
        sock.close()

        # Check if the port is available
        if result == 0:
            return True
    except OSError:
        pass
    return False


def sanitize_url(url: str) -> str:
    """Return a sanitized url."""
    if not re.match(RE_URL, url):
        # Not a URL, just return it back
        return url

    return re.sub(RE_URL, r"\1example.com\3", url)
