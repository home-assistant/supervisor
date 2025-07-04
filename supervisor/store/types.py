"""Repository type definitions for the store."""

from enum import StrEnum

from ..const import REPOSITORY_CORE, REPOSITORY_LOCAL, URL_HASSIO_ADDONS


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


# All repositories that are considered "built-in" and protected from removal
ALL_BUILTIN_REPOSITORIES = {repo.value for repo in BuiltinRepository}
