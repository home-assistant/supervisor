"""Backup consts."""
from enum import StrEnum

BUF_SIZE = 2**20 * 4  # 4MB


class BackupType(StrEnum):
    """Backup type enum."""

    FULL = "full"
    PARTIAL = "partial"


class BackupJobStage(StrEnum):
    """Backup job stage enum."""

    ADDON_REPOSITORIES = "addon_repositories"
    ADDONS = "addons"
    DOCKER_CONFIG = "docker_config"
    FINISHING_FILE = "finishing_file"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    AWAIT_ADDON_RESTARTS = "await_addon_restarts"


class RestoreJobStage(StrEnum):
    """Restore job stage enum."""

    ADDON_REPOSITORIES = "addon_repositories"
    ADDONS = "addons"
    AWAIT_ADDON_RESTARTS = "await_addon_restarts"
    AWAIT_HOME_ASSISTANT_RESTART = "await_home_assistant_restart"
    CHECK_HOME_ASSISTANT = "check_home_assistant"
    DOCKER_CONFIG = "docker_config"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    REMOVE_DELTA_ADDONS = "remove_delta_addons"
