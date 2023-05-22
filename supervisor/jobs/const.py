"""Jobs constants."""
from enum import Enum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_JOBS = Path(SUPERVISOR_DATA, "jobs.json")

ATTR_IGNORE_CONDITIONS = "ignore_conditions"


class JobCondition(str, Enum):
    """Job condition enum."""

    AUTO_UPDATE = "auto_update"
    FREE_SPACE = "free_space"
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


class JobExecutionLimit(str, Enum):
    """Job Execution limits."""

    ONCE = "once"
    SINGLE_WAIT = "single_wait"
    THROTTLE = "throttle"
    THROTTLE_WAIT = "throttle_wait"
    THROTTLE_RATE_LIMIT = "throttle_rate_limit"
