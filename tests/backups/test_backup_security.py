"""Security tests for backup tar extraction with tar filter."""

import io
from pathlib import Path
import tarfile

import pytest
from securetar import SecureTarFile

from supervisor.backups.backup import Backup
from supervisor.coresys import CoreSys
from supervisor.exceptions import BackupInvalidError


def _create_tar_gz(
    path: Path,
    members: list[tarfile.TarInfo],
    file_data: dict[str, bytes] | None = None,
) -> None:
    """Create a tar.gz file with specified members."""
    if file_data is None:
        file_data = {}
    with tarfile.open(path, "w:gz") as tar:
        for info in members:
            data = file_data.get(info.name)
            if data is not None:
                tar.addfile(info, io.BytesIO(data))
            else:
                tar.addfile(info)


def test_path_traversal_rejected(tmp_path: Path):
    """Test that path traversal in member names is rejected."""
    traversal_info = tarfile.TarInfo(name="../../etc/passwd")
    traversal_info.size = 9
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(tar_path, [traversal_info], {"../../etc/passwd": b"malicious"})

    dest = tmp_path / "out"
    dest.mkdir()
    with (
        tarfile.open(tar_path, "r:gz") as tar,
        pytest.raises(tarfile.OutsideDestinationError),
    ):
        tar.extractall(path=dest, filter="tar")


def test_symlink_write_through_rejected(tmp_path: Path):
    """Test that writing through a symlink to outside destination is rejected.

    The tar filter's realpath check follows already-extracted symlinks on disk,
    catching write-through attacks even without explicit link target validation.
    """
    # Symlink pointing outside, then a file entry writing through it
    link_info = tarfile.TarInfo(name="escape")
    link_info.type = tarfile.SYMTYPE
    link_info.linkname = "../outside"
    file_info = tarfile.TarInfo(name="escape/evil.py")
    file_info.size = 9
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(
        tar_path,
        [link_info, file_info],
        {"escape/evil.py": b"malicious"},
    )

    dest = tmp_path / "out"
    dest.mkdir()
    with (
        tarfile.open(tar_path, "r:gz") as tar,
        pytest.raises(tarfile.OutsideDestinationError),
    ):
        tar.extractall(path=dest, filter="tar")

    # The evil file must not exist outside the destination
    assert not (tmp_path / "outside" / "evil.py").exists()


def test_absolute_name_stripped_and_extracted(tmp_path: Path):
    """Test that absolute member names have leading / stripped and extract safely."""
    info = tarfile.TarInfo(name="/etc/test.conf")
    info.size = 5
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(tar_path, [info], {"/etc/test.conf": b"hello"})

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest, filter="tar")

    # Extracted inside destination with leading / stripped
    assert (dest / "etc" / "test.conf").read_text() == "hello"


def test_valid_backup_with_internal_symlinks(tmp_path: Path):
    """Test that valid backups with internal relative symlinks extract correctly."""
    dir_info = tarfile.TarInfo(name="subdir")
    dir_info.type = tarfile.DIRTYPE
    dir_info.mode = 0o755

    file_info = tarfile.TarInfo(name="subdir/config.yaml")
    file_info.size = 11

    link_info = tarfile.TarInfo(name="config_link")
    link_info.type = tarfile.SYMTYPE
    link_info.linkname = "subdir/config.yaml"

    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(
        tar_path,
        [dir_info, file_info, link_info],
        {"subdir/config.yaml": b"key: value\n"},
    )

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest, filter="tar")

    assert (dest / "subdir" / "config.yaml").read_text() == "key: value\n"
    assert (dest / "config_link").is_symlink()
    assert (dest / "config_link").read_text() == "key: value\n"


def test_uid_gid_preserved(tmp_path: Path):
    """Test that tar filter preserves file ownership."""
    info = tarfile.TarInfo(name="owned_file.txt")
    info.size = 5
    info.uid = 1000
    info.gid = 1000
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(tar_path, [info], {"owned_file.txt": b"hello"})

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        # Extract member via filter only (don't actually extract, just check
        # the filter preserves uid/gid)
        for member in tar:
            filtered = tarfile.tar_filter(member, str(dest))
            assert filtered.uid == 1000
            assert filtered.gid == 1000


async def test_backup_open_rejects_path_traversal(coresys: CoreSys, tmp_path: Path):
    """Test that Backup.open() raises BackupInvalidError for path traversal."""
    tar_path = tmp_path / "malicious.tar"
    traversal_info = tarfile.TarInfo(name="../../etc/passwd")
    traversal_info.size = 9
    with tarfile.open(tar_path, "w:") as tar:
        tar.addfile(traversal_info, io.BytesIO(b"malicious"))

    backup = Backup(coresys, tar_path, "test", None)
    with pytest.raises(BackupInvalidError):
        async with backup.open(None):
            pass


async def test_homeassistant_restore_rejects_path_traversal(
    coresys: CoreSys, tmp_supervisor_data: Path
):
    """Test that Home Assistant restore raises BackupInvalidError for path traversal."""
    tar_path = tmp_supervisor_data / "homeassistant.tar.gz"
    traversal_info = tarfile.TarInfo(name="../../etc/passwd")
    traversal_info.size = 9
    _create_tar_gz(tar_path, [traversal_info], {"../../etc/passwd": b"malicious"})

    tar_file = SecureTarFile(tar_path, "r", gzip=True)
    with pytest.raises(BackupInvalidError):
        await coresys.homeassistant.restore(tar_file)
