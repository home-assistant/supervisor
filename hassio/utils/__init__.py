"""Tools file for HassIO."""
from datetime import datetime
import hashlib
import logging
import re
import uuid

_LOGGER = logging.getLogger(__name__)
RE_STRING = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")


def convert_to_ascii(raw):
    """Convert binary to ascii and remove colors."""
    return RE_STRING.sub("", raw.decode())


def create_token():
    """Create token for API access."""
    return hashlib.sha256(uuid.uuid4().bytes).hexdigest()


def process_lock(method):
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


class AsyncThrottle:
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
