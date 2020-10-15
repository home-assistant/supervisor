"""Tests for resolution manager."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from supervisor.const import (
    ATTR_DATE,
    ATTR_SLUG,
    ATTR_TYPE,
    SNAPSHOT_FULL,
    SNAPSHOT_PARTIAL,
)
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionError
from supervisor.resolution.const import ContextType, SuggestionType, UnsupportedReason
from supervisor.resolution.data import Suggestion
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

    coresys.resolution.storage.clean_full_snapshots()
    assert newest_full_snapshot in coresys.snapshots.list_snapshots
    assert (
        len(
            [x for x in coresys.snapshots.list_snapshots if x.sys_type == SNAPSHOT_FULL]
        )
        == 1
    )


@pytest.mark.asyncio
async def test_api_resolution_dismiss_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_snapshot = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    assert SuggestionType.CLEAR_FULL_SNAPSHOT == coresys.resolution.suggestions[-1].type
    await coresys.resolution.dismiss_suggestion(clear_snapshot)
    assert clear_snapshot not in coresys.resolution.suggestions


@pytest.mark.asyncio
async def test_api_resolution_apply_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_snapshot = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )
    coresys.resolution.suggestions = create_snapshot = Suggestion(
        SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    with patch("supervisor.snapshots.SnapshotManager", return_value=MagicMock()):
        await coresys.resolution.apply_suggestion(clear_snapshot)
        await coresys.resolution.apply_suggestion(create_snapshot)

        assert clear_snapshot not in coresys.resolution.suggestions
        assert create_snapshot not in coresys.resolution.suggestions

    with pytest.raises(ResolutionError):
        await coresys.resolution.apply_suggestion(clear_snapshot)
