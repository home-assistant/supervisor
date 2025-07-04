"""Repository type definitions for the store."""

from enum import StrEnum

from ..const import REPOSITORY_CORE, REPOSITORY_LOCAL


class BuiltinRepository(StrEnum):
    """All built-in repositories that come pre-configured."""

    # Local repository (non-git, special handling)
    LOCAL = REPOSITORY_LOCAL

    # Git-based built-in repositories
    CORE = REPOSITORY_CORE
    COMMUNITY_ADDONS = "https://github.com/hassio-addons/repository"
    ESPHOME = "https://github.com/esphome/home-assistant-addon"
    MUSIC_ASSISTANT = "https://github.com/music-assistant/home-assistant-addon"


# All repositories that are considered "built-in" and protected from removal
ALL_BUILTIN_REPOSITORIES = {repo.value for repo in BuiltinRepository}
