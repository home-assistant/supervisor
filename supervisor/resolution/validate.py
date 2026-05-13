"""Validate resolution configuration schema."""

from pathlib import Path

import voluptuous as vol

from ..const import ATTR_CHECKS, ATTR_ENABLED

# Maps check module filename stem -> public API slug for checks whose slug
# differs from their module name (i.e., slug overrides for backward compat).
_CHECK_SLUG_OVERRIDES: dict[str, str] = {
    "app_pwned": "addon_pwned",
    "deprecated_app": "deprecated_addon",
    "deprecated_arch_app": "deprecated_arch_addon",
    "detached_app_missing": "detached_addon_missing",
    "detached_app_removed": "detached_addon_removed",
}


def get_valid_modules(folder, *, base=__file__) -> list[str]:
    """Validate check name."""
    module_files = Path(base).parent.joinpath(folder)
    if not module_files.exists():
        raise vol.Invalid(f"Module folder '{folder}' not found!")

    return [
        module.stem
        for module in module_files.glob("*.py")
        if module.name not in ("base.py", "__init__.py")
    ]


def _get_check_slug(module_name: str) -> str:
    """Return the public slug for a check module (may differ from module name)."""
    return _CHECK_SLUG_OVERRIDES.get(module_name, module_name)


SCHEMA_CHECK_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_ENABLED, default=True): bool,
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_CHECKS_CONFIG = vol.Schema(
    {
        vol.Required(
            _get_check_slug(check), default=SCHEMA_CHECK_CONFIG({})
        ): SCHEMA_CHECK_CONFIG
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
