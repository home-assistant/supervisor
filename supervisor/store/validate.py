"""Validate add-ons options schema."""

import voluptuous as vol

from ..const import ATTR_MAINTAINER, ATTR_NAME, ATTR_REPOSITORIES, ATTR_URL
from ..validate import RE_REPOSITORY
from .const import StoreType

URL_COMMUNITY_ADDONS = "https://github.com/hassio-addons/repository"
URL_ESPHOME = "https://github.com/esphome/home-assistant-addon"
URL_MUSIC_ASSISTANT = "https://github.com/music-assistant/home-assistant-addon"
BUILTIN_REPOSITORIES = {
    StoreType.CORE,
    StoreType.LOCAL,
    URL_COMMUNITY_ADDONS,
    URL_ESPHOME,
    URL_MUSIC_ASSISTANT,
}

# pylint: disable=no-value-for-parameter
SCHEMA_REPOSITORY_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): str,
        vol.Optional(ATTR_URL): vol.Url(),
        vol.Optional(ATTR_MAINTAINER): str,
    },
    extra=vol.REMOVE_EXTRA,
)


def ensure_builtin_repositories(addon_repositories: list[str]) -> list[str]:
    """Ensure builtin repositories are in list.

    Note: This should not be used in validation as the resulting list is not
    stable. This can have side effects when comparing data later on.
    """
    return list(set(addon_repositories) | BUILTIN_REPOSITORIES)


def validate_repository(repository: str) -> str:
    """Validate a valid repository."""
    if repository in [StoreType.CORE, StoreType.LOCAL]:
        return repository

    data = RE_REPOSITORY.match(repository)
    if not data:
        raise vol.Invalid("No valid repository format!") from None

    # Validate URL
    # pylint: disable=no-value-for-parameter
    vol.Url()(data.group("url"))

    return repository


repositories = vol.All([validate_repository], vol.Unique())

SCHEMA_STORE_FILE = vol.Schema(
    {
        vol.Optional(
            ATTR_REPOSITORIES, default=list(BUILTIN_REPOSITORIES)
        ): repositories,
    },
    extra=vol.REMOVE_EXTRA,
)
