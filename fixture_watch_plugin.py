"""Diagnostic pytest plugin logging per-test start and end with wall-clock time."""

import os
from pathlib import Path
import time

import pytest

OUT = Path(os.environ["FIXTURE_WATCH_LOG"])


def _write(tag: str, nodeid: str) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as handle:
        handle.write(f"{time.time():.3f} {os.getpid()} {tag} {nodeid}\n")


def pytest_sessionstart(session: pytest.Session) -> None:
    """Log session start."""
    _write("SESSION_START", "")


def pytest_runtest_logstart(nodeid: str, location: tuple[str, int | None, str]) -> None:
    """Log test start."""
    _write("START", nodeid)


def pytest_runtest_logfinish(
    nodeid: str, location: tuple[str, int | None, str]
) -> None:
    """Log test end, after teardown."""
    _write("END", nodeid)


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Log session end."""
    _write("SESSION_FINISH", "")
