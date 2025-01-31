"""Test backups."""

from os import listdir
from pathlib import Path
from shutil import copy

import pytest

from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys

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
        f"Backup in backup_test and None both have slug d9c48f8b but are not the same!"
        not in caplog.text
    )
    assert enc_backup.all_locations == {
        None: {"path": enc_tar, "protected": True},
        "backup_test": {"path": unc_tar, "protected": False},
    }
