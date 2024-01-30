"""Test addons api."""

import asyncio
from unittest.mock import MagicMock, PropertyMock, patch

from aiohttp.test_utils import TestClient

from supervisor.addons.addon import Addon
from supervisor.addons.build import AddonBuild
from supervisor.arch import CpuArch
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.store.repository import Repository

from ..const import TEST_ADDON_SLUG


def _create_test_event(name: str, state: ContainerState) -> DockerContainerStateEvent:
    """Create a container state event."""
    return DockerContainerStateEvent(
        name=name,
        state=state,
        id="abc123",
        time=1,
    )


async def test_addons_info(
    api_client: TestClient, coresys: CoreSys, install_addon_ssh: Addon
):
    """Test getting addon info."""
    install_addon_ssh.state = AddonState.STOPPED
    install_addon_ssh.ingress_panel = True
    install_addon_ssh.protected = True
    install_addon_ssh.watchdog = False

    resp = await api_client.get(f"/addons/{TEST_ADDON_SLUG}/info")
    result = await resp.json()
    assert result["data"]["version_latest"] == "9.2.1"
    assert result["data"]["version"] == "9.2.1"
    assert result["data"]["state"] == "stopped"
    assert result["data"]["ingress_panel"] is True
    assert result["data"]["protected"] is True
    assert result["data"]["watchdog"] is False


# DEPRECATED - Remove with legacy routing logic on 1/2023
async def test_addons_info_not_installed(
    api_client: TestClient, coresys: CoreSys, repository: Repository
):
    """Test getting addon info for not installed addon."""
    resp = await api_client.get(f"/addons/{TEST_ADDON_SLUG}/info")
    result = await resp.json()
    assert result["data"]["version_latest"] == "9.2.1"
    assert result["data"]["version"] is None
    assert result["data"]["state"] == "unknown"
    assert result["data"]["update_available"] is False
    assert result["data"]["options"] == {
        "authorized_keys": [],
        "apks": [],
        "password": "",
        "server": {"tcp_forwarding": False},
    }


async def test_api_addon_logs(
    api_client: TestClient, docker_logs: MagicMock, install_addon_ssh: Addon
):
    """Test addon logs."""
    resp = await api_client.get("/addons/local_ssh/logs")
    assert resp.status == 200
    assert resp.content_type == "application/octet-stream"
    content = await resp.read()
    assert content.split(b"\n")[0:2] == [
        b"\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os\x1b[0m",
        b"\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os/AppArmor\x1b[0m",
    ]


async def test_api_addon_start_healthcheck(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test starting an addon waits for healthy."""
    install_addon_ssh.path_data.mkdir()
    container.attrs["Config"] = {"Healthcheck": "exists"}
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    state_changes: list[AddonState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes
        await asyncio.sleep(0.01)

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_addon_ssh.state)

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with patch.object(DockerAddon, "run", new=container_events_task):
        resp = await api_client.post("/addons/local_ssh/start")

    assert state_changes == [AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert resp.status == 200


async def test_api_addon_restart_healthcheck(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test restarting an addon waits for healthy."""
    install_addon_ssh.path_data.mkdir()
    container.attrs["Config"] = {"Healthcheck": "exists"}
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    state_changes: list[AddonState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes
        await asyncio.sleep(0.01)

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_addon_ssh.state)

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with patch.object(DockerAddon, "run", new=container_events_task):
        resp = await api_client.post("/addons/local_ssh/restart")

    assert state_changes == [AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert resp.status == 200


async def test_api_addon_rebuild_healthcheck(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test rebuilding an addon waits for healthy."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container.status = "running"
    install_addon_ssh.path_data.mkdir()
    container.attrs["Config"] = {"Healthcheck": "exists"}
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STARTUP

    state_changes: list[AddonState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        )
        state_changes.append(install_addon_ssh.state)

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_addon_ssh.state)
        await asyncio.sleep(0)

        await install_addon_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with patch.object(
        AddonBuild, "is_valid", new=PropertyMock(return_value=True)
    ), patch.object(DockerAddon, "is_running", return_value=False), patch.object(
        Addon, "need_build", new=PropertyMock(return_value=True)
    ), patch.object(
        CpuArch, "supported", new=PropertyMock(return_value=["amd64"])
    ), patch.object(DockerAddon, "run", new=container_events_task):
        resp = await api_client.post("/addons/local_ssh/rebuild")

    assert state_changes == [AddonState.STOPPED, AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert resp.status == 200
