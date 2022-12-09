"""Test BackupManager class."""

from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

from supervisor.addons.addon import Addon
from supervisor.backups.const import BackupType
from supervisor.backups.manager import BackupManager
from supervisor.const import FOLDER_HOMEASSISTANT, FOLDER_SHARE, CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import AddonsError, DockerError

from tests.const import TEST_ADDON_SLUG


async def test_do_backup_full(coresys: CoreSys, backup_mock, install_addon_ssh):
    """Test creating Backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_full()

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][3] == BackupType.FULL
    assert backup_instance.new.call_args[0][4] is None
    assert backup_instance.new.call_args[0][5] is True

    backup_instance.store_homeassistant.assert_called_once()
    backup_instance.store_repositories.assert_called_once()
    backup_instance.store_dockerconfig.assert_called_once()

    backup_instance.store_addons.assert_called_once()
    assert install_addon_ssh in backup_instance.store_addons.call_args[0][0]

    backup_instance.store_folders.assert_called_once()
    assert len(backup_instance.store_folders.call_args[0][0]) == 4

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_full_uncompressed(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating Backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_full(compressed=False)

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][3] == BackupType.FULL
    assert backup_instance.new.call_args[0][4] is None
    assert backup_instance.new.call_args[0][5] is False

    backup_instance.store_homeassistant.assert_called_once()
    backup_instance.store_repositories.assert_called_once()
    backup_instance.store_dockerconfig.assert_called_once()

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
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_partial(homeassistant=False)

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][3] == BackupType.PARTIAL
    assert backup_instance.new.call_args[0][4] is None
    assert backup_instance.new.call_args[0][5] is True

    backup_instance.store_homeassistant.assert_not_called()
    backup_instance.store_repositories.assert_called_once()
    backup_instance.store_dockerconfig.assert_called_once()

    backup_instance.store_addons.assert_not_called()

    backup_instance.store_folders.assert_not_called()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_partial_minimal_uncompressed(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating minimal partial Backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_partial(
        homeassistant=False, compressed=False
    )

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][3] == BackupType.PARTIAL
    assert backup_instance.new.call_args[0][4] is None
    assert backup_instance.new.call_args[0][5] is False

    backup_instance.store_homeassistant.assert_not_called()
    backup_instance.store_repositories.assert_called_once()
    backup_instance.store_dockerconfig.assert_called_once()

    backup_instance.store_addons.assert_not_called()

    backup_instance.store_folders.assert_not_called()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_backup_partial_maximal(
    coresys: CoreSys, backup_mock, install_addon_ssh
):
    """Test creating maximal partial Backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    # backup_mock fixture causes Backup() to be a MagicMock
    backup_instance: MagicMock = await manager.do_backup_partial(
        addons=[TEST_ADDON_SLUG],
        folders=[FOLDER_SHARE, FOLDER_HOMEASSISTANT],
        homeassistant=True,
    )

    # Check Backup has been created without password
    assert backup_instance.new.call_args[0][3] == BackupType.PARTIAL
    assert backup_instance.new.call_args[0][4] is None
    assert backup_instance.new.call_args[0][5] is True

    backup_instance.store_homeassistant.assert_called_once()
    backup_instance.store_repositories.assert_called_once()
    backup_instance.store_dockerconfig.assert_called_once()

    backup_instance.store_addons.assert_called_once()
    assert install_addon_ssh in backup_instance.store_addons.call_args[0][0]

    backup_instance.store_folders.assert_called_once()
    assert len(backup_instance.store_folders.call_args[0][0]) == 1
    backup_instance.store_homeassistant.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_full(coresys: CoreSys, full_backup_mock, install_addon_ssh):
    """Test restoring full Backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)
    install_addon_ssh.uninstall = AsyncMock(return_value=None)

    manager = BackupManager(coresys)

    backup_instance = full_backup_mock.return_value
    await manager.do_restore_full(backup_instance)

    backup_instance.restore_homeassistant.assert_called_once()
    backup_instance.restore_repositories.assert_called_once()
    backup_instance.restore_dockerconfig.assert_called_once()

    backup_instance.restore_addons.assert_called_once()
    install_addon_ssh.uninstall.assert_not_called()

    backup_instance.restore_folders.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_full_different_addon(
    coresys: CoreSys, full_backup_mock, install_addon_ssh
):
    """Test restoring full Backup with different addons than installed."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)
    install_addon_ssh.uninstall = AsyncMock(return_value=None)

    manager = BackupManager(coresys)

    backup_instance = full_backup_mock.return_value
    backup_instance.addon_list = ["differentslug"]
    await manager.do_restore_full(backup_instance)

    backup_instance.restore_homeassistant.assert_called_once()
    backup_instance.restore_repositories.assert_called_once()
    backup_instance.restore_dockerconfig.assert_called_once()

    backup_instance.restore_addons.assert_called_once()
    install_addon_ssh.uninstall.assert_called_once()

    backup_instance.restore_folders.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_partial_minimal(
    coresys: CoreSys, partial_backup_mock, install_addon_ssh
):
    """Test restoring partial Backup minimal."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)

    manager = BackupManager(coresys)

    backup_instance = partial_backup_mock.return_value
    await manager.do_restore_partial(backup_instance, homeassistant=False)

    backup_instance.restore_homeassistant.assert_not_called()
    backup_instance.restore_repositories.assert_not_called()
    backup_instance.restore_dockerconfig.assert_called_once()

    backup_instance.restore_addons.assert_not_called()

    backup_instance.restore_folders.assert_not_called()

    assert coresys.core.state == CoreState.RUNNING


async def test_do_restore_partial_maximal(coresys: CoreSys, partial_backup_mock):
    """Test restoring partial Backup minimal."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)
    coresys.homeassistant.core.stop = AsyncMock(return_value=None)
    coresys.homeassistant.core.update = AsyncMock(return_value=None)

    manager = BackupManager(coresys)

    backup_instance = partial_backup_mock.return_value
    await manager.do_restore_partial(
        backup_instance,
        addons=[TEST_ADDON_SLUG],
        folders=[FOLDER_SHARE, FOLDER_HOMEASSISTANT],
        homeassistant=True,
    )

    backup_instance.restore_homeassistant.assert_called_once()
    backup_instance.restore_repositories.assert_called_once()
    backup_instance.restore_dockerconfig.assert_called_once()

    backup_instance.restore_addons.assert_called_once()

    backup_instance.restore_folders.assert_called_once()
    backup_instance.restore_homeassistant.assert_called_once()

    assert coresys.core.state == CoreState.RUNNING


async def test_fail_invalid_full_backup(coresys: CoreSys, full_backup_mock: MagicMock):
    """Test restore fails with invalid backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    backup_instance = full_backup_mock.return_value
    backup_instance.protected = True
    backup_instance.set_password.return_value = False

    assert await manager.do_restore_full(backup_instance) is False

    backup_instance.protected = False
    backup_instance.supervisor_version = "2022.08.4"
    with patch.object(
        type(coresys.supervisor), "version", new=PropertyMock(return_value="2022.08.3")
    ):
        assert await manager.do_restore_full(backup_instance) is False


async def test_fail_invalid_partial_backup(
    coresys: CoreSys, partial_backup_mock: MagicMock
):
    """Test restore fails with invalid backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    manager = BackupManager(coresys)

    backup_instance = partial_backup_mock.return_value
    backup_instance.protected = True
    backup_instance.set_password.return_value = False

    assert await manager.do_restore_partial(backup_instance) is False

    backup_instance.protected = False
    backup_instance.homeassistant = None

    assert (
        await manager.do_restore_partial(backup_instance, homeassistant=True) is False
    )

    backup_instance.supervisor_version = "2022.08.4"
    with patch.object(
        type(coresys.supervisor), "version", new=PropertyMock(return_value="2022.08.3")
    ):
        assert await manager.do_restore_partial(backup_instance) is False


async def test_backup_error(
    coresys: CoreSys,
    backup_mock: MagicMock,
    install_addon_ssh: Addon,
    capture_exception: Mock,
):
    """Test error captured when backup fails."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_mock.return_value.store_addons.side_effect = (err := AddonsError())
    await coresys.backups.do_backup_full()

    capture_exception.assert_called_once_with(err)


async def test_restore_error(
    coresys: CoreSys, full_backup_mock: MagicMock, capture_exception: Mock
):
    """Test restoring full Backup."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.core.start = AsyncMock(return_value=None)

    backup_instance = full_backup_mock.return_value
    backup_instance.restore_dockerconfig.side_effect = (err := DockerError())
    await coresys.backups.do_restore_full(backup_instance)

    capture_exception.assert_called_once_with(err)
