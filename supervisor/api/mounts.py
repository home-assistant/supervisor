"""Inits file for supervisor mounts REST API."""

from typing import Any, cast

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ID,
    ATTR_NAME,
    ATTR_SERIAL,
    ATTR_SIZE,
    ATTR_STATE,
    ATTR_TYPE,
    ATTR_UUID,
)
from ..coresys import CoreSysAttributes
from ..dbus.const import DBUS_OBJECT_BASE
from ..dbus.udisks2.block import UDisks2Block
from ..exceptions import APIError, APINotFound, DBusObjectError, MountInvalidError
from ..mounts.const import (
    ATTR_DEFAULT_BACKUP_MOUNT,
    ATTR_FILESYSTEM,
    ATTR_READ_ONLY,
    MountType,
    MountUsage,
)
from ..mounts.disks import validate_block_for_mount
from ..mounts.mount import Mount, disk_mount_uuids
from ..mounts.validate import (
    SCHEMA_BASE_MOUNT_CONFIG,
    SCHEMA_MOUNT_CIFS,
    SCHEMA_MOUNT_NFS,
    MountData,
    usage_specific_validation,
)
from .const import (
    ATTR_CANDIDATES,
    ATTR_CONNECTION_BUS,
    ATTR_DEVICE,
    ATTR_DRIVE,
    ATTR_EJECTABLE,
    ATTR_LABEL,
    ATTR_MODEL,
    ATTR_MOUNTS,
    ATTR_REMOVABLE,
    ATTR_USER_PATH,
    ATTR_VENDOR,
)
from .utils import api_process, api_validate

SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_DEFAULT_BACKUP_MOUNT): vol.Maybe(str),
    }
)


def _device_identifier_required(config: dict[str, Any]) -> dict[str, Any]:
    """Require at least one of device and uuid for a disk mount."""
    if not config.get(ATTR_DEVICE) and not config.get(ATTR_UUID):
        raise vol.Invalid("Disk mounts require either device or uuid")

    return config


# API input only; a persisted disk mount is validated in mounts/validate.py.
# Both identifiers may be supplied together so a candidates entry can be
# posted back as-is: resolution goes by uuid and the device is checked for
# agreement. `filesystem` is deliberately not accepted - resolving through
# UDisks2 is what runs the mountable-device guard, and REMOVE_EXTRA on the
# base schema drops the value a client echoes back from GET /mounts.
_SCHEMA_MOUNT_DISK = vol.All(
    SCHEMA_BASE_MOUNT_CONFIG.extend(
        {
            vol.Required(ATTR_TYPE): vol.All(
                MountType.DISK.value, vol.Coerce(MountType)
            ),
            vol.Optional(ATTR_DEVICE): str,
            vol.Optional(ATTR_UUID): str,
        }
    ),
    _device_identifier_required,
)

SCHEMA_MOUNT_CONFIG = vol.All(
    vol.Any(SCHEMA_MOUNT_CIFS, SCHEMA_MOUNT_NFS, _SCHEMA_MOUNT_DISK),
    usage_specific_validation,
)


class APIMounts(CoreSysAttributes):
    """Handle REST API for mounting options."""

    def _extract_mount(self, request: web.Request) -> Mount:
        """Extract mount from request or raise."""
        name = request.match_info["mount"]
        if name not in self.sys_mounts:
            raise APINotFound(f"No mount exists with name {name}")
        return self.sys_mounts.get(name)

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return MountManager info."""
        return {
            ATTR_DEFAULT_BACKUP_MOUNT: self.sys_mounts.default_backup_mount.name
            if self.sys_mounts.default_backup_mount
            else None,
            ATTR_MOUNTS: [
                mount.to_dict()
                | {
                    ATTR_STATE: mount.state,
                    ATTR_USER_PATH: mount.container_where.as_posix()
                    if mount.container_where
                    else None,
                }
                for mount in self.sys_mounts.mounts
            ],
        }

    @api_process
    async def candidates(self, request: web.Request) -> dict[str, Any]:
        """Return local block devices that could be used as a disk mount."""
        # A host without UDisks2 has nothing to offer and cannot be asked.
        if not self.sys_dbus.udisks2.is_connected:
            return {ATTR_CANDIDATES: []}

        # Refresh first so a disk plugged in moments ago shows up, the same
        # way data disk migration re-reads before it enumerates.
        await self.sys_dbus.udisks2.update()

        used_uuids = disk_mount_uuids(self.sys_mounts.mounts)
        candidates: list[dict[str, Any]] = []
        for block in self.sys_dbus.udisks2.block_devices:
            try:
                validate_block_for_mount(self.coresys, block, used_uuids=used_uuids)
            except MountInvalidError:
                # Same guard the create path uses, so the two can never
                # disagree about what is mountable.
                continue

            candidates.append(self._candidate_to_dict(block))

        return {ATTR_CANDIDATES: candidates}

    def _candidate_to_dict(self, block: UDisks2Block) -> dict[str, Any]:
        """Return API representation of a mount candidate."""
        return {
            ATTR_TYPE: MountType.DISK,
            ATTR_DEVICE: block.device.as_posix(),
            ATTR_UUID: block.id_uuid,
            ATTR_LABEL: block.id_label,
            ATTR_FILESYSTEM: block.id_type,
            ATTR_SIZE: block.size,
            ATTR_READ_ONLY: block.read_only,
            ATTR_DRIVE: self._drive_to_dict(block),
        }

    def _drive_to_dict(self, block: UDisks2Block) -> dict[str, Any] | None:
        """Return API representation of the drive a candidate belongs to.

        Tolerant of a missing drive: a drive object can disappear between
        enumeration and lookup on a disk being unplugged.
        """
        if not block.drive or block.drive == DBUS_OBJECT_BASE:
            return None

        try:
            drive = self.sys_dbus.udisks2.get_drive(block.drive)
        except DBusObjectError:
            return None

        return {
            ATTR_VENDOR: drive.vendor,
            ATTR_MODEL: drive.model,
            ATTR_SERIAL: drive.serial,
            ATTR_ID: drive.id,
            ATTR_SIZE: drive.size,
            ATTR_CONNECTION_BUS: drive.connection_bus,
            ATTR_REMOVABLE: drive.removable,
            ATTR_EJECTABLE: drive.ejectable,
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

        await self.sys_mounts.save_data()

    @api_process
    async def create_mount(self, request: web.Request) -> None:
        """Create a new mount in supervisor."""
        body = cast(MountData, await api_validate(SCHEMA_MOUNT_CONFIG, request))

        if body["name"] in self.sys_mounts:
            raise APIError(f"A mount already exists with name {body['name']}")

        mount = Mount.from_dict(self.coresys, body)
        await self.sys_mounts.create_mount(mount)

        # If it's a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())

            # If there's no default backup mount, set it to the new mount
            if not self.sys_mounts.default_backup_mount:
                self.sys_mounts.default_backup_mount = mount

        await self.sys_mounts.save_data()

    @api_process
    async def update_mount(self, request: web.Request) -> None:
        """Update an existing mount in supervisor."""
        current = self._extract_mount(request)
        name_schema = vol.Schema(
            {vol.Optional(ATTR_NAME, default=current.name): current.name},
            extra=vol.ALLOW_EXTRA,
        )
        body = cast(
            MountData,
            await api_validate(vol.All(name_schema, SCHEMA_MOUNT_CONFIG), request),
        )

        mount = Mount.from_dict(self.coresys, body)
        await self.sys_mounts.create_mount(mount)

        # If it's a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())

        # If this mount was the default backup mount and isn't for backups any more, remove it
        elif self.sys_mounts.default_backup_mount == mount:
            self.sys_mounts.default_backup_mount = None

        await self.sys_mounts.save_data()

    @api_process
    async def delete_mount(self, request: web.Request) -> None:
        """Delete an existing mount in supervisor."""
        current = self._extract_mount(request)
        mount = await self.sys_mounts.remove_mount(current.name)

        # If it was a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())

        await self.sys_mounts.save_data()

    @api_process
    async def reload_mount(self, request: web.Request) -> None:
        """Reload an existing mount in supervisor."""
        mount = self._extract_mount(request)
        await self.sys_mounts.reload_mount(mount.name)

        # If it's a backup mount, reload backups
        if mount.usage == MountUsage.BACKUP:
            self.sys_create_task(self.sys_backups.reload())
