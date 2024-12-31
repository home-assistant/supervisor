"""Backups RESTful API."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import errno
import logging
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any

from aiohttp import web
from aiohttp.hdrs import CONTENT_DISPOSITION
import voluptuous as vol

from ..backups.backup import Backup
from ..backups.const import LOCATION_CLOUD_BACKUP, LOCATION_TYPE
from ..backups.validate import ALL_FOLDERS, FOLDER_HOMEASSISTANT, days_until_stale
from ..const import (
    ATTR_ADDONS,
    ATTR_BACKUPS,
    ATTR_COMPRESSED,
    ATTR_CONTENT,
    ATTR_DATE,
    ATTR_DAYS_UNTIL_STALE,
    ATTR_EXTRA,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_HOMEASSISTANT_EXCLUDE_DATABASE,
    ATTR_JOB_ID,
    ATTR_LOCATION,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PROTECTED,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_SUPERVISOR_VERSION,
    ATTR_TIMEOUT,
    ATTR_TYPE,
    ATTR_VERSION,
    REQUEST_FROM,
    BusEvent,
    CoreState,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APIForbidden, APINotFound
from ..jobs import JobSchedulerOptions
from ..mounts.const import MountUsage
from ..resolution.const import UnhealthyReason
from .const import (
    ATTR_ADDITIONAL_LOCATIONS,
    ATTR_BACKGROUND,
    ATTR_LOCATIONS,
    ATTR_SIZE_BYTES,
    CONTENT_TYPE_TAR,
)
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

ALL_ADDONS_FLAG = "ALL"

RE_SLUGIFY_NAME = re.compile(r"[^A-Za-z0-9]+")
RE_BACKUP_FILENAME = re.compile(r"^[^\\\/]+\.tar$")

# Backwards compatible
# Remove: 2022.08
_ALL_FOLDERS = ALL_FOLDERS + [FOLDER_HOMEASSISTANT]


def _ensure_list(item: Any) -> list:
    """Ensure value is a list."""
    if not isinstance(item, list):
        return [item]
    return item


# pylint: disable=no-value-for-parameter
SCHEMA_RESTORE_FULL = vol.Schema(
    {
        vol.Optional(ATTR_PASSWORD): vol.Maybe(str),
        vol.Optional(ATTR_BACKGROUND, default=False): vol.Boolean(),
        vol.Optional(ATTR_LOCATION): vol.Maybe(str),
    }
)

SCHEMA_RESTORE_PARTIAL = SCHEMA_RESTORE_FULL.extend(
    {
        vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
        vol.Optional(ATTR_ADDONS): vol.All([str], vol.Unique()),
        vol.Optional(ATTR_FOLDERS): vol.All([vol.In(_ALL_FOLDERS)], vol.Unique()),
    }
)

SCHEMA_BACKUP_FULL = vol.Schema(
    {
        vol.Optional(ATTR_NAME): str,
        vol.Optional(ATTR_PASSWORD): vol.Maybe(str),
        vol.Optional(ATTR_COMPRESSED): vol.Maybe(vol.Boolean()),
        vol.Optional(ATTR_LOCATION): vol.All(
            _ensure_list, [vol.Maybe(str)], vol.Unique()
        ),
        vol.Optional(ATTR_HOMEASSISTANT_EXCLUDE_DATABASE): vol.Boolean(),
        vol.Optional(ATTR_BACKGROUND, default=False): vol.Boolean(),
        vol.Optional(ATTR_EXTRA): dict,
    }
)

SCHEMA_BACKUP_PARTIAL = SCHEMA_BACKUP_FULL.extend(
    {
        vol.Optional(ATTR_ADDONS): vol.Or(
            ALL_ADDONS_FLAG, vol.All([str], vol.Unique())
        ),
        vol.Optional(ATTR_FOLDERS): vol.All([vol.In(_ALL_FOLDERS)], vol.Unique()),
        vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
    }
)

SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_DAYS_UNTIL_STALE): days_until_stale,
    }
)

SCHEMA_FREEZE = vol.Schema(
    {
        vol.Optional(ATTR_TIMEOUT): vol.All(int, vol.Range(min=1)),
    }
)

SCHEMA_REMOVE = vol.Schema(
    {
        vol.Optional(ATTR_LOCATION): vol.All(
            _ensure_list, [vol.Maybe(str)], vol.Unique()
        ),
    }
)


class APIBackups(CoreSysAttributes):
    """Handle RESTful API for backups functions."""

    def _extract_slug(self, request):
        """Return backup, throw an exception if it doesn't exist."""
        backup = self.sys_backups.get(request.match_info.get("slug"))
        if not backup:
            raise APINotFound("Backup does not exist")
        return backup

    def _list_backups(self):
        """Return list of backups."""
        return [
            {
                ATTR_SLUG: backup.slug,
                ATTR_NAME: backup.name,
                ATTR_DATE: backup.date,
                ATTR_TYPE: backup.sys_type,
                ATTR_SIZE: backup.size,
                ATTR_SIZE_BYTES: backup.size_bytes,
                ATTR_LOCATION: backup.location,
                ATTR_LOCATIONS: backup.locations,
                ATTR_PROTECTED: backup.protected,
                ATTR_COMPRESSED: backup.compressed,
                ATTR_CONTENT: {
                    ATTR_HOMEASSISTANT: backup.homeassistant_version is not None,
                    ATTR_ADDONS: backup.addon_list,
                    ATTR_FOLDERS: backup.folders,
                },
            }
            for backup in self.sys_backups.list_backups
            if backup.location != LOCATION_CLOUD_BACKUP
        ]

    @api_process
    async def list(self, request):
        """Return backup list."""
        data_backups = self._list_backups()

        if request.path == "/snapshots":
            # Kept for backwards compability
            return {"snapshots": data_backups}

        return {ATTR_BACKUPS: data_backups}

    @api_process
    async def info(self, request):
        """Return backup list and manager info."""
        return {
            ATTR_BACKUPS: self._list_backups(),
            ATTR_DAYS_UNTIL_STALE: self.sys_backups.days_until_stale,
        }

    @api_process
    async def options(self, request):
        """Set backup manager options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_DAYS_UNTIL_STALE in body:
            self.sys_backups.days_until_stale = body[ATTR_DAYS_UNTIL_STALE]

        self.sys_backups.save_data()

    @api_process
    async def reload(self, _):
        """Reload backup list."""
        await asyncio.shield(self.sys_backups.reload())
        return True

    @api_process
    async def backup_info(self, request):
        """Return backup info."""
        backup = self._extract_slug(request)

        data_addons = []
        for addon_data in backup.addons:
            data_addons.append(
                {
                    ATTR_SLUG: addon_data[ATTR_SLUG],
                    ATTR_NAME: addon_data[ATTR_NAME],
                    ATTR_VERSION: addon_data[ATTR_VERSION],
                    ATTR_SIZE: addon_data[ATTR_SIZE],
                }
            )

        return {
            ATTR_SLUG: backup.slug,
            ATTR_TYPE: backup.sys_type,
            ATTR_NAME: backup.name,
            ATTR_DATE: backup.date,
            ATTR_SIZE: backup.size,
            ATTR_SIZE_BYTES: backup.size_bytes,
            ATTR_COMPRESSED: backup.compressed,
            ATTR_PROTECTED: backup.protected,
            ATTR_SUPERVISOR_VERSION: backup.supervisor_version,
            ATTR_HOMEASSISTANT: backup.homeassistant_version,
            ATTR_LOCATION: backup.location,
            ATTR_LOCATIONS: backup.locations,
            ATTR_ADDONS: data_addons,
            ATTR_REPOSITORIES: backup.repositories,
            ATTR_FOLDERS: backup.folders,
            ATTR_HOMEASSISTANT_EXCLUDE_DATABASE: backup.homeassistant_exclude_database,
            ATTR_EXTRA: backup.extra,
        }

    def _location_to_mount(self, location: str | None) -> LOCATION_TYPE:
        """Convert a single location to a mount if possible."""
        if not location or location == LOCATION_CLOUD_BACKUP:
            return location

        mount = self.sys_mounts.get(location)
        if mount.usage != MountUsage.BACKUP:
            raise APIError(
                f"Mount {mount.name} is not used for backups, cannot backup to there"
            )

        return mount

    def _location_field_to_mount(self, body: dict[str, Any]) -> dict[str, Any]:
        """Change location field to mount if necessary."""
        body[ATTR_LOCATION] = self._location_to_mount(body.get(ATTR_LOCATION))
        return body

    def _validate_cloud_backup_location(
        self, request: web.Request, location: list[str | None] | str | None
    ) -> None:
        """Cloud backup location is only available to Home Assistant."""
        if not isinstance(location, list):
            location = [location]
        if (
            LOCATION_CLOUD_BACKUP in location
            and request.get(REQUEST_FROM) != self.sys_homeassistant
        ):
            raise APIForbidden(
                f"Location {LOCATION_CLOUD_BACKUP} is only available for Home Assistant"
            )

    async def _background_backup_task(
        self, backup_method: Callable, *args, **kwargs
    ) -> tuple[asyncio.Task, str]:
        """Start backup task in  background and return task and job ID."""
        event = asyncio.Event()
        job, backup_task = self.sys_jobs.schedule_job(
            backup_method, JobSchedulerOptions(), *args, **kwargs
        )

        async def release_on_freeze(new_state: CoreState):
            if new_state == CoreState.FREEZE:
                event.set()

        # Wait for system to get into freeze state before returning
        # If the backup fails validation it will raise before getting there
        listener = self.sys_bus.register_event(
            BusEvent.SUPERVISOR_STATE_CHANGE, release_on_freeze
        )
        try:
            event_task = self.sys_create_task(event.wait())
            _, pending = await asyncio.wait(
                (
                    backup_task,
                    event_task,
                ),
                return_when=asyncio.FIRST_COMPLETED,
            )
            # It seems backup returned early (error or something), make sure to cancel
            # the event task to avoid "Task was destroyed but it is pending!" errors.
            if event_task in pending:
                event_task.cancel()
            return (backup_task, job.uuid)
        finally:
            self.sys_bus.remove_listener(listener)

    @api_process
    async def backup_full(self, request: web.Request):
        """Create full backup."""
        body = await api_validate(SCHEMA_BACKUP_FULL, request)
        locations: list[LOCATION_TYPE] | None = None

        if ATTR_LOCATION in body:
            location_names: list[str | None] = body.pop(ATTR_LOCATION)
            self._validate_cloud_backup_location(request, location_names)

            locations = [
                self._location_to_mount(location) for location in location_names
            ]
            body[ATTR_LOCATION] = locations.pop(0)
            if locations:
                body[ATTR_ADDITIONAL_LOCATIONS] = locations

        background = body.pop(ATTR_BACKGROUND)
        backup_task, job_id = await self._background_backup_task(
            self.sys_backups.do_backup_full, **body
        )

        if background and not backup_task.done():
            return {ATTR_JOB_ID: job_id}

        backup: Backup = await backup_task
        if backup:
            return {ATTR_JOB_ID: job_id, ATTR_SLUG: backup.slug}
        raise APIError(
            f"An error occurred while making backup, check job '{job_id}' or supervisor logs for details",
            job_id=job_id,
        )

    @api_process
    async def backup_partial(self, request: web.Request):
        """Create a partial backup."""
        body = await api_validate(SCHEMA_BACKUP_PARTIAL, request)
        locations: list[LOCATION_TYPE] | None = None

        if ATTR_LOCATION in body:
            location_names: list[str | None] = body.pop(ATTR_LOCATION)
            self._validate_cloud_backup_location(request, location_names)

            locations = [
                self._location_to_mount(location) for location in location_names
            ]
            body[ATTR_LOCATION] = locations.pop(0)
            if locations:
                body[ATTR_ADDITIONAL_LOCATIONS] = locations

        if body.get(ATTR_ADDONS) == ALL_ADDONS_FLAG:
            body[ATTR_ADDONS] = list(self.sys_addons.local)

        background = body.pop(ATTR_BACKGROUND)
        backup_task, job_id = await self._background_backup_task(
            self.sys_backups.do_backup_partial, **body
        )

        if background and not backup_task.done():
            return {ATTR_JOB_ID: job_id}

        backup: Backup = await backup_task
        if backup:
            return {ATTR_JOB_ID: job_id, ATTR_SLUG: backup.slug}
        raise APIError(
            f"An error occurred while making backup, check job '{job_id}' or supervisor logs for details",
            job_id=job_id,
        )

    @api_process
    async def restore_full(self, request: web.Request):
        """Full restore of a backup."""
        backup = self._extract_slug(request)
        body = await api_validate(SCHEMA_RESTORE_FULL, request)
        self._validate_cloud_backup_location(
            request, body.get(ATTR_LOCATION, backup.location)
        )
        background = body.pop(ATTR_BACKGROUND)
        restore_task, job_id = await self._background_backup_task(
            self.sys_backups.do_restore_full, backup, **body
        )

        if background and not restore_task.done() or await restore_task:
            return {ATTR_JOB_ID: job_id}
        raise APIError(
            f"An error occurred during restore of {backup.slug}, check job '{job_id}' or supervisor logs for details",
            job_id=job_id,
        )

    @api_process
    async def restore_partial(self, request: web.Request):
        """Partial restore a backup."""
        backup = self._extract_slug(request)
        body = await api_validate(SCHEMA_RESTORE_PARTIAL, request)
        self._validate_cloud_backup_location(
            request, body.get(ATTR_LOCATION, backup.location)
        )
        background = body.pop(ATTR_BACKGROUND)
        restore_task, job_id = await self._background_backup_task(
            self.sys_backups.do_restore_partial, backup, **body
        )

        if background and not restore_task.done() or await restore_task:
            return {ATTR_JOB_ID: job_id}
        raise APIError(
            f"An error occurred during restore of {backup.slug}, check job '{job_id}' or supervisor logs for details",
            job_id=job_id,
        )

    @api_process
    async def freeze(self, request: web.Request):
        """Initiate manual freeze for external backup."""
        body = await api_validate(SCHEMA_FREEZE, request)
        await asyncio.shield(self.sys_backups.freeze_all(**body))

    @api_process
    async def thaw(self, request: web.Request):
        """Begin thaw after manual freeze."""
        await self.sys_backups.thaw_all()

    @api_process
    async def remove(self, request: web.Request):
        """Remove a backup."""
        backup = self._extract_slug(request)
        body = await api_validate(SCHEMA_REMOVE, request)
        locations: list[LOCATION_TYPE] | None = None

        if ATTR_LOCATION in body:
            self._validate_cloud_backup_location(request, body[ATTR_LOCATION])
            locations = [self._location_to_mount(name) for name in body[ATTR_LOCATION]]
        else:
            self._validate_cloud_backup_location(request, backup.location)

        return self.sys_backups.remove(backup, locations=locations)

    @api_process
    async def download(self, request: web.Request):
        """Download a backup file."""
        backup = self._extract_slug(request)
        # Query will give us '' for /backups, convert value to None
        location = request.query.get(ATTR_LOCATION, backup.location) or None
        self._validate_cloud_backup_location(request, location)
        if location not in backup.all_locations:
            raise APIError(f"Backup {backup.slug} is not in location {location}")

        _LOGGER.info("Downloading backup %s", backup.slug)
        response = web.FileResponse(backup.all_locations[location])
        response.content_type = CONTENT_TYPE_TAR
        response.headers[CONTENT_DISPOSITION] = (
            f"attachment; filename={RE_SLUGIFY_NAME.sub('_', backup.name)}.tar"
        )
        return response

    @api_process
    async def upload(self, request: web.Request):
        """Upload a backup file."""
        location: LOCATION_TYPE = None
        locations: list[LOCATION_TYPE] | None = None
        tmp_path = self.sys_config.path_tmp
        if ATTR_LOCATION in request.query:
            location_names: list[str] = request.query.getall(ATTR_LOCATION)
            self._validate_cloud_backup_location(request, location_names)
            # Convert empty string to None if necessary
            locations = [
                self._location_to_mount(location) if location else None
                for location in location_names
            ]
            location = locations.pop(0)

            if location and location != LOCATION_CLOUD_BACKUP:
                tmp_path = location.local_where

        with TemporaryDirectory(dir=tmp_path.as_posix()) as temp_dir:
            tar_file = Path(temp_dir, "backup.tar")
            reader = await request.multipart()
            contents = await reader.next()
            try:
                with tar_file.open("wb") as backup:
                    while True:
                        chunk = await contents.read_chunk()
                        if not chunk:
                            break
                        backup.write(chunk)

            except OSError as err:
                if err.errno == errno.EBADMSG and location in {
                    LOCATION_CLOUD_BACKUP,
                    None,
                }:
                    self.sys_resolution.unhealthy = UnhealthyReason.OSERROR_BAD_MESSAGE
                _LOGGER.error("Can't write new backup file: %s", err)
                return False

            except asyncio.CancelledError:
                return False

            backup = await asyncio.shield(
                self.sys_backups.import_backup(
                    tar_file, location=location, additional_locations=locations
                )
            )

        if backup:
            return {ATTR_SLUG: backup.slug}
        return False
