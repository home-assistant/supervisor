"""Security tests for backup_data_filter."""

import io
from pathlib import Path
import tarfile

from supervisor.backups.utils import backup_data_filter


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


def test_absolute_symlink_skipped(tmp_path: Path):
    """Test that absolute symlinks are skipped during extraction."""
    evil_info = tarfile.TarInfo(name="evil_link")
    evil_info.type = tarfile.SYMTYPE
    evil_info.linkname = "/etc/shadow"
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(tar_path, [evil_info, normal_info], {"normal.txt": b"hello"})

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest, filter=backup_data_filter)

    assert (dest / "normal.txt").read_text() == "hello"
    assert not (dest / "evil_link").exists()


def test_relative_symlink_escape_skipped(tmp_path: Path):
    """Test that relative symlinks escaping destination are skipped."""
    evil_info = tarfile.TarInfo(name="escape_link")
    evil_info.type = tarfile.SYMTYPE
    evil_info.linkname = "../../etc/shadow"
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(tar_path, [evil_info, normal_info], {"normal.txt": b"hello"})

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest, filter=backup_data_filter)

    assert (dest / "normal.txt").read_text() == "hello"
    assert not (dest / "escape_link").exists()


def test_device_node_skipped(tmp_path: Path):
    """Test that device nodes are skipped during extraction."""
    evil_info = tarfile.TarInfo(name="evil_device")
    evil_info.type = tarfile.CHRTYPE
    evil_info.devmajor = 1
    evil_info.devminor = 5  # /dev/zero
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(tar_path, [evil_info, normal_info], {"normal.txt": b"hello"})

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest, filter=backup_data_filter)

    assert (dest / "normal.txt").read_text() == "hello"
    assert not (dest / "evil_device").exists()


def test_path_traversal_skipped(tmp_path: Path):
    """Test that path traversal entries are skipped."""
    traversal_info = tarfile.TarInfo(name="../../etc/passwd")
    traversal_info.size = 9
    normal_info = tarfile.TarInfo(name="normal.txt")
    normal_info.size = 5
    tar_path = tmp_path / "test.tar.gz"
    _create_tar_gz(
        tar_path,
        [traversal_info, normal_info],
        {"../../etc/passwd": b"malicious", "normal.txt": b"hello"},
    )

    dest = tmp_path / "out"
    dest.mkdir()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest, filter=backup_data_filter)

    assert (dest / "normal.txt").read_text() == "hello"
    assert not (dest / "../../etc/passwd").exists()


def test_valid_internal_symlinks_extracted(tmp_path: Path):
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
        tar.extractall(path=dest, filter=backup_data_filter)

    assert (dest / "subdir" / "config.yaml").read_text() == "key: value\n"
    assert (dest / "config_link").is_symlink()
    assert (dest / "config_link").read_text() == "key: value\n"
