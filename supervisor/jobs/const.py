"""Jobs constants."""
from enum import Enum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_JOBS = Path(SUPERVISOR_DATA, "jobs.json")

ATTR_IGNORE_CONDITIONS = "ignore_conditions"


class JobCondition(str, Enum):
    """Job condition enum."""

    FREE_SPACE = "free_space"
    HEALTHY = "healthy"
    INTERNET_SYSTEM = "internet_system"
    INTERNET_HOST = "internet_host"
    RUNNING = "running"
    HAOS = "haos"


class JobExecutionLimit(str, Enum):
    """Job Execution limits."""

    SINGLE_WAIT = "single_wait"
    ONCE = "once"
    THROTTLE = "throttle"
    THROTTLE_WAIT = "throttle_wait"
