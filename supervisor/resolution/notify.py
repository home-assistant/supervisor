"""Helper to notify Core about issues.

This helper creates persistant notification in the Core UI.
In the future we want to remove this in favour of a "center" in the UI.
"""

import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError
from .checks.core_security import SecurityReference
from .const import ContextType, IssueType
from .data import Issue

_LOGGER: logging.Logger = logging.getLogger(__name__)

ISSUE_SECURITY_CUSTOM_COMP_2021_1_5 = Issue(
    IssueType.SECURITY,
    ContextType.CORE,
    reference=SecurityReference.CUSTOM_COMPONENTS_BELOW_2021_1_5,
)


class ResolutionNotify(CoreSysAttributes):
    """Notify class for resolution."""

    def __init__(self, coresys: CoreSys):
        """Initialize the notify class."""
        self.coresys = coresys

    async def issue_notifications(self):
        """Create persistant notifications about issues."""
        if (
            not self.sys_resolution.issues
            or not await self.sys_homeassistant.api.check_api_state()
        ):
            return

        # This one issue must remain a persistent notification rather then a repair because repairs didn't exist in HA 2021.1.5
        if ISSUE_SECURITY_CUSTOM_COMP_2021_1_5 in self.sys_resolution.issues:
            try:
                async with self.sys_homeassistant.api.make_request(
                    "post",
                    "api/services/persistent_notification/create",
                    json={
                        "title": "Security notification",
                        "message": "The Supervisor detected that this version of Home Assistant could be insecure in combination with custom integrations. [Update as soon as possible.](/hassio/dashboard)\n\nFor more information see the [Security alert](https://www.home-assistant.io/latest-security-alert).",
                        "notification_id": "supervisor_update_home_assistant_2021_1_5",
                    },
                ) as resp:
                    if resp.status in (200, 201):
                        _LOGGER.debug("Successfully created persistent_notification")
                    else:
                        _LOGGER.error("Can't create persistant notification")
            except HomeAssistantAPIError as err:
                _LOGGER.error("Can't create persistant notification: %s", err)
