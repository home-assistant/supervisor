"""Custom log messages."""

import logging
import re

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_BIND_FAILED = re.compile(
    r".*[listen tcp|Bind for].*(?:[0-9]{1,3}\.){3}[0-9]{1,3}:(\d*).*[bind|failed]:[address already in use|port is already allocated].*"
)


def format_message(message: str) -> str:
    """Return a formatted message if it's known."""
    match = RE_BIND_FAILED.match(message)
    if match:
        return (
            f"Port '{match.group(1)}' is already in use by something else on the host."
        )

    return message
