"""Test the require_running_system API guard.

Covers the start/restart/rebuild/update routes gated by
supervisor.api.utils.require_running_system: they must reject the call with
a 400 and the system_not_ready_error error_key - and must not invoke the
underlying business-logic method - whenever Supervisor isn't in
CoreState.RUNNING (e.g. while still booting, or while frozen for a backup
restore).
"""

from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.apps.app import App
from supervisor.apps.manager import AppManager
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.plugins.audio import PluginAudio
from supervisor.plugins.cli import PluginCli
from supervisor.plugins.dns import PluginDns
from supervisor.plugins.multicast import PluginMulticast
from supervisor.plugins.observer import PluginObserver

from ..const import TEST_ADDON_SLUG

# States that must be rejected. Not exhaustive (e.g. omits INITIALIZE,
# SHUTDOWN, STOPPING, CLOSE) but covers the two scenarios called out in the
# require_running_system docstring: still booting, and restoring a backup.
BLOCKED_STATES = [CoreState.SETUP, CoreState.STARTUP, CoreState.FREEZE]


async def _assert_blocked(resp, mocked: AsyncMock) -> None:
    """Assert the call was rejected before reaching the business logic."""
    assert resp.status == 400
    body = await resp.json()
    assert body["error_key"] == "system_not_ready_error"
    mocked.assert_not_called()


@pytest.mark.parametrize("blocked_state", BLOCKED_STATES)
@pytest.mark.parametrize("method", ["start", "restart", "rebuild"])
async def test_app_lifecycle_blocked_when_not_running(
    app_api_client_with_root: tuple[TestClient, str],
    install_app_ssh: App,
    coresys: CoreSys,
    method: str,
    blocked_state: CoreState,
):
    """Test app start/restart/rebuild are rejected unless Supervisor is running."""
    client, root = app_api_client_with_root
    await coresys.core.set_state(blocked_state)

    with patch.object(App, method, new=AsyncMock()) as mocked:
        resp = await client.post(f"{root}/{TEST_ADDON_SLUG}/{method}")

    await _assert_blocked(resp, mocked)


@pytest.mark.parametrize("blocked_state", BLOCKED_STATES)
async def test_app_update_blocked_when_not_running(
    store_app_api_client_with_root: tuple[TestClient, str],
    install_app_ssh: App,
    coresys: CoreSys,
    blocked_state: CoreState,
):
    """Test app update (via the store API) is rejected unless Supervisor is running."""
    client, root = store_app_api_client_with_root
    await coresys.core.set_state(blocked_state)

    with patch.object(AppManager, "update", new=AsyncMock()) as mocked:
        resp = await client.post(f"/{root}/{TEST_ADDON_SLUG}/update")

    await _assert_blocked(resp, mocked)


@pytest.mark.parametrize("blocked_state", BLOCKED_STATES)
@pytest.mark.parametrize("method", ["start", "restart", "rebuild", "update"])
async def test_core_lifecycle_blocked_when_not_running(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    method: str,
    blocked_state: CoreState,
):
    """Test Core start/restart/rebuild/update are rejected unless Supervisor is running."""
    client, root = core_api_client_with_root
    await coresys.core.set_state(blocked_state)

    with patch.object(HomeAssistantCore, method, new=AsyncMock()) as mocked:
        resp = await client.post(f"{root}/{method}")

    await _assert_blocked(resp, mocked)


@pytest.mark.parametrize("blocked_state", BLOCKED_STATES)
@pytest.mark.parametrize(
    ("plugin_path", "plugin_class", "method"),
    [
        ("audio", PluginAudio, "update"),
        ("audio", PluginAudio, "restart"),
        ("dns", PluginDns, "update"),
        ("dns", PluginDns, "restart"),
        ("multicast", PluginMulticast, "update"),
        ("multicast", PluginMulticast, "restart"),
        ("cli", PluginCli, "update"),
        ("observer", PluginObserver, "update"),
    ],
)
async def test_plugin_lifecycle_blocked_when_not_running(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    plugin_path: str,
    plugin_class: type,
    method: str,
    blocked_state: CoreState,
):
    """Test plugin update/restart routes are rejected unless Supervisor is running."""
    client, prefix = api_client_with_prefix
    await coresys.core.set_state(blocked_state)

    with patch.object(plugin_class, method, new=AsyncMock()) as mocked:
        resp = await client.post(f"{prefix}/{plugin_path}/{method}")

    await _assert_blocked(resp, mocked)
