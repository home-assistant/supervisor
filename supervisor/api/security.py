"""Init file for Supervisor Security RESTful API."""
import asyncio
import logging
from typing import Any

from aiohttp import web
import attr
import voluptuous as vol

from ..const import ATTR_CONTENT_TRUST, ATTR_FORCE_SECURITY, ATTR_PWNED
from ..coresys import CoreSysAttributes
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_PWNED): vol.Boolean(),
        vol.Optional(ATTR_CONTENT_TRUST): vol.Boolean(),
        vol.Optional(ATTR_FORCE_SECURITY): vol.Boolean(),
    }
)


class APISecurity(CoreSysAttributes):
    """Handle RESTful API for Security functions."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return Security information."""
        return {
            ATTR_CONTENT_TRUST: self.sys_security.content_trust,
            ATTR_PWNED: self.sys_security.pwned,
            ATTR_FORCE_SECURITY: self.sys_security.force,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set options for Security."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_PWNED in body:
            self.sys_security.pwned = body[ATTR_PWNED]
        if ATTR_CONTENT_TRUST in body:
            self.sys_security.content_trust = body[ATTR_CONTENT_TRUST]
        if ATTR_FORCE_SECURITY in body:
            self.sys_security.force = body[ATTR_FORCE_SECURITY]

        self.sys_security.save_data()

        await self.sys_resolution.evaluate.evaluate_system()

    @api_process
    async def integrity_check(self, request: web.Request) -> dict[str, Any]:
        """Run backend integrity check."""
        result = await asyncio.shield(self.sys_security.integrity_check())
        return attr.asdict(result)
