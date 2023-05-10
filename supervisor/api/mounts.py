"""Inits file for supervisor mounts REST API."""

from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import ATTR_NAME, ATTR_STATE
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..mounts.const import ATTR_DEFAULT_BACKUP_MOUNT, MountUsage
from ..mounts.mount import Mount
from ..mounts.validate import SCHEMA_MOUNT_CONFIG
from .const import ATTR_MOUNTS
from .utils import api_process, api_validate

SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_DEFAULT_BACKUP_MOUNT): vol.Maybe(str),
    }
)


class APIMounts(CoreSysAttributes):
    """Handle REST API for mounting options."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return MountManager info."""
        return {
            ATTR_DEFAULT_BACKUP_MOUNT: self.sys_mounts.default_backup_mount.name
            if self.sys_mounts.default_backup_mount
            else None,
            ATTR_MOUNTS: [
                mount.to_dict() | {ATTR_STATE: mount.state}
                for mount in self.sys_mounts.mounts
            ],
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set Mount Manager options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_DEFAULT_BACKUP_MOUNT in body:
            name: str | None = body[ATTR_DEFAULT_BACKUP_MOUNT]
            if name is None:
                self.sys_mounts.default_backup_mount = None
            elif (mount := self.sys_mounts.get(name)).usage != MountUsage.BACKUP:
                raise APIError(
                    f"Mount {name} is not used for backups, cannot use it as default backup mount"
                )
            else:
                self.sys_mounts.default_backup_mount = mount

        self.sys_mounts.save_data()

    @api_process
    async def create_mount(self, request: web.Request) -> None:
        """Create a new mount in supervisor."""
        body = await api_validate(SCHEMA_MOUNT_CONFIG, request)

        if body[ATTR_NAME] in self.sys_mounts:
            raise APIError(f"A mount already exists with name {body[ATTR_NAME]}")

        mount = Mount.from_dict(self.coresys, body)
        await self.sys_mounts.create_mount(mount)

        # If it's a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())

            # If there's no default backup mount, set it to the new mount
            if not self.sys_mounts.default_backup_mount:
                self.sys_mounts.default_backup_mount = mount

        self.sys_mounts.save_data()

    @api_process
    async def update_mount(self, request: web.Request) -> None:
        """Update an existing mount in supervisor."""
        name = request.match_info.get("mount")
        name_schema = vol.Schema(
            {vol.Optional(ATTR_NAME, default=name): name}, extra=vol.ALLOW_EXTRA
        )
        body = await api_validate(vol.All(name_schema, SCHEMA_MOUNT_CONFIG), request)

        if name not in self.sys_mounts:
            raise APIError(f"No mount exists with name {name}")

        mount = Mount.from_dict(self.coresys, body)
        await self.sys_mounts.create_mount(mount)

        # If it's a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())

        # If this mount was the default backup mount and isn't for backups any more, remove it
        elif self.sys_mounts.default_backup_mount == mount:
            self.sys_mounts.default_backup_mount = None

        self.sys_mounts.save_data()

    @api_process
    async def delete_mount(self, request: web.Request) -> None:
        """Delete an existing mount in supervisor."""
        name = request.match_info.get("mount")
        mount = await self.sys_mounts.remove_mount(name)

        # If it was a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())

        self.sys_mounts.save_data()

    @api_process
    async def reload_mount(self, request: web.Request) -> None:
        """Reload an existing mount in supervisor."""
        name = request.match_info.get("mount")
        await self.sys_mounts.reload_mount(name)

        # If it's a backup mount, reload backups
        if self.sys_mounts.get(name).usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())
