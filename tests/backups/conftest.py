"""Mock test."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supervisor.backups.backup import BackupLocation
from supervisor.backups.const import LOCATION_CLOUD_BACKUP, LOCATION_TYPE, BackupType
from supervisor.backups.validate import ALL_FOLDERS
from supervisor.coresys import CoreSys
from supervisor.mounts.mount import Mount

from tests.const import TEST_ADDON_SLUG


@pytest.fixture(name="backup_mock")
def fixture_backup_mock():
    """Backup class mock."""
    with patch("supervisor.backups.manager.Backup") as backup_mock:
        backup_instance = MagicMock()
        backup_mock.return_value = backup_instance

        backup_instance.store_addons = AsyncMock(return_value=None)
        backup_instance.store_folders = AsyncMock(return_value=None)
        backup_instance.store_homeassistant = AsyncMock(return_value=None)
        backup_instance.store_addons = AsyncMock(return_value=None)
        backup_instance.restore_folders = AsyncMock(return_value=True)
        backup_instance.restore_homeassistant = AsyncMock(return_value=None)
        backup_instance.restore_addons = AsyncMock(return_value=(True, []))
        backup_instance.restore_repositories = AsyncMock(return_value=None)
        backup_instance.remove_delta_addons = AsyncMock(return_value=True)

        yield backup_mock


@pytest.fixture
def partial_backup_mock(backup_mock):
    """Partial backup mock."""
    backup_instance = backup_mock.return_value
    backup_instance.sys_type = BackupType.PARTIAL
    backup_instance.folders = []
    backup_instance.addon_list = [TEST_ADDON_SLUG]
    backup_instance.supervisor_version = "9999.09.9.dev9999"
    backup_instance.location = None
    backup_instance.all_locations = {
        None: BackupLocation(path=Path("/"), protected=False, size_bytes=0)
    }
    backup_instance.validate_backup = AsyncMock()
    yield backup_mock


@pytest.fixture
def full_backup_mock(backup_mock):
    """Full backup mock."""
    backup_instance = backup_mock.return_value
    backup_instance.sys_type = BackupType.FULL
    backup_instance.folders = ALL_FOLDERS
    backup_instance.addon_list = [TEST_ADDON_SLUG]
    backup_instance.supervisor_version = "9999.09.9.dev9999"
    backup_instance.location = None
    backup_instance.all_locations = {
        None: BackupLocation(path=Path("/"), protected=False, size_bytes=0)
    }
    backup_instance.validate_backup = AsyncMock()
    yield backup_mock


@pytest.fixture(name="backup_locations")
async def fixture_backup_locations(
    request: pytest.FixtureRequest, coresys: CoreSys, mount_propagation, mock_is_mount
) -> list[LOCATION_TYPE]:
    """Return a list of prcoessed backup locations."""
    locations: list[LOCATION_TYPE] = []
    loaded = False
    for location in request.param:
        if location in {None, LOCATION_CLOUD_BACKUP}:
            locations.append(location)
        else:
            if not loaded:
                await coresys.mounts.load()

            await coresys.mounts.create_mount(
                Mount.from_dict(
                    coresys,
                    {
                        "name": location,
                        "usage": "backup",
                        "type": "cifs",
                        "server": "test.local",
                        "share": "test",
                    },
                )
            )
            locations.append(coresys.mounts.get(location))

    return locations
