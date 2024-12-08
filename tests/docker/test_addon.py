"""Test docker addon setup."""

import asyncio
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from docker.errors import NotFound
from docker.types import Mount
import pytest

from supervisor.addons import validate as vd
from supervisor.addons.addon import Addon
from supervisor.addons.model import Data
from supervisor.addons.options import AddonOptions
from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.dbus.agent.cgroup import CGroup
from supervisor.docker.addon import DockerAddon
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import CoreDNSError, DockerNotFound
from supervisor.hardware.data import Device
from supervisor.os.manager import OSManager
from supervisor.plugins.dns import PluginDns
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from ..common import load_json_fixture
from . import DEV_MOUNT


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
    coresys: CoreSys,
    addonsdata_system: dict[str, Data],
    config_file: str | dict[str, Any],
) -> DockerAddon:
    """Make and return docker addon object."""
    config = (
        load_json_fixture(config_file) if isinstance(config_file, str) else config_file
    )
    config = vd.SCHEMA_ADDON_CONFIG(config)
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

    # Dev added as ro with bind-recursive=writable option
    assert DEV_MOUNT in docker_addon.mounts

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
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].append("homeassistant_config")
    docker_addon = get_docker_addon(coresys, addonsdata_system, config)

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


def test_addon_map_addon_configs_folder(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test mounts for addon which maps addon configs folder."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].append("all_addon_configs")
    docker_addon = get_docker_addon(coresys, addonsdata_system, config)

    # Addon configs folder included
    assert (
        Mount(
            type="bind",
            source=coresys.config.path_extern_addon_configs.as_posix(),
            target="/addon_configs",
            read_only=True,
        )
        in docker_addon.mounts
    )


def test_addon_map_addon_config_folder(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test mounts for addon which maps its own config folder."""
    docker_addon = get_docker_addon(
        coresys, addonsdata_system, "addon-config-map-addon_config.json"
    )

    # Addon config folder included
    assert (
        Mount(
            type="bind",
            source=docker_addon.addon.path_extern_config.as_posix(),
            target="/config",
            read_only=True,
        )
        in docker_addon.mounts
    )


def test_addon_map_addon_config_folder_with_custom_target(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test mounts for addon which maps its own config folder and sets target path."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].remove("addon_config")
    config["map"].append(
        {"type": "addon_config", "read_only": False, "path": "/custom/target/path"}
    )
    docker_addon = get_docker_addon(coresys, addonsdata_system, config)

    # Addon config folder included
    assert (
        Mount(
            type="bind",
            source=docker_addon.addon.path_extern_config.as_posix(),
            target="/custom/target/path",
            read_only=False,
        )
        in docker_addon.mounts
    )


def test_addon_map_data_folder_with_custom_target(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test mounts for addon which sets target path for data folder."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].append({"type": "data", "path": "/custom/data/path"})
    docker_addon = get_docker_addon(coresys, addonsdata_system, config)

    # Addon config folder included
    assert (
        Mount(
            type="bind",
            source=docker_addon.addon.path_extern_data.as_posix(),
            target="/custom/data/path",
            read_only=False,
        )
        in docker_addon.mounts
    )


def test_addon_ignore_on_config_map(
    coresys: CoreSys, addonsdata_system: dict[str, Data], path_extern
):
    """Test mounts for addon don't include addon config or homeassistant when config included."""
    config = load_json_fixture("basic-addon-config.json")
    config["map"].extend(["addon_config", "homeassistant_config"])
    docker_addon = get_docker_addon(coresys, addonsdata_system, config)

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

    with (
        patch.object(DockerAddon, "stop"),
        patch.object(
            AddonOptions, "validate", new=PropertyMock(return_value=lambda _: None)
        ),
        pytest.raises(DockerNotFound),
    ):
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

    with (
        patch.object(DockerAddon, "stop"),
        patch.object(
            AddonOptions, "validate", new=PropertyMock(return_value=lambda _: None)
        ),
        patch.object(PluginDns, "add_host", side_effect=(err := CoreDNSError())),
    ):
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

    with (
        patch.object(
            DockerAddon,
            "ip_address",
            new=PropertyMock(return_value=IPv4Address("172.30.33.1")),
        ),
        patch.object(PluginDns, "delete_host", side_effect=(err := CoreDNSError())),
    ):
        await docker_addon.stop()

        capture_exception.assert_called_once_with(err)


TEST_DEV_PATH = "/dev/ttyAMA0"
TEST_SYSFS_PATH = "/sys/devices/platform/soc/ffe09000.usb/ff500000.usb/xhci-hcd.0.auto/usb1/1-1/1-1.1/1-1.1:1.0/tty/ttyACM0"
TEST_HW_DEVICE = Device(
    name="ttyACM0",
    path=Path("/dev/ttyAMA0"),
    sysfs=Path(
        "/sys/devices/platform/soc/ffe09000.usb/ff500000.usb/xhci-hcd.0.auto/usb1/1-1/1-1.1/1-1.1:1.0/tty/ttyACM0"
    ),
    subsystem="tty",
    parent=Path(
        "/sys/devices/platform/soc/ffe09000.usb/ff500000.usb/xhci-hcd.0.auto/usb1/1-1/1-1.1/1-1.1:1.0"
    ),
    links=[
        Path(
            "/dev/serial/by-id/usb-Texas_Instruments_TI_CC2531_USB_CDC___0X0123456789ABCDEF-if00"
        ),
        Path("/dev/serial/by-path/platform-xhci-hcd.0.auto-usb-0:1.1:1.0"),
        Path("/dev/serial/by-path/platform-xhci-hcd.0.auto-usbv2-0:1.1:1.0"),
    ],
    attributes={},
    children=[],
)


@pytest.mark.usefixtures("path_extern")
@pytest.mark.parametrize(
    ("dev_path", "cgroup", "is_os"),
    [
        (TEST_DEV_PATH, "1", True),
        (TEST_SYSFS_PATH, "1", True),
        (TEST_DEV_PATH, "1", False),
        (TEST_SYSFS_PATH, "1", False),
        (TEST_DEV_PATH, "2", True),
        (TEST_SYSFS_PATH, "2", True),
    ],
)
async def test_addon_new_device(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    docker: DockerAPI,
    dev_path: str,
    cgroup: str,
    is_os: bool,
):
    """Test new device that is listed in static devices."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_addon_ssh.data["devices"] = [dev_path]
    container.id = 123
    docker.info.cgroup = cgroup

    with (
        patch.object(Addon, "write_options"),
        patch.object(OSManager, "available", new=PropertyMock(return_value=is_os)),
        patch.object(CGroup, "add_devices_allowed") as add_devices,
    ):
        await install_addon_ssh.start()

        coresys.bus.fire_event(
            BusEvent.HARDWARE_NEW_DEVICE,
            TEST_HW_DEVICE,
        )
        await asyncio.sleep(0.01)

        add_devices.assert_called_once_with(123, "c 0:0 rwm")


@pytest.mark.usefixtures("path_extern")
@pytest.mark.parametrize("dev_path", [TEST_DEV_PATH, TEST_SYSFS_PATH])
async def test_addon_new_device_no_haos(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    docker: DockerAPI,
    dev_path: str,
):
    """Test new device that is listed in static devices on non HAOS system with CGroup V2."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_addon_ssh.data["devices"] = [dev_path]
    docker.info.cgroup = "2"

    with (
        patch.object(Addon, "write_options"),
        patch.object(OSManager, "available", new=PropertyMock(return_value=False)),
        patch.object(CGroup, "add_devices_allowed") as add_devices,
    ):
        await install_addon_ssh.start()

        coresys.bus.fire_event(
            BusEvent.HARDWARE_NEW_DEVICE,
            TEST_HW_DEVICE,
        )
        await asyncio.sleep(0.01)

        add_devices.assert_not_called()

    # Issue added with hardware event since access cannot be added dynamically
    assert install_addon_ssh.device_access_missing_issue in coresys.resolution.issues
    assert (
        Suggestion(
            SuggestionType.EXECUTE_RESTART, ContextType.ADDON, reference="local_ssh"
        )
        in coresys.resolution.suggestions
    )

    # Stopping and removing the container clears it as access granted on next start
    await install_addon_ssh.stop()
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
