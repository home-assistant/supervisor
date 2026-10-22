"""Helpers for Unix socket files."""

from collections.abc import Iterable
from pathlib import Path


def prepare_socket_dir(path: Path) -> None:
    """Create the parent directory of a socket and remove a stale file at its path.

    Must be run in executor.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # asyncio only replaces a stale socket, any other file fails the bind
    path.unlink(missing_ok=True)


def remove_socket_files(directory: Path, names: Iterable[str]) -> None:
    """Remove socket files from a directory, leaving the directory in place.

    Must be run in executor.
    """
    for name in names:
        Path(directory, name).unlink(missing_ok=True)
