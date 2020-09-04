"""Custom log messages."""
import re

RE_BIND_FAILED = re.compile(r".*Bind for.*:(\d*) failed: port is already allocated.*")


def format_message(message: str) -> str:
    """Return a formated message if it's known."""
    match = RE_BIND_FAILED.match(message)
    if match:
        return (
            f"Port '{match.group(1)}' is already in use by something else on the host."
        )

    return message
