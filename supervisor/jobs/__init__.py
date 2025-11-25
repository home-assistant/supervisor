"""Supervisor job manager."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Generator
from contextlib import contextmanager, suppress
from contextvars import Context, ContextVar, Token
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Self, cast
from uuid import uuid4

from attr.validators import gt, lt
from attrs import Attribute, define, field
from attrs.setters import convert as attr_convert, frozen, validate as attr_validate
from attrs.validators import ge, le

from ..const import BusEvent
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError, JobNotFound, JobStartException
from ..homeassistant.const import WSEvent
from ..utils.common import FileConfiguration
from ..utils.dt import utcnow
from ..utils.sentinel import DEFAULT
from .const import ATTR_IGNORE_CONDITIONS, FILE_CONFIG_JOBS, JobCondition
from .validate import SCHEMA_JOBS_CONFIG

# Context vars only act as a global within the same asyncio task
# When a new asyncio task is started the current context is copied over.
# Modifications to it in one task are not visible to others though.
# This allows us to track what job is currently in progress in each task.
_CURRENT_JOB: ContextVar[str | None] = ContextVar("current_job", default=None)

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


def _invalid_if_done(instance: SupervisorJob, *_) -> None:
    """Validate that job is not done."""
    if instance.done:
        raise ValueError("Cannot update a job that is done")


def _on_change(instance: SupervisorJob, attribute: Attribute, value: Any) -> Any:
    """Forward a change to a field on to the listener if defined."""
    value = attr_convert(instance, attribute, value)
    value = attr_validate(instance, attribute, value)
    if instance.on_change:
        instance.on_change(instance, attribute, value)
    return value


def _invalid_if_started(instance: SupervisorJob, *_) -> None:
    """Validate that job has not been started."""
    if instance.done is not None:
        raise ValueError("Field cannot be updated once job has started")


@define(frozen=True)
class ChildJobSyncFilter:
    """Filter to identify a child job to sync progress from."""

    name: str
    reference: str | None | type[DEFAULT] = DEFAULT
    progress_allocation: float = field(default=1.0, validator=[gt(0.0), le(1.0)])

    def matches(self, job: SupervisorJob) -> bool:
        """Return true if job matches filter."""
        return job.name == self.name and self.reference in (DEFAULT, job.reference)


@define(frozen=True)
class ParentJobSync:
    """Parent job sync details."""

    uuid: str
    starting_progress: float = field(validator=[ge(0.0), lt(100.0)])
    progress_allocation: float = field(validator=[gt(0.0), le(1.0)])


@define
class SupervisorJobError:
    """Representation of an error occurring during a supervisor job."""

    type_: type[HassioError] = HassioError
    message: str = (
        "Unknown error, see Supervisor logs (check with 'ha supervisor logs')"
    )
    stage: str | None = None

    def as_dict(self) -> dict[str, str | None]:
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
    )
    stage: str | None = field(
        default=None, validator=[_invalid_if_done], on_setattr=_on_change
    )
    parent_id: str | None = field(factory=_CURRENT_JOB.get, on_setattr=frozen)
    done: bool | None = field(init=False, default=None, on_setattr=_on_change)
    on_change: Callable[[SupervisorJob, Attribute, Any], None] | None = None
    internal: bool = field(default=False)
    errors: list[SupervisorJobError] = field(
        init=False, factory=list, on_setattr=_on_change
    )
    release_event: asyncio.Event | None = None
    extra: dict[str, Any] | None = None
    child_job_syncs: list[ChildJobSyncFilter] | None = None
    parent_job_syncs: list[ParentJobSync] = field(init=False, factory=list)

    def as_dict(self) -> dict[str, Any]:
        """Return dictionary representation."""
        return {
            "name": self.name,
            "reference": self.reference,
            "uuid": self.uuid,
            "progress": round(self.progress, 1),
            "stage": self.stage,
            "done": self.done,
            "parent_id": self.parent_id,
            "errors": [err.as_dict() for err in self.errors],
            "created": self.created.isoformat(),
            "extra": self.extra,
        }

    def capture_error(self, err: HassioError | None = None) -> None:
        """Capture an error or record that an unknown error has occurred."""
        if err:
            new_error = SupervisorJobError(type(err), str(err), self.stage)
        else:
            new_error = SupervisorJobError(stage=self.stage)
        self.errors += [new_error]

    @contextmanager
    def start(self) -> Generator[Self]:
        """Start the job in the current task.

        This can only be called if the parent ID matches the job running in the current task.
        This is to ensure that each asyncio task can only be doing one job at a time as that
        determines what resources it can and cannot access.
        """
        if self.done is not None:
            raise JobStartException("Job has already been started")
        if _CURRENT_JOB.get() != self.parent_id:
            raise JobStartException("Job has a different parent from current job")

        self.done = False
        token: Token[str | None] | None = None
        try:
            token = _CURRENT_JOB.set(self.uuid)
            yield self
        # Cannot have an else without an except so we do nothing and re-raise
        except:  # noqa: TRY203
            raise
        else:
            self.update(progress=100, done=True)
        finally:
            if not self.done:
                self.done = True
            if token:
                _CURRENT_JOB.reset(token)

    def update(
        self,
        progress: float | None = None,
        stage: str | None = None,
        extra: dict[str, Any] | None | type[DEFAULT] = DEFAULT,
        done: bool | None = None,
    ) -> None:
        """Update multiple fields with one on change event."""
        on_change = self.on_change
        self.on_change = None

        if progress is not None:
            self.progress = progress
        if stage is not None:
            self.stage = stage
        if extra is not DEFAULT:
            self.extra = cast(dict[str, Any] | None, extra)

        # Done has special event. use that to trigger on change if included
        # If not then just use any other field to trigger
        self.on_change = on_change
        if done is not None:
            self.done = done
        else:
            self.reference = self.reference


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
        if job_id := _CURRENT_JOB.get():
            with suppress(JobNotFound):
                return self.get_job(job_id)
        raise RuntimeError("No job for the current asyncio task!", _LOGGER.critical)

    @property
    def is_job(self) -> bool:
        """Return true if there is an active job for the current asyncio task."""
        return _CURRENT_JOB.get() is not None

    def _on_job_change(
        self, job: SupervisorJob, attribute: Attribute, value: Any
    ) -> None:
        """Take on change actions such as notify home assistant and sync progress."""
        # Job object will be before the change. Combine the change with current data
        if attribute.name == "errors":
            value = [err.as_dict() for err in value]
        job_data = job.as_dict() | {attribute.name: value}

        # Notify Home Assistant of change if its not internal
        if not job.internal:
            self.sys_homeassistant.websocket.supervisor_event(WSEvent.JOB, job_data)

        # If we have any parent job syncs, sync progress to them
        for sync in job.parent_job_syncs:
            try:
                parent_job = self.get_job(sync.uuid)
            except JobNotFound:
                # Shouldn't happen but failure to find a parent for progress
                # reporting shouldn't raise and break the active job
                continue

            progress = min(
                100,
                sync.starting_progress
                + (sync.progress_allocation * job_data["progress"]),
            )
            # Using max would always trigger on change even if progress was unchanged
            # pylint: disable-next=R1731
            if parent_job.progress < progress:  # noqa: PLR1730
                parent_job.progress = progress

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
        parent_id: str | None | type[DEFAULT] = DEFAULT,
        child_job_syncs: list[ChildJobSyncFilter] | None = None,
    ) -> SupervisorJob:
        """Create a new job."""
        kwargs: dict[str, Any] = {
            "reference": reference,
            "stage": initial_stage,
            "on_change": self._on_job_change,
            "internal": internal,
            "child_job_syncs": child_job_syncs,
        }
        if parent_id is not DEFAULT:
            kwargs["parent_id"] = parent_id

        job = SupervisorJob(name, **kwargs)

        # Shouldn't happen but inability to find a parent for progress reporting
        # shouldn't raise and break the active job
        with suppress(JobNotFound):
            curr_parent = job
            while curr_parent.parent_id:
                curr_parent = self.get_job(curr_parent.parent_id)
                if not curr_parent.child_job_syncs:
                    continue

                # HACK: If parent trigger the same child job, we just skip this second
                # sync. Maybe it would be better to have this reflected in the job stage
                # and reset progress to 0 instead? There is no support for such stage
                # information on Core update entities today though.
                if curr_parent.done is True or curr_parent.progress >= 100:
                    _LOGGER.debug(
                        "Skipping parent job sync for done parent job %s",
                        curr_parent.name,
                    )
                    continue

                # Break after first match at each parent as it doesn't make sense
                # to match twice. But it could match multiple parents
                for sync in curr_parent.child_job_syncs:
                    if sync.matches(job):
                        job.parent_job_syncs.append(
                            ParentJobSync(
                                curr_parent.uuid,
                                starting_progress=curr_parent.progress,
                                progress_allocation=sync.progress_allocation,
                            )
                        )
                        break

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
        job_method: Callable[..., Coroutine],
        options: JobSchedulerOptions,
        *args,
        **kwargs,
    ) -> tuple[SupervisorJob, asyncio.Task | asyncio.TimerHandle]:
        """Schedule a job to run later and return job and task or timer handle."""
        job = self.new_job(parent_id=None)

        def _wrap_task() -> asyncio.Task:
            return self.sys_create_task(
                job_method(*args, _job__use_existing=job, **kwargs)
            )

        if options.start_at:
            return (job, self.sys_call_at(options.start_at, _wrap_task))
        if options.delayed_start:
            return (job, self.sys_call_later(options.delayed_start, _wrap_task))

        return (job, _wrap_task())
