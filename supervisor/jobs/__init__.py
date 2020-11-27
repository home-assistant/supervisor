"""Supervisor job manager."""
from contextvars import ContextVar
import logging
from typing import Dict, List, Optional
from uuid import uuid4

from ..coresys import CoreSys, CoreSysAttributes
from ..utils.json import JsonConfig
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__package__)
CONTEXT = ContextVar("id")


class SupervisorJob(CoreSysAttributes):
    """Supervisor running job class."""

    def __init__(self, coresys: CoreSys, name: Optional[str] = None):
        """Initialize the JobManager class."""
        self.coresys: CoreSys = coresys
        self._name: Optional[str] = name
        self._progress: int = 0
        self._stage: Optional[str] = None

    @property
    def id(self) -> str:
        """Return the ID for the job."""
        return self.sys_jobs.context.get()

    @property
    def name(self) -> str:
        """Return the name for the job."""
        return self._name or self.id

    @property
    def progress(self) -> int:
        """Return the current progress."""
        return self._progress

    @property
    def stage(self) -> Optional[str]:
        """Return the current stage."""
        return self._stage

    def update(
        self, progress: Optional[int] = None, stage: Optional[str] = None
    ) -> None:
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


class JobManager(JsonConfig, CoreSysAttributes):
    """Job class."""

    def __init__(self, coresys: CoreSys):
        """Initialize the JobManager class."""
        super().__init__(FILE_CONFIG_JOBS, SCHEMA_JOBS_CONFIG)
        self.coresys: CoreSys = coresys
        self.context = CONTEXT
        self._jobs: Dict[str, SupervisorJob] = {}

    @property
    def jobs(self) -> List[SupervisorJob]:
        """Return a list of current jobs."""
        return self._jobs

    @property
    def ignore_conditions(self) -> List[JobCondition]:
        """Return a list of ingore condition."""
        return self._data[ATTR_IGNORE_CONDITIONS]

    @property
    def job(self) -> SupervisorJob:
        """Return the current job based on context ID."""
        try:
            self.context.get()
        except LookupError:
            self.context.set(str(uuid4().hex))

        context = self.context.get()

        if context not in self._jobs:
            self._jobs[context] = SupervisorJob(self.coresys)

        return self._jobs[context]

    @ignore_conditions.setter
    def ignore_conditions(self, value: List[JobCondition]) -> None:
        """Set a list of ignored condition."""
        self._data[ATTR_IGNORE_CONDITIONS] = value

    def get_job(self, name: str) -> SupervisorJob:
        """Return a job, create one if it does not exsist."""
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
