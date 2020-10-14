"""
Helper to notify Core about issues.

This helper creates persistant notification in the Core UI.
In the future we want to remove this in favour of a "center" in the UI.
"""
import logging

from ..coresys import CoreSys
from ..exceptions import HomeAssistantAPIError
from .const import IssueType

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def create_notifications(coresys: CoreSys):
    """Create persistant notifications about issues."""
    if not coresys.resolution.issues or not coresys.homeassistant.core.is_running():
        return

    issues = []

    for issue in coresys.resolution.issues:
        if issue == IssueType.FREE_SPACE:
            issues.append(
                {
                    "title": "Available space is less than 1GB!",
                    "message": f"Available space is {coresys.host.info.free_space}GB, see https://www.home-assistant.io/more-info/free-space for more information.",
                    "notification_id": "supervisor_issue_free_space",
                }
            )

    for issue in issues:
        try:
            async with coresys.homeassistant.api.make_request(
                "post",
                "api/services/persistent_notification/create",
                json=issue,
            ) as resp:
                if resp.status in (200, 201):
                    _LOGGER.debug("Sucessfully created persistent_notification")
                else:
                    _LOGGER.error("Can't create persistant notification")
        except HomeAssistantAPIError:
            _LOGGER.error("Can't create persistant notification")
