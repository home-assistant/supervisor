"""Test addons api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from supervisor.addons.addon import Addon
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.store.repository import Repository

from ..const import TEST_ADDON_SLUG
from .test_host import DEFAULT_RANGE


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
    await api_client.get("/addons/local_ssh/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "addon_local_ssh"},
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    await api_client.get("/addons/local_ssh/logs/follow")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "addon_local_ssh", "follow": ""},
        range_header=DEFAULT_RANGE,
    )
