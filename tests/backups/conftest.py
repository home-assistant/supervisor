"""Mock test."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supervisor.backups.const import BackupType
from supervisor.backups.validate import ALL_FOLDERS

from tests.const import TEST_ADDON_SLUG


@pytest.fixture(name="backup_mock")
def fixture_backup_mock():
    """Backup class mock."""
    with patch("supervisor.backups.manager.Backup") as backup_mock:
        backup_instance = MagicMock()
        backup_mock.return_value = backup_instance

        backup_instance.store_addons = AsyncMock(return_value=None)
        backup_instance.store_folders = AsyncMock(return_value=None)
        backup_instance.restore_addons = AsyncMock(return_value=None)
        backup_instance.restore_folders = AsyncMock(return_value=None)
        backup_instance.restore_repositories = AsyncMock(return_value=None)

        yield backup_mock


@pytest.fixture
def partial_backup_mock(backup_mock):
    """Partial backup mock."""
    backup_instance = backup_mock.return_value
    backup_instance.sys_type = BackupType.PARTIAL
    backup_instance.folders = []
    backup_instance.addon_list = [TEST_ADDON_SLUG]
    yield backup_mock


@pytest.fixture
def full_backup_mock(backup_mock):
    """Full backup mock."""
    backup_instance = backup_mock.return_value
    backup_instance.sys_type = BackupType.FULL
    backup_instance.folders = ALL_FOLDERS
    backup_instance.addon_list = [TEST_ADDON_SLUG]
    yield backup_mock
