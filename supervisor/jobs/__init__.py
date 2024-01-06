"""Supervisor job manager."""
from collections.abc import Callable
from contextlib import contextmanager
from contextvars import Context, ContextVar, Token
import logging
from typing import Any
from uuid import UUID, uuid4

from attrs import Attribute, define, field
from attrs.setters import convert as attr_convert, frozen, validate as attr_validate
from attrs.validators import ge, le

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError, JobNotFound, JobStartException
from ..homeassistant.const import WSEvent
from ..utils.common import FileConfiguration
from ..utils.sentry import capture_exception
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

# Context vars only act as a global within the same asyncio task
# When a new asyncio task is started the current context is copied over.
# Modifications to it in one task are not visible to others though.
# This allows us to track what job is currently in progress in each task.
_CURRENT_JOB: ContextVar[UUID] = ContextVar("current_job")

_LOGGER: logging.Logger = logging.getLogger(__name__)


def _remove_current_job(context: Context) -> Context:
    """Remove the current job from the context."""
    context.run(_CURRENT_JOB.set, None)
    return context


def _invalid_if_done(instance: "SupervisorJob", *_) -> None:
    """Validate that job is not done."""
    if instance.done:
        raise ValueError("Cannot update a job that is done")


def _on_change(instance: "SupervisorJob", attribute: Attribute, value: Any) -> Any:
    """Forward a change to a field on to the listener if defined."""
    value = attr_convert(instance, attribute, value)
    value = attr_validate(instance, attribute, value)
    if instance.on_change:
        instance.on_change(instance, attribute, value)
    return value


@define
class SupervisorJobError:
    """Representation of an error occurring during a supervisor job."""

    type_: type[HassioError] = HassioError
    message: str = "Unknown error, see supervisor logs"

    def as_dict(self) -> dict[str, str]:
        """Return dictionary representation."""
        return {"type": self.type_.__name__, "message": self.message}


@define
class SupervisorJob:
    """Representation of a job running in supervisor."""

    name: str = field(on_setattr=frozen)
    reference: str | None = field(default=None, on_setattr=_on_change)
    progress: float = field(
        default=0,
        validator=[ge(0), le(100), _invalid_if_done],
        on_setattr=_on_change,
        converter=lambda val: round(val, 1),
    )
    stage: str | None = field(
        default=None, validator=[_invalid_if_done], on_setattr=_on_change
    )
    uuid: UUID = field(init=False, factory=lambda: uuid4().hex, on_setattr=frozen)
    parent_id: UUID | None = field(
        init=False, factory=lambda: _CURRENT_JOB.get(None), on_setattr=frozen
    )
    done: bool | None = field(init=False, default=None, on_setattr=_on_change)
    on_change: Callable[["SupervisorJob", Attribute, Any], None] | None = field(
        default=None, on_setattr=frozen
    )
    internal: bool = field(default=False, on_setattr=frozen)
    errors: list[SupervisorJobError] = field(
        init=False, factory=list, on_setattr=_on_change
    )

    def as_dict(self) -> dict[str, Any]:
        """Return dictionary representation."""
        return {
            "name": self.name,
            "reference": self.reference,
            "uuid": self.uuid,
            "progress": self.progress,
            "stage": self.stage,
            "done": self.done,
            "parent_id": self.parent_id,
            "errors": [err.as_dict() for err in self.errors],
        }

    def capture_error(self, err: HassioError | None = None) -> None:
        """Capture an error or record that an unknown error has occurred."""
        if err:
            new_error = SupervisorJobError(type(err), str(err))
        else:
            new_error = SupervisorJobError()
        self.errors += [new_error]

    @contextmanager
    def start(self):
        """Start the job in the current task.

        This can only be called if the parent ID matches the job running in the current task.
        This is to ensure that each asyncio task can only be doing one job at a time as that
        determines what resources it can and cannot access.
        """
        if self.done is not None:
            raise JobStartException("Job has already been started")
        if _CURRENT_JOB.get(None) != self.parent_id:
            raise JobStartException("Job has a different parent from current job")

        self.done = False
        token: Token[UUID] | None = None
        try:
            token = _CURRENT_JOB.set(self.uuid)
            yield self
        finally:
            self.done = True
            if token:
                _CURRENT_JOB.reset(token)


class JobManager(FileConfiguration, CoreSysAttributes):
    """Job Manager class."""

    def __init__(self, coresys: CoreSys):
        """Initialize the JobManager class."""
        super().__init__(FILE_CONFIG_JOBS, SCHEMA_JOBS_CONFIG)
        self.coresys: CoreSys = coresys
        self._jobs: dict[str, SupervisorJob] = {}

        # Ensure tasks created via CoreSys.create_task do not have a parent
        self.coresys.add_set_task_context_callback(_remove_current_job)

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

    @property
    def current(self) -> SupervisorJob:
        """Return current job of the asyncio task.

        Must be called from within a job. Raises RuntimeError if there is no current job.
        """
        try:
            return self.get_job(_CURRENT_JOB.get())
        except (LookupError, JobNotFound) as err:
            capture_exception(err)
            raise RuntimeError("No job for the current asyncio task!") from None

    @property
    def is_job(self) -> bool:
        """Return true if there is an active job for the current asyncio task."""
        return bool(_CURRENT_JOB.get(None))

    def _notify_on_job_change(
        self, job: SupervisorJob, attribute: Attribute, value: Any
    ) -> None:
        """Notify Home Assistant of a change to a job."""
        self.sys_homeassistant.websocket.supervisor_event(
            WSEvent.JOB, job.as_dict() | {attribute.alias: value}
        )

    def new_job(
        self,
        name: str,
        reference: str | None = None,
        initial_stage: str | None = None,
        internal: bool = False,
    ) -> SupervisorJob:
        """Create a new job."""
        job = SupervisorJob(
            name,
            reference=reference,
            stage=initial_stage,
            on_change=None if internal else self._notify_on_job_change,
            internal=internal,
        )
        self._jobs[job.uuid] = job
        return job

    def get_job(self, uuid: UUID) -> SupervisorJob:
        """Return a job by uuid. Raises if it does not exist."""
        if uuid not in self._jobs:
            raise JobNotFound(f"No job found with id {uuid}")
        return self._jobs[uuid]

    def remove_job(self, job: SupervisorJob) -> None:
        """Remove a job by UUID."""
        if job.uuid not in self._jobs:
            raise JobNotFound(f"Could not find job {job.name}", _LOGGER.error)

        if job.done is False:
            _LOGGER.warning("Removing incomplete job %s from job manager", job.name)

        del self._jobs[job.uuid]
