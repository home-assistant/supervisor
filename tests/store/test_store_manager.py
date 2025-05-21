"""Test store manager."""

from datetime import datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArch
from supervisor.backups.manager import BackupManager
from supervisor.coresys import CoreSys
from supervisor.exceptions import AddonsNotSupportedError, StoreJobError
from supervisor.homeassistant.module import HomeAssistant
from supervisor.store import StoreManager
from supervisor.store.addon import AddonStore
from supervisor.store.git import GitRepo
from supervisor.store.repository import Repository

from tests.common import load_yaml_fixture


async def test_default_load(coresys: CoreSys):
    """Test default load from config."""
    store_manager = await StoreManager(coresys).load_config()
    refresh_cache_calls: set[str] = set()

    async def mock_refresh_cache(obj: AddonStore):
        nonlocal refresh_cache_calls
        refresh_cache_calls.add(obj.slug)

    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch.object(type(coresys.config), "addons_repositories", return_value=[]),
        patch("pathlib.Path.exists", return_value=True),
        patch.object(AddonStore, "refresh_path_cache", new=mock_refresh_cache),
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
    assert (
        "https://github.com/music-assistant/home-assistant-addon"
        in store_manager.repository_urls
    )
    # NOTE: When adding new stores, make sure to add it to tests/fixtures/addons/git/
    assert refresh_cache_calls == {
        "local_ssh",
        "local_example",
        "core_samba",
        "local_example_image",
    }


async def test_load_with_custom_repository(coresys: CoreSys):
    """Test load from config with custom repository."""

    async def mock_refresh_cache(_):
        pass

    with (
        patch(
            "supervisor.utils.common.read_json_or_yaml_file",
            return_value={"repositories": ["http://example.com"]},
        ),
        patch("pathlib.Path.is_file", return_value=True),
    ):
        store_manager = await StoreManager(coresys).load_config()

    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch.object(type(coresys.config), "addons_repositories", return_value=[]),
        patch("supervisor.store.repository.Repository.validate", return_value=True),
        patch("pathlib.Path.exists", return_value=True),
        patch.object(AddonStore, "refresh_path_cache", new=mock_refresh_cache),
    ):
        await store_manager.load()

    assert len(store_manager.all) == 6
    assert isinstance(store_manager.get("core"), Repository)
    assert isinstance(store_manager.get("local"), Repository)

    assert len(store_manager.repository_urls) == 4
    assert (
        "https://github.com/hassio-addons/repository" in store_manager.repository_urls
    )
    assert (
        "https://github.com/esphome/home-assistant-addon"
        in store_manager.repository_urls
    )
    assert (
        "https://github.com/music-assistant/home-assistant-addon"
        in store_manager.repository_urls
    )
    assert "http://example.com" in store_manager.repository_urls


async def test_reload_fails_if_out_of_date(coresys: CoreSys):
    """Test reload fails when supervisor not updated."""
    with (
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        pytest.raises(StoreJobError),
    ):
        await coresys.store.reload()


@pytest.mark.parametrize(
    "config,log",
    [
        (
            {"arch": ["i386"]},
            "Add-on local_ssh not supported on this platform, supported architectures: i386",
        ),
        (
            {"machine": ["odroid-n2"]},
            "Add-on local_ssh not supported on this machine, supported machine types: odroid-n2",
        ),
        (
            {"machine": ["!qemux86-64"]},
            "Add-on local_ssh not supported on this machine, supported machine types: !qemux86-64",
        ),
        (
            {"homeassistant": AwesomeVersion("2023.1.1")},
            "Add-on local_ssh not supported on this system, requires Home Assistant version 2023.1.1 or greater",
        ),
    ],
)
async def test_update_unavailable_addon(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    caplog: pytest.LogCaptureFixture,
    config: dict[str, Any],
    log: str,
):
    """Test updating addon when new version not available for system."""
    addon_config = dict(
        await coresys.run_in_executor(
            load_yaml_fixture, "addons/local/ssh/config.yaml"
        ),
        version=AwesomeVersion("10.0.0"),
        **config,
    )

    with (
        patch.object(BackupManager, "do_backup_partial") as backup,
        patch.object(AddonStore, "data", new=PropertyMock(return_value=addon_config)),
        patch.object(CpuArch, "supported", new=PropertyMock(return_value=["amd64"])),
        patch.object(CoreSys, "machine", new=PropertyMock(return_value="qemux86-64")),
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2022.1.1")),
        ),
        patch("shutil.disk_usage", return_value=(42, 42, (1024.0**3))),
    ):
        with pytest.raises(AddonsNotSupportedError):
            await coresys.addons.update("local_ssh", backup=True)

        backup.assert_not_called()

    assert log in caplog.text


@pytest.mark.parametrize(
    "config,log",
    [
        (
            {"arch": ["i386"]},
            "Add-on local_ssh not supported on this platform, supported architectures: i386",
        ),
        (
            {"machine": ["odroid-n2"]},
            "Add-on local_ssh not supported on this machine, supported machine types: odroid-n2",
        ),
        (
            {"machine": ["!qemux86-64"]},
            "Add-on local_ssh not supported on this machine, supported machine types: !qemux86-64",
        ),
        (
            {"homeassistant": AwesomeVersion("2023.1.1")},
            "Add-on local_ssh not supported on this system, requires Home Assistant version 2023.1.1 or greater",
        ),
    ],
)
async def test_install_unavailable_addon(
    coresys: CoreSys,
    repository: Repository,
    caplog: pytest.LogCaptureFixture,
    config: dict[str, Any],
    log: str,
):
    """Test updating addon when new version not available for system."""
    addon_config = dict(
        await coresys.run_in_executor(
            load_yaml_fixture, "addons/local/ssh/config.yaml"
        ),
        version=AwesomeVersion("10.0.0"),
        **config,
    )

    with (
        patch.object(AddonStore, "data", new=PropertyMock(return_value=addon_config)),
        patch.object(CpuArch, "supported", new=PropertyMock(return_value=["amd64"])),
        patch.object(CoreSys, "machine", new=PropertyMock(return_value="qemux86-64")),
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2022.1.1")),
        ),
        patch("shutil.disk_usage", return_value=(42, 42, (1024.0**3))),
        pytest.raises(AddonsNotSupportedError),
    ):
        await coresys.addons.install("local_ssh")

    assert log in caplog.text


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_reload(coresys: CoreSys, supervisor_internet):
    """Test store reload."""
    await coresys.store.load()
    assert len(coresys.store.all) == 5

    with patch.object(GitRepo, "pull") as git_pull:
        await coresys.store.reload()

        assert git_pull.call_count == 4


async def test_addon_version_timestamp(coresys: CoreSys, install_addon_example: Addon):
    """Test timestamp tracked for addon's version."""
    # When unset, version timestamp set to utcnow on store load
    assert (timestamp := install_addon_example.latest_version_timestamp)

    # Reload of the store does not change timestamp unless version changes
    await coresys.store.reload()
    assert timestamp == install_addon_example.latest_version_timestamp

    # If a new version is seen processing repo, reset to utc now
    install_addon_example.data_store["version"] = "1.1.0"

    with patch(
        "pathlib.Path.stat",
        return_value=SimpleNamespace(
            st_mode=0o100644, st_mtime=datetime.now().timestamp()
        ),
    ):
        await coresys.store.reload()
    assert timestamp < install_addon_example.latest_version_timestamp
