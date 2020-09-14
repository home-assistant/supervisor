"""Custom log messages."""
import logging
import re

import sentry_sdk

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_BIND_FAILED = re.compile(r".*Bind for.*:(\d*) failed: port is already allocated.*")


def format_message(message: str) -> str:
    """Return a formated message if it's known."""
    try:
        match = RE_BIND_FAILED.match(message)
        if match:
            return f"Port '{match.group(1)}' is already in use by something else on the host."
    except TypeError as err:
        sentry_sdk.capture_exception(err)
        _LOGGER.error("Type of message is not string - %s", err)

    return message
