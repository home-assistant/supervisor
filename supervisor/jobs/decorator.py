"""Job decorator."""
import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import Any

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    HassioError,
    JobConditionException,
    JobException,
    JobGroupExecutionLimitExceeded,
)
from ..host.const import HostFeature
from ..resolution.const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType
from ..utils.sentry import capture_exception
from .const import JobCondition, JobExecutionLimit
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
        on_condition: JobException | None = None,
        limit: JobExecutionLimit | None = None,
        throttle_period: timedelta
        | Callable[[CoreSys, datetime, list[datetime] | None], timedelta]
        | None = None,
        throttle_max_calls: int | None = None,
        internal: bool = False,
    ):
        """Initialize the Job class."""
        if name in _JOB_NAMES:
            raise RuntimeError(f"A job already exists with name {name}!")

        _JOB_NAMES.add(name)
        self.name = name
        self.conditions = conditions
        self.cleanup = cleanup
        self.on_condition = on_condition
        self.limit = limit
        self._throttle_period = throttle_period
        self.throttle_max_calls = throttle_max_calls
        self._lock: asyncio.Semaphore | None = None
        self._method = None
        self._last_call: dict[str | None, datetime] = {}
        self._rate_limited_calls: dict[str, list[datetime]] | None = None
        self._internal = internal

        # Validate Options
        if (
            self.limit
            in (
                JobExecutionLimit.THROTTLE,
                JobExecutionLimit.THROTTLE_WAIT,
                JobExecutionLimit.THROTTLE_RATE_LIMIT,
                JobExecutionLimit.GROUP_THROTTLE,
                JobExecutionLimit.GROUP_THROTTLE_WAIT,
                JobExecutionLimit.GROUP_THROTTLE_RATE_LIMIT,
            )
            and self._throttle_period is None
        ):
            raise RuntimeError(
                f"Job {name} is using execution limit {limit.value} without a throttle period!"
            )

        if self.limit in (
            JobExecutionLimit.THROTTLE_RATE_LIMIT,
            JobExecutionLimit.GROUP_THROTTLE_RATE_LIMIT,
        ):
            if self.throttle_max_calls is None:
                raise RuntimeError(
                    f"Job {name} is using execution limit {limit.value} without throttle max calls!"
                )

            self._rate_limited_calls = {}

    def last_call(self, group_name: str | None = None) -> datetime:
        """Return last call datetime."""
        return self._last_call.get(group_name, datetime.min)

    def set_last_call(self, value: datetime, group_name: str | None = None) -> None:
        """Set last call datetime."""
        self._last_call[group_name] = value

    def rate_limited_calls(
        self, group_name: str | None = None
    ) -> list[datetime] | None:
        """Return rate limited calls if used."""
        if self._rate_limited_calls is None:
            return None

        return self._rate_limited_calls.get(group_name, [])

    def add_rate_limited_call(
        self, value: datetime, group_name: str | None = None
    ) -> None:
        """Add a rate limited call to list if used."""
        if self._rate_limited_calls is None:
            raise RuntimeError(
                f"Rate limited calls not available for limit type {self.limit}"
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
                f"Rate limited calls not available for limit type {self.limit}"
            )

        self._rate_limited_calls[group_name] = value

    def throttle_period(self, group_name: str | None = None) -> timedelta | None:
        """Return throttle period."""
        if self._throttle_period is None:
            return None

        if isinstance(self._throttle_period, timedelta):
            return self._throttle_period

        return self._throttle_period(
            self.coresys,
            self.last_call(group_name),
            self.rate_limited_calls(group_name),
        )

    def _post_init(self, obj: JobGroup | CoreSysAttributes) -> JobGroup | None:
        """Runtime init."""
        # Coresys
        try:
            self.coresys = obj.coresys
        except AttributeError:
            pass
        if not self.coresys:
            raise RuntimeError(f"Job on {self.name} need to be an coresys object!")

        # Setup lock for limits
        if self._lock is None:
            self._lock = asyncio.Semaphore()

        # Job groups
        if self.limit in (
            JobExecutionLimit.GROUP_ONCE,
            JobExecutionLimit.GROUP_WAIT,
            JobExecutionLimit.GROUP_THROTTLE,
            JobExecutionLimit.GROUP_THROTTLE_WAIT,
            JobExecutionLimit.GROUP_THROTTLE_RATE_LIMIT,
        ):
            try:
                _ = obj.acquire and obj.release
            except AttributeError:
                raise RuntimeError(
                    f"Job on {self.name} need to be a JobGroup to use group based limits!"
                ) from None

            return obj
        return None

    def __call__(self, method):
        """Call the wrapper logic."""
        self._method = method

        @wraps(method)
        async def wrapper(obj: JobGroup | CoreSysAttributes, *args, **kwargs) -> Any:
            """Wrap the method.

            This method must be on an instance of CoreSysAttributes. If a JOB_GROUP limit
            is used, then it must be on an instance of JobGroup.
            """
            job_group = self._post_init(obj)
            group_name: str | None = job_group.group_name if job_group else None
            job = self.sys_jobs.new_job(
                self.name,
                job_group.job_reference if job_group else None,
                internal=self._internal,
            )

            # Handle condition
            if self.conditions:
                try:
                    await self._check_conditions()
                except JobConditionException as err:
                    error_msg = str(err)
                    if self.on_condition is None:
                        _LOGGER.info(error_msg)
                        return
                    raise self.on_condition(error_msg, _LOGGER.warning) from None

            # Handle exection limits
            if self.limit in (JobExecutionLimit.SINGLE_WAIT, JobExecutionLimit.ONCE):
                await self._acquire_exection_limit()
            elif self.limit in (
                JobExecutionLimit.GROUP_ONCE,
                JobExecutionLimit.GROUP_WAIT,
            ):
                try:
                    await obj.acquire(job, self.limit == JobExecutionLimit.GROUP_WAIT)
                except JobGroupExecutionLimitExceeded as err:
                    if self.on_condition:
                        raise self.on_condition(str(err)) from err
                    raise err
            elif self.limit in (
                JobExecutionLimit.THROTTLE,
                JobExecutionLimit.GROUP_THROTTLE,
            ):
                time_since_last_call = datetime.now() - self.last_call(group_name)
                if time_since_last_call < self.throttle_period(group_name):
                    return
            elif self.limit in (
                JobExecutionLimit.THROTTLE_WAIT,
                JobExecutionLimit.GROUP_THROTTLE_WAIT,
            ):
                await self._acquire_exection_limit()
                time_since_last_call = datetime.now() - self.last_call(group_name)
                if time_since_last_call < self.throttle_period(group_name):
                    self._release_exception_limits()
                    return
            elif self.limit in (
                JobExecutionLimit.THROTTLE_RATE_LIMIT,
                JobExecutionLimit.GROUP_THROTTLE_RATE_LIMIT,
            ):
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
                        f"Rate limit exceeded, more then {self.throttle_max_calls} calls in {self.throttle_period(group_name)}",
                    )

            # Execute Job
            with job.start(on_done=self.sys_jobs.remove_job if self.cleanup else None):
                try:
                    self.set_last_call(datetime.now(), group_name)
                    if self.rate_limited_calls(group_name) is not None:
                        self.add_rate_limited_call(
                            self.last_call(group_name), group_name
                        )

                    return await self._method(obj, *args, **kwargs)
                except HassioError as err:
                    raise err
                except Exception as err:
                    _LOGGER.exception("Unhandled exception: %s", err)
                    capture_exception(err)
                    raise JobException() from err
                finally:
                    self._release_exception_limits()
                    if self.limit in (
                        JobExecutionLimit.GROUP_ONCE,
                        JobExecutionLimit.GROUP_WAIT,
                    ):
                        obj.release()

        return wrapper

    async def _check_conditions(self):
        """Check conditions."""
        used_conditions = set(self.conditions) - set(self.sys_jobs.ignore_conditions)
        ignored_conditions = set(self.conditions) & set(self.sys_jobs.ignore_conditions)

        # Check if somethings is ignored
        if ignored_conditions:
            _LOGGER.critical(
                "The following job conditions are ignored and will make the system unstable when they occur: %s",
                ignored_conditions,
            )

        if JobCondition.HEALTHY in used_conditions and not self.sys_core.healthy:
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, system is not healthy - {', '.join(self.sys_resolution.unhealthy)}"
            )

        if (
            JobCondition.RUNNING in used_conditions
            and self.sys_core.state != CoreState.RUNNING
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, system is not running - {self.sys_core.state!s}"
            )

        if (
            JobCondition.FREE_SPACE in used_conditions
            and self.sys_host.info.free_space < MINIMUM_FREE_SPACE_THRESHOLD
        ):
            self.sys_resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, not enough free space ({self.sys_host.info.free_space}GB) left on the device"
            )

        if JobCondition.INTERNET_SYSTEM in used_conditions:
            await self.sys_supervisor.check_connectivity()
            if not self.sys_supervisor.connectivity:
                raise JobConditionException(
                    f"'{self._method.__qualname__}' blocked from execution, no supervisor internet connection"
                )

        if JobCondition.INTERNET_HOST in used_conditions:
            await self.sys_host.network.check_connectivity()
            if (
                self.sys_host.network.connectivity is not None
                and not self.sys_host.network.connectivity
            ):
                raise JobConditionException(
                    f"'{self._method.__qualname__}' blocked from execution, no host internet connection"
                )

        if JobCondition.HAOS in used_conditions and not self.sys_os.available:
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, no Home Assistant OS available"
            )

        if (
            JobCondition.OS_AGENT in used_conditions
            and HostFeature.OS_AGENT not in self.sys_host.features
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, no Home Assistant OS-Agent available"
            )

        if (
            JobCondition.HOST_NETWORK in used_conditions
            and not self.sys_dbus.network.is_connected
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, host Network Manager not available"
            )

        if (
            JobCondition.AUTO_UPDATE in used_conditions
            and not self.sys_updater.auto_update
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, supervisor auto updates disabled"
            )

        if (
            JobCondition.SUPERVISOR_UPDATED in used_conditions
            and self.sys_supervisor.need_update
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, supervisor needs to be updated first"
            )

        if JobCondition.PLUGINS_UPDATED in used_conditions and (
            out_of_date := [
                plugin for plugin in self.sys_plugins.all_plugins if plugin.need_update
            ]
        ):
            errors = await asyncio.gather(
                *[plugin.update() for plugin in out_of_date], return_exceptions=True
            )

            if update_failures := [
                out_of_date[i].slug for i in range(len(errors)) if errors[i] is not None
            ]:
                raise JobConditionException(
                    f"'{self._method.__qualname__}' blocked from execution, was unable to update plugin(s) {', '.join(update_failures)} and all plugins must be up to date first"
                )

        if (
            JobCondition.MOUNT_AVAILABLE in used_conditions
            and HostFeature.MOUNT not in self.sys_host.features
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, mounting not supported on system"
            )

    async def _acquire_exection_limit(self) -> None:
        """Process exection limits."""
        if self.limit not in (
            JobExecutionLimit.SINGLE_WAIT,
            JobExecutionLimit.ONCE,
            JobExecutionLimit.THROTTLE_WAIT,
            JobExecutionLimit.GROUP_THROTTLE_WAIT,
        ):
            return

        if self.limit == JobExecutionLimit.ONCE and self._lock.locked():
            on_condition = (
                JobException if self.on_condition is None else self.on_condition
            )
            raise on_condition("Another job is running")

        await self._lock.acquire()

    def _release_exception_limits(self) -> None:
        """Release possible exception limits."""
        if self.limit not in (
            JobExecutionLimit.SINGLE_WAIT,
            JobExecutionLimit.ONCE,
            JobExecutionLimit.THROTTLE_WAIT,
            JobExecutionLimit.GROUP_THROTTLE_WAIT,
        ):
            return
        self._lock.release()
