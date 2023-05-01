"""Inits file for supervisor mounts REST API."""

from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import ATTR_NAME, ATTR_STATE
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..mounts.mount import Mount
from ..mounts.validate import SCHEMA_MOUNT_CONFIG
from .const import ATTR_MOUNTS
from .utils import api_process, api_validate


class APIMounts(CoreSysAttributes):
    """Handle REST API for mounting options."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return MountManager info."""
        return {
            ATTR_MOUNTS: [
                mount.to_dict() | {ATTR_STATE: mount.state}
                for mount in self.sys_mounts.mounts
            ]
        }

    @api_process
    async def create_mount(self, request: web.Request) -> None:
        """Create a new mount in supervisor."""
        body = await api_validate(SCHEMA_MOUNT_CONFIG, request)

        if body[ATTR_NAME] in self.sys_mounts:
            raise APIError(f"A mount already exists with name {body[ATTR_NAME]}")

        await self.sys_mounts.create_mount(Mount.from_dict(self.coresys, body))
        self.sys_mounts.save_data()

    @api_process
    async def update_mount(self, request: web.Request) -> None:
        """Update an existing mount in supervisor."""
        mount = request.match_info.get("mount")
        name_schema = vol.Schema(
            {vol.Optional(ATTR_NAME, default=mount): mount}, extra=vol.ALLOW_EXTRA
        )
        body = await api_validate(vol.All(name_schema, SCHEMA_MOUNT_CONFIG), request)

        if mount not in self.sys_mounts:
            raise APIError(f"No mount exists with name {mount}")

        await self.sys_mounts.create_mount(Mount.from_dict(self.coresys, body))
        self.sys_mounts.save_data()

    @api_process
    async def delete_mount(self, request: web.Request) -> None:
        """Delete an existing mount in supervisor."""
        mount = request.match_info.get("mount")

        if mount not in self.sys_mounts:
            raise APIError(f"No mount exists with name {mount}")

        await self.sys_mounts.remove_mount(mount)
        self.sys_mounts.save_data()

    @api_process
    async def reload_mount(self, request: web.Request) -> None:
        """Reload an existing mount in supervisor."""
        mount = request.match_info.get("mount")

        if mount not in self.sys_mounts:
            raise APIError(f"No mount exists with name {mount}")

        await self.sys_mounts.reload_mount(mount)
