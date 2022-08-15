"""Supervisor job manager."""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..utils.common import FileConfiguration
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SupervisorJob(CoreSysAttributes):
    """Supervisor running job class."""

    def __init__(self, coresys: CoreSys, name: str):
        """Initialize the JobManager class."""
        self.coresys: CoreSys = coresys
        self.name: str = name
        self._progress: int = 0
        self._stage: str | None = None

    @property
    def progress(self) -> int:
        """Return the current progress."""
        return self._progress

    @property
    def stage(self) -> str | None:
        """Return the current stage."""
        return self._stage

    def update(self, progress: int | None = None, stage: str | None = None) -> None:
        """Update the job object."""
        if progress is not None:
            if progress >= round(100):
                self.sys_jobs.remove_job(self)
                return
            self._progress = round(progress)
        if stage is not None:
            self._stage = stage
        _LOGGER.debug(
            "Job updated; name: %s, progress: %s, stage: %s",
            self.name,
            self.progress,
            self.stage,
        )


class JobManager(FileConfiguration, CoreSysAttributes):
    """Job class."""

    def __init__(self, coresys: CoreSys):
        """Initialize the JobManager class."""
        super().__init__(FILE_CONFIG_JOBS, SCHEMA_JOBS_CONFIG)
        self.coresys: CoreSys = coresys
        self._jobs: dict[str, SupervisorJob] = {}

    @property
    def jobs(self) -> list[SupervisorJob]:
        """Return a list of current jobs."""
        return self._jobs

    @property
    def ignore_conditions(self) -> list[JobCondition]:
        """Return a list of ingore condition."""
        return self._data[ATTR_IGNORE_CONDITIONS]

    @ignore_conditions.setter
    def ignore_conditions(self, value: list[JobCondition]) -> None:
        """Set a list of ignored condition."""
        self._data[ATTR_IGNORE_CONDITIONS] = value

    def get_job(self, name: str) -> SupervisorJob:
        """Return a job, create one if it does not exist."""
        if name not in self._jobs:
            self._jobs[name] = SupervisorJob(self.coresys, name)

        return self._jobs[name]

    def remove_job(self, job: SupervisorJob) -> None:
        """Remove a job."""
        if job.name in self._jobs:
            del self._jobs[job.name]

    def clear(self) -> None:
        """Clear all jobs."""
        self._jobs.clear()
