"""Test docker app setup."""

import asyncio
from dataclasses import replace
from http import HTTPStatus
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

import aiodocker
import pytest

from supervisor.addons import validate as vd
from supervisor.addons.addon import App
from supervisor.addons.model import Data
from supervisor.addons.options import AppOptions
from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.dbus.agent.cgroup import CGroup
from supervisor.docker.addon import DockerApp
from supervisor.docker.const import (
    DockerMount,
    MountBindOptions,
    MountType,
    PropagationMode,
)
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
    """Mock AppsData.system."""
    with patch(
        "supervisor.addons.data.AppsData.system", new_callable=PropertyMock
    ) as mock:
        yield mock


@pytest.fixture(name="addonsdata_user", autouse=True)
def fixture_addonsdata_user() -> dict[str, Data]:
    """Mock AppsData.user."""
    with patch(
        "supervisor.addons.data.AppsData.user", new_callable=PropertyMock
    ) as mock:
        mock.return_value = MagicMock()
        yield mock


def get_docker_app(
    coresys: CoreSys,
    addonsdata_system: dict[str, Data],
    config_file: str | dict[str, Any],
) -> DockerApp:
    """Make and return docker app object."""
    config = (
        load_json_fixture(config_file) if isinstance(config_file, str) else config_file
    )
    config = vd.SCHEMA_ADDON_CONFIG(config)
    slug = config.get("slug")
    addonsdata_system.return_value = {slug: config}

    app = App(coresys, config.get("slug"))
    docker_app = DockerApp(coresys, app)
    return docker_app


@pytest.mark.usefixtures("path_extern")
def test_base_volumes_included(coresys: CoreSys, addonsdata_system: dict[str, Data]):
    """Dev and data volumes always included."""
    docker_app = get_docker_app(coresys, addonsdata_system, "basic-addon-config.json")

    # Dev added as ro with bind-recursive=writable option
    assert DEV_MOUNT in docker_app.mounts

    # Data added as rw
    assert (
        DockerMount(
            type=MountType.BIND,
            source=docker_app.app.path_extern_data.as_posix(),
            target="/data",
            read_only=False,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_app_map_folder_defaults(coresys: CoreSys, addonsdata_system: dict[str, Data]):
    """Validate defaults for mapped folders in apps."""
    docker_app = get_docker_app(coresys, addonsdata_system, "basic-addon-config.json")
    # Config added and is marked rw
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_homeassistant.as_posix(),
            target="/config",
            read_only=False,
        )
        in docker_app.mounts
    )

    # SSL added and defaults to ro
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_ssl.as_posix(),
            target="/ssl",
            read_only=True,
        )
        in docker_app.mounts
    )

    # Media added and propagation set
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_media.as_posix(),
            target="/media",
            read_only=True,
            bind_options=MountBindOptions(propagation=PropagationMode.RSLAVE),
        )
        in docker_app.mounts
    )

    # Share added and propagation set
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_share.as_posix(),
            target="/share",
            read_only=True,
            bind_options=MountBindOptions(propagation=PropagationMode.RSLAVE),
        )
        in docker_app.mounts
    )

    # Backup not added
    assert "/backup" not in [mount.target for mount in docker_app.mounts]


@pytest.mark.usefixtures("path_extern")
def test_app_map_homeassistant_folder(
    coresys: CoreSys, addonsdata_system: dict[str, Data]
):
    """Test mounts for app which maps homeassistant folder."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].append("homeassistant_config")
    docker_app = get_docker_app(coresys, addonsdata_system, config)

    # Home Assistant config folder mounted to /homeassistant, not /config
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_homeassistant.as_posix(),
            target="/homeassistant",
            read_only=True,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_app_map_app_configs_folder(
    coresys: CoreSys, addonsdata_system: dict[str, Data]
):
    """Test mounts for app which maps app configs folder."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].append("all_addon_configs")
    docker_app = get_docker_app(coresys, addonsdata_system, config)

    # App configs folder included
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_app_configs.as_posix(),
            target="/addon_configs",
            read_only=True,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_app_map_app_config_folder(
    coresys: CoreSys, addonsdata_system: dict[str, Data]
):
    """Test mounts for app which maps its own config folder."""
    docker_app = get_docker_app(
        coresys, addonsdata_system, "addon-config-map-addon_config.json"
    )

    # App config folder included
    assert (
        DockerMount(
            type=MountType.BIND,
            source=docker_app.app.path_extern_config.as_posix(),
            target="/config",
            read_only=True,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_app_map_app_config_folder_with_custom_target(
    coresys: CoreSys, addonsdata_system: dict[str, Data]
):
    """Test mounts for app which maps its own config folder and sets target path."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].remove("addon_config")
    config["map"].append(
        {"type": "addon_config", "read_only": False, "path": "/custom/target/path"}
    )
    docker_app = get_docker_app(coresys, addonsdata_system, config)

    # App config folder included
    assert (
        DockerMount(
            type=MountType.BIND,
            source=docker_app.app.path_extern_config.as_posix(),
            target="/custom/target/path",
            read_only=False,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_app_map_data_folder_with_custom_target(
    coresys: CoreSys, addonsdata_system: dict[str, Data]
):
    """Test mounts for app which sets target path for data folder."""
    config = load_json_fixture("addon-config-map-addon_config.json")
    config["map"].append({"type": "data", "path": "/custom/data/path"})
    docker_app = get_docker_app(coresys, addonsdata_system, config)

    # App config folder included
    assert (
        DockerMount(
            type=MountType.BIND,
            source=docker_app.app.path_extern_data.as_posix(),
            target="/custom/data/path",
            read_only=False,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_app_ignore_on_config_map(coresys: CoreSys, addonsdata_system: dict[str, Data]):
    """Test mounts for app don't include app config or homeassistant when config included."""
    config = load_json_fixture("basic-addon-config.json")
    config["map"].extend(["addon_config", "homeassistant_config"])
    docker_app = get_docker_app(coresys, addonsdata_system, config)

    # Config added and is marked rw
    assert (
        DockerMount(
            type=MountType.BIND,
            source=coresys.config.path_extern_homeassistant.as_posix(),
            target="/config",
            read_only=False,
        )
        in docker_app.mounts
    )

    # Mount for app's specific config folder omitted since config in map field
    assert len([mount for mount in docker_app.mounts if mount.target == "/config"]) == 1
    # Home Assistant mount omitted since config in map field
    assert "/homeassistant" not in [mount.target for mount in docker_app.mounts]


@pytest.mark.usefixtures("path_extern")
def test_journald_app(coresys: CoreSys, addonsdata_system: dict[str, Data]):
    """Validate volume for journald option."""
    docker_app = get_docker_app(
        coresys, addonsdata_system, "journald-addon-config.json"
    )

    assert (
        DockerMount(
            type=MountType.BIND,
            source="/var/log/journal",
            target="/var/log/journal",
            read_only=True,
        )
        in docker_app.mounts
    )
    assert (
        DockerMount(
            type=MountType.BIND,
            source="/run/log/journal",
            target="/run/log/journal",
            read_only=True,
        )
        in docker_app.mounts
    )


@pytest.mark.usefixtures("path_extern")
def test_not_journald_app(coresys: CoreSys, addonsdata_system: dict[str, Data]):
    """Validate journald option defaults off."""
    docker_app = get_docker_app(coresys, addonsdata_system, "basic-addon-config.json")

    assert "/var/log/journal" not in [mount.target for mount in docker_app.mounts]


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_app_run_docker_error(
    coresys: CoreSys, addonsdata_system: dict[str, Data]
):
    """Test docker error when app is run."""
    await coresys.dbus.timedate.connect(coresys.dbus.bus)
    coresys.docker.containers.create.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "missing"}
    )
    docker_app = get_docker_app(coresys, addonsdata_system, "basic-addon-config.json")

    with (
        patch.object(DockerApp, "stop"),
        patch.object(
            AppOptions, "validate", new=PropertyMock(return_value=lambda _: None)
        ),
        pytest.raises(DockerNotFound),
    ):
        await docker_app.run()

    assert (
        Issue(IssueType.MISSING_IMAGE, ContextType.ADDON, reference="test_addon")
        in coresys.resolution.issues
    )


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_app_run_add_host_error(
    coresys: CoreSys, addonsdata_system: dict[str, Data], capture_exception: Mock
):
    """Test error adding host when app is run."""
    await coresys.dbus.timedate.connect(coresys.dbus.bus)
    docker_app = get_docker_app(coresys, addonsdata_system, "basic-addon-config.json")

    with (
        patch.object(DockerApp, "stop"),
        patch.object(
            AppOptions, "validate", new=PropertyMock(return_value=lambda _: None)
        ),
        patch.object(PluginDns, "add_host", side_effect=(err := CoreDNSError())),
    ):
        await docker_app.run()

        capture_exception.assert_called_once_with(err)


async def test_app_stop_delete_host_error(
    coresys: CoreSys, addonsdata_system: dict[str, Data], capture_exception: Mock
):
    """Test error deleting host when app is stopped."""
    docker_app = get_docker_app(coresys, addonsdata_system, "basic-addon-config.json")

    with (
        patch.object(
            DockerApp,
            "ip_address",
            new=PropertyMock(return_value=IPv4Address("172.30.33.1")),
        ),
        patch.object(PluginDns, "delete_host", side_effect=(err := CoreDNSError())),
    ):
        await docker_app.stop()

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


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
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
async def test_app_new_device(
    coresys: CoreSys,
    install_app_ssh: App,
    container: MagicMock,
    docker: DockerAPI,
    dev_path: str,
    cgroup: str,
    is_os: bool,
):
    """Test new device that is listed in static devices."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_app_ssh.data["devices"] = [dev_path]
    container.id = 123
    docker._info = replace(docker.info, cgroup=cgroup)  # pylint: disable=protected-access

    with (
        patch.object(App, "write_options"),
        patch.object(OSManager, "available", new=PropertyMock(return_value=is_os)),
        patch.object(
            CGroup, "add_devices_allowed", new_callable=AsyncMock
        ) as add_devices,
    ):
        await install_app_ssh.start()

        await asyncio.gather(
            *coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, TEST_HW_DEVICE)
        )

        add_devices.assert_called_once_with(123, "c 0:0 rwm")


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
@pytest.mark.parametrize("dev_path", [TEST_DEV_PATH, TEST_SYSFS_PATH])
async def test_app_new_device_no_haos(
    coresys: CoreSys, install_app_ssh: App, docker: DockerAPI, dev_path: str
):
    """Test new device that is listed in static devices on non HAOS system with CGroup V2."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_app_ssh.data["devices"] = [dev_path]
    docker._info = replace(docker.info, cgroup="2")  # pylint: disable=protected-access

    with (
        patch.object(App, "write_options"),
        patch.object(OSManager, "available", new=PropertyMock(return_value=False)),
        patch.object(
            CGroup, "add_devices_allowed", new_callable=AsyncMock
        ) as add_devices,
    ):
        await install_app_ssh.start()

        await asyncio.gather(
            *coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, TEST_HW_DEVICE)
        )

        add_devices.assert_not_called()

    # Issue added with hardware event since access cannot be added dynamically
    assert install_app_ssh.device_access_missing_issue in coresys.resolution.issues
    assert (
        Suggestion(
            SuggestionType.EXECUTE_RESTART, ContextType.ADDON, reference="local_ssh"
        )
        in coresys.resolution.suggestions
    )

    # Stopping and removing the container clears it as access granted on next start
    await install_app_ssh.stop()
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


async def test_ulimits_integration(coresys: CoreSys, install_app_ssh: App):
    """Test ulimits integration with Docker app."""
    docker_app = DockerApp(coresys, install_app_ssh)

    # Test default case (no ulimits, no realtime)
    assert docker_app.ulimits is None

    # Test with realtime enabled (should have built-in ulimits)
    install_app_ssh.data["realtime"] = True
    ulimits = docker_app.ulimits
    assert ulimits is not None
    assert len(ulimits) == 2
    # Check for rtprio limit
    rtprio_limit = next((u for u in ulimits if u.name == "rtprio"), None)
    assert rtprio_limit is not None
    assert rtprio_limit.soft == 90
    assert rtprio_limit.hard == 99
    # Check for memlock limit
    memlock_limit = next((u for u in ulimits if u.name == "memlock"), None)
    assert memlock_limit is not None
    assert memlock_limit.soft == 128 * 1024 * 1024
    assert memlock_limit.hard == 128 * 1024 * 1024

    # Test with configurable ulimits (simple format)
    install_app_ssh.data["realtime"] = False
    install_app_ssh.data["ulimits"] = {"nofile": 65535, "nproc": 32768}
    ulimits = docker_app.ulimits
    assert ulimits is not None
    assert len(ulimits) == 2

    nofile_limit = next((u for u in ulimits if u.name == "nofile"), None)
    assert nofile_limit is not None
    assert nofile_limit.soft == 65535
    assert nofile_limit.hard == 65535

    nproc_limit = next((u for u in ulimits if u.name == "nproc"), None)
    assert nproc_limit is not None
    assert nproc_limit.soft == 32768
    assert nproc_limit.hard == 32768

    # Test with configurable ulimits (detailed format)
    install_app_ssh.data["ulimits"] = {
        "nofile": {"soft": 20000, "hard": 40000},
        "memlock": {"soft": 67108864, "hard": 134217728},
    }
    ulimits = docker_app.ulimits
    assert ulimits is not None
    assert len(ulimits) == 2

    nofile_limit = next((u for u in ulimits if u.name == "nofile"), None)
    assert nofile_limit is not None
    assert nofile_limit.soft == 20000
    assert nofile_limit.hard == 40000

    memlock_limit = next((u for u in ulimits if u.name == "memlock"), None)
    assert memlock_limit is not None
    assert memlock_limit.soft == 67108864
    assert memlock_limit.hard == 134217728

    # Test mixed format and realtime (realtime + custom ulimits)
    install_app_ssh.data["realtime"] = True
    install_app_ssh.data["ulimits"] = {
        "nofile": 65535,
        "core": {"soft": 0, "hard": 0},  # Disable core dumps
    }
    ulimits = docker_app.ulimits
    assert ulimits is not None
    assert (
        len(ulimits) == 4
    )  # rtprio, memlock (from realtime) + nofile, core (from config)

    # Check realtime limits still present
    rtprio_limit = next((u for u in ulimits if u.name == "rtprio"), None)
    assert rtprio_limit is not None

    # Check custom limits added
    nofile_limit = next((u for u in ulimits if u.name == "nofile"), None)
    assert nofile_limit is not None
    assert nofile_limit.soft == 65535
    assert nofile_limit.hard == 65535

    core_limit = next((u for u in ulimits if u.name == "core"), None)
    assert core_limit is not None
    assert core_limit.soft == 0
    assert core_limit.hard == 0
