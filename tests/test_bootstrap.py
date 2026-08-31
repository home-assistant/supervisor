"""Test bootstrap."""

# pylint: disable=protected-access

from supervisor.bootstrap import _migrate_legacy_paths
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
