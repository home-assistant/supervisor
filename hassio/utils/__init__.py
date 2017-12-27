"""Tools file for HassIO."""
from datetime import datetime
import re

RE_STRING = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")


def convert_to_ascii(raw):
    """Convert binary to ascii and remove colors."""
    return RE_STRING.sub("", raw.decode())


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
