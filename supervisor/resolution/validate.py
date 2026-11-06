"""Validate resolution configuration schema."""

import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from ..const import (
    ATTR_CHECKS,
    ATTR_CONTEXT,
    ATTR_ENABLED,
    ATTR_ISSUES,
    ATTR_REFERENCE,
    ATTR_REFERENCE_EXTRA,
    ATTR_SUGGESTIONS,
    ATTR_TYPE,
)
from .const import LEGACY_CHECK_SLUG_MAP, ContextType, IssueType, SuggestionType

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Maps check module filename stem -> public API slug for checks whose slug
# differs from their module name (i.e., slug overrides for backward compat).
_CHECK_SLUG_OVERRIDES: dict[str, str] = {}


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


def _migrate_checks_config(data: dict) -> dict:
    """Migrate legacy check slug keys to current slug keys."""
    if not isinstance(data, dict):
        raise vol.Invalid("Expected a dictionary for checks configuration")
    return {LEGACY_CHECK_SLUG_MAP.get(key, key): value for key, value in data.items()}


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

SCHEMA_ISSUE_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_TYPE): vol.Coerce(IssueType),
        vol.Required(ATTR_CONTEXT): vol.Coerce(ContextType),
        vol.Optional(ATTR_REFERENCE, default=None): vol.Maybe(str),
        vol.Optional(ATTR_REFERENCE_EXTRA, default=None): vol.Maybe(dict),
        vol.Optional(ATTR_SUGGESTIONS, default=list): [vol.Coerce(SuggestionType)],
    },
    extra=vol.REMOVE_EXTRA,
)


def _validate_issues_config(data: Any) -> list[dict[str, Any]]:
    """Validate stored issues, dropping invalid ones.

    An issue type unknown to this version must not reset the whole file.
    """
    if not isinstance(data, list):
        raise vol.Invalid("Expected a list of issues")

    issues: list[dict[str, Any]] = []
    for issue in data:
        try:
            issues.append(SCHEMA_ISSUE_CONFIG(issue))
        except vol.Invalid as err:
            _LOGGER.warning("Dropping invalid stored issue %s: %s", issue, err)
    return issues


SCHEMA_RESOLUTION_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_CHECKS, default=SCHEMA_CHECKS_CONFIG({})): vol.All(
            _migrate_checks_config, SCHEMA_CHECKS_CONFIG
        ),
        vol.Required(ATTR_ISSUES, default=list): _validate_issues_config,
    },
    extra=vol.REMOVE_EXTRA,
)
