"""Validate add-ons options schema."""

from enum import StrEnum
from pathlib import Path

import voluptuous as vol

from ..const import (
    ATTR_MAINTAINER,
    ATTR_NAME,
    ATTR_REPOSITORIES,
    ATTR_URL,
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
    URL_HASSIO_ADDONS,
)
from ..coresys import CoreSys
from ..validate import RE_REPOSITORY
from .utils import get_hash_from_repository

URL_COMMUNITY_ADDONS = "https://github.com/hassio-addons/repository"
URL_ESPHOME = "https://github.com/esphome/home-assistant-addon"
URL_MUSIC_ASSISTANT = "https://github.com/music-assistant/home-assistant-addon"


class BuiltinRepository(StrEnum):
    """Built-in add-on repository."""

    CORE = "core"
    LOCAL = "local"
    COMMUNITY_ADDONS = URL_COMMUNITY_ADDONS
    ESPHOME = URL_ESPHOME
    MUSIC_ASSISTANT = URL_MUSIC_ASSISTANT

    def __init__(self, value: str) -> None:
        """Initialize repository item."""
        if value == REPOSITORY_LOCAL:
            self.id = value
            self.url = ""
        elif value == REPOSITORY_CORE:
            self.id = value
            self.url = URL_HASSIO_ADDONS
        else:
            self.id = get_hash_from_repository(value)
            self.url = value

    def get_path(self, coresys: CoreSys) -> Path:
        """Get path to git repo for repository."""
        if self.id == REPOSITORY_LOCAL:
            return coresys.config.path_addons_local
        if self.id == REPOSITORY_CORE:
            return coresys.config.path_addons_core
        return Path(coresys.config.path_addons_git, self.id)


BUILTIN_REPOSITORIES = {r.value for r in BuiltinRepository}


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
    if repository in [REPOSITORY_CORE, REPOSITORY_LOCAL]:
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
