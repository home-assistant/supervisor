"""
Helper to notify Core about issues.

This helper creates persistant notification in the Core UI.
In the future we want to remove this in favour of a "center" in the UI.
"""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError
from .const import IssueType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionNotify(CoreSysAttributes):
    """Notify class for resolution."""

    def __init__(self, coresys: CoreSys):
        """Initialize the notify class."""
        self.coresys = coresys

    async def issue_notifications(self):
        """Create persistant notifications about issues."""
        if (
            not self.sys_resolution.issues
            or not self.sys_homeassistant.api.check_api_state()
        ):
            return

        messages = []

        for issue in self.sys_resolution.issues:
            if issue.type == IssueType.FREE_SPACE:
                messages.append(
                    {
                        "title": "Available space is less than 1GB!",
                        "message": f"Available space is {self.sys_host.info.free_space}GB, see https://www.home-assistant.io/more-info/free-space for more information.",
                        "notification_id": "supervisor_issue_free_space",
                    }
                )

        for message in messages:
            try:
                async with self.sys_homeassistant.api.make_request(
                    "post",
                    "api/services/persistent_notification/create",
                    json=message,
                ) as resp:
                    if resp.status in (200, 201):
                        _LOGGER.debug("Sucessfully created persistent_notification")
                    else:
                        _LOGGER.error("Can't create persistant notification")
            except HomeAssistantAPIError:
                _LOGGER.error("Can't create persistant notification")
