"""Test docker addon setup."""
from ipaddress import IPv4Address
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from docker.errors import NotFound
from docker.types import Mount
import pytest

from supervisor.addons import validate as vd
from supervisor.addons.addon import Addon
from supervisor.addons.model import Data
from supervisor.addons.options import AddonOptions
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.exceptions import CoreDNSError, DockerNotFound
from supervisor.plugins.dns import PluginDns
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue

from ..common import load_json_fixture


@pytest.fixture(name="addonsdata_system")
def fixture_addonsdata_system() -> dict[str, Data]:
    """Mock AddonsData.system."""
    with patch(
        "supervisor.addons.data.AddonsData.system", new_callable=PropertyMock
    ) as mock:
        yield mock


@pytest.fixture(name="addonsdata_user", autouse=True)
def fixture_addonsdata_user() -> dict[str, Data]:
    """Mock AddonsData.user."""
    with patch(
        "supervisor.addons.data.AddonsData.user", new_callable=PropertyMock
    ) as mock:
        mock.return_value = MagicMock()
        yield mock


def get_docker_addon(
    coresys: CoreSys, addonsdata_system: dict[str, Data], config_file: str
):
    """Make and return docker addon object."""
    config = vd.SCHEMA_ADDON_CONFIG(load_json_fixture(config_file))
    slug = config.get("slug")
    addonsdata_system.return_value = {slug: config}

    addon = Addon(coresys, config.get("slug"))
    docker_addon = DockerAddon(coresys, addon)
    return docker_addon


def test_base_volumes_included(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Dev and data volumes always included."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )

    # Dev added as ro
    assert (
        Mount(type="bind", source="/dev", target="/dev", read_only=True)
        in docker_addon.mounts
    )

    # Data added as rw
    assert (
        Mount(
            type="bind",
            source=docker_addon.addon.path_extern_data.as_posix(),
            target="/data",
            read_only=False,
        )
        in docker_addon.mounts
    )


def test_addon_map_folder_defaults(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Validate defaults for mapped folders in addons."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )
    # Config added and is marked rw
    assert (
        Mount(
            type="bind",
            source=coresys.config.path_extern_homeassistant.as_posix(),
            target="/config",
            read_only=False,
        )
        in docker_addon.mounts
    )

    # Mount for addon's specific config folder omitted since config in map field
    assert (
        len([mount for mount in docker_addon.mounts if mount["Target"] == "/config"])
        == 1
    )
    # Home Assistant mount omitted since config in map field
    assert "/homeassistant" not in [mount["Target"] for mount in docker_addon.mounts]

    # SSL added and defaults to ro
    assert (
        Mount(
            type="bind",
            source=coresys.config.path_extern_ssl.as_posix(),
            target="/ssl",
            read_only=True,
        )
        in docker_addon.mounts
    )

    # Media added and propagation set
    assert (
        Mount(
            type="bind",
            source=coresys.config.path_extern_media.as_posix(),
            target="/media",
            read_only=True,
            propagation="rslave",
        )
        in docker_addon.mounts
    )

    # Share added and propagation set
    assert (
        Mount(
            type="bind",
            source=coresys.config.path_extern_share.as_posix(),
            target="/share",
            read_only=True,
            propagation="rslave",
        )
        in docker_addon.mounts
    )

    # Backup not added
    assert "/backup" not in [mount["Target"] for mount in docker_addon.mounts]


def test_addon_map_homeassistant_folder(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test mounts for addon which maps homeassistant folder."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "homeassistant-addon-config.json"
    )

    # Home Assistant config folder mounted to /homeassistant, not /config
    assert (
        Mount(
            type="bind",
            source=coresys.config.path_extern_homeassistant.as_posix(),
            target="/homeassistant",
            read_only=True,
        )
        in docker_addon.mounts
    )

    # Addon's config folder mounted to /config
    assert (
        Mount(
            type="bind",
            source=docker_addon.addon.path_extern_config.as_posix(),
            target="/config",
            read_only=False,
        )
        in docker_addon.mounts
    )

    # Home Assistant folder not mounted to config when using homeassistant map option
    assert (
        len([mount for mount in docker_addon.mounts if mount["Target"] == "/config"])
        == 1
    )


def test_journald_addon(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Validate volume for journald option."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "journald-addon-config.json"
    )

    assert (
        Mount(
            type="bind",
            source="/var/log/journal",
            target="/var/log/journal",
            read_only=True,
        )
        in docker_addon.mounts
    )
    assert (
        Mount(
            type="bind",
            source="/run/log/journal",
            target="/run/log/journal",
            read_only=True,
        )
        in docker_addon.mounts
    )


def test_not_journald_addon(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Validate journald option defaults off."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )

    assert "/var/log/journal" not in [mount["Target"] for mount in docker_addon.mounts]


async def test_addon_run_docker_error(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test docker error when addon is run."""
    await coresys.dbus.timedate.connect(coresys.dbus.bus)
    coresys.docker.containers.create.side_effect = NotFound("Missing")
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )

    with patch.object(DockerAddon, "stop"), patch.object(
        AddonOptions, "validate", new=PropertyMock(return_value=lambda _: None)
    ), pytest.raises(DockerNotFound):
        await docker_addon.run()

    assert (
        Issue(IssueType.MISSING_IMAGE, ContextType.ADDON, reference="test_addon")
        in coresys.resolution.issues
    )


async def test_addon_run_add_host_error(
    coresys: CoreSys,
    addonsdata_system: dict[str, Data],
    capture_exception: Mock,
    path_extern,
):
    """Test error adding host when addon is run."""
    await coresys.dbus.timedate.connect(coresys.dbus.bus)
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )

    with patch.object(DockerAddon, "stop"), patch.object(
        AddonOptions, "validate", new=PropertyMock(return_value=lambda _: None)
    ), patch.object(PluginDns, "add_host", side_effect=(err := CoreDNSError())):
        await docker_addon.run()

        capture_exception.assert_called_once_with(err)


async def test_addon_stop_delete_host_error(
    coresys: CoreSys,
    addonsdata_system: dict[str, Data],
    capture_exception: Mock,
):
    """Test error deleting host when addon is stopped."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "basic-addon-config.json"
    )

    with patch.object(
        DockerAddon,
        "ip_address",
        new=PropertyMock(return_value=IPv4Address("172.30.33.1")),
    ), patch.object(PluginDns, "delete_host", side_effect=(err := CoreDNSError())):
        await docker_addon.stop()

        capture_exception.assert_called_once_with(err)
