"""Supervisor job manager."""

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import contextmanager
from contextvars import Context, ContextVar, Token
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any
from uuid import uuid4

from attrs import Attribute, define, field
from attrs.setters import convert as attr_convert, frozen, validate as attr_validate
from attrs.validators import ge, le

from ..const import BusEvent
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError, JobNotFound, JobStartException
from ..homeassistant.const import WSEvent
from ..utils.common import FileConfiguration
from ..utils.dt import utcnow
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

# Context vars only act as a global within the same asyncio task
# When a new asyncio task is started the current context is copied over.
# Modifications to it in one task are not visible to others though.
# This allows us to track what job is currently in progress in each task.
_CURRENT_JOB: ContextVar[str] = ContextVar("current_job")

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass
class JobSchedulerOptions:
    """Options for scheduling a job."""

    start_at: datetime | None = None
    delayed_start: float = 0  # Ignored if start_at is set


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


def _invalid_if_started(instance: "SupervisorJob", *_) -> None:
    """Validate that job has not been started."""
    if instance.done is not None:
        raise ValueError("Field cannot be updated once job has started")


@define
class SupervisorJobError:
    """Representation of an error occurring during a supervisor job."""

    type_: type[HassioError] = HassioError
    message: str = "Unknown error, see supervisor logs"
    stage: str | None = None

    def as_dict(self) -> dict[str, str]:
        """Return dictionary representation."""
        return {
            "type": self.type_.__name__,
            "message": self.message,
            "stage": self.stage,
        }


@define(order=True)
class SupervisorJob:
    """Representation of a job running in supervisor."""

    created: datetime = field(init=False, factory=utcnow, on_setattr=frozen)
    uuid: str = field(init=False, factory=lambda: uuid4().hex, on_setattr=frozen)
    name: str | None = field(default=None, validator=[_invalid_if_started])
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
    parent_id: str | None = field(
        factory=lambda: _CURRENT_JOB.get(None), on_setattr=frozen
    )
    done: bool | None = field(init=False, default=None, on_setattr=_on_change)
    on_change: Callable[["SupervisorJob", Attribute, Any], None] | None = field(
        default=None, on_setattr=frozen
    )
    internal: bool = field(default=False)
    errors: list[SupervisorJobError] = field(
        init=False, factory=list, on_setattr=_on_change
    )
    release_event: asyncio.Event | None = None

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
            "created": self.created.isoformat(),
        }

    def capture_error(self, err: HassioError | None = None) -> None:
        """Capture an error or record that an unknown error has occurred."""
        if err:
            new_error = SupervisorJobError(type(err), str(err), self.stage)
        else:
            new_error = SupervisorJobError(stage=self.stage)
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
        token: Token[str] | None = None
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
        except (LookupError, JobNotFound):
            raise RuntimeError(
                "No job for the current asyncio task!", _LOGGER.critical
            ) from None

    @property
    def is_job(self) -> bool:
        """Return true if there is an active job for the current asyncio task."""
        return bool(_CURRENT_JOB.get(None))

    def _notify_on_job_change(
        self, job: SupervisorJob, attribute: Attribute, value: Any
    ) -> None:
        """Notify Home Assistant of a change to a job and bus on job start/end."""
        if attribute.name == "errors":
            value = [err.as_dict() for err in value]

        self.sys_homeassistant.websocket.supervisor_event(
            WSEvent.JOB, job.as_dict() | {attribute.name: value}
        )

        if attribute.name == "done":
            if value is False:
                self.sys_bus.fire_event(BusEvent.SUPERVISOR_JOB_START, job)
            if value is True:
                self.sys_bus.fire_event(BusEvent.SUPERVISOR_JOB_END, job)

    def new_job(
        self,
        name: str | None = None,
        reference: str | None = None,
        initial_stage: str | None = None,
        internal: bool = False,
        no_parent: bool = False,
    ) -> SupervisorJob:
        """Create a new job."""
        job = SupervisorJob(
            name,
            reference=reference,
            stage=initial_stage,
            on_change=None if internal else self._notify_on_job_change,
            internal=internal,
            **({"parent_id": None} if no_parent else {}),
        )
        self._jobs[job.uuid] = job
        return job

    def get_job(self, uuid: str) -> SupervisorJob:
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

        # Clean up any completed sub jobs of this one
        for sub_job in self.jobs:
            if sub_job.parent_id == job.uuid and job.done:
                self.remove_job(sub_job)

    def schedule_job(
        self,
        job_method: Callable[..., Awaitable[Any]],
        options: JobSchedulerOptions,
        *args,
        **kwargs,
    ) -> tuple[SupervisorJob, asyncio.Task | asyncio.TimerHandle]:
        """Schedule a job to run later and return job and task or timer handle."""
        job = self.new_job(no_parent=True)

        def _wrap_task() -> asyncio.Task:
            return self.sys_create_task(
                job_method(*args, _job__use_existing=job, **kwargs)
            )

        if options.start_at:
            return (job, self.sys_call_at(options.start_at, _wrap_task))
        if options.delayed_start:
            return (job, self.sys_call_later(options.delayed_start, _wrap_task))

        return (job, _wrap_task())
