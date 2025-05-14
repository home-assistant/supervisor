"""Test BackupManager class."""

import asyncio
import errno
from functools import partial
from pathlib import Path
from shutil import copy, rmtree
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
from dbus_fast import DBusError
import pytest

from supervisor.addons.addon import Addon
from supervisor.addons.const import AddonBackupMode
from supervisor.addons.model import AddonModel
from supervisor.backups.backup import Backup, BackupLocation
from supervisor.backups.const import LOCATION_TYPE, BackupJobStage, BackupType
from supervisor.backups.manager import BackupManager
from supervisor.const import FOLDER_HOMEASSISTANT, FOLDER_SHARE, AddonState, CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    BackupError,
    BackupFileNotFoundError,
    BackupInvalidError,
    BackupJobError,
    BackupMountDownError,
    DockerError,
)
from supervisor.homeassistant.api import HomeAssistantAPI
from supervisor.homeassistant.const import WSType
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant
from supervisor.jobs import JobSchedulerOptions
from supervisor.jobs.const import JobCondition
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import UnhealthyReason
from supervisor.utils.json import read_json_file, write_json_file

from tests.common import get_fixture_path
from tests.const import TEST_ADDON_SLUG
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService


async def test_do_backup_full(coresys: CoreSys, backup_mock, install_addon_ssh):
    """Test creating Backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_full()

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][2] == BackupType.FULL
    assert backup_instance.new.call_args[0][3] is None
    assert backup_instance.new.call_args[0][4] is True

    backup_instance.store_homeassistant.assert_called_once()
    backup_instance.store_repositories.assert_called_once()

    backup_instance.store_addons.assert_called_once()
    assert install_addon_ssh in backup_instance.store_addons.call_args[0][0]

    backup_instance.store_folders.assert_called_once()
    assert len(backup_instance.store_folders.call_args[0][0]) == 4

    assert coresys.core.state == CoreState.RUNNING


@pytest.mark.parametrize(
    ("filename", "filename_expected"),
    [("../my file.tar", "/data/backup/my file.tar"), (None, "/data/backup/{}.tar")],
)
async def test_do_backup_full_with_filename(
    coresys: CoreSys, filename: str, filename_expected: str, backup_mock
):
    """Test creating Backup with a specific file name."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    # backup_mock fixture causes Backup() to be a MagicMock
    await manager.do_backup_full(filename=filename)

    slug = backup_mock.call_args[0][2]
    assert str(backup_mock.call_args[0][1]) == filename_expected.format(slug)

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_full_uncompressed(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating Backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_full(compressed=False)

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][2] == BackupType.FULL
    assert backup_instance.new.call_args[0][3] is None
    assert backup_instance.new.call_args[0][4] is False

    backup_instance.store_homeassistant.assert_called_once()
    backup_instance.store_repositories.assert_called_once()

    backup_instance.store_addons.assert_called_once()
    assert install_addon_ssh in backup_instance.store_addons.call_args[0][0]

    backup_instance.store_folders.assert_called_once()
    assert len(backup_instance.store_folders.call_args[0][0]) == 4
    backup_instance.store_homeassistant.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_partial_minimal(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating minimal partial Backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_partial(homeassistant=False)

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][2] == BackupType.PARTIAL
    assert backup_instance.new.call_args[0][3] is None
    assert backup_instance.new.call_args[0][4] is True

    backup_instance.store_homeassistant.assert_not_called()
    backup_instance.store_repositories.assert_called_once()

    backup_instance.store_addons.assert_not_called()

    backup_instance.store_folders.assert_not_called()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_partial_minimal_uncompressed(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating minimal partial Backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_partial(
        homeassistant=False, compressed=False
    )

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][2] == BackupType.PARTIAL
    assert backup_instance.new.call_args[0][3] is None
    assert backup_instance.new.call_args[0][4] is False

    backup_instance.store_homeassistant.assert_not_called()
    backup_instance.store_repositories.assert_called_once()

    backup_instance.store_addons.assert_not_called()

    backup_instance.store_folders.assert_not_called()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_partial_maximal(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating maximal partial Backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_partial(
        addons=[TEST_ADDON_SLUG],
        folders=[FOLDER_SHARE, FOLDER_HOMEASSISTANT],
        homeassistant=True,
    )

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][2] == BackupType.PARTIAL
    assert backup_instance.new.call_args[0][3] is None
    assert backup_instance.new.call_args[0][4] is True

    backup_instance.store_homeassistant.assert_called_once()
    backup_instance.store_repositories.assert_called_once()

    backup_instance.store_addons.assert_called_once()
    assert install_addon_ssh in backup_instance.store_addons.call_args[0][0]

    backup_instance.store_folders.assert_called_once()
    assert len(backup_instance.store_folders.call_args[0][0]) == 1
    backup_instance.store_homeassistant.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_full(
    coresys: CoreSys, supervisor_internet, full_backup_mock, install_addon_ssh
):
    """Test restoring full Backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)
    install_addon_ssh.uninstall = AsyncMock(return_value=None)

    manager = await BackupManager(coresys).load_config()

    backup_instance = full_backup_mock.return_value
    backup_instance.sys_addons = coresys.addons
    backup_instance.remove_delta_addons = partial(
        Backup.remove_delta_addons, backup_instance
    )
    assert await manager.do_restore_full(backup_instance)

    backup_instance.restore_homeassistant.assert_called_once()
    backup_instance.restore_repositories.assert_called_once()

    backup_instance.restore_addons.assert_called_once()
    install_addon_ssh.uninstall.assert_not_called()

    backup_instance.restore_folders.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_full_different_addon(
    coresys: CoreSys, supervisor_internet, full_backup_mock, install_addon_ssh
):
    """Test restoring full Backup with different addons than installed."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)
    install_addon_ssh.uninstall = AsyncMock(return_value=None)

    manager = await BackupManager(coresys).load_config()

    backup_instance = full_backup_mock.return_value
    backup_instance.addon_list = ["differentslug"]
    backup_instance.sys_addons = coresys.addons
    backup_instance.remove_delta_addons = partial(
        Backup.remove_delta_addons, backup_instance
    )
    assert await manager.do_restore_full(backup_instance)

    backup_instance.restore_homeassistant.assert_called_once()
    backup_instance.restore_repositories.assert_called_once()

    backup_instance.restore_addons.assert_called_once()
    install_addon_ssh.uninstall.assert_called_once()

    backup_instance.restore_folders.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_partial_minimal(
    coresys: CoreSys, supervisor_internet, partial_backup_mock, install_addon_ssh
):
    """Test restoring partial Backup minimal."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)

    manager = await BackupManager(coresys).load_config()

    backup_instance = partial_backup_mock.return_value
    assert await manager.do_restore_partial(backup_instance, homeassistant=False)

    backup_instance.restore_homeassistant.assert_not_called()
    backup_instance.restore_repositories.assert_not_called()

    backup_instance.restore_addons.assert_not_called()

    backup_instance.restore_folders.assert_not_called()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_partial_maximal(
    coresys: CoreSys, supervisor_internet, partial_backup_mock
):
    """Test restoring partial Backup minimal."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)

    manager = await BackupManager(coresys).load_config()

    backup_instance = partial_backup_mock.return_value
    assert await manager.do_restore_partial(
        backup_instance,
        addons=[TEST_ADDON_SLUG],
        folders=[FOLDER_SHARE, FOLDER_HOMEASSISTANT],
        homeassistant=True,
    )

    backup_instance.restore_homeassistant.assert_called_once()
    backup_instance.restore_repositories.assert_called_once()

    backup_instance.restore_addons.assert_called_once()

    backup_instance.restore_folders.assert_called_once()
    backup_instance.restore_homeassistant.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_fail_invalid_full_backup(
    coresys: CoreSys,
    supervisor_internet,
    full_backup_mock: MagicMock,
    partial_backup_mock: MagicMock,
):
    """Test restore fails with invalid backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    with pytest.raises(BackupInvalidError):
        await manager.do_restore_full(partial_backup_mock.return_value)

    backup_instance = full_backup_mock.return_value
    backup_instance.all_locations[None].protected = True
    backup_instance.validate_backup.side_effect = BackupInvalidError()

    with pytest.raises(BackupInvalidError):
        await manager.do_restore_full(backup_instance)

    backup_instance.all_locations[None].protected = False
    backup_instance.supervisor_version = "2022.08.4"
    with (
        patch.object(
            type(coresys.supervisor),
            "version",
            new=PropertyMock(return_value="2022.08.3"),
        ),
        pytest.raises(BackupInvalidError),
    ):
        await manager.do_restore_full(backup_instance)


async def test_fail_invalid_partial_backup(
    coresys: CoreSys, supervisor_internet, partial_backup_mock: MagicMock
):
    """Test restore fails with invalid backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    backup_instance = partial_backup_mock.return_value
    backup_instance.all_locations[None].protected = True
    backup_instance.validate_backup.side_effect = BackupInvalidError()

    with pytest.raises(BackupInvalidError):
        await manager.do_restore_partial(backup_instance)

    backup_instance.all_locations[None].protected = False
    backup_instance.homeassistant = None

    with pytest.raises(BackupInvalidError):
        await manager.do_restore_partial(backup_instance, homeassistant=True)

    backup_instance.supervisor_version = "2022.08.4"
    with (
        patch.object(
            type(coresys.supervisor),
            "version",
            new=PropertyMock(return_value="2022.08.3"),
        ),
        pytest.raises(BackupInvalidError),
    ):
        await manager.do_restore_partial(backup_instance)


async def test_backup_error_homeassistant(
    coresys: CoreSys,
    backup_mock: MagicMock,
    install_addon_ssh: Addon,
    capture_exception: Mock,
):
    """Test error collected and file deleted when Home Assistant Core backup fails."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_instance = backup_mock.return_value

    backup_instance.store_homeassistant.side_effect = (
        err := BackupError("Error while storing homeassistant")
    )

    job, backup_task = coresys.jobs.schedule_job(
        coresys.backups.do_backup_full, JobSchedulerOptions()
    )
    assert await backup_task is None

    assert job.errors[0].type_ is type(err)
    assert job.errors[0].message == str(err)
    assert job.errors[0].stage == BackupJobStage.HOME_ASSISTANT

    backup_instance.tarfile.unlink.assert_called_once()


async def test_backup_error_capture(
    coresys: CoreSys,
    backup_mock: MagicMock,
    install_addon_ssh: Addon,
    capture_exception: Mock,
):
    """Test error captured when backup fails."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_mock.return_value.store_folders.side_effect = (err := OSError())
    backup = await coresys.backups.do_backup_full()

    assert backup is None

    capture_exception.assert_called_once_with(err)


async def test_restore_error(
    coresys: CoreSys,
    supervisor_internet,
    full_backup_mock: MagicMock,
    capture_exception: Mock,
):
    """Test restoring full Backup with errors."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)

    backup_instance = full_backup_mock.return_value
    backup_instance.protected = False
    backup_instance.restore_homeassistant.side_effect = BackupError()
    with pytest.raises(BackupError):
        await coresys.backups.do_restore_full(backup_instance)
    capture_exception.assert_not_called()

    backup_instance.restore_homeassistant.side_effect = (err := DockerError())
    with pytest.raises(BackupError):
        await coresys.backups.do_restore_full(backup_instance)
    capture_exception.assert_called_once_with(err)


async def test_backup_media_with_mounts(
    coresys: CoreSys,
    supervisor_internet,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test backing up media folder with mounts."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.response_get_unit = [
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]

    # Make some normal test files
    (test_file_1 := coresys.config.path_media / "test.txt").touch()
    (test_dir := coresys.config.path_media / "test").mkdir()
    (test_file_2 := coresys.config.path_media / "test" / "inner.txt").touch()

    # Add a media mount
    await coresys.mounts.load()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "media_test",
                "usage": "media",
                "type": "cifs",
                "server": "test.local",
                "share": "test",
            },
        )
    )
    assert (mount_dir := coresys.config.path_media / "media_test").is_dir()

    # Make a partial backup
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    backup: Backup = await coresys.backups.do_backup_partial("test", folders=["media"])

    # Remove the mount and wipe the media folder
    systemd_unit_service.active_state = "inactive"
    await coresys.mounts.remove_mount("media_test")
    rmtree(coresys.config.path_media)
    coresys.config.path_media.mkdir()

    # Restore the backup and check that only the test files we made returned
    with patch.object(DockerHomeAssistant, "is_running", return_value=True):
        await coresys.backups.do_restore_partial(backup, folders=["media"])

    assert test_file_1.exists()
    assert test_dir.is_dir()
    assert test_file_2.exists()
    assert not mount_dir.exists()


async def test_backup_media_with_mounts_retains_files(
    coresys: CoreSys,
    supervisor_internet,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test backing up media folder with mounts retains mount files."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_unit_service.active_state = ["active", "active", "active", "inactive"]
    systemd_service.response_get_unit = [
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]

    # Add a media mount
    await coresys.mounts.load()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "media_test",
                "usage": "media",
                "type": "cifs",
                "server": "test.local",
                "share": "test",
            },
        )
    )

    # Make a partial backup
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    backup: Backup = await coresys.backups.do_backup_partial("test", folders=["media"])

    systemd_service.StopUnit.calls.clear()
    systemd_service.StartTransientUnit.calls.clear()
    with patch.object(DockerHomeAssistant, "is_running", return_value=True):
        await coresys.backups.do_restore_partial(backup, folders=["media"])

    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-media-media_test.mount", "fail")
    ]
    assert systemd_service.StartTransientUnit.calls == [
        ("mnt-data-supervisor-media-media_test.mount", "fail", ANY, [])
    ]


async def test_backup_share_with_mounts(
    coresys: CoreSys,
    supervisor_internet,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test backing up share folder with mounts."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_unit_service.active_state = [
        "active",
        "active",
        "active",
        "inactive",
        "active",
        "inactive",
    ]
    systemd_service.response_get_unit = [
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]

    # Make some normal test files
    (test_file_1 := coresys.config.path_share / "test.txt").touch()
    (test_dir := coresys.config.path_share / "test").mkdir()
    (test_file_2 := coresys.config.path_share / "test" / "inner.txt").touch()

    # Add a media mount
    await coresys.mounts.load()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "share_test",
                "usage": "share",
                "type": "cifs",
                "server": "test.local",
                "share": "test",
            },
        )
    )
    assert (mount_dir := coresys.config.path_share / "share_test").is_dir()

    # Make a partial backup
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    backup: Backup = await coresys.backups.do_backup_partial("test", folders=["share"])

    # Remove the mount and wipe the media folder
    await coresys.mounts.remove_mount("share_test")
    rmtree(coresys.config.path_share)
    coresys.config.path_share.mkdir()

    # Restore the backup and check that only the test files we made returned
    with patch.object(DockerHomeAssistant, "is_running", return_value=True):
        await coresys.backups.do_restore_partial(backup, folders=["share"])

    assert test_file_1.exists()
    assert test_dir.is_dir()
    assert test_file_2.exists()
    assert not mount_dir.exists()


async def test_full_backup_to_mount(
    coresys: CoreSys,
    supervisor_internet,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test full backup to and restoring from a mount."""
    (marker := coresys.config.path_homeassistant / "test.txt").touch()

    # Add a backup mount
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    assert "backup_test" in coresys.backups.backup_locations
    assert coresys.backups.backup_locations["backup_test"] == mount_dir

    # Make a backup and add it to mounts. Confirm it exists in the right place
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    backup: Backup = await coresys.backups.do_backup_full("test", location=mount)
    assert (mount_dir / f"{backup.slug}.tar").exists()

    # Reload and check that backups in mounts are listed
    await coresys.backups.reload()
    assert coresys.backups.get(backup.slug)

    # Remove marker file and restore. Confirm it comes back
    marker.unlink()

    with patch.object(DockerHomeAssistant, "is_running", return_value=True):
        await coresys.backups.do_restore_full(backup)

    assert marker.exists()


async def test_partial_backup_to_mount(
    coresys: CoreSys,
    supervisor_internet,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test partial backup to and restoring from a mount."""
    (marker := coresys.config.path_homeassistant / "test.txt").touch()

    # Add a backup mount
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    assert "backup_test" in coresys.backups.backup_locations
    assert coresys.backups.backup_locations["backup_test"] == mount_dir

    # Make a backup and add it to mounts. Confirm it exists in the right place
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2023.1.1")),
    ):
        backup: Backup = await coresys.backups.do_backup_partial(
            "test", homeassistant=True, location=mount
        )

        assert (mount_dir / f"{backup.slug}.tar").exists()

        # Reload and check that backups in mounts are listed
        await coresys.backups.reload()
        assert coresys.backups.get(backup.slug)

        # Remove marker file and restore. Confirm it comes back
        marker.unlink()

        with patch.object(DockerHomeAssistant, "is_running", return_value=True):
            await coresys.backups.do_restore_partial(backup, homeassistant=True)

    assert marker.exists()


async def test_backup_to_down_mount_error(
    coresys: CoreSys,
    mock_is_mount: MagicMock,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test backup to mount when down raises error."""
    # Add a backup mount
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    assert "backup_test" in coresys.backups.backup_locations
    assert coresys.backups.backup_locations["backup_test"] == mount_dir

    # Attempt to make a backup which fails because is_mount on directory is false
    mock_is_mount.return_value = False
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    with pytest.raises(BackupMountDownError):
        await coresys.backups.do_backup_full("test", location=mount)
    with pytest.raises(BackupMountDownError):
        await coresys.backups.do_backup_partial(
            "test", location=mount, homeassistant=True
        )


async def test_backup_to_local_with_default(
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test making backup to local when a default mount is specified."""
    # Add a default backup mount
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    coresys.mounts.default_backup_mount = mount

    # Make a backup for local. Confirm it exists in the right place
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2023.1.1")),
    ):
        backup: Backup = await coresys.backups.do_backup_partial(
            "test", homeassistant=True, location=None
        )

    assert (coresys.config.path_backup / f"{backup.slug}.tar").exists()


async def test_backup_to_default(
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test making backup to default mount."""
    # Add a default backup mount
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    coresys.mounts.default_backup_mount = mount

    # Make a backup for default. Confirm it exists in the right place
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2023.1.1")),
    ):
        backup: Backup = await coresys.backups.do_backup_partial(
            "test", homeassistant=True
        )

    assert (mount_dir / f"{backup.slug}.tar").exists()


async def test_backup_to_default_mount_down_error(
    coresys: CoreSys,
    mock_is_mount: MagicMock,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test making backup to default mount when it is down."""
    # Add a default backup mount
    (coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    coresys.mounts.default_backup_mount = mount

    # Attempt to make a backup which fails because is_mount on directory is false
    mock_is_mount.return_value = False
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with pytest.raises(BackupMountDownError):
        await coresys.backups.do_backup_partial("test", homeassistant=True)


async def test_load_network_error(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    mock_is_mount: MagicMock,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test load of backup manager when there is a network error."""
    (coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)
    caplog.clear()

    # This should not raise, manager should just ignore backup locations with errors
    mock_is_mount.return_value = False
    mock_path = MagicMock()
    mock_path.is_dir.side_effect = OSError("Host is down")
    mock_path.as_posix.return_value = "/data/backup_test"
    with patch.object(Mount, "local_where", new=PropertyMock(return_value=mock_path)):
        await coresys.backups.load()

    assert "Could not list backups from /data/backup_test" in caplog.text


async def test_backup_with_healthcheck(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test backup of addon with healthcheck in cold mode."""
    container.status = "running"
    container.attrs["Config"] = {"Healthcheck": "exists"}
    install_addon_ssh.path_data.mkdir()
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STARTUP

    state_changes: list[AddonState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes
        await asyncio.sleep(0.01)

        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            )
        )

        state_changes.append(install_addon_ssh.state)
        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            )
        )

        state_changes.append(install_addon_ssh.state)
        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.HEALTHY,
                id="abc123",
                time=1,
            )
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with (
        patch.object(DockerAddon, "run", new=container_events_task),
        patch.object(
            AddonModel,
            "backup_mode",
            new=PropertyMock(return_value=AddonBackupMode.COLD),
        ),
        patch.object(DockerAddon, "is_running", side_effect=[True, False, False]),
    ):
        backup = await coresys.backups.do_backup_partial(
            homeassistant=False, addons=["local_ssh"]
        )

    assert backup
    assert state_changes == [AddonState.STOPPED, AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert coresys.core.state == CoreState.RUNNING

    await _container_events_task


async def test_restore_with_healthcheck(
    coresys: CoreSys,
    supervisor_internet,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test backup of addon with healthcheck in cold mode."""
    container.status = "running"
    container.attrs["Config"] = {"Healthcheck": "exists"}
    install_addon_ssh.path_data.mkdir()
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STARTUP

    backup = await coresys.backups.do_backup_partial(
        homeassistant=False, addons=["local_ssh"]
    )
    state_changes: list[AddonState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes

        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            )
        )

        state_changes.append(install_addon_ssh.state)
        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            )
        )

        state_changes.append(install_addon_ssh.state)
        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.HEALTHY,
                id="abc123",
                time=1,
            )
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with (
        patch.object(DockerAddon, "run", new=container_events_task),
        patch.object(DockerAddon, "is_running", return_value=False),
        patch.object(AddonModel, "_validate_availability"),
        patch.object(Addon, "with_ingress", new=PropertyMock(return_value=False)),
    ):
        await coresys.backups.do_restore_partial(backup, addons=["local_ssh"])

    assert state_changes == [AddonState.STOPPED, AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert coresys.core.state == CoreState.RUNNING

    await _container_events_task


def _make_backup_message_for_assert(
    *,
    action: str = "full_backup",
    reference: str,
    stage: str | None,
    done: bool = False,
):
    """Make a backup message to use for assert test."""
    return {
        "type": "supervisor/event",
        "data": {
            "event": "job",
            "data": {
                "name": f"backup_manager_{action}",
                "reference": reference,
                "uuid": ANY,
                "progress": 0,
                "stage": stage,
                "done": done,
                "parent_id": None,
                "errors": [],
                "created": ANY,
            },
        },
    }


async def test_backup_progress(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    ha_ws_client: AsyncMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test progress is tracked during backups."""
    container.status = "running"
    install_addon_ssh.path_data.mkdir()
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(
            AddonModel,
            "backup_mode",
            new=PropertyMock(return_value=AddonBackupMode.COLD),
        ),
        patch("supervisor.addons.addon.asyncio.Event.wait"),
    ):
        full_backup: Backup = await coresys.backups.do_backup_full()
    await asyncio.sleep(0)

    messages = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0]["type"] == WSType.SUPERVISOR_EVENT
        and call.args[0]["data"].get("data", {}).get("name")
        == "backup_manager_full_backup"
    ]
    assert messages == [
        _make_backup_message_for_assert(reference=None, stage=None),
        _make_backup_message_for_assert(reference=full_backup.slug, stage=None),
        _make_backup_message_for_assert(
            reference=full_backup.slug, stage="addon_repositories"
        ),
        _make_backup_message_for_assert(
            reference=full_backup.slug, stage="home_assistant"
        ),
        _make_backup_message_for_assert(reference=full_backup.slug, stage="addons"),
        _make_backup_message_for_assert(reference=full_backup.slug, stage="folders"),
        _make_backup_message_for_assert(
            reference=full_backup.slug, stage="finishing_file"
        ),
        _make_backup_message_for_assert(
            reference=full_backup.slug, stage="await_addon_restarts"
        ),
        _make_backup_message_for_assert(
            reference=full_backup.slug, stage="await_addon_restarts", done=True
        ),
    ]

    ha_ws_client.async_send_command.reset_mock()
    partial_backup: Backup = await coresys.backups.do_backup_partial(
        addons=["local_ssh"], folders=["media", "share", "ssl"]
    )
    await asyncio.sleep(0)

    messages = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0]["type"] == WSType.SUPERVISOR_EVENT
        and call.args[0]["data"].get("data", {}).get("name")
        == "backup_manager_partial_backup"
    ]
    assert messages == [
        _make_backup_message_for_assert(
            action="partial_backup", reference=None, stage=None
        ),
        _make_backup_message_for_assert(
            action="partial_backup", reference=partial_backup.slug, stage=None
        ),
        _make_backup_message_for_assert(
            action="partial_backup",
            reference=partial_backup.slug,
            stage="addon_repositories",
        ),
        _make_backup_message_for_assert(
            action="partial_backup", reference=partial_backup.slug, stage="addons"
        ),
        _make_backup_message_for_assert(
            action="partial_backup", reference=partial_backup.slug, stage="folders"
        ),
        _make_backup_message_for_assert(
            action="partial_backup",
            reference=partial_backup.slug,
            stage="finishing_file",
        ),
        _make_backup_message_for_assert(
            action="partial_backup",
            reference=partial_backup.slug,
            stage="finishing_file",
            done=True,
        ),
    ]


async def test_restore_progress(
    coresys: CoreSys,
    supervisor_internet,
    install_addon_ssh: Addon,
    container: MagicMock,
    ha_ws_client: AsyncMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test progress is tracked during backups."""
    container.status = "running"
    install_addon_ssh.path_data.mkdir()
    install_addon_ssh.state = AddonState.STARTED
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    full_backup: Backup = await coresys.backups.do_backup_full()
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.reset_mock()

    # Install another addon to be uninstalled
    # Duplicate code from install_addon_example fixture
    # Apparently request.getfixturevalue does not work with async fixtures: https://github.com/pytest-dev/pytest-asyncio/issues/112
    store = coresys.addons.store["local_example"]
    await coresys.addons.data.install(store)
    # pylint: disable-next=protected-access
    coresys.addons.data._data = coresys.addons.data._schema(coresys.addons.data._data)
    coresys.addons.local[store.slug] = Addon(coresys, store.slug)

    with (
        patch("supervisor.addons.addon.asyncio.Event.wait"),
        patch.object(HomeAssistant, "restore"),
        patch.object(HomeAssistantCore, "update"),
        patch.object(AddonModel, "_validate_availability"),
        patch.object(AddonModel, "with_ingress", new=PropertyMock(return_value=False)),
    ):
        await coresys.backups.do_restore_full(full_backup)
    await asyncio.sleep(0)

    messages = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0]["type"] == WSType.SUPERVISOR_EVENT
        and call.args[0]["data"].get("data", {}).get("name")
        == "backup_manager_full_restore"
    ]
    assert messages == [
        _make_backup_message_for_assert(
            action="full_restore", reference=None, stage=None
        ),
        _make_backup_message_for_assert(
            action="full_restore", reference=full_backup.slug, stage=None
        ),
        _make_backup_message_for_assert(
            action="full_restore", reference=full_backup.slug, stage="folders"
        ),
        _make_backup_message_for_assert(
            action="full_restore",
            reference=full_backup.slug,
            stage="home_assistant",
        ),
        _make_backup_message_for_assert(
            action="full_restore",
            reference=full_backup.slug,
            stage="remove_delta_addons",
        ),
        _make_backup_message_for_assert(
            action="full_restore",
            reference=full_backup.slug,
            stage="addon_repositories",
        ),
        _make_backup_message_for_assert(
            action="full_restore", reference=full_backup.slug, stage="addons"
        ),
        _make_backup_message_for_assert(
            action="full_restore",
            reference=full_backup.slug,
            stage="await_addon_restarts",
        ),
        _make_backup_message_for_assert(
            action="full_restore",
            reference=full_backup.slug,
            stage="await_home_assistant_restart",
        ),
        _make_backup_message_for_assert(
            action="full_restore",
            reference=full_backup.slug,
            stage="await_home_assistant_restart",
            done=True,
        ),
    ]

    folders_backup: Backup = await coresys.backups.do_backup_partial(
        folders=["media", "share", "ssl"]
    )
    ha_ws_client.async_send_command.reset_mock()
    await coresys.backups.do_restore_partial(
        folders_backup, folders=["media", "share", "ssl"]
    )
    await asyncio.sleep(0)

    messages = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0]["type"] == WSType.SUPERVISOR_EVENT
        and call.args[0]["data"].get("data", {}).get("name")
        == "backup_manager_partial_restore"
    ]
    assert messages == [
        _make_backup_message_for_assert(
            action="partial_restore", reference=None, stage=None
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=folders_backup.slug,
            stage=None,
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=folders_backup.slug,
            stage="folders",
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=folders_backup.slug,
            stage="folders",
            done=True,
        ),
    ]

    container.status = "stopped"
    install_addon_ssh.state = AddonState.STOPPED
    addon_backup: Backup = await coresys.backups.do_backup_partial(addons=["local_ssh"])

    ha_ws_client.async_send_command.reset_mock()
    with (
        patch.object(AddonModel, "_validate_availability"),
        patch.object(HomeAssistantCore, "start"),
    ):
        await coresys.backups.do_restore_partial(addon_backup, addons=["local_ssh"])
    await asyncio.sleep(0)

    messages = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0]["type"] == WSType.SUPERVISOR_EVENT
        and call.args[0]["data"].get("data", {}).get("name")
        == "backup_manager_partial_restore"
    ]
    assert messages == [
        _make_backup_message_for_assert(
            action="partial_restore", reference=None, stage=None
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=addon_backup.slug,
            stage=None,
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=addon_backup.slug,
            stage="addon_repositories",
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=addon_backup.slug,
            stage="addons",
        ),
        _make_backup_message_for_assert(
            action="partial_restore",
            reference=addon_backup.slug,
            stage="addons",
            done=True,
        ),
    ]


async def test_freeze_thaw(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    ha_ws_client: AsyncMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test manual freeze and thaw for external snapshots."""
    container.status = "running"
    install_addon_ssh.path_data.mkdir()
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container.exec_run.return_value = (0, None)
    ha_ws_client.ha_version = AwesomeVersion("2022.1.0")

    with (
        patch.object(
            AddonModel, "backup_pre", new=PropertyMock(return_value="pre_backup")
        ),
        patch.object(
            AddonModel, "backup_post", new=PropertyMock(return_value="post_backup")
        ),
    ):
        # Run the freeze
        await coresys.backups.freeze_all()
        container.exec_run.assert_called_once_with("pre_backup")
        assert coresys.core.state == CoreState.FREEZE

        await asyncio.sleep(0)
        messages = [
            call.args[0]
            for call in ha_ws_client.async_send_command.call_args_list
            if call.args[0]["type"] in ["backup/start", "backup/end"]
            or call.args[0]["data"].get("data", {}).get("name")
            in ["backup_manager_freeze_all", "backup_manager_thaw_all"]
        ]
        assert messages == [
            _make_backup_message_for_assert(
                action="freeze_all", reference=None, stage=None
            ),
            {"type": "backup/start"},
            _make_backup_message_for_assert(
                action="freeze_all", reference=None, stage="home_assistant"
            ),
            _make_backup_message_for_assert(
                action="freeze_all", reference=None, stage="addons"
            ),
            _make_backup_message_for_assert(
                action="thaw_all", reference=None, stage=None
            ),
            _make_backup_message_for_assert(
                action="freeze_all", reference=None, stage="addons", done=True
            ),
        ]

        # Release the thaw task
        container.exec_run.reset_mock()
        ha_ws_client.async_send_command.reset_mock()
        await coresys.backups.thaw_all()
        container.exec_run.assert_called_once_with("post_backup")
        assert coresys.core.state == CoreState.RUNNING

        await asyncio.sleep(0)
        messages = [
            call.args[0]
            for call in ha_ws_client.async_send_command.call_args_list
            if call.args[0]["type"] in ["backup/start", "backup/end"]
            or call.args[0]["data"].get("data", {}).get("name")
            in ["backup_manager_freeze_all", "backup_manager_thaw_all"]
        ]
        assert messages == [
            {"type": "backup/end"},
            _make_backup_message_for_assert(
                action="thaw_all", reference=None, stage="home_assistant"
            ),
            _make_backup_message_for_assert(
                action="thaw_all", reference=None, stage="addons"
            ),
            _make_backup_message_for_assert(
                action="thaw_all", reference=None, stage="addons", done=True
            ),
        ]


async def test_freeze_thaw_timeout(
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    caplog: pytest.LogCaptureFixture,
    tmp_supervisor_data,
    path_extern,
):
    """Test manual freeze ends due to timeout expiration."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    ha_ws_client.ha_version = AwesomeVersion("2022.1.0")

    await coresys.backups.freeze_all(timeout=0.01)
    assert coresys.core.state == CoreState.FREEZE
    await asyncio.sleep(0)
    assert any(
        call.args[0] == {"type": "backup/start"}
        for call in ha_ws_client.async_send_command.call_args_list
    )

    ha_ws_client.async_send_command.reset_mock()
    await asyncio.sleep(0.02)
    assert coresys.core.state == CoreState.RUNNING
    assert any(
        call.args[0] == {"type": "backup/end"}
        for call in ha_ws_client.async_send_command.call_args_list
    )
    assert "Timeout waiting for signal to thaw after manual freeze" in caplog.text


async def test_cannot_manually_thaw_normal_freeze(coresys: CoreSys):
    """Test thaw_all cannot be used unless freeze was started by freeze_all method."""
    await coresys.core.set_state(CoreState.FREEZE)
    with pytest.raises(BackupError):
        await coresys.backups.thaw_all()


async def test_restore_only_reloads_ingress_on_change(
    coresys: CoreSys,
    supervisor_internet,
    install_addon_ssh: Addon,
    tmp_supervisor_data,
    path_extern,
):
    """Test restore only tells core to reload ingress when something has changed."""
    install_addon_ssh.path_data.mkdir()
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_no_ingress: Backup = await coresys.backups.do_backup_partial(
        addons=["local_ssh"]
    )

    install_addon_ssh.ingress_panel = True
    await install_addon_ssh.save_persist()
    backup_with_ingress: Backup = await coresys.backups.do_backup_partial(
        addons=["local_ssh"]
    )

    async def mock_is_running(*_) -> bool:
        return True

    with (
        patch.object(HomeAssistantCore, "is_running", new=mock_is_running),
        patch.object(AddonModel, "_validate_availability"),
        patch.object(DockerAddon, "attach"),
        patch.object(HomeAssistantAPI, "make_request") as make_request,
    ):
        make_request.return_value.__aenter__.return_value.status = 200

        # Has ingress before and after - not called
        await coresys.backups.do_restore_partial(
            backup_with_ingress, addons=["local_ssh"]
        )
        make_request.assert_not_called()

        # Restore removes ingress - tell Home Assistant
        await coresys.backups.do_restore_partial(
            backup_no_ingress, addons=["local_ssh"]
        )
        make_request.assert_called_once_with(
            "delete", "api/hassio_push/panel/local_ssh"
        )

        # No ingress before or after - not called
        make_request.reset_mock()
        await coresys.backups.do_restore_partial(
            backup_no_ingress, addons=["local_ssh"]
        )
        make_request.assert_not_called()

        # Restore adds ingress - tell Home Assistant
        await coresys.backups.do_restore_partial(
            backup_with_ingress, addons=["local_ssh"]
        )
        make_request.assert_called_once_with("post", "api/hassio_push/panel/local_ssh")


async def test_restore_new_addon(
    coresys: CoreSys,
    supervisor_internet,
    install_addon_example: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test restore installing new addon."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    assert not install_addon_example.path_data.exists()
    assert not install_addon_example.path_config.exists()

    backup: Backup = await coresys.backups.do_backup_partial(addons=["local_example"])
    await coresys.addons.uninstall("local_example")
    assert "local_example" not in coresys.addons.local

    with (
        patch.object(AddonModel, "_validate_availability"),
        patch.object(DockerAddon, "attach"),
    ):
        assert await coresys.backups.do_restore_partial(
            backup, addons=["local_example"]
        )

    assert "local_example" in coresys.addons.local
    assert install_addon_example.path_data.exists()
    assert install_addon_example.path_config.exists()


async def test_restore_preserves_data_config(
    coresys: CoreSys,
    supervisor_internet,
    install_addon_example: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test restore preserves data and config."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    install_addon_example.path_data.mkdir()
    (test_data := install_addon_example.path_data / "data.txt").touch()
    install_addon_example.path_config.mkdir()
    (test_config := install_addon_example.path_config / "config.yaml").touch()

    backup: Backup = await coresys.backups.do_backup_partial(addons=["local_example"])
    (test_config2 := install_addon_example.path_config / "config2.yaml").touch()

    await coresys.addons.uninstall("local_example")
    assert not install_addon_example.path_data.exists()
    assert install_addon_example.path_config.exists()
    assert test_config2.exists()

    with (
        patch.object(AddonModel, "_validate_availability"),
        patch.object(DockerAddon, "attach"),
    ):
        assert await coresys.backups.do_restore_partial(
            backup, addons=["local_example"]
        )

    assert test_data.exists()
    assert test_config.exists()
    assert not test_config2.exists()


async def test_backup_to_mount_bypasses_free_space_condition(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test backing up to a mount bypasses the check on local free space."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda _: 0.1

    # These fail due to lack of local free space
    with pytest.raises(BackupJobError):
        await coresys.backups.do_backup_full()
    with pytest.raises(BackupJobError):
        await coresys.backups.do_backup_partial(folders=["media"])

    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.response_get_unit = [
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]

    # Add a backup mount
    await coresys.mounts.load()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "backup_test",
                "usage": "backup",
                "type": "cifs",
                "server": "test.local",
                "share": "test",
            },
        )
    )
    mount = coresys.mounts.get("backup_test")

    # These succeed because local free space does not matter when using a mount
    await coresys.backups.do_backup_full(location=mount)
    await coresys.backups.do_backup_partial(folders=["media"], location=mount)


@pytest.mark.parametrize(
    "partial_backup,exclude_db_setting",
    [(False, True), (True, True), (False, False), (True, False)],
)
async def test_skip_homeassistant_database(
    coresys: CoreSys,
    container: MagicMock,
    partial_backup: bool,
    exclude_db_setting: bool | None,
    tmp_supervisor_data,
    path_extern,
):
    """Test exclude database option skips database in backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.jobs.ignore_conditions = [
        JobCondition.INTERNET_HOST,
        JobCondition.INTERNET_SYSTEM,
    ]
    coresys.homeassistant.version = AwesomeVersion("2023.09.0")
    coresys.homeassistant.backups_exclude_database = exclude_db_setting

    test_file = coresys.config.path_homeassistant / "configuration.yaml"
    test_db = coresys.config.path_homeassistant / "home-assistant_v2.db"
    test_db_wal = coresys.config.path_homeassistant / "home-assistant_v2.db-wal"
    test_db_shm = coresys.config.path_homeassistant / "home-assistant_v2.db-shm"

    def setup_1():
        test_db.touch()
        test_db_wal.touch()
        test_db_shm.touch()
        write_json_file(test_file, {"default_config": {}})

    await coresys.run_in_executor(setup_1)

    kwargs = {} if exclude_db_setting else {"homeassistant_exclude_database": True}
    if partial_backup:
        backup: Backup = await coresys.backups.do_backup_partial(
            homeassistant=True, **kwargs
        )
    else:
        backup: Backup = await coresys.backups.do_backup_full(**kwargs)

    def setup_2():
        test_file.unlink()
        write_json_file(test_db, {"hello": "world"})
        write_json_file(test_db_wal, {"hello": "world"})

    await coresys.run_in_executor(setup_2)

    with (
        patch.object(HomeAssistantCore, "update"),
        patch.object(HomeAssistantCore, "start"),
    ):
        await coresys.backups.do_restore_partial(backup, homeassistant=True)

    def test_assertions():
        assert read_json_file(test_file) == {"default_config": {}}
        assert read_json_file(test_db) == {"hello": "world"}
        assert read_json_file(test_db_wal) == {"hello": "world"}
        assert not test_db_shm.exists()

    await coresys.run_in_executor(test_assertions)


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
@pytest.mark.parametrize(
    ("backup_locations", "location_name", "healthy_expected"),
    [
        (["test"], "test", True),
        ([None], None, False),
    ],
    indirect=["backup_locations"],
)
async def test_backup_remove_error(
    coresys: CoreSys,
    backup_locations: list[LOCATION_TYPE],
    location_name: str | None,
    healthy_expected: bool,
):
    """Test removing a backup error."""
    location: LOCATION_TYPE = backup_locations[0]
    backup_base_path = coresys.backups._get_base_path(location)  # pylint: disable=protected-access
    backup_base_path.mkdir(exist_ok=True)
    copy(get_fixture_path("backup_example.tar"), backup_base_path)

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))

    assert location_name in backup.all_locations
    backup.all_locations[location_name].path = (tar_file_mock := MagicMock())
    tar_file_mock.unlink.side_effect = (err := OSError())

    err.errno = errno.EBUSY
    with pytest.raises(BackupError):
        await coresys.backups.remove(backup)
    assert coresys.core.healthy is True

    err.errno = errno.EBADMSG
    with pytest.raises(BackupError):
        await coresys.backups.remove(backup)
    assert coresys.core.healthy is healthy_expected


@pytest.mark.parametrize(
    "error_path,healthy_expected",
    [(Path("/data/backup"), False), (Path("/data/mounts/backup_test"), True)],
)
async def test_reload_error(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    error_path: Path,
    healthy_expected: bool,
    mock_is_mount: MagicMock,
    path_extern,
    mount_propagation,
):
    """Test error during reload."""
    err = OSError()

    def mock_is_dir(path: Path) -> bool:
        """Mock of is_dir."""
        if path == error_path:
            raise err
        return True

    # Add a backup mount
    await coresys.mounts.load()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "backup_test",
                "usage": "backup",
                "type": "cifs",
                "server": "test.local",
                "share": "test",
            },
        )
    )

    mock_is_mount.return_value = False
    with (
        patch("supervisor.backups.manager.Path.is_dir", new=mock_is_dir),
        patch("supervisor.backups.manager.Path.glob", return_value=[]),
    ):
        err.errno = errno.EBUSY
        await coresys.backups.reload()

        assert "Could not list backups" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        await coresys.backups.reload()

        assert "Could not list backups" in caplog.text
        assert coresys.core.healthy is healthy_expected


async def test_monitoring_after_full_restore(
    coresys: CoreSys,
    supervisor_internet,
    full_backup_mock,
    install_addon_ssh,
    container,
):
    """Test monitoring of addon state still works after full restore."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)

    manager = await BackupManager(coresys).load_config()

    backup_instance = full_backup_mock.return_value
    backup_instance.protected = False
    assert await manager.do_restore_full(backup_instance)

    backup_instance.restore_addons.assert_called_once_with([TEST_ADDON_SLUG])
    assert coresys.core.state == CoreState.RUNNING
    coresys.docker.unload.assert_not_called()


async def test_monitoring_after_partial_restore(
    coresys: CoreSys,
    supervisor_internet,
    partial_backup_mock,
    install_addon_ssh,
    container,
):
    """Test monitoring of addon state still works after full restore."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = await BackupManager(coresys).load_config()

    backup_instance = partial_backup_mock.return_value
    backup_instance.protected = False
    assert await manager.do_restore_partial(backup_instance, addons=[TEST_ADDON_SLUG])

    backup_instance.restore_addons.assert_called_once_with([TEST_ADDON_SLUG])
    assert coresys.core.state == CoreState.RUNNING
    coresys.docker.unload.assert_not_called()


@pytest.mark.parametrize(
    "pre_backup_error",
    [
        {
            "code": "pre_backup_actions_failed",
            "message": "Database migration in progress",
        },
        {"code": "unknown_command", "message": "Unknown command."},
    ],
)
async def test_core_pre_backup_actions_failed(
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    caplog: pytest.LogCaptureFixture,
    pre_backup_error: dict[str, str],
    tmp_supervisor_data,
    path_extern,
):
    """Test pre-backup actions failed in HA core stops backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    ha_ws_client.ha_version = AwesomeVersion("2024.7.0")
    ha_ws_client.async_send_command.return_value = {
        "error": pre_backup_error,
        "id": 1,
        "success": False,
        "type": "result",
    }

    assert not await coresys.backups.do_backup_full()
    assert (
        f"Preparing backup of Home Assistant Core failed due to: {pre_backup_error['message']}"
        in caplog.text
    )


@pytest.mark.usefixtures("mount_propagation", "mock_is_mount", "path_extern")
async def test_reload_multiple_locations(coresys: CoreSys, tmp_supervisor_data: Path):
    """Test reload with a backup that exists in multiple locations."""
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)

    assert not coresys.backups.list_backups

    backup_file = get_fixture_path("backup_example.tar")
    copy(backup_file, tmp_supervisor_data / "core/backup")
    await coresys.backups.reload()

    assert coresys.backups.list_backups
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location == ".cloud_backup"
    assert backup.locations == [".cloud_backup"]
    assert backup.all_locations.keys() == {".cloud_backup"}

    copy(backup_file, tmp_supervisor_data / "backup")
    await coresys.backups.reload()

    assert coresys.backups.list_backups
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location is None
    assert backup.locations == [None]
    assert backup.all_locations.keys() == {".cloud_backup", None}

    copy(backup_file, mount_dir)
    await coresys.backups.reload()

    assert coresys.backups.list_backups
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location in {None, "backup_test"}
    assert None in backup.locations
    assert "backup_test" in backup.locations
    assert backup.all_locations.keys() == {".cloud_backup", None, "backup_test"}


@pytest.mark.usefixtures("mount_propagation", "mock_is_mount", "path_extern")
async def test_partial_reload_multiple_locations(
    coresys: CoreSys, tmp_supervisor_data: Path
):
    """Test a partial reload with a backup that exists in multiple locations."""
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)

    assert not coresys.backups.list_backups

    backup_file = get_fixture_path("backup_example.tar")
    copy(backup_file, tmp_supervisor_data / "core/backup")
    await coresys.backups.reload()

    assert coresys.backups.list_backups
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location == ".cloud_backup"
    assert backup.locations == [".cloud_backup"]
    assert backup.all_locations.keys() == {".cloud_backup"}

    copy(backup_file, tmp_supervisor_data / "backup")
    await coresys.backups.reload()

    assert coresys.backups.list_backups
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location is None
    assert backup.locations == [None]
    assert backup.all_locations.keys() == {".cloud_backup", None}

    copy(backup_file, mount_dir)
    await coresys.backups.reload()

    assert coresys.backups.list_backups
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location is None
    assert backup.locations == [None, "backup_test"]
    assert backup.all_locations.keys() == {".cloud_backup", None, "backup_test"}


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_backup_remove_multiple_locations(coresys: CoreSys):
    """Test removing a backup that exists in multiple locations."""
    backup_file = get_fixture_path("backup_example.tar")
    location_1 = Path(copy(backup_file, coresys.config.path_backup))
    location_2 = Path(copy(backup_file, coresys.config.path_core_backup))

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.all_locations == {
        None: BackupLocation(path=location_1, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=location_2, protected=False, size_bytes=10240
        ),
    }

    await coresys.backups.remove(backup)
    assert not location_1.exists()
    assert not location_2.exists()
    assert not coresys.backups.get("7fed74c8")


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_backup_remove_one_location_of_multiple(coresys: CoreSys):
    """Test removing a backup that exists in multiple locations from one location."""
    backup_file = get_fixture_path("backup_example.tar")
    location_1 = Path(copy(backup_file, coresys.config.path_backup))
    location_2 = Path(copy(backup_file, coresys.config.path_core_backup))

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.all_locations == {
        None: BackupLocation(path=location_1, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=location_2, protected=False, size_bytes=10240
        ),
    }

    await coresys.backups.remove(backup, locations=[".cloud_backup"])
    assert location_1.exists()
    assert not location_2.exists()
    assert coresys.backups.get("7fed74c8")
    assert backup.all_locations == {
        None: BackupLocation(path=location_1, protected=False, size_bytes=10240),
    }


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_addon_backup_excludes(
    coresys: CoreSys, supervisor_internet, install_addon_example: Addon
):
    """Test backup excludes option for addons."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    install_addon_example.path_data.mkdir(parents=True)
    (test1 := install_addon_example.path_data / "test1").touch()
    (test_dir := install_addon_example.path_data / "test_dir").mkdir()
    (test2 := test_dir / "test2").touch()
    (test3 := test_dir / "test3").touch()

    install_addon_example.data["backup_exclude"] = ["test1", "*/test2"]
    backup = await coresys.backups.do_backup_partial(addons=["local_example"])
    test1.unlink()
    test2.unlink()
    test3.unlink()
    test_dir.rmdir()

    await coresys.backups.do_restore_partial(backup, addons=["local_example"])
    assert not test1.exists()
    assert not test2.exists()
    assert test_dir.is_dir()
    assert test3.exists()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_remove_non_existing_backup_raises(
    coresys: CoreSys,
):
    """Test removing a backup error."""
    location: LOCATION_TYPE = None
    backup_base_path = coresys.backups._get_base_path(location)  # pylint: disable=protected-access
    backup_base_path.mkdir(exist_ok=True)
    copy(get_fixture_path("backup_example.tar"), backup_base_path)

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))

    assert None in backup.all_locations
    backup.all_locations[None].path = (tar_file_mock := MagicMock())
    tar_file_mock.unlink.side_effect = (err := FileNotFoundError())
    err.errno = errno.ENOENT

    with pytest.raises(BackupFileNotFoundError):
        await coresys.backups.remove(backup)


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
@pytest.mark.parametrize(
    ("error_num", "unhealthy", "default_location", "additional_location"),
    [
        (errno.EBUSY, False, None, ".cloud_backup"),
        (errno.EBUSY, False, ".cloud_backup", None),
        (errno.EBADMSG, True, None, ".cloud_backup"),
        (errno.EBADMSG, True, ".cloud_backup", None),
    ],
)
async def test_backup_multiple_locations_oserror(
    coresys: CoreSys,
    error_num: int,
    unhealthy: bool,
    default_location: str | None,
    additional_location: str | None,
):
    """Test backup to multiple locations raises oserror."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch("supervisor.backups.manager.copy", side_effect=(err := OSError())):
        err.errno = error_num
        backup: Backup | None = await coresys.backups.do_backup_full(
            name="test",
            location=default_location,
            additional_locations=[additional_location],
        )

    assert backup
    assert coresys.backups.get(backup.slug) == backup
    assert backup.location == default_location
    assert additional_location not in backup.all_locations
    assert (
        UnhealthyReason.OSERROR_BAD_MESSAGE in coresys.resolution.unhealthy
    ) is unhealthy


@pytest.mark.parametrize("same_mount", [True, False])
async def test_get_upload_path_for_backup_location(
    coresys: CoreSys,
    same_mount,
):
    """Test get_upload_path_for_location with local backup location."""
    manager = BackupManager(coresys)

    target_path = coresys.config.path_backup
    tmp_path = coresys.config.path_tmp

    def make_stat_mock(target_path: Path, tmp_path: Path, same_mount: bool):
        def _mock_stat(self):
            if self == target_path:
                return SimpleNamespace(st_dev=1)
            if self == tmp_path:
                return SimpleNamespace(st_dev=1 if same_mount else 2)
            raise ValueError(f"Unexpected path: {self}")

        return _mock_stat

    with patch(
        "pathlib.Path.stat", new=make_stat_mock(target_path, tmp_path, same_mount)
    ):
        result = await manager.get_upload_path_for_location(None)

        if same_mount:
            assert result == tmp_path
        else:
            assert result == target_path


async def test_get_upload_path_for_mount_location(
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test get_upload_path_for_location with a Mount location."""
    manager = BackupManager(coresys)

    await coresys.mounts.load()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "test_mount",
            "usage": "backup",
            "type": "cifs",
            "server": "server.local",
            "share": "test",
        },
    )
    await coresys.mounts.create_mount(mount)

    result = await manager.get_upload_path_for_location(mount)

    assert result == mount.local_where
