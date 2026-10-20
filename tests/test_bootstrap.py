"""Test bootstrap."""

# pylint: disable=protected-access

from datetime import UTC, datetime
import logging
from unittest.mock import patch

import pytest

from supervisor.bootstrap import SupervisorLogFormatter, _migrate_legacy_paths
from supervisor.coresys import CoreSys


def test_migrate_legacy_paths_removes_emergency_folder(
    coresys: CoreSys, tmp_supervisor_data
):
    """Test the emergency folder of the eager-mount design is cleaned up."""
    emergency = coresys.config.path_supervisor / "emergency"
    (emergency / "media_test").mkdir(parents=True)

    _migrate_legacy_paths(coresys)

    assert not emergency.exists()


def test_migrate_legacy_paths_keeps_non_empty_emergency_folder(
    coresys: CoreSys, tmp_supervisor_data
):
    """Test a leftover file keeps the emergency folder in place."""
    emergency = coresys.config.path_supervisor / "emergency"
    emergency.mkdir(parents=True)
    (emergency / "leftover").write_text("data", encoding="utf-8")

    _migrate_legacy_paths(coresys)

    assert emergency.is_dir()


@pytest.mark.parametrize(
    ("timezone", "expected"),
    [
        pytest.param("UTC", "2026-10-15 08:40:11.123+00:00", id="utc"),
        pytest.param("Europe/Prague", "2026-10-15 10:40:11.123+02:00", id="positive"),
        pytest.param(
            "America/New_York", "2026-10-15 04:40:11.123-04:00", id="negative"
        ),
        pytest.param("Asia/Kolkata", "2026-10-15 14:10:11.123+05:30", id="half-hour"),
    ],
)
async def test_log_formatter_timestamp(
    coresys: CoreSys, timezone: str, expected: str
) -> None:
    """Test log timestamps carry milliseconds and the UTC offset."""
    await coresys.config.set_timezone(timezone)
    record = logging.makeLogRecord(
        {"created": datetime(2026, 10, 15, 8, 40, 11, 123456, UTC).timestamp()}
    )

    with patch.object(SupervisorLogFormatter, "coresys", coresys):
        assert SupervisorLogFormatter().formatTime(record) == expected
