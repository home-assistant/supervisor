"""Job decorator."""
import asyncio
from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import Any, Optional

import sentry_sdk

from ..const import CoreState
from ..coresys import CoreSysAttributes
from ..exceptions import HassioError, JobConditionException, JobException
from ..host.const import HostFeature
from ..resolution.const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType
from .const import JobCondition, JobExecutionLimit

_LOGGER: logging.Logger = logging.getLogger(__package__)


class Job(CoreSysAttributes):
    """Supervisor job decorator."""

    def __init__(
        self,
        name: Optional[str] = None,
        conditions: Optional[list[JobCondition]] = None,
        cleanup: bool = True,
        on_condition: Optional[JobException] = None,
        limit: Optional[JobExecutionLimit] = None,
        throttle_period: Optional[timedelta] = None,
        throttle_max_calls: Optional[int] = None,
    ):
        """Initialize the Job class."""
        self.name = name
        self.conditions = conditions
        self.cleanup = cleanup
        self.on_condition = on_condition
        self.limit = limit
        self.throttle_period = throttle_period
        self.throttle_max_calls = throttle_max_calls
        self._lock: Optional[asyncio.Semaphore] = None
        self._method = None
        self._last_call = datetime.min
        self._rate_limited_calls: Optional[list[datetime]] = None

        # Validate Options
        if (
            self.limit
            in (
                JobExecutionLimit.THROTTLE,
                JobExecutionLimit.THROTTLE_WAIT,
                JobExecutionLimit.THROTTLE_RATE_LIMIT,
            )
            and self.throttle_period is None
        ):
            raise RuntimeError("Using Job without a Throttle period!")

        if self.limit == JobExecutionLimit.THROTTLE_RATE_LIMIT:
            if self.throttle_max_calls is None:
                raise RuntimeError("Using rate limit without throttle max calls!")

            self._rate_limited_calls = []

    def _post_init(self, args: tuple[Any]) -> None:
        """Runtime init."""
        if self.name is None:
            self.name = str(self._method.__qualname__).lower().replace(".", "_")

        # Coresys
        try:
            self.coresys = args[0].coresys
        except AttributeError:
            pass
        if not self.coresys:
            raise RuntimeError(f"Job on {self.name} need to be an coresys object!")

        # Others
        if self._lock is None:
            self._lock = asyncio.Semaphore()

    def __call__(self, method):
        """Call the wrapper logic."""
        self._method = method

        @wraps(method)
        async def wrapper(*args, **kwargs) -> Any:
            """Wrap the method."""
            self._post_init(args)

            job = self.sys_jobs.get_job(self.name)

            # Handle condition
            if self.conditions:
                try:
                    self._check_conditions()
                except JobConditionException as err:
                    error_msg = str(err)
                    if self.on_condition is None:
                        _LOGGER.info(error_msg)
                        return
                    raise self.on_condition(error_msg, _LOGGER.warning) from None

            # Handle exection limits
            if self.limit in (JobExecutionLimit.SINGLE_WAIT, JobExecutionLimit.ONCE):
                await self._acquire_exection_limit()
            elif self.limit == JobExecutionLimit.THROTTLE:
                time_since_last_call = datetime.now() - self._last_call
                if time_since_last_call < self.throttle_period:
                    return
            elif self.limit == JobExecutionLimit.THROTTLE_WAIT:
                await self._acquire_exection_limit()
                time_since_last_call = datetime.now() - self._last_call
                if time_since_last_call < self.throttle_period:
                    self._release_exception_limits()
                    return
            elif self.limit == JobExecutionLimit.THROTTLE_RATE_LIMIT:
                # Only reprocess array when necessary (at limit)
                if len(self._rate_limited_calls) >= self.throttle_max_calls:
                    self._rate_limited_calls = [
                        call
                        for call in self._rate_limited_calls
                        if call > datetime.now() - self.throttle_period
                    ]

                if len(self._rate_limited_calls) >= self.throttle_max_calls:
                    on_condition = (
                        JobException if self.on_condition is None else self.on_condition
                    )
                    raise on_condition(
                        f"Rate limit exceeded, more then {self.throttle_max_calls} calls in {self.throttle_period}",
                    )

            # Execute Job
            try:
                self._last_call = datetime.now()
                if self._rate_limited_calls is not None:
                    self._rate_limited_calls.append(self._last_call)

                return await self._method(*args, **kwargs)
            except HassioError as err:
                raise err
            except Exception as err:
                _LOGGER.exception("Unhandled exception: %s", err)
                sentry_sdk.capture_exception(err)
                raise JobException() from err
            finally:
                if self.cleanup:
                    self.sys_jobs.remove_job(job)
                self._release_exception_limits()

        return wrapper

    def _check_conditions(self):
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
                f"'{self._method.__qualname__}' blocked from execution, system is not healthy"
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

        if (
            JobCondition.INTERNET_SYSTEM in self.conditions
            and not self.sys_supervisor.connectivity
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, no supervisor internet connection"
            )

        if (
            JobCondition.INTERNET_HOST in self.conditions
            and self.sys_host.network.connectivity is not None
            and not self.sys_host.network.connectivity
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, no host internet connection"
            )

        if JobCondition.HAOS in self.conditions and not self.sys_os.available:
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, no Home Assistant OS available"
            )

        if (
            JobCondition.OS_AGENT in self.conditions
            and HostFeature.OS_AGENT not in self.sys_host.features
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, no Home Assistant OS-Agent available"
            )

        if (
            JobCondition.HOST_NETWORK in self.conditions
            and not self.sys_dbus.network.is_connected
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, host Network Manager not available"
            )

        if (
            JobCondition.AUTO_UPDATE in self.conditions
            and not self.sys_updater.auto_update
        ):
            raise JobCondition(
                f"'{self._method.__qualname__}' blocked from execution, supervisor auto updates disabled"
            )

        if (
            JobCondition.SUPERVISOR_UPDATED in self.conditions
            and self.sys_supervisor.need_update
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, supervisor needs to be updated first"
            )

        if JobCondition.PLUGINS_UPDATED in self.conditions and 0 < len(
            [plugin for plugin in self.sys_plugins.all_plugins if plugin.need_update]
        ):
            raise JobConditionException(
                f"'{self._method.__qualname__}' blocked from execution, plugin(s) {', '.join([plugin.slug for plugin in self.sys_plugins.all_plugins if plugin.need_update])} need to be updated first"
            )

    async def _acquire_exection_limit(self) -> None:
        """Process exection limits."""
        if self.limit not in (
            JobExecutionLimit.SINGLE_WAIT,
            JobExecutionLimit.ONCE,
            JobExecutionLimit.THROTTLE_WAIT,
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
        ):
            return
        self._lock.release()
