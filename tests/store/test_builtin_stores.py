"""Test local and core store."""

from supervisor.coresys import CoreSys


def test_local_store(coresys: CoreSys, repository) -> None:
    """Test loading from local store."""
    assert coresys.store.get("local")

    assert "local_ssh" in coresys.addons.store


def test_core_store(coresys: CoreSys, repository) -> None:
    """Test loading from core store."""
    assert coresys.store.get("core")

    assert "core_samba" in coresys.addons.store
