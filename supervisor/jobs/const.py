"""Jobs constants."""

from enum import StrEnum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_JOBS = Path(SUPERVISOR_DATA, "jobs.json")

ATTR_IGNORE_CONDITIONS = "ignore_conditions"

JOB_GROUP_ADDON = "addon_{slug}"
JOB_GROUP_BACKUP = "backup_{slug}"
JOB_GROUP_BACKUP_MANAGER = "backup_manager"
JOB_GROUP_DOCKER_INTERFACE = "container_{name}"
JOB_GROUP_HOME_ASSISTANT_CORE = "home_assistant_core"


class JobCondition(StrEnum):
    """Job condition enum."""

    AUTO_UPDATE = "auto_update"
    FREE_SPACE = "free_space"
    FROZEN = "frozen"
    HAOS = "haos"
    HEALTHY = "healthy"
    HOST_NETWORK = "host_network"
    INTERNET_HOST = "internet_host"
    INTERNET_SYSTEM = "internet_system"
    MOUNT_AVAILABLE = "mount_available"
    OS_AGENT = "os_agent"
    PLUGINS_UPDATED = "plugins_updated"
    RUNNING = "running"
    SUPERVISOR_UPDATED = "supervisor_updated"


class JobExecutionLimit(StrEnum):
    """Job Execution limits."""

    ONCE = "once"
    SINGLE_WAIT = "single_wait"
    THROTTLE = "throttle"
    THROTTLE_WAIT = "throttle_wait"
    THROTTLE_RATE_LIMIT = "throttle_rate_limit"
    GROUP_ONCE = "group_once"
    GROUP_WAIT = "group_wait"
    GROUP_THROTTLE = "group_throttle"
    GROUP_THROTTLE_WAIT = "group_throttle_wait"
    GROUP_THROTTLE_RATE_LIMIT = "group_throttle_rate_limit"
