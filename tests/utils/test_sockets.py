"""Test Unix socket file helpers."""

from collections.abc import Callable, Generator
from pathlib import Path
import socket
import tempfile

import pytest

from supervisor.utils.sockets import prepare_socket_dir, remove_socket_files


@pytest.fixture(name="short_tmp_path")
def fixture_short_tmp_path() -> Generator[Path]:
    """Return a tmp dir short enough for sun_path (pytest's tmp_path is too long on macOS)."""
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp_dir:
        yield Path(tmp_dir)


def _bind_stale_socket(path: Path) -> None:
    """Leave a socket file behind with no listener, like a crashed process."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    sock.close()


def _plant_nothing(path: Path) -> None:
    """Leave the socket directory missing."""


def _plant_regular_file(path: Path) -> None:
    """Leave a regular file at the socket path."""
    path.parent.mkdir()
    path.write_text("stale")


def _plant_socket_file(path: Path) -> None:
    """Leave a stale socket file at the socket path."""
    path.parent.mkdir()
    _bind_stale_socket(path)


@pytest.mark.parametrize(
    "plant",
    [
        pytest.param(_plant_nothing, id="missing-dir"),
        pytest.param(_plant_regular_file, id="stale-regular-file"),
        pytest.param(_plant_socket_file, id="stale-socket-file"),
    ],
)
def test_prepare_socket_dir(short_tmp_path: Path, plant: Callable[[Path], None]):
    """Test the socket path is ready to bind afterwards."""
    path = short_tmp_path / "core" / "test.sock"
    plant(path)

    prepare_socket_dir(path)

    assert path.parent.is_dir()
    assert not path.exists()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(str(path))


def test_prepare_socket_dir_never_removes_directory(short_tmp_path: Path):
    """Test a directory at the socket path is not removed."""
    path = short_tmp_path / "test.sock"
    path.mkdir()

    with pytest.raises(OSError, match=r"test\.sock"):
        prepare_socket_dir(path)

    assert path.is_dir()


def test_remove_socket_files(short_tmp_path: Path):
    """Test named socket files are removed and everything else is kept."""
    _bind_stale_socket(short_tmp_path / "core.sock")
    (short_tmp_path / "other.sock").write_text("keep")

    remove_socket_files(short_tmp_path, ["core.sock", "missing.sock"])

    assert short_tmp_path.is_dir()
    assert not (short_tmp_path / "core.sock").exists()
    assert (short_tmp_path / "other.sock").exists()


def test_remove_socket_files_missing_dir(short_tmp_path: Path):
    """Test removing from a directory that does not exist is a no-op."""
    remove_socket_files(short_tmp_path / "missing", ["core.sock"])

    assert not (short_tmp_path / "missing").exists()


def test_remove_socket_files_never_removes_directory(short_tmp_path: Path):
    """Test a directory with a socket file name is not removed."""
    (short_tmp_path / "core.sock").mkdir()

    with pytest.raises(OSError, match=r"core\.sock"):
        remove_socket_files(short_tmp_path, ["core.sock"])

    assert (short_tmp_path / "core.sock").is_dir()
