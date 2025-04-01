"""Test backups."""

from contextlib import AbstractContextManager, nullcontext as does_not_raise
from os import listdir
from pathlib import Path
from shutil import copy
import tarfile
from unittest.mock import MagicMock, patch

import pytest

from supervisor.backups.backup import Backup, BackupLocation
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    BackupFileExistError,
    BackupFileNotFoundError,
    BackupInvalidError,
    BackupPermissionError,
)

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


async def test_new_backup_permission_error(coresys: CoreSys, tmp_path: Path):
    """Test if a permission error is correctly handled when a new backup is created."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    assert not listdir(tmp_path)

    with (
        patch(
            "tarfile.open",
            MagicMock(side_effect=PermissionError),
        ),
        pytest.raises(BackupPermissionError),
    ):
        async with backup.create():
            assert len(listdir(tmp_path)) == 1
            assert backup.tarfile.exists()


async def test_new_backup_exists_error(coresys: CoreSys, tmp_path: Path):
    """Test if a permission error is correctly handled when a new backup is created."""
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    backup_file.touch()

    with (
        pytest.raises(BackupFileExistError),
    ):
        async with backup.create():
            pass


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
    assert enc_backup.all_locations == {
        None: BackupLocation(path=unc_tar, protected=False, size_bytes=10240),
    }


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
        None: BackupLocation(path=enc_tar, protected=True, size_bytes=10240),
        "backup_test": BackupLocation(path=unc_tar, protected=False, size_bytes=10240),
    }


@pytest.mark.parametrize(
    (
        "tarfile_side_effect",
        "securetar_side_effect",
        "expected_exception",
    ),
    [
        (None, None, does_not_raise()),  # Successful validation
        (
            FileNotFoundError,
            None,
            pytest.raises(
                BackupFileNotFoundError,
                match=r"Cannot validate backup at [^, ]+, file does not exist!",
            ),
        ),  # File not found
        (
            None,
            tarfile.ReadError,
            pytest.raises(
                BackupInvalidError, match="Invalid password for backup 93b462f8"
            ),
        ),  # Invalid password
    ],
)
async def test_validate_backup(
    coresys: CoreSys,
    tmp_path: Path,
    tarfile_side_effect: type[Exception] | None,
    securetar_side_effect: type[Exception] | None,
    expected_exception: AbstractContextManager,
):
    """Parameterized test for validate_backup."""
    enc_tar = Path(copy(get_fixture_path("backup_example_enc.tar"), tmp_path))
    enc_backup = Backup(coresys, enc_tar, "test", None)
    await enc_backup.load()

    backup_tar_mock = MagicMock(spec_set=tarfile.TarFile)
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
                return_value=backup_context_mock,
                side_effect=tarfile_side_effect,
            ),
        ),
        patch(
            "supervisor.backups.backup.SecureTarFile",
            MagicMock(side_effect=securetar_side_effect),
        ),
        expected_exception,
    ):
        await enc_backup.validate_backup(None)
