"""Test docker addon setup."""
from typing import Dict
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from supervisor.addons import validate as vd
from supervisor.addons.addon import Addon
from supervisor.addons.model import Data
from supervisor.const import SYSTEMD_JOURNAL_PERSISTENT, SYSTEMD_JOURNAL_VOLATILE
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon

from ..common import load_json_fixture


@pytest.fixture(name="addonsdata_system")
def fixture_addonsdata_system() -> Dict[str, Data]:
    """Mock AddonsData.system."""
    with patch(
        "supervisor.addons.data.AddonsData.system", new_callable=PropertyMock
    ) as mock:
        yield mock


@pytest.fixture(name="addonsdata_user", autouse=True)
def fixture_addonsdata_user() -> Dict[str, Data]:
    """Mock AddonsData.user."""
    with patch(
        "supervisor.addons.data.AddonsData.user", new_callable=PropertyMock
    ) as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture(name="os_environ", autouse=True)
def fixture_os_environ():
    """Mock os.environ."""
    with patch("supervisor.config.os.environ") as mock:
        yield mock


def get_docker_addon(
    coresys: CoreSys, addonsdata_system: Dict[str, Data], config_file: str
):
    """Make and return docker addon object."""
    config = vd.SCHEMA_ADDON_CONFIG(load_json_fixture(config_file))
    slug = config.get("slug")
    addonsdata_system.return_value = {slug: config}

    addon = Addon(coresys, config.get("slug"))
    docker_addon = DockerAddon(coresys, addon)
    return docker_addon


def test_base_volumes_included(coresys: CoreSys, addonsdata_system: Dict[str, Data]):
    """Dev and data volumes always included."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )
    volumes = docker_addon.volumes

    # Dev added as ro
    assert "/dev" in volumes
    assert volumes["/dev"]["bind"] == "/dev"
    assert volumes["/dev"]["mode"] == "ro"

    # Data added as rw
    data_path = str(docker_addon.addon.path_extern_data)
    assert data_path in volumes
    assert volumes[data_path]["bind"] == "/data"
    assert volumes[data_path]["mode"] == "rw"


def test_addon_map_folder_defaults(
    coresys: CoreSys, addonsdata_system: Dict[str, Data]
):
    """Validate defaults for mapped folders in addons."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )
    volumes = docker_addon.volumes

    # Config added and is marked rw
    config_path = str(docker_addon.sys_config.path_extern_homeassistant)
    assert config_path in volumes
    assert volumes[config_path]["bind"] == "/config"
    assert volumes[config_path]["mode"] == "rw"

    # SSL added and defaults to ro
    ssl_path = str(docker_addon.sys_config.path_extern_ssl)
    assert ssl_path in volumes
    assert volumes[ssl_path]["bind"] == "/ssl"
    assert volumes[ssl_path]["mode"] == "ro"

    # Share not mapped
    assert str(docker_addon.sys_config.path_extern_share) not in volumes


def test_journald_addon_volatile(coresys: CoreSys, addonsdata_system: Dict[str, Data]):
    """Validate volume for journald option, with volatile logs."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "journald-addon-config.json"
    )
    volumes = docker_addon.volumes

    assert str(SYSTEMD_JOURNAL_PERSISTENT) in volumes
    assert volumes.get(str(SYSTEMD_JOURNAL_PERSISTENT)).get("bind") == str(
        SYSTEMD_JOURNAL_VOLATILE
    )
    assert volumes.get(str(SYSTEMD_JOURNAL_PERSISTENT)).get("mode") == "ro"


def test_journald_addon_persistent(
    coresys: CoreSys, addonsdata_system: Dict[str, Data]
):
    """Validate volume for journald option, with persistent logs."""
    with patch("pathlib.Path.exists", return_value=True):
        docker_addon = get_docker_addon(
            coresys, addonsdata_system, "journald-addon-config.json"
        )
        volumes = docker_addon.volumes

    assert str(SYSTEMD_JOURNAL_PERSISTENT) in volumes
    assert volumes.get(str(SYSTEMD_JOURNAL_PERSISTENT)).get("bind") == str(
        SYSTEMD_JOURNAL_PERSISTENT
    )
    assert volumes.get(str(SYSTEMD_JOURNAL_PERSISTENT)).get("mode") == "ro"


def test_not_journald_addon(coresys: CoreSys, addonsdata_system: Dict[str, Data]):
    """Validate journald option defaults off."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )
    volumes = docker_addon.volumes

    assert str(SYSTEMD_JOURNAL_PERSISTENT) not in volumes
