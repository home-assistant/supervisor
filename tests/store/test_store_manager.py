"""Test store manager."""
from unittest.mock import patch

from supervisor.const import ATTR_ADDONS_CUSTOM_LIST
from supervisor.coresys import CoreSys
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
    store_manager = StoreManager(coresys)

    # pylint: disable=protected-access
    coresys.config._data[ATTR_ADDONS_CUSTOM_LIST] = ["http://example.com"]
    assert coresys.config.addons_repositories == ["http://example.com"]

    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
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

    assert coresys.config.addons_repositories == []
