"""Test backups."""

from os import listdir
from pathlib import Path

from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys


async def test_new_backup_stays_in_folder(coresys: CoreSys, tmp_path: Path):
    """Test making a new backup operates entirely within folder where backup will be stored."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test")
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    assert not listdir(tmp_path)

    async with backup:
        assert len(listdir(tmp_path)) == 1
        assert not backup.tarfile.exists()

    assert len(listdir(tmp_path)) == 1
    assert backup.tarfile.exists()
