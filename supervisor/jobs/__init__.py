"""Supervisor job manager."""
from contextlib import contextmanager
from contextvars import ContextVar
from uuid import UUID, uuid4

from attrs import define, field
from attrs.setters import frozen
from attrs.validators import ge, le

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import JobStartException
from ..utils.common import FileConfiguration
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

current_job: ContextVar[UUID] = ContextVar("current_job")


@define
class SupervisorJob:
    """Supervisor running job class."""

    name: str = field(on_setattr=frozen)
    progress: int = field(default=0, validator=[ge(0), le(100)])
    stage: str | None = None
    uuid: UUID = field(init=False, factory=lambda: uuid4().hex, on_setattr=frozen)
    parent_id: UUID = field(
        init=False, factory=lambda: current_job.get(None), on_setattr=frozen
    )
    done: bool = field(init=False, default=False)

    @contextmanager
    def start(self):
        """Start the job in the current task."""
        if self.done:
            raise JobStartException("Job is already complete")
        if current_job.get(None) != self.parent_id:
            raise JobStartException("Job has a different parent from current job")

        try:
            token = current_job.set(self.uuid)
            yield self
        finally:
            self.done = True
            if token:
                current_job.reset(token)


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
        return list(self._jobs.values())

    @property
    def ignore_conditions(self) -> list[JobCondition]:
        """Return a list of ingore condition."""
        return self._data[ATTR_IGNORE_CONDITIONS]

    @ignore_conditions.setter
    def ignore_conditions(self, value: list[JobCondition]) -> None:
        """Set a list of ignored condition."""
        self._data[ATTR_IGNORE_CONDITIONS] = value

    def new_job(self, name: str, initial_stage: str | None = None) -> SupervisorJob:
        """Create a new job."""
        job = SupervisorJob(name, stage=initial_stage)
        self._jobs[job.uuid] = job
        return job

    def get_job(self, uuid: UUID | None = None) -> SupervisorJob | None:
        """Return a job by uuid if it exists. Returns the current job of the thread if uuid omitted."""
        if uuid:
            return self._jobs.get(uuid)

        if uuid := current_job.get(None):
            return self._jobs.get(uuid)
        return None
