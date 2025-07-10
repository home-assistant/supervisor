"""Validate add-ons options schema."""

import voluptuous as vol

from ..const import ATTR_MAINTAINER, ATTR_NAME, ATTR_REPOSITORIES, ATTR_URL
from ..validate import RE_REPOSITORY
from .const import BuiltinRepository

# pylint: disable=no-value-for-parameter
SCHEMA_REPOSITORY_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): str,
        vol.Optional(ATTR_URL): vol.Url(),
        vol.Optional(ATTR_MAINTAINER): str,
    },
    extra=vol.REMOVE_EXTRA,
)


def validate_repository(repository: str) -> str:
    """Validate a valid repository."""
    if repository in BuiltinRepository:
        return repository

    data = RE_REPOSITORY.match(repository)
    if not data:
        raise vol.Invalid("No valid repository format!") from None

    # Validate URL
    # pylint: disable=no-value-for-parameter
    vol.Url()(data.group("url"))

    return repository


repositories = vol.All([validate_repository], vol.Unique())

DEFAULT_REPOSITORIES = [repo.value for repo in BuiltinRepository]

SCHEMA_STORE_FILE = vol.Schema(
    {
        vol.Optional(ATTR_REPOSITORIES, default=DEFAULT_REPOSITORIES): repositories,
    },
    extra=vol.REMOVE_EXTRA,
)
