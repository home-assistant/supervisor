"""Init file for Supervisor Jobs RESTful API."""
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..coresys import CoreSysAttributes
from ..jobs.const import ATTR_IGNORE_CONDITIONS, JobCondition
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema(
    {vol.Optional(ATTR_IGNORE_CONDITIONS): [vol.Coerce(JobCondition)]}
)


class APIJobs(CoreSysAttributes):
    """Handle RESTful API for OS functions."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return JobManager information."""
        return {
            ATTR_IGNORE_CONDITIONS: self.sys_jobs.ignore_conditions,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set options for JobManager."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_IGNORE_CONDITIONS in body:
            self.sys_jobs.ignore_conditions = body[ATTR_IGNORE_CONDITIONS]

        self.sys_jobs.save_data()

        await self.sys_resolution.evaluate.evaluate_system()

    @api_process
    async def reset(self, request: web.Request) -> None:
        """Reset options for JobManager."""
        self.sys_jobs.reset_data()
