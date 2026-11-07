"""Test the API endpoints shared by all plugins."""

from unittest.mock import AsyncMock, PropertyMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import DockerError
from supervisor.host.const import LogFormatter

from tests.common import load_json_fixture

PLUGINS = ["audio", "cli", "dns", "multicast", "observer"]


@pytest.fixture(name="running_container")
def fixture_running_container(container: DockerContainer) -> DockerContainer:
    """Report the plugin container as running."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    return container


@pytest.mark.parametrize("slug", PLUGINS)
async def test_api_plugin_info(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys, slug: str
) -> None:
    """Test plugin info includes the common version fields."""
    api_client, prefix = api_client_with_prefix
    plugin = getattr(coresys.plugins, slug)
    plugin.version = AwesomeVersion("2024.01.0")

    with patch.object(
        type(plugin),
        "latest_version",
        new=PropertyMock(return_value=AwesomeVersion("2024.02.0")),
    ):
        resp = await api_client.get(f"{prefix}/{slug}/info")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["version"] == "2024.01.0"
    assert result["data"]["version_latest"] == "2024.02.0"
    assert result["data"]["update_available"] is True


@pytest.mark.parametrize("slug", PLUGINS)
async def test_api_plugin_logs(advanced_logs_tester, slug: str) -> None:
    """Test plugin logs."""
    await advanced_logs_tester(f"/{slug}", f"hassio_{slug}", LogFormatter.VERBOSE)


@pytest.mark.parametrize("slug", PLUGINS)
async def test_api_plugin_stats_v1(
    api_client: TestClient, running_container: DockerContainer, slug: str
) -> None:
    """Test plugin stats on the v1 API."""
    running_container.stats = AsyncMock(
        return_value=[load_json_fixture("container_stats.json")]
    )

    resp = await api_client.get(f"/{slug}/stats")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000


@pytest.mark.usefixtures("running_container")
@pytest.mark.parametrize("slug", PLUGINS)
async def test_api_plugin_stats_v2(api_client_v2: TestClient, slug: str) -> None:
    """Test plugin stats on the v2 API are always one-shot."""
    stats_fixture = load_json_fixture("container_stats.json")
    del stats_fixture["precpu_stats"]

    with patch.object(
        DockerAPI, "_query_one_shot_stats", AsyncMock(return_value=stats_fixture)
    ):
        resp = await api_client_v2.get(f"/v2/{slug}/stats")

    assert resp.status == 200
    result = await resp.json()
    assert "cpu_percent" not in result["data"]
    assert result["data"]["memory_usage"] == 59700000


@pytest.mark.usefixtures("tmp_supervisor_data")
@pytest.mark.parametrize("slug", PLUGINS)
async def test_api_plugin_restart(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys, slug: str
) -> None:
    """Test plugin restart."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)

    with patch.object(DockerInterface, "restart") as restart:
        resp = await api_client.post(f"{prefix}/{slug}/restart")

    assert resp.status == 200
    restart.assert_called_once()


@pytest.mark.usefixtures("tmp_supervisor_data")
@pytest.mark.parametrize(
    ("slug", "error_key"),
    [
        pytest.param("audio", "audio_restart_error", id="audio"),
        pytest.param("cli", "cli_restart_error", id="cli"),
        pytest.param("dns", "coredns_restart_error", id="dns"),
        pytest.param("multicast", "multicast_restart_error", id="multicast"),
        pytest.param("observer", "observer_restart_error", id="observer"),
    ],
)
async def test_api_plugin_restart_failed(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    slug: str,
    error_key: str,
) -> None:
    """Test a failed plugin operation returns its keyed error as a server error."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)

    with patch.object(DockerInterface, "restart", side_effect=DockerError):
        resp = await api_client.post(f"{prefix}/{slug}/restart")

    assert resp.status == 500
    result = await resp.json()
    assert result["error_key"] == error_key
    assert result["message"].endswith("Check Supervisor logs for details")


@pytest.mark.parametrize("slug", PLUGINS)
async def test_api_plugin_update(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys, slug: str
) -> None:
    """Test plugin update defaults to the latest version."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)
    plugin = getattr(coresys.plugins, slug)
    plugin.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.02.0")),
        ),
        patch.object(type(plugin), "update") as update,
    ):
        resp = await api_client.post(f"{prefix}/{slug}/update")

    assert resp.status == 200
    update.assert_called_once_with(AwesomeVersion("2024.02.0"))


@pytest.mark.parametrize(
    ("slug", "error_key"),
    [
        pytest.param("audio", "audio_update_already_installed_error", id="audio"),
        pytest.param("cli", "cli_update_already_installed_error", id="cli"),
        pytest.param("dns", "coredns_update_already_installed_error", id="dns"),
        pytest.param(
            "multicast", "multicast_update_already_installed_error", id="multicast"
        ),
        pytest.param(
            "observer", "observer_update_already_installed_error", id="observer"
        ),
    ],
)
async def test_api_plugin_update_same_version(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    slug: str,
    error_key: str,
) -> None:
    """Test plugin update is rejected for the version already in use."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)
    getattr(coresys.plugins, slug).version = AwesomeVersion("2024.01.0")

    resp = await api_client.post(
        f"{prefix}/{slug}/update", json={"version": "2024.01.0"}
    )

    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == error_key
    assert result["extra_fields"] == {"version": "2024.01.0"}


@pytest.mark.parametrize(
    ("slug", "error_key"),
    [
        pytest.param("audio", "audio_not_installed_error", id="audio"),
        pytest.param("cli", "cli_not_installed_error", id="cli"),
        pytest.param("dns", "coredns_not_installed_error", id="dns"),
        pytest.param("multicast", "multicast_not_installed_error", id="multicast"),
        pytest.param("observer", "observer_not_installed_error", id="observer"),
    ],
)
async def test_api_plugin_update_not_installed(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    slug: str,
    error_key: str,
) -> None:
    """Test plugin update is rejected while the plugin is not installed."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)
    plugin = getattr(coresys.plugins, slug)
    plugin._data.pop("version", None)  # pylint: disable=protected-access

    with patch.object(
        type(plugin),
        "latest_version",
        new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
    ):
        resp = await api_client.post(f"{prefix}/{slug}/update")

    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == error_key
