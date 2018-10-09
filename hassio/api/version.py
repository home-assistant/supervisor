"""Init file for Hass.io version RESTful API."""
import logging

from .utils import api_process
from ..const import (
    ATTR_HOMEASSISTANT, ATTR_SUPERVISOR, ATTR_MACHINE, ATTR_ARCH, ATTR_HASSOS,
    ATTR_CHANNEL, ATTR_HOSTNAME)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class APIVersion(CoreSysAttributes):
    """Handle RESTful API for version functions."""

    @api_process
    async def info(self, request):
        """Show version info."""
        return {
            ATTR_SUPERVISOR: self.sys_supervisor.version,
            ATTR_HOMEASSISTANT: self.sys_homeassistant.version,
            ATTR_HASSOS: self.sys_hassos.version,
            ATTR_HOSTNAME: self.sys_host.info.hostname,
            ATTR_MACHINE: self.sys_machine,
            ATTR_ARCH: self.sys_arch,
            ATTR_CHANNEL: self.sys_updater.channel,
        }
