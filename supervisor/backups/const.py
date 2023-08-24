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
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    METADATA = "metadata"
    AWAIT_ADDON_RESTARTS = "await_addon_restarts"


class RestoreJobStage(StrEnum):
    """Restore job stage enum."""

    ADDONS = "addons"
    ADDON_REPOSITORIES = "addon_repositories"
    AWAIT_ADDON_RESTARTS = "await_addon_restarts"
    AWAIT_HOME_ASSISTANT_RESTART = "await_home_assistant_restart"
    CHECK_HOME_ASSISTANT = "check_home_assistant"
    DOCKER_CONFIG = "docker_config"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    REMOVE_DELTA_ADDONS = "remove_delta_addons"
