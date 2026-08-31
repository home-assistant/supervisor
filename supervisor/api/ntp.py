"""REST API for NTP configuration."""

import asyncio
import re
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import ATTR_SERVERS
from ..coresys import CoreSysAttributes
from ..exceptions import APINotFound
from ..host.const import HostFeature
from .const import ATTR_FALLBACK_SERVERS
from .utils import api_process, api_validate

RE_NTP_SERVER = re.compile(r"^[^\s#]+\Z")

NTP_SERVER = vol.All(str, vol.Match(RE_NTP_SERVER))

SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_SERVERS): [NTP_SERVER],
        vol.Optional(ATTR_FALLBACK_SERVERS): [NTP_SERVER],
    }
)


class APINTP(CoreSysAttributes):
    """Handle REST API for NTP configuration."""

    def _check_available(self) -> None:
        """Check if OS Agent Timesyncd configuration is available."""
        if HostFeature.NTP not in self.sys_host.features:
            raise APINotFound(
                "Home Assistant OS 18.3 or newer required for NTP settings"
            )

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return NTP server configuration."""
        self._check_available()

        return {
            ATTR_SERVERS: self.sys_dbus.agent.timesyncd.ntp_servers,
            ATTR_FALLBACK_SERVERS: self.sys_dbus.agent.timesyncd.fallback_ntp_servers,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set NTP server configuration."""
        self._check_available()
        body = await api_validate(SCHEMA_OPTIONS, request)

        await asyncio.shield(
            self.sys_host.control.set_ntp_servers(
                servers=body.get(ATTR_SERVERS),
                fallback_servers=body.get(ATTR_FALLBACK_SERVERS),
            )
        )
