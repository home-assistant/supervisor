"""Repository type definitions for the store."""

from enum import StrEnum
from pathlib import Path

from ..const import REPOSITORY_CORE, REPOSITORY_LOCAL, URL_HASSIO_ADDONS
from ..coresys import CoreSys
from .utils import get_hash_from_repository


class BuiltinRepository(StrEnum):
    """All built-in repositories that come pre-configured."""

    # Local repository (non-git, special handling)
    LOCAL = REPOSITORY_LOCAL

    # Git-based built-in repositories
    CORE = REPOSITORY_CORE
    COMMUNITY_ADDONS = "https://github.com/hassio-addons/repository"
    ESPHOME = "https://github.com/esphome/home-assistant-addon"
    MUSIC_ASSISTANT = "https://github.com/music-assistant/home-assistant-addon"

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


# All repositories that are considered "built-in" and protected from removal
ALL_BUILTIN_REPOSITORIES = {repo.value for repo in BuiltinRepository}
