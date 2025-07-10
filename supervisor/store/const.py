"""Constants for the add-on store."""

from enum import StrEnum
from pathlib import Path

from ..const import (
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
    SUPERVISOR_DATA,
    URL_HASSIO_ADDONS,
)

FILE_HASSIO_STORE = Path(SUPERVISOR_DATA, "store.json")
"""Repository type definitions for the store."""


class BuiltinRepository(StrEnum):
    """All built-in repositories that come pre-configured."""

    # Local repository (non-git, special handling)
    LOCAL = REPOSITORY_LOCAL

    # Git-based built-in repositories
    CORE = REPOSITORY_CORE
    COMMUNITY_ADDONS = "https://github.com/hassio-addons/repository"
    ESPHOME = "https://github.com/esphome/home-assistant-addon"
    MUSIC_ASSISTANT = "https://github.com/music-assistant/home-assistant-addon"

    @property
    def git_url(self) -> str:
        """Return the git URL for this repository."""
        if self == BuiltinRepository.LOCAL:
            raise RuntimeError("Local repository does not have a git URL")
        if self == BuiltinRepository.CORE:
            return URL_HASSIO_ADDONS
        else:
            return self.value  # For URL-based repos, value is the URL
