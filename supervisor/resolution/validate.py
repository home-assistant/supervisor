"""Validate resolution configuration schema."""
from pathlib import Path

import voluptuous as vol

from ..const import ATTR_CHECKS, ATTR_ENABLED

_INVALID_BASE = ("base.py", "__init__.py")


def valid_check_name(check: str):
    """Validate check name."""
    check_file = Path(__file__).parent.joinpath(f"checks/{check}.py")
    if not check_file.exists() or check_file.name in _INVALID_BASE:
        raise vol.Invalid(f"Check '{check}' not found!") from None
    return check


SCHEMA_CHECK_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_ENABLED): bool,
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_RESOLUTION_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_CHECKS, default=dict): {
            valid_check_name: SCHEMA_CHECK_CONFIG
        },
    },
    extra=vol.REMOVE_EXTRA,
)
