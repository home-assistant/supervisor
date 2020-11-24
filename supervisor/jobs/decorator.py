"""Job decorator."""
import logging
from typing import List, Optional

import sentry_sdk

from ..const import CoreState
from ..coresys import CoreSys
from ..exceptions import HassioError, JobException
from ..resolution.const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType
from .const import JobCondition

_LOGGER: logging.Logger = logging.getLogger(__package__)


class Job:
    """Supervisor job decorator."""

    def __init__(
        self,
        name: Optional[str] = None,
        conditions: Optional[List[JobCondition]] = None,
        cleanup: bool = True,
    ):
        """Initialize the Job class."""
        self.name = name
        self.conditions = conditions
        self.cleanup = cleanup
        self._coresys: Optional[CoreSys] = None
        self._method = None

    def __call__(self, method):
        """Call the wrapper logic."""
        self._method = method

        async def wrapper(*args, **kwargs):
            """Wrap the method."""
            if self.name is None:
                self.name = str(self._method.__qualname__).lower().replace(".", "_")
            try:
                self._coresys = args[0].coresys
            except AttributeError:
                return False

            if not self._coresys:
                raise JobException(f"coresys is missing on {self.name}")

            job = self._coresys.jobs.get_job(self.name)

            if self.conditions and not self._check_conditions():
                return False

            try:
                return await self._method(*args, **kwargs)
            except HassioError as err:
                raise err
            except Exception as err:
                _LOGGER.exception("Unhandled exception: %s", err)
                sentry_sdk.capture_exception(err)
                raise JobException() from err
            finally:
                if self.cleanup:
                    self._coresys.jobs.remove_job(job)

        return wrapper

    def _check_conditions(self):
        """Check conditions."""
        used_conditions = set(self.conditions) - set(
            self._coresys.jobs.ignore_conditions
        )
        ignored_conditions = set(self.conditions) & set(
            self._coresys.jobs.ignore_conditions
        )

        # Check if somethings is ignored
        if ignored_conditions:
            _LOGGER.critical(
                "The following job conditions are ignored and will make the system unstable when they occur: %s",
                ignored_conditions,
            )

        if JobCondition.HEALTHY in used_conditions and not self._coresys.core.healthy:
            _LOGGER.warning(
                "'%s' blocked from execution, system is not healthy",
                self._method.__qualname__,
            )
            return False

        if (
            JobCondition.RUNNING in used_conditions
            and self._coresys.core.state != CoreState.RUNNING
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, system is not running",
                self._method.__qualname__,
            )
            return False

        if (
            JobCondition.FREE_SPACE in used_conditions
            and self._coresys.host.info.free_space < MINIMUM_FREE_SPACE_THRESHOLD
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, not enough free space (%sGB) left on the device",
                self._method.__qualname__,
                self._coresys.host.info.free_space,
            )
            self._coresys.resolution.create_issue(
                IssueType.FREE_SPACE, ContextType.SYSTEM
            )
            return False

        if (
            JobCondition.INTERNET_SYSTEM in self.conditions
            and not self._coresys.supervisor.connectivity
            and self._coresys.core.state in (CoreState.SETUP, CoreState.RUNNING)
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, no supervisor internet connection",
                self._method.__qualname__,
            )
            return False

        if (
            JobCondition.INTERNET_HOST in self.conditions
            and self._coresys.host.network.connectivity is not None
            and not self._coresys.host.network.connectivity
            and self._coresys.core.state in (CoreState.SETUP, CoreState.RUNNING)
        ):
            _LOGGER.warning(
                "'%s' blocked from execution, no host internet connection",
                self._method.__qualname__,
            )
            return False

        return True
