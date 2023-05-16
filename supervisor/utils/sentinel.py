"""Sentinel to use when None is a valid value."""

from typing import Literal


class SentinelMeta(type):
    """Metaclass for sentinel to improve representation and make falsy.

    Credit to https://stackoverflow.com/a/69243488 .
    """

    def __repr__(cls) -> str:
        """Represent class more like an enum."""
        return f"<{cls.__name__}>"

    def __bool__(cls) -> Literal[False]:
        """Return false as a sentinel is akin to an empty value."""
        return False


class DEFAULT(metaclass=SentinelMeta):
    """Sentinel for default value when None is valid."""
