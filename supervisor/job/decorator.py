"""Job decorator."""
from enum import Enum
import logging
from typing import List, Optional

from ..const import CoreState
from ..coresys import CoreSys
from ..exceptions import HassioError, JobException
from ..resolution.const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType

_LOGGER: logging.Logger = logging.getLogger(__package__)


class JobCondition(str, Enum):
    """Job condition enum."""

    FREE_SPACE = "free_space"
    HEALTHY = "healthy"
    INTERNET = "internet"


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

            if self.conditions and not await self._check_conditions():
                return False

            try:
                result = await self._method(*args, **kwargs)
            except HassioError as err:
                _LOGGER.error(err)
                raise JobException() from err
            finally:
                if self.cleanup:
                    self._coresys.jobs.remove_job(job)

            return result

        return wrapper

    async def _check_conditions(self):
        """Check conditions."""
        if JobCondition.HEALTHY in self.conditions:
            if not self._coresys.core.healthy:
                _LOGGER.warning(
                    "'%s' blocked from execution, system is not healthy",
                    self._method.__qualname__,
                )
                return False

        if JobCondition.FREE_SPACE in self.conditions:
            free_space = self._coresys.host.info.free_space
            if free_space < MINIMUM_FREE_SPACE_THRESHOLD:
                _LOGGER.warning(
                    "'%s' blocked from execution, not enough free space (%sGB) left on the device",
                    self._method.__qualname__,
                    free_space,
                )
                self._coresys.resolution.create_issue(
                    IssueType.FREE_SPACE, ContextType.SYSTEM
                )
                return False

        if JobCondition.INTERNET in self.conditions:
            if self._coresys.core.state == CoreState.RUNNING:
                await self._coresys.host.network.check_connectivity()
                await self._coresys.supervisor.check_connectivity()
            if (
                not self._coresys.supervisor.connectivity
                or not self._coresys.host.network.connectivity
            ):
                _LOGGER.warning(
                    "'%s' blocked from execution, no internet connection",
                    self._method.__qualname__,
                )
                return False

        return True
