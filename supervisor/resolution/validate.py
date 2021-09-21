"""Validate resolution configuration schema."""
from pathlib import Path

import voluptuous as vol

from ..const import ATTR_CHECKS, ATTR_ENABLED


def get_valid_modules(folder) -> list[str]:
    """Validate check name."""
    module_files = Path(__file__).parent.joinpath(folder)
    if not module_files.exists():
        raise vol.Invalid(f"Module folder '{folder}' not found!")

    return [
        module.stem
        for module in module_files.glob("*.py")
        if module.name not in ("base.py", "__init__.py")
    ]


SCHEMA_CHECK_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_ENABLED, default=True): bool,
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_CHECKS_CONFIG = vol.Schema(
    {
        vol.Required(check, default=SCHEMA_CHECK_CONFIG({})): SCHEMA_CHECK_CONFIG
        for check in get_valid_modules("checks")
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_RESOLUTION_CONFIG = vol.Schema(
    {
        vol.Required(
            ATTR_CHECKS, default=SCHEMA_CHECKS_CONFIG({})
        ): SCHEMA_CHECKS_CONFIG,
    },
    extra=vol.REMOVE_EXTRA,
)
