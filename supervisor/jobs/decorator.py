"""Job decorator."""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import Any, cast

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    HassioError,
    JobConditionException,
    JobException,
    JobGroupExecutionLimitExceeded,
)
from ..host.const import HostFeature
from ..resolution.const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    ContextType,
    IssueType,
    UnsupportedReason,
)
from ..utils.sentry import async_capture_exception
from . import ChildJobSyncFilter, SupervisorJob
from .const import JobConcurrency, JobCondition, JobThrottle
from .job_group import JobGroup

_LOGGER: logging.Logger = logging.getLogger(__package__)
_JOB_NAMES: set[str] = set()


class Job(CoreSysAttributes):
    """Supervisor job decorator."""

    def __init__(
        self,
        name: str,
        conditions: list[JobCondition] | None = None,
        cleanup: bool = True,
        on_condition: type[JobException] | None = None,
        concurrency: JobConcurrency | None = None,
        throttle: JobThrottle | None = None,
        throttle_period: timedelta
        | Callable[[CoreSys, datetime, list[datetime] | None], timedelta]
        | None = None,
        throttle_max_calls: int | None = None,
        internal: bool = False,
        child_job_syncs: list[ChildJobSyncFilter] | None = None,
    ):  # pylint: disable=too-many-positional-arguments
        """Initialize the Job decorator.

        Args:
            name (str): Unique name for the job. Must not be duplicated.
            conditions (list[JobCondition] | None): List of conditions that must be met before the job runs.
            cleanup (bool): Whether to clean up the job after execution. Defaults to True. If set to False, the job will remain accessible through the Supervisor API until the next restart.
            on_condition (type[JobException] | None): Exception type to raise if a job condition fails. If None, logs the failure.
            concurrency (JobConcurrency | None): Concurrency control policy (e.g., reject, queue, group-based).
            throttle (JobThrottle | None): Throttling policy (e.g., throttle, rate_limit, group-based).
            throttle_period (timedelta | Callable | None): Throttle period as a timedelta or a callable returning a timedelta (for throttled jobs).
            throttle_max_calls (int | None): Maximum number of calls allowed within the throttle period (for rate-limited jobs).
            internal (bool): Whether the job is internal (not exposed through the Supervisor API). Defaults to False.
            child_job_syncs (list[ChildJobSyncFilter] | None): Use if jobs progress should be kept in sync with progress of one or more of its child jobs.ye

        Raises:
            RuntimeError: If job name is not unique, or required throttle parameters are missing for the selected throttle policy.

        """
        if name in _JOB_NAMES:
            raise RuntimeError(f"A job already exists with name {name}!")

        _JOB_NAMES.add(name)
        self.name = name
        self.conditions = conditions
        self.cleanup = cleanup
        self.on_condition = on_condition
        self._throttle_period = throttle_period
        self._throttle_max_calls = throttle_max_calls
        self._lock: asyncio.Lock | None = None
        self._last_call: dict[str | None, datetime] = {}
        self._rate_limited_calls: dict[str | None, list[datetime]] | None = None
        self._internal = internal
        self._child_job_syncs = child_job_syncs

        self.concurrency = concurrency
        self.throttle = throttle

        # Validate Options
        self._validate_parameters()

    def _is_group_concurrency(self) -> bool:
        """Check if this job uses group-level concurrency."""
        return self.concurrency in (
            JobConcurrency.GROUP_REJECT,
            JobConcurrency.GROUP_QUEUE,
        )

    def _is_group_throttle(self) -> bool:
        """Check if this job uses group-level throttling."""
        return self.throttle in (
            JobThrottle.GROUP_THROTTLE,
            JobThrottle.GROUP_RATE_LIMIT,
        )

    def _is_rate_limit_throttle(self) -> bool:
        """Check if this job uses rate limiting (job or group level)."""
        return self.throttle in (
            JobThrottle.RATE_LIMIT,
            JobThrottle.GROUP_RATE_LIMIT,
        )

    def _validate_parameters(self) -> None:
        """Validate job parameters."""
        # Validate throttle parameters
        if self.throttle is not None and self._throttle_period is None:
            raise RuntimeError(
                f"Job {self.name} is using throttle {self.throttle} without a throttle period!"
            )

        if self._is_rate_limit_throttle():
            if self._throttle_max_calls is None:
                raise RuntimeError(
                    f"Job {self.name} is using throttle {self.throttle} without throttle max calls!"
                )
            self._rate_limited_calls = {}

    @property
    def throttle_max_calls(self) -> int:
        """Return max calls for throttle."""
        if self._throttle_max_calls is None:
            raise RuntimeError("No throttle max calls set for job!")
        return self._throttle_max_calls

    @property
    def lock(self) -> asyncio.Lock:
        """Return lock for limits."""
        # asyncio.Lock objects must be created in event loop
        # Since this is sync code it is not safe to create if missing here
        if not self._lock:
            raise RuntimeError("Lock has not been created yet!")
        return self._lock

    def last_call(self, group_name: str | None = None) -> datetime:
        """Return last call datetime."""
        return self._last_call.get(group_name, datetime.min)

    def set_last_call(self, value: datetime, group_name: str | None = None) -> None:
        """Set last call datetime."""
        self._last_call[group_name] = value

    def rate_limited_calls(self, group_name: str | None = None) -> list[datetime]:
        """Return rate limited calls if used."""
        if self._rate_limited_calls is None:
            raise RuntimeError(
                "Rate limited calls not available for this throttle type"
            )

        return self._rate_limited_calls.get(group_name, [])

    def add_rate_limited_call(
        self, value: datetime, group_name: str | None = None
    ) -> None:
        """Add a rate limited call to list if used."""
        if self._rate_limited_calls is None:
            raise RuntimeError(
                "Rate limited calls not available for this throttle type"
            )

        if group_name in self._rate_limited_calls:
            self._rate_limited_calls[group_name].append(value)
        else:
            self._rate_limited_calls[group_name] = [value]

    def set_rate_limited_calls(
        self, value: list[datetime], group_name: str | None = None
    ) -> None:
        """Set rate limited calls if used."""
        if self._rate_limited_calls is None:
            raise RuntimeError(
                "Rate limited calls not available for this throttle type"
            )

        self._rate_limited_calls[group_name] = value

    def throttle_period(self, group_name: str | None = None) -> timedelta:
        """Return throttle period."""
        if self._throttle_period is None:
            raise RuntimeError("No throttle period set for Job!")

        if isinstance(self._throttle_period, timedelta):
            return self._throttle_period

        return self._throttle_period(
            self.coresys,
            self.last_call(group_name),
            self.rate_limited_calls(group_name) if self._rate_limited_calls else None,
        )

    def _post_init(self, obj: JobGroup | CoreSysAttributes) -> JobGroup | None:
        """Runtime init."""
        # Coresys
        with suppress(AttributeError):
            self.coresys = obj.coresys
        if not self.coresys:
            raise RuntimeError(f"Job on {self.name} need to be an coresys object!")

        # Setup lock for limits
        if self._lock is None:
            self._lock = asyncio.Lock()

        # Job groups
        job_group: JobGroup | None = None
        with suppress(AttributeError):
            if obj.acquire and obj.release:  # type: ignore
                job_group = cast(JobGroup, obj)

        # Check for group-based parameters
        if not job_group:
            if self._is_group_concurrency():
                raise RuntimeError(
                    f"Job {self.name} uses group concurrency ({self.concurrency}) but is not on a JobGroup! "
                    f"The class must inherit from JobGroup to use GROUP_REJECT or GROUP_QUEUE."
                ) from None
            if self._is_group_throttle():
                raise RuntimeError(
                    f"Job {self.name} uses group throttling ({self.throttle}) but is not on a JobGroup! "
                    f"The class must inherit from JobGroup to use GROUP_THROTTLE or GROUP_RATE_LIMIT."
                ) from None

        return job_group

    def _handle_job_condition_exception(self, err: JobConditionException) -> None:
        """Handle a job condition failure."""
        error_msg = str(err)
        if self.on_condition is None:
            _LOGGER.info(error_msg)
            return
        raise self.on_condition(error_msg, _LOGGER.warning) from None

    def __call__(self, method: Callable[..., Awaitable]):
        """Call the wrapper logic."""

        @wraps(method)
        async def wrapper(
            obj: JobGroup | CoreSysAttributes,
            *args,
            _job__use_existing: SupervisorJob | None = None,
            _job_override__cleanup: bool | None = None,
            **kwargs,
        ) -> Any:
            """Wrap the method.

            This method must be on an instance of CoreSysAttributes. If a JOB_GROUP limit
            is used, then it must be on an instance of JobGroup.
            """
            job_group = self._post_init(obj)
            group_name: str | None = job_group.group_name if job_group else None
            if _job__use_existing:
                job = _job__use_existing
                job.name = self.name
                job.internal = self._internal
                job.child_job_syncs = self._child_job_syncs
                if job_group:
                    job.reference = job_group.job_reference
            else:
                job = self.sys_jobs.new_job(
                    self.name,
                    job_group.job_reference if job_group else None,
                    internal=self._internal,
                    child_job_syncs=self._child_job_syncs,
                )

            try:
                # Handle condition
                if self.conditions:
                    try:
                        await Job.check_conditions(
                            self, set(self.conditions), method.__qualname__
                        )
                    except JobConditionException as err:
                        return self._handle_job_condition_exception(err)

                # Handle execution limits using context manager
                async with self._concurrency_control(job_group, job):
                    if not await self._handle_throttling(group_name):
                        return  # Job was throttled, exit early

                    # Execute Job
                    with job.start():
                        try:
                            self.set_last_call(datetime.now(), group_name)
                            if self._rate_limited_calls is not None:
                                self.add_rate_limited_call(
                                    self.last_call(group_name), group_name
                                )

                            return await method(obj, *args, **kwargs)

                        # If a method has a conditional JobCondition, they must check it in the method
                        # These should be handled like normal JobConditions as much as possible
                        except JobConditionException as err:
                            return self._handle_job_condition_exception(err)
                        except HassioError as err:
                            job.capture_error(err)
                            raise err
                        except Exception as err:
                            _LOGGER.exception("Unhandled exception: %s", err)
                            job.capture_error()
                            await async_capture_exception(err)
                            raise JobException() from err

            # Jobs that weren't started are always cleaned up. Also clean up done jobs if required
            finally:
                if (
                    job.done is None
                    or _job_override__cleanup
                    or _job_override__cleanup is None
                    and self.cleanup
                ):
                    self.sys_jobs.remove_job(job)

        return wrapper

    @staticmethod
    async def check_conditions(
        coresys: CoreSysAttributes, conditions: set[JobCondition], method_name: str
    ):
        """Check conditions."""
        used_conditions = set(conditions) - set(coresys.sys_jobs.ignore_conditions)
        ignored_conditions = set(conditions) & set(coresys.sys_jobs.ignore_conditions)

        # Check if somethings is ignored
        if ignored_conditions:
            _LOGGER.critical(
                "The following job conditions are ignored and will make the system unstable when they occur: %s",
                ignored_conditions,
            )

        if JobCondition.HEALTHY in used_conditions and not coresys.sys_core.healthy:
            raise JobConditionException(
                f"'{method_name}' blocked from execution, system is not healthy - {', '.join(coresys.sys_resolution.unhealthy)}"
            )

        if (
            JobCondition.RUNNING in used_conditions
            and coresys.sys_core.state != CoreState.RUNNING
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, system is not running - {coresys.sys_core.state!s}"
            )

        if (
            JobCondition.FROZEN in used_conditions
            and coresys.sys_core.state != CoreState.FREEZE
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, system is not frozen - {coresys.sys_core.state!s}"
            )

        if (
            JobCondition.FREE_SPACE in used_conditions
            and (free_space := await coresys.sys_host.info.free_space())
            < MINIMUM_FREE_SPACE_THRESHOLD
        ):
            coresys.sys_resolution.create_issue(
                IssueType.FREE_SPACE, ContextType.SYSTEM
            )
            raise JobConditionException(
                f"'{method_name}' blocked from execution, not enough free space ({free_space}GB) left on the device"
            )

        if JobCondition.INTERNET_SYSTEM in used_conditions:
            await coresys.sys_supervisor.check_connectivity()
            if not coresys.sys_supervisor.connectivity:
                raise JobConditionException(
                    f"'{method_name}' blocked from execution, no supervisor internet connection"
                )

        if JobCondition.INTERNET_HOST in used_conditions:
            await coresys.sys_host.network.check_connectivity()
            if (
                coresys.sys_host.network.connectivity is not None
                and not coresys.sys_host.network.connectivity
            ):
                raise JobConditionException(
                    f"'{method_name}' blocked from execution, no host internet connection"
                )

        if JobCondition.HAOS in used_conditions and not coresys.sys_os.available:
            raise JobConditionException(
                f"'{method_name}' blocked from execution, no Home Assistant OS available"
            )

        if (
            JobCondition.OS_AGENT in used_conditions
            and HostFeature.OS_AGENT not in coresys.sys_host.features
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, no Home Assistant OS-Agent available"
            )

        if (
            JobCondition.OS_SUPPORTED in used_conditions
            and UnsupportedReason.OS_VERSION in coresys.sys_resolution.unsupported
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, unsupported OS version"
            )

        if (
            JobCondition.HOME_ASSISTANT_CORE_SUPPORTED in used_conditions
            and UnsupportedReason.HOME_ASSISTANT_CORE_VERSION
            in coresys.sys_resolution.unsupported
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, unsupported Home Assistant Core version"
            )

        if (
            JobCondition.HOST_NETWORK in used_conditions
            and not coresys.sys_dbus.network.is_connected
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, host Network Manager not available"
            )

        if (
            JobCondition.AUTO_UPDATE in used_conditions
            and not coresys.sys_updater.auto_update
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, supervisor auto updates disabled"
            )

        if (
            JobCondition.SUPERVISOR_UPDATED in used_conditions
            and coresys.sys_supervisor.need_update
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, supervisor needs to be updated first"
            )

        if JobCondition.PLUGINS_UPDATED in used_conditions and (
            out_of_date := [
                plugin
                for plugin in coresys.sys_plugins.all_plugins
                if plugin.need_update
            ]
        ):
            errors = await asyncio.gather(
                *[plugin.update() for plugin in out_of_date], return_exceptions=True
            )

            if update_failures := [
                out_of_date[i].slug for i in range(len(errors)) if errors[i] is not None
            ]:
                raise JobConditionException(
                    f"'{method_name}' blocked from execution, was unable to update plugin(s) {', '.join(update_failures)} and all plugins must be up to date first"
                )

        if (
            JobCondition.MOUNT_AVAILABLE in used_conditions
            and HostFeature.MOUNT not in coresys.sys_host.features
        ):
            raise JobConditionException(
                f"'{method_name}' blocked from execution, mounting not supported on system"
            )

    def _release_concurrency_control(
        self, job_group: JobGroup | None, job: SupervisorJob
    ) -> None:
        """Release concurrency control locks."""
        if self._is_group_concurrency():
            # Group-level concurrency: delegate to job group
            cast(JobGroup, job_group).release(job)
        elif self.concurrency in (JobConcurrency.REJECT, JobConcurrency.QUEUE):
            # Job-level concurrency: use semaphore
            if self.lock.locked():
                self.lock.release()

    async def _handle_concurrency_control(
        self, job_group: JobGroup | None, job: SupervisorJob
    ) -> None:
        """Handle concurrency control limits."""
        if self._is_group_concurrency():
            # Group-level concurrency: delegate to job group
            try:
                await cast(JobGroup, job_group).acquire(
                    job, wait=self.concurrency == JobConcurrency.GROUP_QUEUE
                )
            except JobGroupExecutionLimitExceeded as err:
                if self.on_condition:
                    raise self.on_condition(str(err)) from err
                raise err
        elif self.concurrency == JobConcurrency.REJECT:
            # Job-level reject: fail if lock is taken
            if self.lock.locked():
                on_condition = (
                    JobException if self.on_condition is None else self.on_condition
                )
                raise on_condition("Another job is running")
            await self.lock.acquire()
        elif self.concurrency == JobConcurrency.QUEUE:
            # Job-level queue: wait for lock
            await self.lock.acquire()

    @asynccontextmanager
    async def _concurrency_control(
        self, job_group: JobGroup | None, job: SupervisorJob
    ) -> AsyncIterator[None]:
        """Context manager for concurrency control that ensures locks are always released."""
        await self._handle_concurrency_control(job_group, job)
        try:
            yield
        finally:
            self._release_concurrency_control(job_group, job)

    async def _handle_throttling(self, group_name: str | None) -> bool:
        """Handle throttling limits. Returns True if job should continue, False if throttled."""
        if self.throttle in (JobThrottle.THROTTLE, JobThrottle.GROUP_THROTTLE):
            time_since_last_call = datetime.now() - self.last_call(group_name)
            throttle_period = self.throttle_period(group_name)
            if time_since_last_call < throttle_period:
                # Always return False when throttled (skip execution)
                return False
        elif self._is_rate_limit_throttle():
            # Only reprocess array when necessary (at limit)
            if len(self.rate_limited_calls(group_name)) >= self.throttle_max_calls:
                self.set_rate_limited_calls(
                    [
                        call
                        for call in self.rate_limited_calls(group_name)
                        if call > datetime.now() - self.throttle_period(group_name)
                    ],
                    group_name,
                )

            if len(self.rate_limited_calls(group_name)) >= self.throttle_max_calls:
                on_condition = (
                    JobException if self.on_condition is None else self.on_condition
                )
                raise on_condition(
                    f"Rate limit exceeded, more than {self.throttle_max_calls} calls in {self.throttle_period(group_name)}",
                )

        return True
