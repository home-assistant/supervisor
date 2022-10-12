"""Test Host API."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys

DEFAULT_RANGE = "entries=:-100:"
# pylint: disable=protected-access


@pytest.fixture(name="coresys_disk_info")
async def fixture_coresys_disk_info(coresys: CoreSys) -> CoreSys:
    """Mock basic disk information for host APIs."""
    coresys.hardware.disk.get_disk_life_time = lambda _: 0
    coresys.hardware.disk.get_disk_free_space = lambda _: 5000
    coresys.hardware.disk.get_disk_total_space = lambda _: 50000
    coresys.hardware.disk.get_disk_used_space = lambda _: 45000

    yield coresys


@pytest.mark.asyncio
async def test_api_host_info(api_client: TestClient, coresys_disk_info: CoreSys):
    """Test host info api."""
    coresys = coresys_disk_info

    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    resp = await api_client.get("/host/info")
    result = await resp.json()

    assert result["data"]["apparmor_version"] == "2.13.2"


async def test_api_host_features(
    api_client: TestClient, coresys_disk_info: CoreSys, dbus_is_connected
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
    api_client: TestClient, coresys_disk_info: CoreSys, dbus_is_connected
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


async def test_api_boot_ids_info(api_client: TestClient, journald_logs: MagicMock):
    """Test getting boot IDs."""
    resp = await api_client.get("/host/logs/boots")
    result = await resp.json()
    assert result["data"] == {"0": "ccc", "-1": "bbb", "-2": "aaa"}


async def test_api_identifiers_info(api_client: TestClient, journald_logs: MagicMock):
    """Test getting syslog identifiers."""
    resp = await api_client.get("/host/logs/identifiers")
    result = await resp.json()
    assert result["data"] == ["hassio_supervisor", "hassos-config", "kernel"]


async def test_advanced_logs(
    api_client: TestClient, coresys: CoreSys, journald_logs: MagicMock
):
    """Test advanced logging API entries with identifier and custom boot."""
    await api_client.get("/host/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    identifier = "dropbear"
    await api_client.get(f"/host/logs/identifiers/{identifier}")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": identifier}, range_header=DEFAULT_RANGE
    )

    journald_logs.reset_mock()

    bootid = "798cc03bcd77465482b6a1c43dc6a5fc"
    await api_client.get(f"/host/logs/boots/{bootid}")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": bootid,
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    await api_client.get(f"/host/logs/boots/{bootid}/identifiers/{identifier}")
    journald_logs.assert_called_once_with(
        params={"_BOOT_ID": bootid, "SYSLOG_IDENTIFIER": identifier},
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    headers = {"Range": "entries=:-19:10"}
    await api_client.get("/host/logs", headers=headers)
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=headers["Range"],
    )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/follow")
    journald_logs.assert_called_once_with(
        params={
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
            "follow": "",
        },
        range_header=DEFAULT_RANGE,
    )


async def test_advanced_logs_boot_id_offset(
    api_client: TestClient, coresys: CoreSys, journald_logs: MagicMock
):
    """Test advanced logging API when using an offset as boot ID."""
    await api_client.get("/host/logs/boots/0")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "ccc",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/boots/-2")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "aaa",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/boots/2")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "bbb",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()


async def test_advanced_logs_errors(api_client: TestClient):
    """Test advanced logging API errors."""
    # coresys = coresys_logs_control
    resp = await api_client.get("/host/logs")
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "No systemd-journal-gatewayd Unix socket available"

    headers = {"Accept": "application/json"}
    resp = await api_client.get("/host/logs", headers=headers)
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Invalid content type requested. Only text/plain supported for now."
    )
