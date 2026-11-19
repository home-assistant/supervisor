"""App static data."""

from datetime import timedelta
from enum import StrEnum
from typing import Self

from ..backups.const import (
    JOB_FREEZE_ALL,
    JOB_FULL_BACKUP,
    JOB_FULL_RESTORE,
    JOB_PARTIAL_BACKUP,
    JOB_PARTIAL_RESTORE,
    JOB_THAW_ALL,
)
from ..jobs.const import JobCondition
from ..resolution.const import JOB_RUN_AUTOFIX


class AppBackupMode(StrEnum):
    """Backup mode of an App."""

    HOT = "hot"
    COLD = "cold"


class MappingType(StrEnum):
    """Mapping type of an App Folder."""

    DATA = "data"
    CONFIG = "config"
    SSL = "ssl"
    LOCAL_APPS = "local_apps"
    BACKUP = "backup"
    SHARE = "share"
    MEDIA = "media"
    HOMEASSISTANT_CONFIG = "homeassistant_config"
    ALL_APP_CONFIGS = "all_app_configs"
    APP_CONFIG = "app_config"

    # Legacy, deprecated as of 2026.07; use app equivalents
    ADDONS = "addons"
    ALL_ADDON_CONFIGS = "all_addon_configs"
    ADDON_CONFIG = "addon_config"


class AppOperation(StrEnum):
    """Operation in progress on an App and the job which performs it."""

    job_name: str

    def __new__(cls, value: str, job_name: str) -> Self:
        """Create an operation performed by the named job."""
        operation = str.__new__(cls, value)
        operation._value_ = value
        operation.job_name = job_name
        return operation

    BACKING_UP = "backing_up", "app_backup"
    INSTALLING = "installing", "app_manager_install"
    REBUILDING = "rebuilding", "app_manager_rebuild"
    RESTARTING = "restarting", "app_restart"
    RESTORING = "restoring", "app_manager_restore"
    STARTING = "starting", "app_start"
    STOPPING = "stopping", "app_stop"
    UNINSTALLING = "uninstalling", "app_manager_uninstall"
    UPDATING = "updating", "app_manager_update"


class AppOperationInitiator(StrEnum):
    """What started an operation on an App."""

    API = "api"
    AUTOFIX = "autofix"
    BACKUP = "backup"
    BOOT = "boot"
    REPAIR = "repair"
    RESTORE = "restore"
    SUPERVISOR = "supervisor"
    WATCHDOG = "watchdog"


ATTR_BACKUP = "backup"
ATTR_BREAKING_VERSIONS = "breaking_versions"
ATTR_CODENOTARY = "codenotary"
ATTR_LOG_FORMAT = "log_format"
ATTR_READ_ONLY = "read_only"
ATTR_PATH = "path"
WATCHDOG_RETRY_SECONDS = 10

# Flipped to False late in the deprecation cycle, before the TCP API is removed
SUPERVISOR_API_TCP_DEFAULT = True
WATCHDOG_MAX_ATTEMPTS = 5
WATCHDOG_THROTTLE_PERIOD = timedelta(minutes=30)
WATCHDOG_THROTTLE_MAX_CALLS = 10

APP_UPDATE_CONDITIONS = [
    JobCondition.FREE_SPACE,
    JobCondition.HEALTHY,
    JobCondition.INTERNET_HOST,
    JobCondition.PLUGINS_UPDATED,
    JobCondition.SUPERVISOR_UPDATED,
]

RE_SLUG = r"[-_.A-Za-z0-9]+"
# Keeps the app's socket path within sun_path (107 characters)
SLUG_MAX_LENGTH = 60

JOB_APP_MANAGER_BOOT = "app_manager_boot"
JOB_APP_MANAGER_REPAIR = "app_manager_repair"
JOB_APP_RESTART_AFTER_PROBLEM = "app_restart_after_problem"

# Jobs which are an operation on the app they reference. The outermost one in a
# job's chain is the operation, so a restart is not reported as stop and start.
OPERATION_JOBS: dict[str, AppOperation] = {
    operation.job_name: operation for operation in AppOperation
}

# Root jobs which identify the initiator of an operation started within them
OPERATION_INITIATOR_JOBS: dict[str, AppOperationInitiator] = {
    JOB_APP_MANAGER_BOOT: AppOperationInitiator.BOOT,
    JOB_APP_MANAGER_REPAIR: AppOperationInitiator.REPAIR,
    JOB_APP_RESTART_AFTER_PROBLEM: AppOperationInitiator.WATCHDOG,
    JOB_FREEZE_ALL: AppOperationInitiator.BACKUP,
    JOB_FULL_BACKUP: AppOperationInitiator.BACKUP,
    JOB_FULL_RESTORE: AppOperationInitiator.RESTORE,
    JOB_PARTIAL_BACKUP: AppOperationInitiator.BACKUP,
    JOB_PARTIAL_RESTORE: AppOperationInitiator.RESTORE,
    JOB_RUN_AUTOFIX: AppOperationInitiator.AUTOFIX,
    JOB_THAW_ALL: AppOperationInitiator.BACKUP,
}
