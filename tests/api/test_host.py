"""Test Host API."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.host.logs import LogsControl

# pylint: disable=protected-access


@pytest.fixture(name="coresys_disk_info")
async def fixture_coresys_disk_info(coresys: CoreSys) -> CoreSys:
    """Mock basic disk information for host APIs."""
    coresys.hardware.disk.get_disk_life_time = lambda _: 0
    coresys.hardware.disk.get_disk_free_space = lambda _: 5000
    coresys.hardware.disk.get_disk_total_space = lambda _: 50000
    coresys.hardware.disk.get_disk_used_space = lambda _: 45000

    yield coresys


@pytest.fixture(name="journald_logs")
async def fixture_journald_logs() -> MagicMock:
    """Mock journald logs and make it available."""
    with patch.object(
        LogsControl, "available", new=PropertyMock(return_value=True)
    ), patch.object(
        LogsControl,
        "boot_ids",
        new=PropertyMock(return_value=["aaa", "bbb", "ccc"]),
    ), patch.object(
        LogsControl, "journald_logs", new=MagicMock()
    ) as logs:
        yield logs


@pytest.mark.asyncio
async def test_api_host_info(api_client, coresys_disk_info: CoreSys):
    """Test host info api."""
    coresys = coresys_disk_info

    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    resp = await api_client.get("/host/info")
    result = await resp.json()

    assert result["data"]["apparmor_version"] == "2.13.2"


async def test_api_host_features(
    api_client, coresys_disk_info: CoreSys, dbus_is_connected
):
    """Test host info features."""
    coresys = coresys_disk_info

    coresys.host.sys_dbus.systemd.is_connected = False
    coresys.host.sys_dbus.network.is_connected = False
    coresys.host.sys_dbus.hostname.is_connected = False
    coresys.host.sys_dbus.timedate.is_connected = False
    coresys.host.sys_dbus.agent.is_connected = False
    coresys.host.sys_dbus.resolved.is_connected = False

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "reboot" not in result["data"]["features"]
    assert "services" not in result["data"]["features"]
    assert "shutdown" not in result["data"]["features"]
    assert "network" not in result["data"]["features"]
    assert "hostname" not in result["data"]["features"]
    assert "timedate" not in result["data"]["features"]
    assert "os_agent" not in result["data"]["features"]
    assert "resolved" not in result["data"]["features"]

    coresys.host.sys_dbus.systemd.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "reboot" in result["data"]["features"]
    assert "services" in result["data"]["features"]
    assert "shutdown" in result["data"]["features"]

    coresys.host.sys_dbus.network.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "network" in result["data"]["features"]

    coresys.host.sys_dbus.hostname.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "hostname" in result["data"]["features"]

    coresys.host.sys_dbus.timedate.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "timedate" in result["data"]["features"]

    coresys.host.sys_dbus.agent.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "os_agent" in result["data"]["features"]

    coresys.host.sys_dbus.resolved.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "resolved" in result["data"]["features"]


async def test_api_llmnr_mdns_info(
    api_client, coresys_disk_info: CoreSys, dbus_is_connected
):
    """Test llmnr and mdns details in info."""
    coresys = coresys_disk_info

    coresys.host.sys_dbus.resolved.is_connected = False

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["broadcast_llmnr"] is None
    assert result["data"]["broadcast_mdns"] is None
    assert result["data"]["llmnr_hostname"] is None

    coresys.host.sys_dbus.resolved.is_connected = True
    await coresys.dbus.resolved.connect(coresys.dbus.bus)
    await coresys.dbus.resolved.update()

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["broadcast_llmnr"] is True
    assert result["data"]["broadcast_mdns"] is False
    assert result["data"]["llmnr_hostname"] == "homeassistant"


async def test_api_boot_ids_info(
    api_client, coresys_disk_info: CoreSys, journald_logs: MagicMock
):
    """Test boot IDs in host info."""
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["boot_ids"] == {"0": "ccc", "-1": "bbb", "-2": "aaa"}


async def test_advanced_logs(api_client, journald_logs: MagicMock):
    """Test advanced logging API entries with identifier and custom boot."""
    await api_client.get("/host/logs/entries")
    journald_logs.assert_called_once_with({}, None)

    journald_logs.reset_mock()

    identifier = "dropbear"
    await api_client.get(f"/host/logs/{identifier}/entries")
    journald_logs.assert_called_once_with({"SYSLOG_IDENTIFIER": identifier}, None)

    journald_logs.reset_mock()

    bootid = "798cc03bcd77465482b6a1c43dc6a5fc"
    await api_client.get(f"/host/logs/boot/{bootid}/entries")
    journald_logs.assert_called_once_with({"_BOOT_ID": bootid}, None)

    journald_logs.reset_mock()

    await api_client.get(f"/host/logs/boot/{bootid}/{identifier}/entries")
    journald_logs.assert_called_once_with(
        {"_BOOT_ID": bootid, "SYSLOG_IDENTIFIER": identifier}, None
    )

    journald_logs.reset_mock()

    headers = {"Range": "entries=:-19:10"}
    await api_client.get("/host/logs/entries", headers=headers)
    journald_logs.assert_called_once_with({}, headers["Range"])

    journald_logs.reset_mock()

    await api_client.get("/host/logs/entries/follow")
    journald_logs.assert_called_once_with({"follow": ""}, None)


async def test_advanced_logs_boot_id_offset(api_client, journald_logs: MagicMock):
    """Test advanced logging API when using an offset as boot ID."""
    await api_client.get("/host/logs/boot/0/entries")
    journald_logs.assert_called_once_with({"_BOOT_ID": "ccc"}, None)

    journald_logs.reset_mock()

    await api_client.get("/host/logs/boot/-2/entries")
    journald_logs.assert_called_once_with({"_BOOT_ID": "aaa"}, None)

    journald_logs.reset_mock()

    await api_client.get("/host/logs/boot/2/entries")
    journald_logs.assert_called_once_with({"_BOOT_ID": "bbb"}, None)

    journald_logs.reset_mock()


async def test_advanced_logs_slug_as_identifier(
    api_client, journald_logs: MagicMock, install_addon_ssh: Addon
):
    """Test advanced logging API when using known slug as syslog identifier."""
    with patch("supervisor.docker.supervisor.os") as os:
        os.environ = {"SUPERVISOR_NAME": "hassio_supervisor"}

        await api_client.get("/host/logs/supervisor/entries")
        journald_logs.assert_called_once_with(
            {"SYSLOG_IDENTIFIER": "hassio_supervisor"}, None
        )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/dns/entries")
    journald_logs.assert_called_once_with({"SYSLOG_IDENTIFIER": "hassio_dns"}, None)

    journald_logs.reset_mock()

    await api_client.get("/host/logs/local_ssh/entries")
    journald_logs.assert_called_once_with(
        {"SYSLOG_IDENTIFIER": "addon_local_ssh"}, None
    )

    journald_logs.reset_mock()


async def test_advanced_logs_errors(api_client):
    """Test advanced logging API errors."""
    # coresys = coresys_logs_control
    resp = await api_client.get("/host/logs/entries")
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "No systemd-journal-gatewayd Unix socket available"

    headers = {"Accept": "application/json"}
    resp = await api_client.get("/host/logs/entries", headers=headers)
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Invalid content type requested. Only text/plain supported for now."
    )

    resp = await api_client.get("/host/logs/boot/-1/entries")
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Unable to obtain boot IDs from host, check logs for errors"
    )

    with patch.object(
        LogsControl, "boot_ids", new=PropertyMock(return_value=["aaa", "bbb", "ccc"])
    ):
        resp = await api_client.get("/host/logs/boot/4/entries")
        result = await resp.json()
        assert result["result"] == "error"
        assert result["message"] == "Logs only contain 3 boots"

        resp = await api_client.get("/host/logs/boot/-3/entries")
        result = await resp.json()
        assert result["result"] == "error"
        assert result["message"] == "Logs only contain 3 boots"
