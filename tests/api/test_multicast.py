"""Test multicast api."""

from unittest.mock import PropertyMock, patch

from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.plugins.multicast import PluginMulticast


async def test_api_multicast_info(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test multicast info reports the enabled state."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/multicast/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["enabled"] is True

    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access
    resp = await api_client.get(f"{prefix}/multicast/info")
    result = await resp.json()
    assert result["data"]["enabled"] is False
    assert result["data"]["update_available"] is False


async def test_api_multicast_options(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test multicast options enable and disable the plugin."""
    api_client, prefix = api_client_with_prefix

    with (
        patch.object(PluginMulticast, "disable") as disable,
        patch.object(PluginMulticast, "enable") as enable,
    ):
        resp = await api_client.post(
            f"{prefix}/multicast/options", json={"enabled": False}
        )
        assert resp.status == 200
        disable.assert_called_once()
        enable.assert_not_called()

        disable.reset_mock()
        resp = await api_client.post(
            f"{prefix}/multicast/options", json={"enabled": True}
        )
        assert resp.status == 200
        enable.assert_called_once()
        disable.assert_not_called()


async def test_api_multicast_disabled_actions(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test restart and update are rejected while the plugin is disabled."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    resp = await api_client.post(f"{prefix}/multicast/restart")
    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == "Multicast plugin is disabled"

    with patch.object(
        PluginMulticast,
        "latest_version",
        new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
    ):
        resp = await api_client.post(f"{prefix}/multicast/update")
    assert resp.status == 400


async def test_api_multicast_update_not_installed(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test update is rejected when enabling did not finish installing."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.plugins.multicast._data.pop("version", None)  # pylint: disable=protected-access

    with patch.object(
        PluginMulticast,
        "latest_version",
        new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
    ):
        resp = await api_client.post(f"{prefix}/multicast/update")

    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == "Plugin multicast is not installed"
