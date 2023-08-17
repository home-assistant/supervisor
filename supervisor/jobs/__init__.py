"""Supervisor job manager."""
from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar, Token
import logging
from uuid import UUID, uuid4

from attrs import define, field
from attrs.setters import frozen
from attrs.validators import ge, le

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import JobNotFound, JobStartException
from ..utils.common import FileConfiguration
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

# Context vars only act as a global within the same asyncio task
# When a new asyncio task is started the current context is copied over.
# Modifications to it in one task are not visible to others though.
# This allows us to track what job is currently in progress in each task.
_CURRENT_JOB: ContextVar[UUID] = ContextVar("current_job")

_LOGGER: logging.Logger = logging.getLogger(__name__)


@define
class SupervisorJob:
    """Representation of a job running in supervisor."""

    name: str = field(on_setattr=frozen)
    reference: str | None = None
    progress: int = field(default=0, validator=[ge(0), le(100)])
    stage: str | None = None
    uuid: UUID = field(init=False, factory=lambda: uuid4().hex, on_setattr=frozen)
    parent_id: UUID = field(
        init=False, factory=lambda: _CURRENT_JOB.get(None), on_setattr=frozen
    )
    done: bool = field(init=False, default=False)

    @contextmanager
    def start(self, *, on_done: Callable[["SupervisorJob"], None] | None = None):
        """Start the job in the current task.

        This can only be called if the parent ID matches the job running in the current task.
        This is to ensure that each asyncio task can only be doing one job at a time as that
        determines what resources it can and cannot access.
        """
        if self.done:
            raise JobStartException("Job is already complete")
        if _CURRENT_JOB.get(None) != self.parent_id:
            raise JobStartException("Job has a different parent from current job")

        token: Token[UUID] | None = None
        try:
            token = _CURRENT_JOB.set(self.uuid)
            yield self
        finally:
            self.done = True
            if token:
                _CURRENT_JOB.reset(token)
            if on_done:
                on_done(self)


class JobManager(FileConfiguration, CoreSysAttributes):
    """Job Manager class."""

    def __init__(self, coresys: CoreSys):
        """Initialize the JobManager class."""
        super().__init__(FILE_CONFIG_JOBS, SCHEMA_JOBS_CONFIG)
        self.coresys: CoreSys = coresys
        self._jobs: dict[str, SupervisorJob] = {}

    @property
    def jobs(self) -> list[SupervisorJob]:
        """Return a list of current jobs."""
        return list(self._jobs.values())

    @property
    def ignore_conditions(self) -> list[JobCondition]:
        """Return a list of ingore condition."""
        return self._data[ATTR_IGNORE_CONDITIONS]

    @ignore_conditions.setter
    def ignore_conditions(self, value: list[JobCondition]) -> None:
        """Set a list of ignored condition."""
        self._data[ATTR_IGNORE_CONDITIONS] = value

    def new_job(
        self, name: str, reference: str | None = None, initial_stage: str | None = None
    ) -> SupervisorJob:
        """Create a new job."""
        job = SupervisorJob(name, reference=reference, stage=initial_stage)
        self._jobs[job.uuid] = job
        return job

    def get_job(self, uuid: UUID | None = None) -> SupervisorJob | None:
        """Return a job by uuid if it exists. Returns the current job of the asyncio task if uuid omitted."""
        if uuid:
            return self._jobs.get(uuid)

        if uuid := _CURRENT_JOB.get(None):
            return self._jobs.get(uuid)

        return None

    def remove_job(self, job: SupervisorJob) -> None:
        """Remove a job by UUID."""
        if job.uuid not in self._jobs:
            raise JobNotFound(f"Could not find job {job.name}", _LOGGER.error)

        if not job.done:
            _LOGGER.warning("Removing incomplete job %s from job manager", job.name)

        del self._jobs[job.uuid]
