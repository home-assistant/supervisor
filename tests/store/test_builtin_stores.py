"""Test local and core store."""

import pytest

from supervisor.coresys import CoreSys
from supervisor.store.const import BuiltinRepository
from supervisor.store.repository import Repository


def test_local_store(coresys: CoreSys, test_repository) -> None:
    """Test loading from local store."""
    assert coresys.store.get("local")

    assert "local_ssh" in coresys.apps.store


def test_core_store(coresys: CoreSys, test_repository) -> None:
    """Test loading from core store."""
    assert coresys.store.get("core")

    assert "core_samba" in coresys.apps.store


@pytest.mark.parametrize(
    ("builtin", "slug"),
    [
        (BuiltinRepository.LOCAL, "local"),
        (BuiltinRepository.CORE, "core"),
        (BuiltinRepository.COMMUNITY_APPS, "a0d7b954"),
        (BuiltinRepository.ESPHOME, "5c53de3b"),
        (BuiltinRepository.MUSIC_ASSISTANT, "d5369777"),
    ],
)
def test_builtin_repository_has_fixed_slug(
    coresys: CoreSys, builtin: BuiltinRepository, slug: str
) -> None:
    """Test built-in repository slugs are fixed and independent from URL hashing."""
    assert builtin.slug == slug
    assert Repository.create(coresys, builtin.value).slug == slug
