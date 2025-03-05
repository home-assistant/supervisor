"""Test addons api."""

import asyncio
from unittest.mock import MagicMock, PropertyMock, patch

from aiohttp import ClientResponse
from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.addons.build import AddonBuild
from supervisor.arch import CpuArch
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import HassioError
from supervisor.store.repository import Repository

from ..const import TEST_ADDON_SLUG
from . import common_test_api_advanced_logs


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
    api_client: TestClient, journald_logs: MagicMock, install_addon_ssh: Addon
):
    """Test addon logs."""
    await common_test_api_advanced_logs(
        "/addons/local_ssh", "addon_local_ssh", api_client, journald_logs
    )


async def test_api_addon_logs_not_installed(api_client: TestClient):
    """Test error is returned for non-existing add-on."""
    resp = await api_client.get("/addons/hic_sunt_leones/logs")

    assert resp.status == 404
    assert resp.content_type == "text/plain"
    content = await resp.text()
    assert content == "Addon hic_sunt_leones does not exist"


async def test_api_addon_logs_error(
    api_client: TestClient,
    journald_logs: MagicMock,
    docker_logs: MagicMock,
    install_addon_ssh: Addon,
):
    """Test errors are properly handled for add-on logs."""
    journald_logs.side_effect = HassioError("Something bad happened!")
    resp = await api_client.get("/addons/local_ssh/logs")

    assert resp.status == 400
    assert resp.content_type == "text/plain"
    content = await resp.text()
    assert content == "Something bad happened!"


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

    with (
        patch.object(AddonBuild, "is_valid", return_value=True),
        patch.object(DockerAddon, "is_running", return_value=False),
        patch.object(Addon, "need_build", new=PropertyMock(return_value=True)),
        patch.object(CpuArch, "supported", new=PropertyMock(return_value=["amd64"])),
        patch.object(DockerAddon, "run", new=container_events_task),
    ):
        resp = await api_client.post("/addons/local_ssh/rebuild")

    assert state_changes == [AddonState.STOPPED, AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert resp.status == 200


async def test_api_addon_uninstall(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_example: Addon,
    tmp_supervisor_data,
    path_extern,
):
    """Test uninstall."""
    install_addon_example.data["map"].append(
        {"type": "addon_config", "read_only": False}
    )
    install_addon_example.path_config.mkdir()
    (test_file := install_addon_example.path_config / "test.txt").touch()

    resp = await api_client.post("/addons/local_example/uninstall")
    assert resp.status == 200
    assert not coresys.addons.get("local_example", local_only=True)
    assert test_file.exists()


async def test_api_addon_uninstall_remove_config(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_example: Addon,
    tmp_supervisor_data,
    path_extern,
):
    """Test uninstall and remove config."""
    install_addon_example.data["map"].append(
        {"type": "addon_config", "read_only": False}
    )
    (test_folder := install_addon_example.path_config).mkdir()
    (install_addon_example.path_config / "test.txt").touch()

    resp = await api_client.post(
        "/addons/local_example/uninstall", json={"remove_config": True}
    )
    assert resp.status == 200
    assert not coresys.addons.get("local_example", local_only=True)
    assert not test_folder.exists()


async def test_api_addon_system_managed(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_example: Addon,
    caplog: pytest.LogCaptureFixture,
    tmp_supervisor_data,
    path_extern,
):
    """Test setting system managed for an addon."""
    install_addon_example.data["ingress"] = False

    # Not system managed
    resp = await api_client.get("/addons")
    body = await resp.json()
    assert body["data"]["addons"][0]["slug"] == "local_example"
    assert body["data"]["addons"][0]["system_managed"] is False

    resp = await api_client.get("/addons/local_example/info")
    body = await resp.json()
    assert body["data"]["system_managed"] is False
    assert body["data"]["system_managed_config_entry"] is None

    # Mark as system managed
    coresys.addons.data.save_data.reset_mock()
    resp = await api_client.post(
        "/addons/local_example/sys_options",
        json={"system_managed": True, "system_managed_config_entry": "abc123"},
    )
    assert resp.status == 200
    coresys.addons.data.save_data.assert_called_once()

    resp = await api_client.get("/addons")
    body = await resp.json()
    assert body["data"]["addons"][0]["system_managed"] is True

    resp = await api_client.get("/addons/local_example/info")
    body = await resp.json()
    assert body["data"]["system_managed"] is True
    assert body["data"]["system_managed_config_entry"] == "abc123"

    # Revert. Log that cannot have a config entry if not system managed
    coresys.addons.data.save_data.reset_mock()
    resp = await api_client.post(
        "/addons/local_example/sys_options",
        json={"system_managed": False, "system_managed_config_entry": "abc123"},
    )
    assert resp.status == 200
    coresys.addons.data.save_data.assert_called_once()
    assert "Ignoring system managed config entry" in caplog.text

    resp = await api_client.get("/addons")
    body = await resp.json()
    assert body["data"]["addons"][0]["system_managed"] is False

    resp = await api_client.get("/addons/local_example/info")
    body = await resp.json()
    assert body["data"]["system_managed"] is False
    assert body["data"]["system_managed_config_entry"] is None


async def test_addon_options_boot_mode_manual_only_invalid(
    api_client: TestClient, install_addon_example: Addon
):
    """Test changing boot mode is invalid if set to manual only."""
    install_addon_example.data["ingress"] = False
    resp = await api_client.get("/addons/local_example/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["boot"] == "manual"
    assert body["data"]["boot_config"] == "manual_only"

    resp = await api_client.post("/addons/local_example/options", json={"boot": "auto"})
    assert resp.status == 400
    body = await resp.json()
    assert (
        body["message"]
        == "Addon local_example boot option is set to manual_only so it cannot be changed"
    )


async def get_message(resp: ClientResponse, json_expected: bool) -> str:
    """Get message from response based on response type."""
    if json_expected:
        body = await resp.json()
        return body["message"]
    return await resp.text()


@pytest.mark.parametrize(
    ("method", "url", "json_expected"),
    [
        ("get", "/addons/bad/info", True),
        ("post", "/addons/bad/uninstall", True),
        ("post", "/addons/bad/start", True),
        ("post", "/addons/bad/stop", True),
        ("post", "/addons/bad/restart", True),
        ("post", "/addons/bad/options", True),
        ("post", "/addons/bad/sys_options", True),
        ("post", "/addons/bad/options/validate", True),
        ("post", "/addons/bad/rebuild", True),
        ("post", "/addons/bad/stdin", True),
        ("post", "/addons/bad/security", True),
        ("get", "/addons/bad/stats", True),
        ("get", "/addons/bad/logs", False),
        ("get", "/addons/bad/logs/follow", False),
        ("get", "/addons/bad/logs/boots/1", False),
        ("get", "/addons/bad/logs/boots/1/follow", False),
    ],
)
async def test_addon_not_found(
    api_client: TestClient, method: str, url: str, json_expected: bool
):
    """Test addon not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    assert await get_message(resp, json_expected) == "Addon bad does not exist"


@pytest.mark.parametrize(
    ("method", "url", "json_expected"),
    [
        ("post", "/addons/local_ssh/uninstall", True),
        ("post", "/addons/local_ssh/start", True),
        ("post", "/addons/local_ssh/stop", True),
        ("post", "/addons/local_ssh/restart", True),
        ("post", "/addons/local_ssh/options", True),
        ("post", "/addons/local_ssh/sys_options", True),
        ("post", "/addons/local_ssh/options/validate", True),
        ("post", "/addons/local_ssh/rebuild", True),
        ("post", "/addons/local_ssh/stdin", True),
        ("post", "/addons/local_ssh/security", True),
        ("get", "/addons/local_ssh/stats", True),
        ("get", "/addons/local_ssh/logs", False),
        ("get", "/addons/local_ssh/logs/follow", False),
        ("get", "/addons/local_ssh/logs/boots/1", False),
        ("get", "/addons/local_ssh/logs/boots/1/follow", False),
    ],
)
@pytest.mark.usefixtures("repository")
async def test_addon_not_installed(
    api_client: TestClient, method: str, url: str, json_expected: bool
):
    """Test addon not installed error."""
    resp = await api_client.request(method, url)
    assert resp.status == 400
    assert await get_message(resp, json_expected) == "Addon is not installed"
