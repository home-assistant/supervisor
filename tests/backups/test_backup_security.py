"""Security tests for backup tar extraction."""

import io
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory

from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys


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


def _setup_backup_for_folder_restore(
    coresys: CoreSys, tmp_path: Path
) -> tuple[Backup, Path]:
    """Set up a backup object ready for _folder_restore testing.

    Returns the backup and the path where inner tar files should be placed.
    """
    backup = Backup(coresys, tmp_path / "test.tar", "test", None)
    backup.new("Test", "2023-07-21T21:05:00.000000+00:00", BackupType.FULL)

    # Create a directory that simulates the extracted outer backup tar
    inner_dir = tmp_path / "extracted_backup"
    inner_dir.mkdir()
    backup._tmp = TemporaryDirectory()
    # Override .name to point at our controlled directory
    backup._tmp.name = str(inner_dir)

    return backup, inner_dir


async def test_absolute_symlink_in_folder_tar_skipped(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test that absolute symlinks in folder tars are skipped during restore."""
    backup, inner_dir = _setup_backup_for_folder_restore(coresys, tmp_path)

    # Create a tar.gz with an absolute symlink and a normal file
    evil_info = tarfile.TarInfo(name="evil_link")
    evil_info.type = tarfile.SYMTYPE
    evil_info.linkname = "/etc/shadow"
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    _create_tar_gz(
        inner_dir / "share.tar.gz",
        [evil_info, normal_info],
        {"normal.txt": b"hello"},
    )

    origin_dir = coresys.config.path_supervisor / "share"
    origin_dir.mkdir(parents=True, exist_ok=True)

    # Should succeed — absolute symlink is skipped, not fatal
    await backup._folder_restore("share")

    # Normal file extracted, dangerous symlink was not
    assert (origin_dir / "normal.txt").read_text() == "hello"
    assert not (origin_dir / "evil_link").exists()


async def test_relative_symlink_escape_in_folder_tar_skipped(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test that relative symlinks escaping destination are skipped."""
    backup, inner_dir = _setup_backup_for_folder_restore(coresys, tmp_path)

    # Create a tar.gz with an escaping symlink and a normal file
    evil_info = tarfile.TarInfo(name="escape_link")
    evil_info.type = tarfile.SYMTYPE
    evil_info.linkname = "../../etc/shadow"
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    _create_tar_gz(
        inner_dir / "share.tar.gz",
        [evil_info, normal_info],
        {"normal.txt": b"hello"},
    )

    origin_dir = coresys.config.path_supervisor / "share"
    origin_dir.mkdir(parents=True, exist_ok=True)

    # Should succeed — escaping symlink is skipped, not fatal
    await backup._folder_restore("share")

    assert (origin_dir / "normal.txt").read_text() == "hello"
    assert not (origin_dir / "escape_link").exists()


async def test_device_node_in_folder_tar_skipped(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test that device nodes in folder tars are skipped during restore."""
    backup, inner_dir = _setup_backup_for_folder_restore(coresys, tmp_path)

    # Create a tar.gz with a character device and a normal file
    evil_info = tarfile.TarInfo(name="evil_device")
    evil_info.type = tarfile.CHRTYPE
    evil_info.devmajor = 1
    evil_info.devminor = 5  # /dev/zero
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    _create_tar_gz(
        inner_dir / "share.tar.gz",
        [evil_info, normal_info],
        {"normal.txt": b"hello"},
    )

    origin_dir = coresys.config.path_supervisor / "share"
    origin_dir.mkdir(parents=True, exist_ok=True)

    # Should succeed — device node is skipped, not fatal
    await backup._folder_restore("share")

    assert (origin_dir / "normal.txt").read_text() == "hello"
    assert not (origin_dir / "evil_device").exists()


async def test_path_traversal_in_folder_tar_rejected(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test that path traversal entries are filtered out by secure_path."""
    backup, inner_dir = _setup_backup_for_folder_restore(coresys, tmp_path)

    # Create a tar.gz with a path traversal entry alongside a normal file
    traversal_info = tarfile.TarInfo(name="../../etc/passwd")
    traversal_info.size = 9
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    _create_tar_gz(
        inner_dir / "share.tar.gz",
        [traversal_info, normal_info],
        {"../../etc/passwd": b"malicious", "normal.txt": b"hello"},
    )

    origin_dir = coresys.config.path_supervisor / "share"
    origin_dir.mkdir(parents=True, exist_ok=True)

    # Should not raise — secure_path silently filters out the traversal entry
    await backup._folder_restore("share")

    # Normal file should be extracted
    assert (origin_dir / "normal.txt").read_text() == "hello"

    # Traversal file should NOT exist anywhere outside origin_dir
    assert not (origin_dir / "../../etc/passwd").exists()


async def test_valid_backup_with_internal_symlinks(
    coresys: CoreSys, tmp_supervisor_data: Path, tmp_path: Path
):
    """Test that valid backups with internal relative symlinks extract correctly."""
    backup, inner_dir = _setup_backup_for_folder_restore(coresys, tmp_path)

    # Create a tar.gz with a directory, a file, and an internal relative symlink
    dir_info = tarfile.TarInfo(name="subdir")
    dir_info.type = tarfile.DIRTYPE
    dir_info.mode = 0o755

    file_info = tarfile.TarInfo(name="subdir/config.yaml")
    file_info.size = 11

    link_info = tarfile.TarInfo(name="config_link")
    link_info.type = tarfile.SYMTYPE
    link_info.linkname = "subdir/config.yaml"

    _create_tar_gz(
        inner_dir / "share.tar.gz",
        [dir_info, file_info, link_info],
        {"subdir/config.yaml": b"key: value\n"},
    )

    origin_dir = coresys.config.path_supervisor / "share"
    origin_dir.mkdir(parents=True, exist_ok=True)

    await backup._folder_restore("share")

    # Verify the symlink was extracted and points to the right target
    assert (origin_dir / "subdir" / "config.yaml").read_text() == "key: value\n"
    assert (origin_dir / "config_link").is_symlink()
    assert (origin_dir / "config_link").read_text() == "key: value\n"
