"""Job decorator."""
import asyncio
from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import Any, List, Optional, Tuple

import sentry_sdk

from ..const import CoreState
from ..coresys import CoreSysAttributes
from ..exceptions import HassioError, JobException
from ..resolution.const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType
from .const import JobCondition, JobExecutionLimit

_LOGGER: logging.Logger = logging.getLogger(__package__)


class Job(CoreSysAttributes):
    """Supervisor job decorator."""

    def __init__(
        self,
        name: Optional[str] = None,
        conditions: Optional[List[JobCondition]] = None,
        cleanup: bool = True,
        on_condition: Optional[JobException] = None,
        limit: Optional[JobExecutionLimit] = None,
        throttle_period: Optional[timedelta] = None,
    ):
        """Initialize the Job class."""
        self.name = name
        self.conditions = conditions
        self.cleanup = cleanup
        self.on_condition = on_condition
        self.limit = limit
        self.throttle_period = throttle_period
        self._lock: Optional[asyncio.Semaphore] = None
        self._method = None
        self._last_call = datetime.min

    def _post_init(self, args: Tuple[Any]) -> None:
        """Runtime init."""
        if self.name is None:
            self.name = str(self._method.__qualname__).lower().replace(".", "_")

        # Coresys
        try:
            self.coresys = args[0].coresys
        except AttributeError:
            pass
        if not self.coresys:
            raise JobException(f"coresys is missing on {self.name}")

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
            if self.conditions and not self._check_conditions():
                if self.on_condition is None:
                    return
                raise self.on_condition()

            # Handle exection limits
            if self.limit == JobExecutionLimit.SINGLE_WAIT:
                await self._acquire_exection_limit()
            elif self.limit == JobExecutionLimit.THROTTLE:
                time_since_last_call = datetime.now() - self._last_call
                if time_since_last_call < self.throttle_period:
                    return
            elif self.limit == JobExecutionLimit.THROTTLE_WAIT:
                time_since_last_call = datetime.now() - self._last_call
                if time_since_last_call < self.throttle_period:
                    if self._lock.locked():
                        await self._acquire_exection_limit()
                        self._release_exception_limits()
                    return
                await self._acquire_exection_limit()

            # Execute Job
            try:
                self._last_call = datetime.now()
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
            _LOGGER.warning(
                "'%s' blocked from execution, system is not healthy",
                self._method.__qualname__,
            )
            return False

        if (
            JobCondition.RUNNING in used_conditions
            and self.sys_core.state != CoreState.RUNNING
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, system is not running - %s",
                self._method.__qualname__,
                self.sys_core.state,
            )
            return False

        if (
            JobCondition.FREE_SPACE in used_conditions
            and self.sys_host.info.free_space < MINIMUM_FREE_SPACE_THRESHOLD
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, not enough free space (%sGB) left on the device",
                self._method.__qualname__,
                self.sys_host.info.free_space,
            )
            self.sys_resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)
            return False

        if (
            JobCondition.INTERNET_SYSTEM in self.conditions
            and not self.sys_supervisor.connectivity
            and self.sys_core.state in (CoreState.SETUP, CoreState.RUNNING)
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, no supervisor internet connection",
                self._method.__qualname__,
            )
            return False

        if (
            JobCondition.INTERNET_HOST in self.conditions
            and self.sys_host.network.connectivity is not None
            and not self.sys_host.network.connectivity
            and self.sys_core.state in (CoreState.SETUP, CoreState.RUNNING)
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, no host internet connection",
                self._method.__qualname__,
            )
            return False

        return True

    async def _acquire_exection_limit(self) -> None:
        """Process exection limits."""
        if self.limit not in (
            JobExecutionLimit.SINGLE_WAIT,
            JobExecutionLimit.THROTTLE_WAIT,
        ):
            return
        await self._lock.acquire()

    def _release_exception_limits(self) -> None:
        """Release possible exception limits."""
        if self.limit not in (
            JobExecutionLimit.SINGLE_WAIT,
            JobExecutionLimit.THROTTLE_WAIT,
        ):
            return
        self._lock.release()
