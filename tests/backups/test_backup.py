"""Test backups."""

from contextlib import AbstractContextManager, nullcontext as does_not_raise
from os import listdir
from pathlib import Path
from shutil import copy
import tarfile
from unittest.mock import MagicMock, patch

import pytest
from securetar import AddFileError

from supervisor.addons.addon import Addon
from supervisor.backups.backup import Backup, BackupLocation
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    AddonsError,
    BackupFileExistError,
    BackupFileNotFoundError,
    BackupInvalidError,
    BackupPermissionError,
)
from supervisor.jobs import JobSchedulerOptions

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


async def test_backup_error_addon(
    coresys: CoreSys, install_addon_ssh: Addon, tmp_path: Path
):
    """Test if errors during add-on backup is correctly recorded in jobs."""
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    install_addon_ssh.backup = MagicMock(
        side_effect=(err := AddonsError("Fake add-on backup error"))
    )

    async with backup.create():
        # Validate that the add-on exception is collected in the main job
        backup_store_addons_job, backup_task = coresys.jobs.schedule_job(
            backup.store_addons, JobSchedulerOptions(), [install_addon_ssh]
        )
        await backup_task
        assert len(backup_store_addons_job.errors) == 1
        assert str(err) in backup_store_addons_job.errors[0].message

        # Check backup_addon_restore child job has the same error
        child_jobs = [
            job
            for job in coresys.jobs.jobs
            if job.parent_id == backup_store_addons_job.uuid
        ]
        assert len(child_jobs) == 1
        assert child_jobs[0].errors[0].message == str(err)


async def test_backup_error_folder(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test if errors during folder backup is correctly recorded in jobs."""
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        # Validate that the folder exception is collected in the main job
        with patch(
            "supervisor.backups.backup.atomic_contents_add",
            MagicMock(
                side_effect=(err := AddFileError(".", "Fake folder backup error"))
            ),
        ):
            backup_store_folders, backup_task = coresys.jobs.schedule_job(
                backup.store_folders, JobSchedulerOptions(), ["media"]
            )
            await backup_task
            assert len(backup_store_folders.errors) == 1
            assert str(err) in backup_store_folders.errors[0].message

            # Check backup_folder_save child job has the same error
            child_jobs = [
                job
                for job in coresys.jobs.jobs
                if job.parent_id == backup_store_folders.uuid
            ]
            assert len(child_jobs) == 1
            assert str(err) in child_jobs[0].errors[0].message


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
