"""Tests for resolution manager."""
from pathlib import Path

from supervisor.const import ATTR_DATE, ATTR_SLUG, ATTR_TYPE
from supervisor.coresys import CoreSys
from supervisor.resolution.const import UnsupportedReason
from supervisor.snapshots.snapshot import Snapshot
from supervisor.utils.dt import utcnow
from supervisor.utils.tar import SecureTarFile


def test_properies(coresys: CoreSys):
    """Test resolution manager properties."""

    assert coresys.core.supported

    coresys.resolution.unsupported = UnsupportedReason.OS
    assert not coresys.core.supported


async def test_clear_snapshots(coresys: CoreSys, tmp_path):
    """Test snapshot cleanup."""
    for slug in ["sn1", "sn2", "sn3", "sn4", "sn5"]:
        temp_tar = Path(tmp_path, f"{slug}.tar")
        with SecureTarFile(temp_tar, "w"):
            pass
        snapshot = Snapshot(coresys, temp_tar)
        snapshot._data = {  # pylint: disable=protected-access
            ATTR_SLUG: slug,
            ATTR_DATE: utcnow().isoformat(),
            ATTR_TYPE: "partial" if "1" in slug or "5" in slug else "full",
        }
        coresys.snapshots.snapshots_obj[snapshot.slug] = snapshot

    newest_full_snapshot = coresys.snapshots.snapshots_obj["sn4"]

    assert newest_full_snapshot in coresys.snapshots.list_snapshots
    assert (
        len([x for x in coresys.snapshots.list_snapshots if x.sys_type == "full"]) == 3
    )

    coresys.resolution.storage.clean_full_snapshots()
    assert newest_full_snapshot in coresys.snapshots.list_snapshots
    assert (
        len([x for x in coresys.snapshots.list_snapshots if x.sys_type == "full"]) == 1
    )
