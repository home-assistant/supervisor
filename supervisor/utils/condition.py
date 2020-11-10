"""Decorators to block execution of methods is a condition is not met."""
import logging

from ..coresys import CoreSys
from ..resolution.const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Condition:
    """Condition class."""

    @staticmethod
    def internet(method):
        """Wrap a method to guard for missing internet."""

        async def wrapper(*args, **kwargs):
            """Wrap the method."""
            coresys: CoreSys = args[0].coresys
            if not coresys.core.internet.connected:
                _LOGGER.warning(
                    "Cloud not run '%s', no internet connection",
                    method.__qualname__,
                )
                return False
            return await method(*args, **kwargs)

        return wrapper

    @staticmethod
    def free_space(method):
        """Wrap a method to guard for low storage."""

        async def wrapper(*args, **kwargs):
            """Wrap the method."""
            coresys: CoreSys = args[0].coresys
            free_space = coresys.host.info.free_space
            if free_space < MINIMUM_FREE_SPACE_THRESHOLD:
                _LOGGER.warning(
                    "Not enough free space (%sGB) left on the device to run '%s'",
                    free_space,
                    method.__qualname__,
                )
                coresys.resolution.create_issue(
                    IssueType.FREE_SPACE, ContextType.SYSTEM
                )
                return False
            return await method(*args, **kwargs)

        return wrapper

    @staticmethod
    def healthy(method):
        """Wrap a method to guard for unhealthy installations."""

        async def wrapper(*args, **kwargs):
            """Wrap the method."""
            coresys: CoreSys = args[0].coresys
            if not coresys.core.healthy:
                _LOGGER.warning(
                    "'%s' blocked from execution, system is not healthy",
                    method.__qualname__,
                )
                return False
            return await method(*args, **kwargs)

        return wrapper
