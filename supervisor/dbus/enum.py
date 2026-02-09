"""D-Bus tolerant enum base classes.

D-Bus services (systemd, NetworkManager, RAUC, UDisks2) can introduce new enum
values at any time via OS updates. Standard enum construction raises ValueError
for unknown values. These base classes use Python's _missing_ hook to create
pseudo-members for unknown values, preventing crashes while preserving the
original value for logging and debugging.
"""

from enum import IntEnum, StrEnum
import logging

import sentry_sdk

_LOGGER: logging.Logger = logging.getLogger(__name__)

_reported: set[tuple[str, object]] = set()


def _report_unknown_value(cls: type, value: object) -> None:
    """Log and report an unknown D-Bus enum value to Sentry."""
    msg = f"Unknown {cls.__name__} value received from D-Bus: {value}"
    _LOGGER.warning(msg)

    key = (cls.__name__, value)
    if key not in _reported and sentry_sdk.is_initialized():
        _reported.add(key)
        sentry_sdk.capture_message(msg, level="warning")


class DBusStrEnum(StrEnum):
    """StrEnum that tolerates unknown values from D-Bus."""

    @classmethod
    def _missing_(cls, value: object) -> "DBusStrEnum | None":
        if not isinstance(value, str):
            return None
        _report_unknown_value(cls, value)
        obj = str.__new__(cls, value)
        obj._name_ = value
        obj._value_ = value
        return obj


class DBusIntEnum(IntEnum):
    """IntEnum that tolerates unknown values from D-Bus."""

    @classmethod
    def _missing_(cls, value: object) -> "DBusIntEnum | None":
        if not isinstance(value, int):
            return None
        _report_unknown_value(cls, value)
        obj = int.__new__(cls, value)
        obj._name_ = f"UNKNOWN_{value}"
        obj._value_ = value
        return obj
