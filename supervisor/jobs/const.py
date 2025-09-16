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
    HOME_ASSISTANT_CORE_SUPPORTED = "home_assistant_core_supported"
    HOST_NETWORK = "host_network"
    INTERNET_HOST = "internet_host"
    INTERNET_SYSTEM = "internet_system"
    MOUNT_AVAILABLE = "mount_available"
    OS_AGENT = "os_agent"
    OS_SUPPORTED = "os_supported"
    PLUGINS_UPDATED = "plugins_updated"
    RUNNING = "running"
    SUPERVISOR_UPDATED = "supervisor_updated"


class JobConcurrency(StrEnum):
    """Job concurrency control.

    Controls how many instances of a job can run simultaneously.

    Individual Concurrency (applies to each method separately):
    - REJECT: Fail immediately if another instance is already running
    - QUEUE: Wait for the current instance to finish, then run

    Group Concurrency (applies across all methods on a JobGroup):
    - GROUP_REJECT: Fail if ANY job is running on the JobGroup
    - GROUP_QUEUE: Wait for ANY running job on the JobGroup to finish

    JobGroup Behavior:
    - All methods on the same JobGroup instance share a single lock
    - Methods can call other methods on the same group without deadlock
    - Uses the JobGroup.group_name for coordination
    - Requires the class to inherit from JobGroup
    """

    REJECT = "reject"  # Fail if already running (was ONCE)
    QUEUE = "queue"  # Wait if already running (was SINGLE_WAIT)
    GROUP_REJECT = "group_reject"  # Was GROUP_ONCE
    GROUP_QUEUE = "group_queue"  # Was GROUP_WAIT


class JobThrottle(StrEnum):
    """Job throttling control.

    Controls how frequently jobs can be executed.

    Individual Throttling (each method has its own throttle state):
    - THROTTLE: Skip execution if called within throttle_period
    - RATE_LIMIT: Allow up to throttle_max_calls within throttle_period, then fail

    Group Throttling (all methods on a JobGroup share throttle state):
    - GROUP_THROTTLE: Skip if ANY method was called within throttle_period
    - GROUP_RATE_LIMIT: Allow up to throttle_max_calls total across ALL methods

    JobGroup Behavior:
    - All methods on the same JobGroup instance share throttle counters/timers
    - Uses the JobGroup.group_name as the key for tracking state
    - If one method is throttled, other methods may also be throttled
    - Requires the class to inherit from JobGroup
    """

    THROTTLE = "throttle"  # Skip if called too frequently
    RATE_LIMIT = "rate_limit"  # Rate limiting with max calls per period
    GROUP_THROTTLE = "group_throttle"  # Group version of THROTTLE
    GROUP_RATE_LIMIT = "group_rate_limit"  # Group version of RATE_LIMIT
