"""Init file for Supervisor Security RESTful API."""

from typing import Any

from aiohttp import web
import voluptuous as vol

from supervisor.exceptions import APIGone

from ..const import ATTR_FORCE_SECURITY, ATTR_PWNED
from ..coresys import CoreSysAttributes
from .utils import api_process, api_validate

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_PWNED): vol.Boolean(),
        vol.Optional(ATTR_FORCE_SECURITY): vol.Boolean(),
    }
)


class APISecurity(CoreSysAttributes):
    """Handle RESTful API for Security functions."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return Security information."""
        return {
            ATTR_PWNED: self.sys_security.pwned,
            ATTR_FORCE_SECURITY: self.sys_security.force,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set options for Security."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_PWNED in body:
            self.sys_security.pwned = body[ATTR_PWNED]
        if ATTR_FORCE_SECURITY in body:
            self.sys_security.force = body[ATTR_FORCE_SECURITY]

        await self.sys_security.save_data()

        await self.sys_resolution.evaluate.evaluate_system()

    @api_process
    async def integrity_check(self, request: web.Request) -> dict[str, Any]:
        """Run backend integrity check.

        CodeNotary integrity checking has been removed. This endpoint now returns
        an error indicating the feature is gone.
        """
        raise APIGone("Integrity check feature has been removed.")
