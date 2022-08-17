"""Test store manager."""
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.bootstrap import migrate_system_env
from supervisor.const import ATTR_ADDONS_CUSTOM_LIST
from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreJobError
from supervisor.store import StoreManager
from supervisor.store.repository import Repository


async def test_default_load(coresys: CoreSys):
    """Test default load from config."""
    store_manager = StoreManager(coresys)

    with patch(
        "supervisor.store.repository.Repository.load", return_value=None
    ), patch.object(
        type(coresys.config), "addons_repositories", return_value=[]
    ), patch(
        "pathlib.Path.exists", return_value=True
    ):
        await store_manager.load()

    assert len(store_manager.all) == 4
    assert isinstance(store_manager.get("core"), Repository)
    assert isinstance(store_manager.get("local"), Repository)

    assert len(store_manager.repository_urls) == 2
    assert (
        "https://github.com/hassio-addons/repository" in store_manager.repository_urls
    )
    assert (
        "https://github.com/esphome/home-assistant-addon"
        in store_manager.repository_urls
    )


async def test_load_with_custom_repository(coresys: CoreSys):
    """Test load from config with custom repository."""
    with patch(
        "supervisor.utils.common.read_json_or_yaml_file",
        return_value={"repositories": ["http://example.com"]},
    ), patch("pathlib.Path.is_file", return_value=True):
        store_manager = StoreManager(coresys)

    with patch(
        "supervisor.store.repository.Repository.load", return_value=None
    ), patch.object(
        type(coresys.config), "addons_repositories", return_value=[]
    ), patch(
        "supervisor.store.repository.Repository.validate", return_value=True
    ), patch(
        "pathlib.Path.exists", return_value=True
    ):
        await store_manager.load()

    assert len(store_manager.all) == 5
    assert isinstance(store_manager.get("core"), Repository)
    assert isinstance(store_manager.get("local"), Repository)

    assert len(store_manager.repository_urls) == 3
    assert (
        "https://github.com/hassio-addons/repository" in store_manager.repository_urls
    )
    assert (
        "https://github.com/esphome/home-assistant-addon"
        in store_manager.repository_urls
    )
    assert "http://example.com" in store_manager.repository_urls


async def test_load_from_core_config(coresys: CoreSys):
    """Test custom repositories loaded from core config when present."""
    # pylint: disable=protected-access
    coresys.config._data[ATTR_ADDONS_CUSTOM_LIST] = ["http://example.com"]
    assert coresys.config.addons_repositories == ["http://example.com"]

    migrate_system_env(coresys)

    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
        "supervisor.store.repository.Repository.validate", return_value=True
    ), patch("pathlib.Path.exists", return_value=True):
        await coresys.store.load()

    assert len(coresys.store.all) == 5
    assert isinstance(coresys.store.get("core"), Repository)
    assert isinstance(coresys.store.get("local"), Repository)

    assert len(coresys.store.repository_urls) == 3
    assert (
        "https://github.com/hassio-addons/repository" in coresys.store.repository_urls
    )
    assert (
        "https://github.com/esphome/home-assistant-addon"
        in coresys.store.repository_urls
    )
    assert "http://example.com" in coresys.store.repository_urls

    assert coresys.config.addons_repositories == []

    coresys.config.save_data.assert_called_once()
    coresys.store.save_data.assert_called_once()


async def test_reload_fails_if_out_of_date(coresys: CoreSys):
    """Test reload fails when supervisor not updated."""
    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ), pytest.raises(StoreJobError):
        await coresys.store.reload()
