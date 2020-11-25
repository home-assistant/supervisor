"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from pathlib import Path

from supervisor.const import (
    ATTR_DATE,
    ATTR_SLUG,
    ATTR_TYPE,
    SNAPSHOT_FULL,
    SNAPSHOT_PARTIAL,
)
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.clear_full_snapshot import FixupClearFullSnapshot
from supervisor.snapshots.snapshot import Snapshot
from supervisor.utils.dt import utcnow
from supervisor.utils.tar import SecureTarFile


async def test_fixup(coresys: CoreSys, tmp_path):
    """Test fixup."""
    clear_full_snapshot = FixupClearFullSnapshot(coresys)

    assert not clear_full_snapshot.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    for slug in ["sn1", "sn2", "sn3", "sn4", "sn5"]:
        temp_tar = Path(tmp_path, f"{slug}.tar")
        with SecureTarFile(temp_tar, "w"):
            pass
        snapshot = Snapshot(coresys, temp_tar)
        snapshot._data = {  # pylint: disable=protected-access
            ATTR_SLUG: slug,
            ATTR_DATE: utcnow().isoformat(),
            ATTR_TYPE: SNAPSHOT_PARTIAL
            if "1" in slug or "5" in slug
            else SNAPSHOT_FULL,
        }
        coresys.snapshots.snapshots_obj[snapshot.slug] = snapshot

    newest_full_snapshot = coresys.snapshots.snapshots_obj["sn4"]

    assert newest_full_snapshot in coresys.snapshots.list_snapshots
    assert (
        len(
            [x for x in coresys.snapshots.list_snapshots if x.sys_type == SNAPSHOT_FULL]
        )
        == 3
    )

    await clear_full_snapshot()
    assert newest_full_snapshot in coresys.snapshots.list_snapshots
    assert (
        len(
            [x for x in coresys.snapshots.list_snapshots if x.sys_type == SNAPSHOT_FULL]
        )
        == 1
    )

    assert len(coresys.resolution.suggestions) == 0
