"""Test backups."""

import asyncio
from contextlib import AbstractContextManager, nullcontext as does_not_raise
import errno
import io
import json
import os
from pathlib import Path
from shutil import copy
import tarfile
import threading
from typing import Any
from unittest.mock import MagicMock, PropertyMock, patch
import zlib

import pytest
from securetar import (
    AddFileError,
    InvalidPasswordError,
    SecureTarFile,
    SecureTarReadError,
)
import voluptuous as vol

from supervisor.apps.app import App
from supervisor.backups.backup import Backup, BackupLocation
from supervisor.backups.const import BUF_SIZE, STREAM_BUF_SIZE, BackupType
from supervisor.config import CoreConfig
from supervisor.const import FOLDER_ADDONS, Folder
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    AppsError,
    BackupError,
    BackupFatalIOError,
    BackupFileExistError,
    BackupFileNotFoundError,
    BackupInvalidError,
    BackupPermissionError,
)
from supervisor.jobs import JobSchedulerOptions
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import UnhealthyReason
from supervisor.utils import remove_folder

from tests.common import get_fixture_path


def _rename_outer_member(backup_file: Path, old_name: str, new_name: str) -> None:
    """Rewrite the outer backup tar with one member renamed."""
    tmp_file = backup_file.with_suffix(".tmp")
    with (
        tarfile.open(backup_file, "r:") as src,
        tarfile.open(tmp_file, "w:") as dst,
    ):
        for member in src.getmembers():
            if Path(member.name).name == old_name:
                member.name = new_name
            dst.addfile(member, src.extractfile(member))
    tmp_file.replace(backup_file)


async def test_new_backup_stays_in_folder(coresys: CoreSys, tmp_path: Path):
    """Test making a new backup operates entirely within folder where backup will be stored."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    assert not list(tmp_path.iterdir())

    async with backup.create():
        assert len(list(tmp_path.iterdir())) == 1
        assert backup.tarfile.exists()

    assert len(list(tmp_path.iterdir())) == 1
    assert backup.tarfile.exists()


async def test_new_backup_permission_error(coresys: CoreSys, tmp_path: Path):
    """Test if a permission error is correctly handled when a new backup is created."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    assert not list(tmp_path.iterdir())

    with (
        patch(
            "tarfile.open",
            MagicMock(side_effect=PermissionError),
        ),
        pytest.raises(BackupPermissionError),
    ):
        async with backup.create():
            pass

    assert not list(tmp_path.iterdir())
    assert not backup.tarfile.exists()


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


async def test_backup_error_app(coresys: CoreSys, install_app_ssh: App, tmp_path: Path):
    """Test if errors during app backup is correctly recorded in jobs."""
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    install_app_ssh.backup = MagicMock(
        side_effect=(err := AppsError("Fake app backup error"))
    )

    async with backup.create():
        # Validate that the app exception is collected in the main job
        backup_store_apps_job, backup_task = await coresys.jobs.schedule_job(
            backup.store_apps, JobSchedulerOptions(), [install_app_ssh]
        )
        await backup_task
        assert len(backup_store_apps_job.errors) == 1
        assert str(err) in backup_store_apps_job.errors[0].message

        # Check backup_addon_restore child job has the same error
        child_jobs = [
            job
            for job in coresys.jobs.jobs
            if job.parent_id == backup_store_apps_job.uuid
        ]
        assert len(child_jobs) == 1
        assert child_jobs[0].errors[0].message == str(err)


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_backup_folder_addons_local_maps_to_apps_local(
    coresys: CoreSys, tmp_path: Path
):
    """Test restoring a legacy addons/local backup archive as apps/local.

    Backups created before the addons/local -> apps/local rename archived
    this folder under the legacy "addons_local" slug. Schema validation
    normalizes "addons/local" to Folder.APPS ("apps/local") in the backup
    metadata on load, but the on-disk archive keeps the legacy slug name.
    Restore must fall back to that legacy archive name.
    """
    apps_local = tmp_path / "apps_local"
    apps_local.mkdir()
    (apps_local / "test_app").mkdir()
    (apps_local / "test_app" / "config.yaml").write_text("name: Test App")

    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    with patch.object(
        CoreConfig, "path_apps_local", new=PropertyMock(return_value=apps_local)
    ):
        async with backup.create():
            await backup.store_folders([Folder.APPS])

        # Simulate a fresh system: remove the on-disk folder before restoring
        await coresys.run_in_executor(remove_folder, apps_local, True)
        assert not list(apps_local.iterdir())

        # Simulate a pre-migration backup: archived under the legacy slug.
        ext = ".tar.gz" if backup.compressed else ".tar"
        _rename_outer_member(
            backup_file, f"apps_local{ext}", f"{FOLDER_ADDONS.replace('/', '_')}{ext}"
        )

        async with backup.open(None):
            await backup.restore_folders([Folder.APPS])

        restored_config = apps_local / "test_app" / "config.yaml"
        assert restored_config.is_file()
        assert restored_config.read_text() == "name: Test App"


async def test_backup_folder_apps_local(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test backup/restore of Folder.APPS uses the apps/local on-disk path."""
    apps_local = tmp_path / "apps_local"
    apps_local.mkdir()
    (apps_local / "test_app").mkdir()
    (apps_local / "test_app" / "config.yaml").write_text("name: Test App")

    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    with patch.object(
        CoreConfig, "path_apps_local", new=PropertyMock(return_value=apps_local)
    ):
        async with backup.create():
            await backup.store_folders([Folder.APPS])

        assert Folder.APPS in backup.folders

        # Simulate a fresh system: remove the on-disk folder before restoring
        await coresys.run_in_executor(remove_folder, apps_local, True)
        assert not list(apps_local.iterdir())

        async with backup.open(None):
            await backup.restore_folders([Folder.APPS])

        restored_config = apps_local / "test_app" / "config.yaml"
        assert restored_config.is_file()
        assert restored_config.read_text() == "name: Test App"


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
            backup_store_folders, backup_task = await coresys.jobs.schedule_job(
                backup.store_folders, JobSchedulerOptions(), [Folder.MEDIA]
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


async def test_backup_oserror_folder_propagates(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test that OSError during folder backup propagates out of create().

    Write-side OSError (e.g. ENOSPC) means the outer tar is corrupt. It is
    wrapped as BackupFatalIOError which store_folders does not swallow, so it
    propagates out of create() and the caller deletes the incomplete backup.
    """
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    with (
        patch(
            "supervisor.backups.backup.atomic_contents_add",
            MagicMock(side_effect=OSError(28, "No space left on device")),
        ),
        pytest.raises(BackupFatalIOError),
    ):
        async with backup.create():
            await backup.store_folders([Folder.MEDIA])


async def test_backup_fatal_error_app_propagates(
    coresys: CoreSys, install_app_ssh: App, tmp_path: Path
):
    """Test that BackupFatalIOError during app backup propagates out of store_addons.

    store_addons swallows BackupError for individual app failures, but
    BackupFatalIOError must not be swallowed since it indicates a corrupt tar.
    """
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    install_app_ssh.backup = MagicMock(side_effect=BackupFatalIOError("Disk full"))

    with pytest.raises(BackupFatalIOError):
        async with backup.create():
            await backup.store_apps([install_app_ssh])


async def test_backup_oserror_close_suppressed_on_error(
    coresys: CoreSys, tmp_path: Path
):
    """Test that a secondary OSError from close is suppressed on error path.

    When an exception already occurred during yield, create() should not raise
    a secondary exception from closing the tar file.
    """
    backup_file = tmp_path / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    with pytest.raises(ValueError, match="test error"):
        async with backup.create():
            raise ValueError("test error")


@pytest.mark.parametrize(
    ("target", "side_effect", "expected"),
    [
        pytest.param(
            "supervisor.backups.backup.json_bytes",
            OSError(errno.ENOSPC, "No space left on device"),
            BackupFatalIOError,
            id="enospc_writing_metadata",
        ),
        pytest.param(
            "supervisor.backups.backup.json_bytes",
            TypeError("Type is not JSON serializable"),
            TypeError,
            id="encode_error",
        ),
        pytest.param(
            "supervisor.backups.backup.SCHEMA_BACKUP",
            vol.Invalid("invalid"),
            ValueError,
            id="invalid_metadata",
        ),
    ],
)
async def test_backup_finalize_error_closes_tar(
    coresys: CoreSys,
    tmp_path: Path,
    target: str,
    side_effect: Exception,
    expected: type[Exception],
):
    """Test the outer tar is closed when finalizing the backup fails."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    with patch(target, side_effect=side_effect), pytest.raises(expected):
        async with backup.create():
            # pylint: disable-next=protected-access
            outer_tar = backup._outer_secure_tarfile.tar

    assert outer_tar.closed
    assert outer_tar.fileobj.closed


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


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_consolidate_failure(coresys: CoreSys, tmp_path: Path):
    """Test consolidate with two backups that are not the same."""
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    tar1 = Path(copy(get_fixture_path("test_consolidate_unc.tar"), tmp_path))
    backup1 = Backup(coresys, tar1, "test", None)
    await backup1.load()

    tar2 = Path(copy(get_fixture_path("backup_example.tar"), mount_dir))
    backup2 = Backup(coresys, tar2, "test", "backup_test")
    await backup2.load()

    with pytest.raises(
        ValueError,
        match=f"Backup {backup1.slug} and {backup2.slug} are not the same backup",
    ):
        backup1.consolidate(backup2)

    # Force slugs to be the same to run the fields check
    backup1._data["slug"] = backup2.slug  # pylint: disable=protected-access
    with pytest.raises(
        BackupInvalidError,
        match=f"Cannot consolidate backups in {backup2.location} and {backup1.location} with slug {backup1.slug}",
    ):
        backup1.consolidate(backup2)


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
        ),  # Invalid password (legacy securetar exception)
        (
            None,
            SecureTarReadError,
            pytest.raises(
                BackupInvalidError, match="Invalid password for backup 93b462f8"
            ),
        ),  # Invalid password (securetar >= 2026.2.0 raises SecureTarReadError)
        (
            None,
            InvalidPasswordError,
            pytest.raises(
                BackupInvalidError, match="Invalid password for backup 93b462f8"
            ),
        ),  # Invalid password (securetar >= 2026.2.0 with v3 backup raises InvalidPasswordError)
    ],
)
async def test_validate_backup(
    coresys: CoreSys,
    tmp_path: Path,
    tarfile_side_effect: type[Exception] | None,
    securetar_side_effect: type[Exception] | None,
    expected_exception: AbstractContextManager,
):
    """Parameterized test for validate_backup.

    Note that it is paramount that BackupInvalidError is raised for invalid password
    cases, as this is used by the Core to determine if a backup password is invalid
    and offer a input field to the user to input the correct password.
    """
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


@pytest.mark.parametrize(
    ("password", "expected_exception"),
    [
        ("supervisor", does_not_raise()),
        (
            "wrong_password",
            pytest.raises(
                BackupInvalidError, match="Invalid password for backup f92f0339"
            ),
        ),
        (
            None,
            pytest.raises(
                BackupInvalidError, match="Invalid password for backup f92f0339"
            ),
        ),
        (
            "",
            pytest.raises(
                BackupInvalidError, match="Invalid password for backup f92f0339"
            ),
        ),
    ],
)
async def test_validate_backup_v3(
    coresys: CoreSys,
    tmp_path: Path,
    password: str | None,
    expected_exception: AbstractContextManager,
):
    """Test validate_backup with a real SecureTar v3 encrypted backup.

    SecureTar v3 uses Argon2id key derivation and raises InvalidPasswordError
    on wrong passwords. It is paramount that BackupInvalidError is raised for
    invalid password cases, as this is used by the Core to determine if a backup
    password is invalid and offer a dialog to the user to input the correct
    password.
    """
    v3_tar = Path(copy(get_fixture_path("backup_example_sec_v3.tar"), tmp_path))
    v3_backup = Backup(coresys, v3_tar, "test", None)
    await v3_backup.load()
    v3_backup.set_password(password)

    with expected_exception:
        await v3_backup.validate_backup(None)


@pytest.mark.parametrize(
    ("password", "expect_protected"),
    [
        ("my_password", True),
        (None, False),
        ("", False),
    ],
)
async def test_new_backup_empty_password_not_protected(
    coresys: CoreSys,
    tmp_path: Path,
    password: str | None,
    expect_protected: bool,
):
    """Test that empty string password is treated as no password on backup creation."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new(
        "test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL, password=password
    )
    assert backup.protected is expect_protected


@pytest.mark.parametrize(
    ("password", "expected_password"),
    [
        ("my_password", "my_password"),
        (None, None),
        ("", None),
    ],
)
def test_set_password_empty_string_is_none(
    coresys: CoreSys,
    tmp_path: Path,
    password: str | None,
    expected_password: str | None,
):
    """Test that set_password treats empty string as None."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.set_password(password)
    assert backup._password == expected_password  # pylint: disable=protected-access


@pytest.mark.parametrize(
    ("password", "expected_bufsize"),
    [
        pytest.param(None, BUF_SIZE, id="unprotected"),
        pytest.param("backup_password", STREAM_BUF_SIZE, id="protected"),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_restore_folder_bufsize(
    coresys: CoreSys,
    tmp_path: Path,
    password: str | None,
    expected_bufsize: int,
):
    """Test encrypted tars are restored with a small buffer, plain ones with a large one."""
    test_file = coresys.config.path_media / "test.txt"
    test_file.write_text("backup content")

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new(
        "test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL, password=password
    )
    async with backup.create():
        await backup.store_folders([Folder.MEDIA])

    test_file.unlink()
    async with backup.open(None):
        with patch(
            "supervisor.backups.backup.SecureTarFile", wraps=SecureTarFile
        ) as secure_tar_mock:
            assert await backup.restore_folders([Folder.MEDIA])

    assert secure_tar_mock.call_args.kwargs["bufsize"] == expected_bufsize
    assert test_file.read_text() == "backup content"


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_restore_encrypted_zero_file_bounded_decompression(
    coresys: CoreSys, tmp_path: Path
):
    """Test restoring a highly compressible encrypted file keeps decompressed chunks small.

    In tar stream mode each input buffer is decompressed in one go, so a large
    buffer of compressed zeros expands to the whole file at once.
    """
    size = 32 * 1024 * 1024
    test_file = coresys.config.path_media / "zeros.bin"
    test_file.write_bytes(bytes(size))

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new(
        "test",
        "2023-07-21T21:05:00.000000+00:00",
        BackupType.FULL,
        password="backup_password",
    )
    async with backup.create():
        await backup.store_folders([Folder.MEDIA])

    max_chunk = 0
    decompressobj = zlib.decompressobj

    class RecordingDecompressor:
        def __init__(self, *args: Any) -> None:
            self._obj = decompressobj(*args)

        def decompress(self, data: bytes, *args: Any) -> bytes:
            nonlocal max_chunk
            out = self._obj.decompress(data, *args)
            max_chunk = max(max_chunk, len(out))
            return out

        def __getattr__(self, name: str) -> Any:
            return getattr(self._obj, name)

    test_file.unlink()
    async with backup.open(None):
        with patch("zlib.decompressobj", RecordingDecompressor):
            assert await backup.restore_folders([Folder.MEDIA])

    assert test_file.stat().st_size == size
    assert max_chunk < size // 2


async def test_store_supervisor_config_nothing_to_backup(
    coresys: CoreSys, tmp_path: Path
):
    """Test storing supervisor config when no mounts or registries configured."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    # Create backup context to enable store_supervisor_config
    async with backup.create():
        # Store config (should do nothing when nothing to back up)
        await backup.store_supervisor_config()


async def test_store_supervisor_config_with_mounts(coresys: CoreSys, tmp_path: Path):
    """Test storing supervisor config when mounts are configured."""
    # Add a test mount directly to manager state (avoids needing dbus)
    mount = Mount.from_dict(
        coresys,
        {
            "name": "test_backup_share",
            "usage": "backup",
            "type": "cifs",
            "server": "192.168.1.100",
            "share": "backup_share",
        },
    )
    coresys.mounts._mounts[mount.name] = mount  # noqa: SLF001  # pylint: disable=protected-access

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    # Create backup context and store supervisor config
    async with backup.create():
        await backup.store_supervisor_config()


async def test_store_supervisor_config_with_registries(
    coresys: CoreSys, tmp_path: Path
):
    """Test storing supervisor config when docker registries are configured."""
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        await backup.store_supervisor_config()


async def test_store_supervisor_config_with_mounts_and_registries(
    coresys: CoreSys, tmp_path: Path
):
    """Test storing supervisor config with both mounts and registries."""
    mount = Mount.from_dict(
        coresys,
        {
            "name": "test_share",
            "usage": "backup",
            "type": "cifs",
            "server": "192.168.1.100",
            "share": "backup_share",
        },
    )
    coresys.mounts._mounts[mount.name] = mount  # noqa: SLF001  # pylint: disable=protected-access
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        await backup.store_supervisor_config()


async def test_restore_supervisor_config_no_tar(coresys: CoreSys, tmp_path: Path):
    """Test restoring supervisor config when backup has no supervisor tar."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    # Create the backup (no mounts or registries, so no supervisor.tar inside)
    async with backup.create():
        pass

    # Open and restore - should succeed with nothing to do
    async with backup.open(None):
        success, tasks = await backup.restore_supervisor_config()
        assert success is True
        assert tasks == []


async def test_restore_supervisor_config_with_registries(
    coresys: CoreSys, tmp_path: Path
):
    """Test restoring docker registries from supervisor config in backup."""
    # Configure registries and create a backup
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }
    coresys.docker.config.registries["docker.io"] = {
        "username": "docker_user",
        "password": "docker_pass",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        await backup.store_supervisor_config()

    # Clear registries
    coresys.docker.config.registries.clear()
    assert not coresys.docker.config.registries

    # Restore from backup
    async with backup.open(None):
        success, tasks = await backup.restore_supervisor_config()
        assert success is True
        assert tasks == []

    # Verify registries were restored
    assert "ghcr.io" in coresys.docker.config.registries
    assert coresys.docker.config.registries["ghcr.io"]["username"] == "user"
    assert coresys.docker.config.registries["ghcr.io"]["password"] == "secret"
    assert "docker.io" in coresys.docker.config.registries
    assert coresys.docker.config.registries["docker.io"]["username"] == "docker_user"


@pytest.mark.parametrize("password", [None, "backup_password"])
async def test_restore_supervisor_config_with_mounts_and_registries(
    coresys: CoreSys, tmp_path: Path, password: str | None
):
    """Test restoring mounts and registries, with and without a backup password.

    Encrypted inner tars are read in streaming mode, so the supervisor tar
    must be read sequentially. Regression test for #7213.
    """
    mount = Mount.from_dict(
        coresys,
        {
            "name": "test_share",
            "usage": "backup",
            "type": "cifs",
            "server": "192.168.1.100",
            "share": "backup_share",
        },
    )
    coresys.mounts._mounts[mount.name] = mount  # noqa: SLF001  # pylint: disable=protected-access
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new(
        "test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL, password=password
    )

    async with backup.create():
        await backup.store_supervisor_config()

    coresys.mounts._mounts.clear()  # noqa: SLF001  # pylint: disable=protected-access
    coresys.docker.config.registries.clear()

    mount_task = MagicMock()
    with patch.object(
        coresys.mounts, "restore_mount", return_value=mount_task
    ) as restore_mount:
        async with backup.open(None):
            success, tasks = await backup.restore_supervisor_config()

    assert success is True
    assert tasks == [mount_task]
    assert restore_mount.call_args[0][0].name == "test_share"
    assert coresys.docker.config.registries["ghcr.io"]["username"] == "user"


@pytest.mark.parametrize("present", ["mounts.json", "docker.json"])
async def test_restore_supervisor_config_single_file(
    coresys: CoreSys, tmp_path: Path, present: str
):
    """Test restoring an encrypted supervisor tar with only one of the JSON files.

    Backups from Supervisor 2026.03.x have no docker.json. Unknown and
    non-file members are skipped.
    """
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new(
        "test",
        "2023-07-21T21:05:00.000000+00:00",
        BackupType.FULL,
        password="backup_password",
    )

    if present == "mounts.json":
        content = {
            "mounts": [
                {
                    "name": "test_share",
                    "usage": "backup",
                    "type": "cifs",
                    "server": "192.168.1.100",
                    "share": "backup_share",
                }
            ]
        }
    else:
        content = {"registries": {"ghcr.io": {"username": "user", "password": "pw"}}}
    content_json = json.dumps(content).encode("utf-8")

    def _write_supervisor_tar() -> None:
        with backup._outer_secure_tarfile.create_tar(  # noqa: SLF001  # pylint: disable=protected-access
            "./supervisor.tar.gz", gzip=True
        ) as tar_file:
            tarinfo = tarfile.TarInfo(name="unknown.json")
            tarinfo.size = len(b"{}")
            tar_file.addfile(tarinfo, io.BytesIO(b"{}"))
            tarinfo = tarfile.TarInfo(name="some_dir")
            tarinfo.type = tarfile.DIRTYPE
            tar_file.addfile(tarinfo)
            tarinfo = tarfile.TarInfo(name=present)
            tarinfo.size = len(content_json)
            tar_file.addfile(tarinfo, io.BytesIO(content_json))

    async with backup.create():
        await coresys.run_in_executor(_write_supervisor_tar)

    mount_task = MagicMock()
    with patch.object(
        coresys.mounts, "restore_mount", return_value=mount_task
    ) as restore_mount:
        async with backup.open(None):
            success, tasks = await backup.restore_supervisor_config()

    assert success is True
    if present == "mounts.json":
        assert tasks == [mount_task]
        assert restore_mount.call_args[0][0].name == "test_share"
        assert not coresys.docker.config.registries
    else:
        assert tasks == []
        restore_mount.assert_not_called()
        assert coresys.docker.config.registries["ghcr.io"]["username"] == "user"


async def test_restore_supervisor_config_registries_merge(
    coresys: CoreSys, tmp_path: Path
):
    """Test that restored registries merge with existing ones."""
    # Set up a registry that will be in the backup
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "ghcr_user",
        "password": "ghcr_pass",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        await backup.store_supervisor_config()

    # Clear backup registry, add a different one
    coresys.docker.config.registries.clear()
    coresys.docker.config.registries["docker.io"] = {
        "username": "hub_user",
        "password": "hub_pass",
    }

    # Restore - should merge backup registries with existing
    async with backup.open(None):
        success, tasks = await backup.restore_supervisor_config()
        assert success is True
        assert tasks == []

    # Both registries should exist
    assert "ghcr.io" in coresys.docker.config.registries
    assert "docker.io" in coresys.docker.config.registries
    assert coresys.docker.config.registries["ghcr.io"]["username"] == "ghcr_user"


async def test_restore_supervisor_config_invalid_docker_data(
    coresys: CoreSys, tmp_path: Path
):
    """Test restore with invalid docker.json reports failure but doesn't crash."""
    # Create a backup with valid registries
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        await backup.store_supervisor_config()

    # Patch the executor to return invalid docker data
    original_run = coresys.run_in_executor

    async def _patched_run(func, *args, **kwargs):
        result = await original_run(func, *args, **kwargs)
        if isinstance(result, tuple) and len(result) == 2:
            # Return mounts_data unchanged, but corrupt docker_data
            return (result[0], {"registries": {"bad": "not_a_valid_registry"}})
        return result

    coresys.docker.config.registries.clear()

    async with backup.open(None):
        with patch.object(coresys, "run_in_executor", side_effect=_patched_run):
            success, tasks = await backup.restore_supervisor_config()
            assert success is False
            assert tasks == []

    # No registries should have been restored
    assert not coresys.docker.config.registries


async def test_store_supervisor_config_tar_error(coresys: CoreSys, tmp_path: Path):
    """Test store_supervisor_config handles tar errors."""
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        with (
            patch.object(
                coresys, "run_in_executor", side_effect=tarfile.TarError("test error")
            ),
            pytest.raises(BackupError, match="Can't write supervisor config tarfile"),
        ):
            await backup.store_supervisor_config()


async def test_restore_supervisor_config_tar_read_error(
    coresys: CoreSys, tmp_path: Path
):
    """Test restore handles tar read errors gracefully."""
    # Create a backup with registries so supervisor.tar exists
    coresys.docker.config.registries["ghcr.io"] = {
        "username": "user",
        "password": "secret",
    }

    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    async with backup.create():
        await backup.store_supervisor_config()

    async with backup.open(None):
        with patch.object(
            coresys,
            "run_in_executor",
            side_effect=tarfile.TarError("corrupted tar"),
        ):
            success, tasks = await backup.restore_supervisor_config()
            assert success is False
            assert tasks == []


@pytest.mark.parametrize(
    ("password", "compressed", "member_name"),
    [
        pytest.param(None, True, "ssl.tar.gz", id="unencrypted"),
        pytest.param("password", True, "ssl.tar.gz", id="encrypted"),
        pytest.param(None, False, "ssl.tar", id="uncompressed"),
        pytest.param("password", False, "ssl.tar", id="encrypted_uncompressed"),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_partial_restore_reads_only_requested_member(
    coresys: CoreSys,
    tmp_path: Path,
    password: str | None,
    compressed: bool,
    member_name: str,
):
    """Test a partial restore reads only the requested inner tar in place."""
    (coresys.config.path_ssl / "cert.pem").write_text("ssl")
    (coresys.config.path_share / "data.txt").write_text("share")

    backup_dir = tmp_path / "backup_location"
    backup_dir.mkdir()
    backup_file = backup_dir / "my_backup.tar"
    backup = Backup(coresys, backup_file, "test", None)
    backup.new(
        "test",
        "2023-07-21T21:05:00.000000+00:00",
        BackupType.PARTIAL,
        password=password,
        compressed=compressed,
    )
    async with backup.create():
        await backup.store_folders([Folder.SSL, Folder.SHARE])

    (coresys.config.path_ssl / "cert.pem").unlink()
    (coresys.config.path_share / "data.txt").write_text("changed")

    with (
        patch.object(
            tarfile.TarFile,
            "extractfile",
            autospec=True,
            side_effect=tarfile.TarFile.extractfile,
        ) as extractfile,
        patch.object(
            tarfile.TarFile,
            "extractall",
            autospec=True,
            side_effect=tarfile.TarFile.extractall,
        ) as extractall,
    ):
        async with backup.open(None):
            assert await backup.restore_folders([Folder.SSL]) is True
            assert list(backup_dir.iterdir()) == [backup_file]

    assert [call.args[1].name for call in extractfile.call_args_list] == [member_name]
    assert [call.kwargs["path"] for call in extractall.call_args_list] == [
        coresys.config.path_ssl
    ]
    assert (coresys.config.path_ssl / "cert.pem").read_text() == "ssl"
    assert (coresys.config.path_share / "data.txt").read_text() == "changed"
    assert list(backup_dir.iterdir()) == [backup_file]


@pytest.mark.parametrize(
    ("fixture", "password"),
    [
        pytest.param("test_consolidate.tar", "test", id="encrypted"),
        pytest.param("test_consolidate_unc.tar", None, id="unencrypted"),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_restore_folder_from_fixture(
    coresys: CoreSys, tmp_path: Path, fixture: str, password: str | None
):
    """Test restoring a folder from backups whose members lack the ./ prefix."""
    backup_dir = tmp_path / "backup_location"
    backup_dir.mkdir()
    backup_file = Path(copy(get_fixture_path(fixture), backup_dir))
    backup = Backup(coresys, backup_file, "test", None)
    assert await backup.load()
    backup.set_password(password)

    (test_file := coresys.config.path_ssl / "test.txt").touch()
    async with backup.open(None):
        assert await backup.restore_folders([Folder.SSL]) is True
        assert list(backup_dir.iterdir()) == [backup_file]

    assert not test_file.exists()


async def test_open_closes_backup_file_on_error(coresys: CoreSys, tmp_path: Path):
    """Test the backup file is closed when restore fails."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    async with backup.create():
        pass

    outer_tars: list[tarfile.TarFile] = []

    # pylint: disable=protected-access
    async def _failing_restore() -> None:
        async with backup.open(None):
            outer_tars.append(backup._restore_tar)
            raise BackupError("restore failed")

    with pytest.raises(BackupError, match="restore failed"):
        await _failing_restore()

    assert outer_tars[0].closed
    assert backup._restore_tar is None


@pytest.mark.parametrize(
    ("error_num", "unhealthy"),
    [
        pytest.param(errno.EIO, False, id="io_error"),
        pytest.param(errno.EBADMSG, True, id="bad_message"),
    ],
)
async def test_open_closes_backup_file_on_index_oserror(
    coresys: CoreSys, tmp_path: Path, error_num: int, unhealthy: bool
):
    """Test the backup file is closed when reading its member index fails."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)
    async with backup.create():
        pass

    outer_tars: list[tarfile.TarFile] = []
    tarfile_open = tarfile.open

    def _record_open(*args: Any, **kwargs: Any) -> tarfile.TarFile:
        outer_tars.append(tar := tarfile_open(*args, **kwargs))
        return tar

    with (
        patch("supervisor.backups.backup.tarfile.open", side_effect=_record_open),
        patch.object(
            tarfile.TarFile, "getmembers", side_effect=OSError(error_num, "error")
        ),
        pytest.raises(BackupError, match="Can't read backup tarfile"),
    ):
        async with backup.open(None):
            pass

    assert outer_tars[0].closed
    assert backup._restore_tar is None  # pylint: disable=protected-access
    assert (
        UnhealthyReason.OSERROR_BAD_MESSAGE in coresys.resolution.unhealthy
    ) is unhealthy


async def test_restore_homeassistant_missing_in_backup(
    coresys: CoreSys, tmp_path: Path
):
    """Test restoring Home Assistant from a backup without it fails before stopping Core."""
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.PARTIAL)
    async with backup.create():
        pass

    with (
        patch.object(coresys.homeassistant.core, "stop") as stop,
        pytest.raises(BackupInvalidError, match="Can't find Home Assistant Core"),
    ):
        async with backup.open(None):
            await backup.restore_homeassistant()

    stop.assert_not_called()


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_open_close_after_cancelled_restore(coresys: CoreSys, tmp_path: Path):
    """Test closing the backup after a cancelled restore fails the stale reader.

    Cancelling the restore does not stop the executor thread extracting an
    inner tar. Closing the outer tar must not let that thread read past the
    close; it fails with ValueError on its next read instead.
    """
    # Larger than any read buffer so the reader must touch the file after close
    (coresys.config.path_ssl / "cert.pem").write_bytes(os.urandom(8 * 2**20))
    backup = Backup(coresys, tmp_path / "my_backup.tar", "test", None)
    backup.new("test", "2023-07-21T21:05:00.000000+00:00", BackupType.PARTIAL)
    async with backup.create():
        await backup.store_folders([Folder.SSL])

    reader_started = threading.Event()
    release_reader = threading.Event()
    reader_done = threading.Event()
    reader_errors: list[BaseException] = []
    extractall = tarfile.TarFile.extractall

    def _blocking_extractall(self: tarfile.TarFile, *args: Any, **kwargs: Any) -> None:
        reader_started.set()
        release_reader.wait(5)
        try:
            extractall(self, *args, **kwargs)
        except BaseException as err:
            reader_errors.append(err)
            raise
        finally:
            reader_done.set()

    async def _restore() -> None:
        async with backup.open(None):
            await backup.restore_folders([Folder.SSL])

    # pylint: disable=protected-access
    with patch.object(
        tarfile.TarFile, "extractall", autospec=True, side_effect=_blocking_extractall
    ):
        restore_task = asyncio.create_task(_restore())
        assert await coresys.run_in_executor(reader_started.wait, 5)
        outer_tar = backup._restore_tar
        restore_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await restore_task

        assert outer_tar.closed
        assert backup._restore_tar is None

        release_reader.set()
        assert await coresys.run_in_executor(reader_done.wait, 5)

    assert len(reader_errors) == 1
    assert isinstance(reader_errors[0], ValueError)
