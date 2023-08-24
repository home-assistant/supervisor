"""Backup consts."""
from enum import StrEnum

BUF_SIZE = 2**20 * 4  # 4MB


class BackupType(StrEnum):
    """Backup type enum."""

    FULL = "full"
    PARTIAL = "partial"


class BackupJobStage(StrEnum):
    """Backup job stage enum."""

    ADDONS = "addons"
    ADDON_RESTARTS = "addon_restarts"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    METADATA = "metadata"


class RestoreJobStage(StrEnum):
    """Restore job stage enum."""

    ADDONS = "addons"
    ADDON_REPOSITORIES = "addon_repositories"
    ADDON_RESTARTS = "addon_restarts"
    DOCKER_CONFIG = "docker_config"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    HOME_ASSISTANT_RESTART = "home_assistant_restart"
    REMOVE_ADDONS = "remove_addons"
