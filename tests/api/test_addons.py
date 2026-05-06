"""Test apps api."""

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import PurePath
from unittest.mock import MagicMock, PropertyMock, patch

import aiodocker
from aiodocker.containers import DockerContainer
from aiohttp import ClientResponse
from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import App
from supervisor.addons.build import AppBuild
from supervisor.arch import CpuArchManager
from supervisor.const import AppState, CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerApp
from supervisor.docker.const import ContainerState
from supervisor.docker.manager import CommandReturn
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import HassioError
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


async def test_apps_info(
    app_api_client_with_root: tuple[TestClient, str], install_app_ssh: App
):
    """Test getting app info."""
    client, root = app_api_client_with_root
    install_app_ssh.state = AppState.STOPPED
    install_app_ssh.ingress_panel = True
    install_app_ssh.protected = True
    install_app_ssh.watchdog = False

    resp = await client.get(f"{root}/{TEST_ADDON_SLUG}/info")
    result = await resp.json()
    assert result["data"]["version_latest"] == "9.2.1"
    assert result["data"]["version"] == "9.2.1"
    assert result["data"]["state"] == "stopped"
    assert result["data"]["ingress_panel"] is True
    assert result["data"]["protected"] is True
    assert result["data"]["watchdog"] is False


# DEPRECATED - Remove with legacy routing logic on 1/2023
async def test_apps_info_not_installed(
    api_client: TestClient, coresys: CoreSys, test_repository: Repository
):
    """Test getting app info for not installed app."""
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


@pytest.mark.usefixtures("install_app_ssh")
async def test_api_app_logs(
    advanced_logs_tester: Callable[[str, str], Awaitable[None]],
):
    """Test app logs."""
    await advanced_logs_tester(
        "/addons/local_ssh", "addon_local_ssh", v2_path_prefix="/apps/local_ssh"
    )


async def test_api_app_logs_not_installed(api_client: TestClient):
    """Test error is returned for non-existing app."""
    resp = await api_client.get("/addons/hic_sunt_leones/logs")

    assert resp.status == 404
    assert resp.content_type == "text/plain"
    content = await resp.text()
    assert content == "App hic_sunt_leones does not exist"


@pytest.mark.usefixtures("docker_logs", "install_app_ssh")
async def test_api_app_logs_error(api_client: TestClient, journald_logs: MagicMock):
    """Test errors are properly handled for app logs."""
    journald_logs.side_effect = HassioError("Something bad happened!")
    resp = await api_client.get("/addons/local_ssh/logs")

    assert resp.status == 400
    assert resp.content_type == "text/plain"
    content = await resp.text()
    assert content == "Something bad happened!"


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_start_healthcheck(
    api_client: TestClient, install_app_ssh: App, container: DockerContainer
):
    """Test starting an app waits for healthy."""
    install_app_ssh.path_data.mkdir()
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    state_changes: list[AppState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes
        await asyncio.sleep(0)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_app_ssh.state)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with patch.object(DockerApp, "run", new=container_events_task):
        resp = await api_client.post("/addons/local_ssh/start")

    assert state_changes == [AppState.STARTUP]
    assert install_app_ssh.state == AppState.STARTED
    assert resp.status == 200


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_restart_healthcheck(
    api_client: TestClient, install_app_ssh: App, container: DockerContainer
):
    """Test restarting an app waits for healthy."""
    install_app_ssh.path_data.mkdir()
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    state_changes: list[AppState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes
        await asyncio.sleep(0)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_app_ssh.state)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with patch.object(DockerApp, "run", new=container_events_task):
        resp = await api_client.post("/addons/local_ssh/restart")

    assert state_changes == [AppState.STARTUP]
    assert install_app_ssh.state == AppState.STARTED
    assert resp.status == 200


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_rebuild_healthcheck(
    api_client: TestClient,
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
):
    """Test rebuilding an app waits for healthy."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    install_app_ssh.path_data.mkdir()
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STARTUP

    state_changes: list[AppState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        )
        state_changes.append(install_app_ssh.state)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_app_ssh.state)
        await asyncio.sleep(0)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with (
        patch.object(AppBuild, "is_valid", return_value=True),
        patch.object(DockerApp, "is_running", return_value=False),
        patch.object(App, "need_build", new=PropertyMock(return_value=True)),
        patch.object(
            CpuArchManager, "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(DockerApp, "run", new=container_events_task),
        patch.object(
            coresys.docker,
            "run_command",
            return_value=CommandReturn(0, ["Build successful"]),
        ),
        patch.object(
            DockerApp, "healthcheck", new=PropertyMock(return_value={"exists": True})
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        resp = await api_client.post("/addons/local_ssh/rebuild")

    assert state_changes == [AppState.STOPPED, AppState.STARTUP]
    assert install_app_ssh.state == AppState.STARTED
    assert resp.status == 200


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_rebuild_force(
    api_client: TestClient,
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
):
    """Test rebuilding an image-based app with force parameter."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    install_app_ssh.path_data.mkdir()
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STARTUP

    state_changes: list[AppState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        )
        state_changes.append(install_app_ssh.state)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        )
        state_changes.append(install_app_ssh.state)
        await asyncio.sleep(0)

        await install_app_ssh.container_state_changed(
            _create_test_event(f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    # Test 1: Without force, image-based app should fail
    with (
        patch.object(AppBuild, "is_valid", return_value=True),
        patch.object(DockerApp, "is_running", return_value=False),
        patch.object(
            App, "need_build", new=PropertyMock(return_value=False)
        ),  # Image-based
        patch.object(
            CpuArchManager, "supported", new=PropertyMock(return_value=["amd64"])
        ),
    ):
        resp = await api_client.post("/addons/local_ssh/rebuild")

    assert resp.status == 400
    result = await resp.json()
    assert "Can't rebuild an image-based app" in result["message"]

    # Reset state for next test
    state_changes.clear()

    # Test 2: With force=True, image-based app should succeed
    with (
        patch.object(AppBuild, "is_valid", return_value=True),
        patch.object(DockerApp, "is_running", return_value=False),
        patch.object(
            App, "need_build", new=PropertyMock(return_value=False)
        ),  # Image-based
        patch.object(
            CpuArchManager, "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(DockerApp, "run", new=container_events_task),
        patch.object(
            coresys.docker,
            "run_command",
            return_value=CommandReturn(0, ["Build successful"]),
        ),
        patch.object(
            DockerApp, "healthcheck", new=PropertyMock(return_value={"exists": True})
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        resp = await api_client.post("/addons/local_ssh/rebuild", json={"force": True})

    assert state_changes == [AppState.STOPPED, AppState.STARTUP]
    assert install_app_ssh.state == AppState.STARTED
    assert resp.status == 200

    await _container_events_task


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_uninstall(
    app_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_example: App,
):
    """Test uninstall."""
    client, root = app_api_client_with_root
    install_app_example.data["map"].append({"type": "addon_config", "read_only": False})
    install_app_example.path_config.mkdir()
    (test_file := install_app_example.path_config / "test.txt").touch()

    resp = await client.post(f"{root}/local_example/uninstall")
    assert resp.status == 200
    assert not coresys.apps.get("local_example", local_only=True)
    assert test_file.exists()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_uninstall_remove_config(
    app_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_example: App,
):
    """Test uninstall and remove config."""
    client, root = app_api_client_with_root
    install_app_example.data["map"].append({"type": "addon_config", "read_only": False})
    (test_folder := install_app_example.path_config).mkdir()
    (install_app_example.path_config / "test.txt").touch()

    resp = await client.post(
        f"{root}/local_example/uninstall", json={"remove_config": True}
    )
    assert resp.status == 200
    assert not coresys.apps.get("local_example", local_only=True)
    assert not test_folder.exists()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_app_system_managed(
    api_client: TestClient,
    coresys: CoreSys,
    install_app_example: App,
    caplog: pytest.LogCaptureFixture,
):
    """Test setting system managed for an app."""
    install_app_example.data["ingress"] = False

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
    coresys.apps.data.save_data.reset_mock()
    resp = await api_client.post(
        "/addons/local_example/sys_options",
        json={"system_managed": True, "system_managed_config_entry": "abc123"},
    )
    assert resp.status == 200
    coresys.apps.data.save_data.assert_called_once()

    resp = await api_client.get("/addons")
    body = await resp.json()
    assert body["data"]["addons"][0]["system_managed"] is True

    resp = await api_client.get("/addons/local_example/info")
    body = await resp.json()
    assert body["data"]["system_managed"] is True
    assert body["data"]["system_managed_config_entry"] == "abc123"

    # Revert. Log that cannot have a config entry if not system managed
    coresys.apps.data.save_data.reset_mock()
    resp = await api_client.post(
        "/addons/local_example/sys_options",
        json={"system_managed": False, "system_managed_config_entry": "abc123"},
    )
    assert resp.status == 200
    coresys.apps.data.save_data.assert_called_once()
    assert "Ignoring system managed config entry" in caplog.text

    resp = await api_client.get("/addons")
    body = await resp.json()
    assert body["data"]["addons"][0]["system_managed"] is False

    resp = await api_client.get("/addons/local_example/info")
    body = await resp.json()
    assert body["data"]["system_managed"] is False
    assert body["data"]["system_managed_config_entry"] is None


async def test_app_options_boot_mode_manual_only_invalid(
    api_client: TestClient, install_app_example: App
):
    """Test changing boot mode is invalid if set to manual only."""
    install_app_example.data["ingress"] = False
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
        == "App local_example boot option is set to manual_only so it cannot be changed"
    )
    assert body["error_key"] == "addon_boot_config_cannot_change_error"
    assert body["extra_fields"] == {
        "addon": "local_example",
        "boot_config": "manual_only",
    }


async def get_message(resp: ClientResponse, json_expected: bool) -> str:
    """Get message from response based on response type."""
    if json_expected:
        body = await resp.json()
        return body["message"]
    return await resp.text()


@pytest.mark.parametrize(
    ("method", "action", "json_expected"),
    [
        ("get", "bad/info", True),
        ("post", "bad/uninstall", True),
        ("post", "bad/start", True),
        ("post", "bad/stop", True),
        ("post", "bad/restart", True),
        ("post", "bad/options", True),
        ("post", "bad/sys_options", True),
        ("post", "bad/options/validate", True),
        ("post", "bad/rebuild", True),
        ("post", "bad/stdin", True),
        ("post", "bad/security", True),
        ("get", "bad/stats", True),
        ("get", "bad/logs", False),
        ("get", "bad/logs/follow", False),
        ("get", "bad/logs/boots/1", False),
        ("get", "bad/logs/boots/1/follow", False),
    ],
)
async def test_app_not_found(
    app_api_client_with_root: tuple[TestClient, str],
    method: str,
    action: str,
    json_expected: bool,
):
    """Test app not found error."""
    client, root = app_api_client_with_root
    resp = await client.request(method, f"{root}/{action}")
    assert resp.status == 404
    assert await get_message(resp, json_expected) == "App bad does not exist"


@pytest.mark.parametrize(
    ("method", "action", "json_expected"),
    [
        ("post", "local_ssh/uninstall", True),
        ("post", "local_ssh/start", True),
        ("post", "local_ssh/stop", True),
        ("post", "local_ssh/restart", True),
        ("post", "local_ssh/options", True),
        ("post", "local_ssh/sys_options", True),
        ("post", "local_ssh/options/validate", True),
        ("post", "local_ssh/rebuild", True),
        ("post", "local_ssh/stdin", True),
        ("post", "local_ssh/security", True),
        ("get", "local_ssh/stats", True),
        ("get", "local_ssh/logs", False),
        ("get", "local_ssh/logs/follow", False),
        ("get", "local_ssh/logs/boots/1", False),
        ("get", "local_ssh/logs/boots/1/follow", False),
    ],
)
@pytest.mark.usefixtures("test_repository")
async def test_app_not_installed(
    app_api_client_with_root: tuple[TestClient, str],
    method: str,
    action: str,
    json_expected: bool,
):
    """Test app not installed error."""
    client, root = app_api_client_with_root
    resp = await client.request(method, f"{root}/{action}")
    assert resp.status == 400
    assert await get_message(resp, json_expected) == "App is not installed"


async def test_app_set_options(
    app_api_client_with_root: tuple[TestClient, str], install_app_example: App
):
    """Test setting options for an app."""
    client, root = app_api_client_with_root
    resp = await client.post(
        f"{root}/local_example/options", json={"options": {"message": "test"}}
    )
    assert resp.status == 200
    assert install_app_example.options == {"message": "test"}


async def test_app_reset_options(
    app_api_client_with_root: tuple[TestClient, str], install_app_example: App
):
    """Test resetting options for an app to defaults.

    Fixes SUPERVISOR-171F.
    """
    client, root = app_api_client_with_root
    # First set some custom options
    install_app_example.options = {"message": "custom"}
    assert install_app_example.persist["options"] == {"message": "custom"}

    # Reset to defaults by sending null
    resp = await client.post(f"{root}/local_example/options", json={"options": None})
    assert resp.status == 200

    # Persisted options should be empty (meaning defaults will be used)
    assert install_app_example.persist["options"] == {}


@pytest.mark.usefixtures("install_app_example")
async def test_app_set_options_error(api_client: TestClient):
    """Test setting options for an app."""
    resp = await api_client.post(
        "/addons/local_example/options", json={"options": {"message": True}}
    )
    assert resp.status == 400
    body = await resp.json()
    assert (
        body["message"]
        == "App local_example has invalid options: not a valid value. Got {'message': True}"
    )
    assert body["error_key"] == "addon_configuration_invalid_error"
    assert body["extra_fields"] == {
        "addon": "local_example",
        "validation_error": "not a valid value. Got {'message': True}",
    }


async def test_app_start_options_error(
    api_client: TestClient,
    install_app_example: App,
    caplog: pytest.LogCaptureFixture,
):
    """Test error writing options when trying to start app."""
    install_app_example.options = {"message": "hello"}

    # Simulate OS error trying to write the file
    with patch("supervisor.utils.json.atomic_write", side_effect=OSError("fail")):
        resp = await api_client.post("/addons/local_example/start")
        assert resp.status == 500
        body = await resp.json()
        assert (
            body["message"]
            == "An unknown error occurred with app local_example. Check Supervisor logs for details"
        )
        assert body["error_key"] == "addon_unknown_error"
        assert body["extra_fields"] == {
            "addon": "local_example",
        }
        assert "App local_example can't write options" in caplog.text

    # Simulate an update with a breaking change for options schema creating failure on start
    caplog.clear()
    install_app_example.data["schema"] = {"message": "bool"}
    resp = await api_client.post("/addons/local_example/start")
    assert resp.status == 400
    body = await resp.json()
    assert (
        body["message"]
        == "App local_example has invalid options: expected boolean. Got {'message': 'hello'}"
    )
    assert body["error_key"] == "addon_configuration_invalid_error"
    assert body["extra_fields"] == {
        "addon": "local_example",
        "validation_error": "expected boolean. Got {'message': 'hello'}",
    }
    assert (
        "App local_example has invalid options: expected boolean. Got {'message': 'hello'}"
        in caplog.text
    )


@pytest.mark.parametrize(("method", "action"), [("get", "stats"), ("post", "stdin")])
@pytest.mark.usefixtures("install_app_example")
async def test_app_not_running_error(
    app_api_client_with_root: tuple[TestClient, str], method: str, action: str
):
    """Test app not running error for endpoints that require that."""
    client, root = app_api_client_with_root
    with patch.object(App, "with_stdin", new=PropertyMock(return_value=True)):
        resp = await client.request(method, f"{root}/local_example/{action}")

    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "App local_example is not running"
    assert body["error_key"] == "addon_not_running_error"
    assert body["extra_fields"] == {"addon": "local_example"}


@pytest.mark.usefixtures("install_app_example")
async def test_app_write_stdin_not_supported_error(
    app_api_client_with_root: tuple[TestClient, str],
):
    """Test error when trying to write stdin to app that does not support it."""
    client, root = app_api_client_with_root
    resp = await client.post(f"{root}/local_example/stdin")
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "App local_example does not support writing to stdin"
    assert body["error_key"] == "addon_not_supported_write_stdin_error"
    assert body["extra_fields"] == {"addon": "local_example"}


@pytest.mark.usefixtures("install_app_ssh")
async def test_app_rebuild_fails_error(api_client: TestClient, coresys: CoreSys):
    """Test error when build fails during rebuild for app."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.docker.containers.create.side_effect = aiodocker.DockerError(
        500, {"message": "fail"}
    )

    with (
        patch.object(
            CpuArchManager,
            "supported",
            new=PropertyMock(return_value=[CpuArch.AARCH64]),
        ),
        patch.object(
            CpuArchManager, "default", new=PropertyMock(return_value=CpuArch.AARCH64)
        ),
        patch.object(AppBuild, "get_docker_args", return_value={"command": ["build"]}),
    ):
        resp = await api_client.post("/addons/local_ssh/rebuild")
    assert resp.status == 500
    body = await resp.json()
    assert (
        body["message"]
        == "An unknown error occurred while trying to build the image for app local_ssh. Check Supervisor logs for details"
    )
    assert body["error_key"] == "addon_build_failed_unknown_error"
    assert body["extra_fields"] == {
        "addon": "local_ssh",
    }


# ── V2 API tests ──────────────────────────────────────────────────────────────


@pytest.mark.usefixtures("install_app_ssh")
async def test_v2_list_apps_uses_apps_key(api_client_v2: TestClient):
    """V2 GET /v2/apps returns 'apps' key (not 'addons')."""
    resp = await api_client_v2.get("/v2/apps")
    assert resp.status == 200
    body = await resp.json()
    assert "apps" in body["data"]
    assert "addons" not in body["data"]
    assert body["data"]["apps"][0]["slug"] == "local_ssh"
