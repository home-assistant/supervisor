"""Test backups."""

from os import listdir
from pathlib import Path
from shutil import copy
import tarfile
from unittest.mock import MagicMock, patch

import pytest

from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys
from supervisor.exceptions import BackupFileNotFoundError, BackupInvalidError

from tests.common import get_fixture_path


async def test_new_backup_stays_in_folder(coresys: CoreSys, tmp_path: Path):
    """Test making a new backup operates entirely within folder where backup will be stored."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    assert not listdir(tmp_path)

    async with backup.create():
        assert len(listdir(tmp_path)) == 1
        assert backup.tarfile.exists()

    assert len(listdir(tmp_path)) == 1
    assert backup.tarfile.exists()


async def test_consolidate_conflict_varied_encryption(
    coresys: CoreSys, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Test consolidate with two backups in same location and varied encryption."""
    enc_tar = Path(copy(get_fixture_path("test_consolidate.tar"), tmp_path))
    enc_backup = Backup(coresys, enc_tar, "test", None)
    await enc_backup.load()

    unc_tar = Path(copy(get_fixture_path("test_consolidate_unc.tar"), tmp_path))
    unc_backup = Backup(coresys, unc_tar, "test", None)
    await unc_backup.load()

    enc_backup.consolidate(unc_backup)
    assert (
        f"Backup d9c48f8b exists in two files in locations None. Ignoring {enc_tar.as_posix()}"
        in caplog.text
    )
    assert enc_backup.all_locations == {None: {"path": unc_tar, "protected": False}}


async def test_consolidate(
    coresys: CoreSys,
    tmp_path: Path,
    tmp_supervisor_data: Path,
    caplog: pytest.LogCaptureFixture,
):
    """Test consolidate with two backups in different location and varied encryption."""
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    enc_tar = Path(copy(get_fixture_path("test_consolidate.tar"), tmp_path))
    enc_backup = Backup(coresys, enc_tar, "test", None)
    await enc_backup.load()

    unc_tar = Path(copy(get_fixture_path("test_consolidate_unc.tar"), mount_dir))
    unc_backup = Backup(coresys, unc_tar, "test", "backup_test")
    await unc_backup.load()

    enc_backup.consolidate(unc_backup)
    assert (
        "Backup in backup_test and None both have slug d9c48f8b but are not the same!"
        not in caplog.text
    )
    assert enc_backup.all_locations == {
        None: {"path": enc_tar, "protected": True},
        "backup_test": {"path": unc_tar, "protected": False},
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tarfile_side_effect, securetar_side_effect, expected_exception",
    [
        (None, None, None),  # Successful validation
        (FileNotFoundError, None, BackupFileNotFoundError),  # File not found
        (None, tarfile.ReadError, BackupInvalidError),  # Invalid password
    ],
)
async def test_validate_backup(
    coresys: CoreSys,
    tmp_path: Path,
    tarfile_side_effect,
    securetar_side_effect,
    expected_exception,
):
    """Parameterized test for validate_password."""
    enc_tar = Path(copy(get_fixture_path("backup_example_enc.tar"), tmp_path))
    enc_backup = Backup(coresys, enc_tar, "test", None)
    await enc_backup.load()

    backup_tar_mock = MagicMock()
    backup_tar_mock.getmembers.return_value = [
        MagicMock(name="test.tar.gz")
    ]  # Fake tar entries
    backup_tar_mock.extractfile.return_value = MagicMock()
    backup_context_mock = MagicMock()
    backup_context_mock.__enter__.return_value = backup_tar_mock
    backup_context_mock.__exit__.return_value = False

    with (
        patch(
            "tarfile.open",
            MagicMock(
                return_value=backup_context_mock, side_effect=tarfile_side_effect
            ),
        ),
        patch(
            "supervisor.backups.backup.SecureTarFile",
            MagicMock(side_effect=securetar_side_effect),
        ),
    ):
        if expected_exception:
            with pytest.raises(expected_exception):
                await enc_backup.validate_backup(None)
        else:
            await enc_backup.validate_backup(None)
