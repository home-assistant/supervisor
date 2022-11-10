"""Custom log messages."""
import logging
import re

from .sentry import capture_exception

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_BIND_FAILED = re.compile(
    r".*[listen tcp|Bind for].*(?:[0-9]{1,3}\.){3}[0-9]{1,3}:(\d*).*[bind|failed]:[address already in use|port is already allocated].*"
)


def format_message(message: str) -> str:
    """Return a formated message if it's known."""
    try:
        match = RE_BIND_FAILED.match(message)
        if match:
            return f"Port '{match.group(1)}' is already in use by something else on the host."
    except TypeError as err:
        _LOGGER.error("The type of message is not a string - %s", err)
        capture_exception(err)

    return message
