"""Test Host API."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import suppress
from datetime import UTC, datetime
import errno
import gc
import time
from typing import Any
from unittest.mock import ANY, MagicMock, patch

from aiohttp import ClientPayloadError
from aiohttp.test_utils import TestClient
from dbus_fast import DBusError, ErrorType
import pytest
import time_machine

from supervisor.api.host import APIHost
from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.dbus.resolved import Resolved
from supervisor.exceptions import (
    HostJournalGatewaydConnectionError,
    MountUsageTimeoutError,
)
from supervisor.homeassistant.api import APIState
from supervisor.host.const import LogFormat, LogFormatter
from supervisor.host.control import SystemControl
from supervisor.mounts.mount import Mount

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.hostname import Hostname as HostnameService
from tests.dbus_service_mocks.systemd import Systemd as SystemdService

DEFAULT_RANGE = "entries=:-99:100"
DEFAULT_RANGE_FOLLOW = "entries=:-99:18446744073709551615"
# pylint: disable=protected-access


@pytest.fixture(name="coresys_disk_info")
async def fixture_coresys_disk_info(coresys: CoreSys) -> AsyncGenerator[CoreSys]:
    """Mock basic disk information for host APIs."""

    async def mock_disk_lifetime(_):
        return 0

    coresys.hardware.disk.get_disk_life_time = mock_disk_lifetime
    coresys.hardware.disk.get_disk_free_space = lambda _: 5000
    coresys.hardware.disk.get_disk_total_space = lambda _: 50000
    coresys.hardware.disk.get_disk_used_space = lambda _: 45000

    return coresys


async def test_api_host_info(
    api_client_with_prefix: tuple[TestClient, str], coresys_disk_info: CoreSys
):
    """Test host info api."""
    api_client, prefix = api_client_with_prefix
    coresys = coresys_disk_info
    dt_utc = datetime(2026, 2, 17, 1, 23, 45, 678901, tzinfo=UTC)

    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    with time_machine.travel(dt_utc, tick=False):
        resp = await api_client.get(f"{prefix}/host/info")
        result = await resp.json()

    assert result["data"]["apparmor_version"] == "2.13.2"
    assert result["data"]["dt_utc"] == "2026-02-17T01:23:45.678901+00:00"


async def test_api_host_features(
    api_client_with_prefix: tuple[TestClient, str],
    coresys_disk_info: CoreSys,
    dbus_is_connected,
):
    """Test host info features."""
    api_client, prefix = api_client_with_prefix
    coresys = coresys_disk_info

    coresys.host.sys_dbus.systemd.is_connected = False
    coresys.host.sys_dbus.network.is_connected = False
    coresys.host.sys_dbus.hostname.is_connected = False
    coresys.host.sys_dbus.timedate.is_connected = False
    coresys.host.sys_dbus.agent.is_connected = False
    coresys.host.sys_dbus.resolved.is_connected = False
    coresys.host.sys_dbus.udisks2.is_connected = False

    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "reboot" not in result["data"]["features"]
    assert "services" not in result["data"]["features"]
    assert "shutdown" not in result["data"]["features"]
    assert "network" not in result["data"]["features"]
    assert "hostname" not in result["data"]["features"]
    assert "timedate" not in result["data"]["features"]
    assert "os_agent" not in result["data"]["features"]
    assert "resolved" not in result["data"]["features"]
    assert "disk" not in result["data"]["features"]

    coresys.host.sys_dbus.systemd.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "reboot" in result["data"]["features"]
    assert "services" in result["data"]["features"]
    assert "shutdown" in result["data"]["features"]

    coresys.host.sys_dbus.network.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "network" in result["data"]["features"]

    coresys.host.sys_dbus.hostname.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "hostname" in result["data"]["features"]

    coresys.host.sys_dbus.timedate.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "timedate" in result["data"]["features"]

    coresys.host.sys_dbus.agent.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "os_agent" in result["data"]["features"]

    coresys.host.sys_dbus.resolved.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "resolved" in result["data"]["features"]

    coresys.host.sys_dbus.udisks2.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert "disk" in result["data"]["features"]


async def test_api_llmnr_mdns_info(
    api_client_with_prefix: tuple[TestClient, str], coresys_disk_info: CoreSys
):
    """Test llmnr and mdns details in info."""
    api_client, prefix = api_client_with_prefix
    coresys = coresys_disk_info
    # pylint: disable=protected-access
    coresys.host.sys_dbus._resolved = Resolved()
    # pylint: enable=protected-access

    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert result["data"]["broadcast_llmnr"] is None
    assert result["data"]["broadcast_mdns"] is None
    assert result["data"]["llmnr_hostname"] is None

    await coresys.dbus.resolved.connect(coresys.dbus.bus)

    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert result["data"]["broadcast_llmnr"] is True
    assert result["data"]["broadcast_mdns"] is False
    assert result["data"]["llmnr_hostname"] == "homeassistant"


async def test_api_boot_ids_info(
    api_client_with_prefix: tuple[TestClient, str], journald_logs: MagicMock
):
    """Test getting boot IDs."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/host/logs/boots")
    result = await resp.json()
    assert result["data"] == {"boots": {"0": "ccc", "-1": "bbb", "-2": "aaa"}}


async def test_api_identifiers_info(
    api_client_with_prefix: tuple[TestClient, str], journald_logs: MagicMock
):
    """Test getting syslog identifiers."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/host/logs/identifiers")
    result = await resp.json()
    assert result["data"] == {
        "identifiers": ["hassio_supervisor", "hassos-config", "kernel"]
    }


async def test_api_virtualization_info(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    coresys_disk_info: CoreSys,
):
    """Test getting virtualization info."""
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]

    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert result["data"]["virtualization"] == ""

    systemd_service.virtualization = "vmware"
    await coresys_disk_info.dbus.systemd.update()

    resp = await api_client.get(f"{prefix}/host/info")
    result = await resp.json()
    assert result["data"]["virtualization"] == "vmware"


async def test_advanced_logs(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    journald_logs: MagicMock,
):
    """Test advanced logging API entries with identifier and custom boot."""
    api_client, prefix = api_client_with_prefix
    await api_client.get(f"{prefix}/host/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    identifier = "dropbear"
    await api_client.get(f"{prefix}/host/logs/identifiers/{identifier}")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": identifier},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    bootid = "798cc03bcd77465482b6a1c43dc6a5fc"
    await api_client.get(f"{prefix}/host/logs/boots/{bootid}")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": bootid,
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get(f"{prefix}/host/logs/boots/{bootid}/identifiers/{identifier}")
    journald_logs.assert_called_once_with(
        params={"_BOOT_ID": bootid, "SYSLOG_IDENTIFIER": identifier},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    headers = {"Range": "entries=:-19:10"}
    await api_client.get(f"{prefix}/host/logs", headers=headers)
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=headers["Range"],
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get(f"{prefix}/host/logs/follow")
    journald_logs.assert_called_once_with(
        params={
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
            "follow": "",
        },
        range_header=DEFAULT_RANGE_FOLLOW,
        accept=LogFormat.JOURNAL,
    )

    # Host logs don't have a /latest endpoint
    resp = await api_client.get(f"{prefix}/host/logs/latest")
    assert resp.status == 404


async def test_advanced_logs_query_parameters(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    journald_logs: MagicMock,
    journal_logs_reader: MagicMock,
):
    """Test advanced logging API entries controlled by query parameters."""
    api_client, prefix = api_client_with_prefix
    # Check lines query parameter
    await api_client.get(f"{prefix}/host/logs?lines=53")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header="entries=:-52:53",
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    # Check verbose logs formatter via query parameter
    await api_client.get(f"{prefix}/host/logs?verbose")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, LogFormatter.VERBOSE, False)

    journal_logs_reader.reset_mock()
    journald_logs.reset_mock()

    # Query parameters should take precedence over headers
    await api_client.get(
        f"{prefix}/host/logs?lines=53&verbose",
        headers={
            "Range": "entries=:-19:10",
            "Accept": "text/plain",
        },
    )
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header="entries=:-52:53",
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, LogFormatter.VERBOSE, False)

    journal_logs_reader.reset_mock()
    journald_logs.reset_mock()

    # Check no_colors query parameter
    await api_client.get(f"{prefix}/host/logs?no_colors")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, LogFormatter.VERBOSE, True)


async def test_advanced_logs_boot_id_offset(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    journald_logs: MagicMock,
):
    """Test advanced logging API when using an offset as boot ID."""
    api_client, prefix = api_client_with_prefix
    await api_client.get(f"{prefix}/host/logs/boots/0")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "ccc",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get(f"{prefix}/host/logs/boots/-2")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "aaa",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get(f"{prefix}/host/logs/boots/2")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "bbb",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()


async def test_advanced_logs_formatters(
    journald_gateway: MagicMock,
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    journal_logs_reader: MagicMock,
):
    """Test advanced logs formatters varying on Accept header."""
    api_client, prefix = api_client_with_prefix

    await api_client.get(f"{prefix}/host/logs")
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.VERBOSE, False)

    journal_logs_reader.reset_mock()

    headers = {"Accept": "text/x-log"}
    await api_client.get(f"{prefix}/host/logs", headers=headers)
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.VERBOSE, False)

    journal_logs_reader.reset_mock()

    await api_client.get(f"{prefix}/host/logs/identifiers/test")
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.PLAIN, False)

    journal_logs_reader.reset_mock()

    headers = {"Accept": "text/x-log"}
    await api_client.get(f"{prefix}/host/logs/identifiers/test", headers=headers)
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.VERBOSE, False)

    journal_logs_reader.reset_mock()

    await api_client.get(
        f"{prefix}/host/logs/identifiers/test", skip_auto_headers={"Accept"}
    )
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.PLAIN, False)


async def test_advanced_logs_errors(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test advanced logging API errors."""
    api_client, prefix = api_client_with_prefix
    with patch("supervisor.host.logs.SYSTEMD_JOURNAL_GATEWAYD_SOCKET") as socket:
        socket.is_socket.return_value = False
        await coresys.host.logs.post_init()
        resp = await api_client.get(f"{prefix}/host/logs")
        assert resp.content_type == "text/plain"
        assert resp.status == 400
        content = await resp.text()
        assert content == "No systemd-journal-gatewayd Unix socket available"

    headers = {"Accept": "application/json"}
    resp = await api_client.get(f"{prefix}/host/logs", headers=headers)
    assert resp.content_type == "text/plain"
    assert resp.status == 400
    content = await resp.text()
    assert (
        content
        == "Invalid content type requested. Only text/plain and text/x-log supported for now."
    )


async def test_advanced_logs_gateway_closed_mid_stream(
    journald_gateway: MagicMock,
    api_client_with_prefix: tuple[TestClient, str],
):
    """Test connection to journal gateway closed mid-stream ends the stream gracefully."""
    api_client, prefix = api_client_with_prefix

    journald_gateway.content.feed_data(b"__CURSOR=cursor1\nMESSAGE=Hello, world!\n\n")

    resp = await api_client.get(f"{prefix}/host/logs/identifiers/test")
    assert resp.status == 200

    # Simulate connection to systemd-journal-gatewayd being closed mid-stream,
    # e.g. because it was stopped on host shutdown.
    journald_gateway.content.set_exception(
        ClientPayloadError("Response payload is not completed")
    )

    assert await resp.text() == "Hello, world!\n"


async def test_advanced_logs_gateway_reset_before_stream(
    journald_gateway: MagicMock,
    api_client_with_prefix: tuple[TestClient, str],
):
    """Test connection reset before the log stream started returns an API error."""
    api_client, prefix = api_client_with_prefix

    journald_gateway.content.set_exception(
        ClientPayloadError("Response payload is not completed")
    )

    resp = await api_client.get(f"{prefix}/host/logs/identifiers/test")
    assert resp.status == 400
    assert (
        await resp.text()
        == "Connection reset when trying to fetch data from systemd-journald."
    )


async def test_advanced_logs_gateway_unavailable(
    api_client_with_prefix: tuple[TestClient, str],
    journald_logs: MagicMock,
    caplog: pytest.LogCaptureFixture,
):
    """Test connection failure to journal gateway returns a plain API error."""
    api_client, prefix = api_client_with_prefix

    journald_logs.side_effect = HostJournalGatewaydConnectionError(
        "Unable to connect to systemd-journal-gatewayd"
    )

    with patch("supervisor.api.utils.async_capture_exception") as capture_exception:
        resp = await api_client.get(f"{prefix}/host/logs")

    assert resp.status == 400
    assert await resp.text() == "Unable to connect to systemd-journal-gatewayd"
    capture_exception.assert_not_called()
    assert "Unexpected error during API call" not in caplog.text


async def test_disk_usage_api(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test disk usage API endpoint."""
    api_client, prefix = api_client_with_prefix
    # Mock the disk usage methods
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        # Mock the main disk usage call
        mock_disk_usage.return_value = (
            1000000000,
            500000000,
            500000000,
        )  # 1GB total, 500MB used, 500MB free

        # Mock the directory structure sizes for each path
        mock_dir_sizes.return_value = [
            {
                "id": "apps_data",
                "label": "Apps Data",
                "used_bytes": 100000000,
                "children": [
                    {"id": "addon1", "label": "addon1", "used_bytes": 50000000}
                ],
            },
            {
                "id": "apps_config",
                "label": "Apps Config",
                "used_bytes": 200000000,
                "children": [
                    {"id": "media1", "label": "media1", "used_bytes": 100000000}
                ],
            },
            {
                "id": "media",
                "label": "Media",
                "used_bytes": 50000000,
                "children": [
                    {"id": "share1", "label": "share1", "used_bytes": 25000000}
                ],
            },
            {
                "id": "share",
                "label": "Share",
                "used_bytes": 300000000,
                "children": [
                    {"id": "backup1", "label": "backup1", "used_bytes": 150000000}
                ],
            },
            {
                "id": "backup",
                "label": "Backup",
                "used_bytes": 10000000,
                "children": [{"id": "ssl1", "label": "ssl1", "used_bytes": 5000000}],
            },
            {
                "id": "ssl",
                "label": "SSL",
                "used_bytes": 40000000,
                "children": [
                    {
                        "id": "homeassistant1",
                        "label": "homeassistant1",
                        "used_bytes": 20000000,
                    }
                ],
            },
            {
                "id": "homeassistant",
                "label": "Home Assistant",
                "used_bytes": 40000000,
                "children": [
                    {
                        "id": "homeassistant1",
                        "label": "homeassistant1",
                        "used_bytes": 20000000,
                    }
                ],
            },
        ]

        # Test default max_depth=1
        resp = await api_client.get(f"{prefix}/host/disks/default/usage")
        assert resp.status == 200
        result = await resp.json()

        assert result["data"]["id"] == "root"
        assert result["data"]["label"] == "Root"
        assert result["data"]["total_bytes"] == 1000000000
        assert result["data"]["used_bytes"] == 500000000
        assert "children" in result["data"]
        children = result["data"]["children"]

        # First child should be system
        assert children[0]["id"] == "system"
        assert children[0]["label"] == "System"

        # Verify all expected directories are present in the remaining children
        expected_data_id = "addons_data" if prefix == "" else "apps_data"
        expected_config_id = "addons_config" if prefix == "" else "apps_config"
        assert children[1]["id"] == expected_data_id
        assert children[2]["id"] == expected_config_id
        assert children[3]["id"] == "media"
        assert children[4]["id"] == "share"
        assert children[5]["id"] == "backup"
        assert children[6]["id"] == "ssl"
        assert children[7]["id"] == "homeassistant"

        # Verify the sizes are correct
        assert children[1]["used_bytes"] == 100000000
        assert children[2]["used_bytes"] == 200000000
        assert children[3]["used_bytes"] == 50000000
        assert children[4]["used_bytes"] == 300000000
        assert children[5]["used_bytes"] == 10000000
        assert children[6]["used_bytes"] == 40000000
        assert children[7]["used_bytes"] == 40000000

        # Verify system space calculation (total used - sum of known paths)
        total_known_space = (
            100000000
            + 200000000
            + 50000000
            + 300000000
            + 10000000
            + 40000000
            + 40000000
        )
        expected_system_space = 500000000 - total_known_space
        assert children[0]["used_bytes"] == expected_system_space

        # Verify disk_usage was called with supervisor path
        mock_disk_usage.assert_called_once_with(coresys.config.path_supervisor)

        # Verify get_dir_sizes was called once with all paths
        assert mock_dir_sizes.call_count == 1
        call_args = mock_dir_sizes.call_args
        assert call_args[0][1] == 1  # max_depth parameter
        paths_dict = call_args[0][0]  # paths dictionary
        assert paths_dict["apps_data"] == coresys.config.path_apps_data
        assert paths_dict["apps_config"] == coresys.config.path_app_configs
        assert paths_dict["media"] == coresys.config.path_media
        assert paths_dict["share"] == coresys.config.path_share
        assert paths_dict["backup"] == coresys.config.path_backup
        assert paths_dict["ssl"] == coresys.config.path_ssl
        assert paths_dict["homeassistant"] == coresys.config.path_homeassistant


async def test_disk_usage_api_with_custom_depth(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test disk usage API endpoint with custom max_depth parameter."""
    api_client, prefix = api_client_with_prefix
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)

        # Mock deeper directory structure
        mock_dir_sizes.return_value = [
            {
                "id": "apps_data",
                "label": "Apps Data",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "apps_config",
                "label": "Apps Config",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "media",
                "label": "Media",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "share",
                "label": "Share",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "backup",
                "label": "Backup",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "ssl",
                "label": "SSL",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "homeassistant",
                "label": "Home Assistant",
                "used_bytes": 100000000,
                "children": [
                    {
                        "id": "addon1",
                        "label": "addon1",
                        "used_bytes": 50000000,
                        "children": [
                            {
                                "id": "subdir1",
                                "label": "subdir1",
                                "used_bytes": 25000000,
                            },
                        ],
                    },
                ],
            },
        ]

        # Test with custom max_depth=2
        resp = await api_client.get(f"{prefix}/host/disks/default/usage?max_depth=2")
        assert resp.status == 200
        result = await resp.json()
        assert result["data"]["used_bytes"] == 500000000
        assert result["data"]["children"]

        # Verify max_depth=2 was passed to get_dir_sizes
        assert mock_dir_sizes.call_count == 1
        call_args = mock_dir_sizes.call_args
        assert call_args[0][1] == 2  # max_depth parameter


async def test_disk_usage_api_invalid_depth(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test disk usage API endpoint with invalid max_depth parameter."""
    api_client, prefix = api_client_with_prefix
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)
        mock_dir_sizes.return_value = [
            {
                "id": "apps_data",
                "label": "Apps Data",
                "used_bytes": 100000000,
            },
            {
                "id": "apps_config",
                "label": "Apps Config",
                "used_bytes": 100000000,
            },
            {
                "id": "media",
                "label": "Media",
                "used_bytes": 100000000,
            },
            {
                "id": "share",
                "label": "Share",
                "used_bytes": 100000000,
            },
            {
                "id": "backup",
                "label": "Backup",
                "used_bytes": 100000000,
            },
            {
                "id": "ssl",
                "label": "SSL",
                "used_bytes": 100000000,
            },
            {
                "id": "homeassistant",
                "label": "Home Assistant",
                "used_bytes": 100000000,
            },
        ]

        # Test with invalid max_depth (non-integer)
        resp = await api_client.get(
            f"{prefix}/host/disks/default/usage?max_depth=invalid"
        )
        assert resp.status == 200
        result = await resp.json()
        assert result["data"]["used_bytes"] == 500000000
        assert result["data"]["children"]

        # Should default to max_depth=1 when invalid value is provided
        assert mock_dir_sizes.call_count == 1
        call_args = mock_dir_sizes.call_args
        assert call_args[0][1] == 1  # Should default to 1


async def test_disk_usage_api_empty_directories(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test disk usage API endpoint with empty directories."""
    api_client, prefix = api_client_with_prefix
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)

        # Mock empty directory structures (no children)
        mock_dir_sizes.return_value = [
            {
                "id": "apps_data",
                "label": "Apps Data",
                "used_bytes": 0,
            },
            {
                "id": "apps_config",
                "label": "Apps Config",
                "used_bytes": 0,
            },
            {
                "id": "media",
                "label": "Media",
                "used_bytes": 0,
            },
            {
                "id": "share",
                "label": "Share",
                "used_bytes": 0,
            },
            {
                "id": "backup",
                "label": "Backup",
                "used_bytes": 0,
            },
            {
                "id": "ssl",
                "label": "SSL",
                "used_bytes": 0,
            },
            {
                "id": "homeassistant",
                "label": "Home Assistant",
                "used_bytes": 0,
            },
        ]

        resp = await api_client.get(f"{prefix}/host/disks/default/usage")
        assert resp.status == 200
        result = await resp.json()

        assert result["data"]["used_bytes"] == 500000000
        children = result["data"]["children"]

        # First child should be system with all the space
        assert children[0]["id"] == "system"
        assert children[0]["used_bytes"] == 500000000

        # All other directories should have size 0
        for i in range(1, len(children)):
            assert children[i]["used_bytes"] == 0


async def test_disk_usage_api_v1_uses_legacy_addon_ids(
    api_client: TestClient, coresys: CoreSys
):
    """Test v1 disk usage response uses legacy addon IDs."""
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)
        mock_dir_sizes.return_value = [
            {"id": "apps_data", "label": "Apps Data", "used_bytes": 100000000},
            {
                "id": "apps_config",
                "label": "Apps Config",
                "used_bytes": 200000000,
            },
            {"id": "media", "label": "Media", "used_bytes": 50000000},
            {"id": "share", "label": "Share", "used_bytes": 300000000},
            {"id": "backup", "label": "Backup", "used_bytes": 10000000},
            {"id": "ssl", "label": "SSL", "used_bytes": 40000000},
            {
                "id": "homeassistant",
                "label": "Home Assistant",
                "used_bytes": 40000000,
            },
        ]

        resp = await api_client.get("/host/disks/default/usage")
        assert resp.status == 200
        result = await resp.json()

        child_ids = [child["id"] for child in result["data"]["children"]]
        assert "addons_data" in child_ids
        assert "addons_config" in child_ids
        assert "apps_data" not in child_ids
        assert "apps_config" not in child_ids


@pytest.mark.parametrize("action", ["reboot", "shutdown"])
async def test_migration_blocks_shutdown(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    action: str,
):
    """Test that an offline db migration in progress stops users from shutting down or rebooting system."""
    api_client, prefix = api_client_with_prefix
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    resp = await api_client.post(f"{prefix}/host/{action}")
    assert resp.status == 503
    result = await resp.json()
    assert (
        result["message"]
        == "Home Assistant offline database migration in progress, please wait until complete before shutting down host"
    )


async def test_force_reboot_during_migration(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test force option reboots even during a migration."""
    api_client, prefix = api_client_with_prefix
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(SystemControl, "reboot") as reboot:
        await api_client.post(f"{prefix}/host/reboot", json={"force": True})
        reboot.assert_called_once()


async def test_force_shutdown_during_migration(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test force option shutdown even during a migration."""
    api_client, prefix = api_client_with_prefix
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(SystemControl, "shutdown") as shutdown:
        await api_client.post(f"{prefix}/host/shutdown", json={"force": True})
        shutdown.assert_called_once()


async def test_set_hostname_invalid_returns_400(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """An INVALID_ARGS rejection from hostnamed becomes a 400 with a structured body."""
    hostname_service: HostnameService = all_dbus_services["hostname"]
    hostname_service.response_set_static_hostname = DBusError(
        ErrorType.INVALID_ARGS, "Invalid static hostname 'bad name'"
    )

    resp = await api_client.post("/host/options", json={"hostname": "bad name"})
    assert resp.status == 400
    body = await resp.json()
    assert body["result"] == "error"
    assert body["message"] == "Invalid hostname 'bad name'"
    assert body["error_key"] == "host_invalid_hostname"
    assert body["extra_fields"] == {"hostname": "bad name"}


def _register_mount(
    coresys: CoreSys, name: str, state: UnitActiveState | None
) -> Mount:
    """Register a CIFS mount with the manager in the given systemd state."""
    mount = Mount.from_dict(
        coresys,
        {
            "name": name,
            "type": "cifs",
            "usage": "media",
            "server": "media.local",
            "share": "media",
        },
    )
    mount._state = state
    coresys.mounts._mounts = {mount.name: mount}
    return mount


@pytest.fixture(name="active_mount")
async def fixture_active_mount(
    coresys: CoreSys, tmp_supervisor_data, path_extern
) -> Mount:
    """Return an active CIFS mount registered with the mount manager."""
    return _register_mount(coresys, "media_test", UnitActiveState.ACTIVE)


@pytest.mark.parametrize(
    "query",
    ["", "?max_depth=0", "?max_depth=1"],
    ids=["depth-default", "depth-explicit-0", "depth-1-emits-nothing"],
)
async def test_disk_usage_api_mount_totals_only(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    active_mount: Mount,
    query: str,
):
    """Test a mount reports totals only without ever walking the tree.

    The directory walker recurses regardless of max_depth and only emits
    children beyond depth 1, so whenever it could not produce output — depth 0
    and depth 1 alike — it has to be skipped outright. Calling it would walk
    the whole mount on every request just to discard the result.
    """
    api_client, prefix = api_client_with_prefix

    with (
        patch.object(coresys.hardware.disk, "disk_usage_for_mount") as mock_disk_usage,
        patch.object(
            coresys.hardware.disk, "get_dir_structure_sizes"
        ) as mock_structure,
    ):
        # Middle value is deliberately wrong: used must come from total - free so
        # that reserved space counts as used, as it does for the system disk.
        mock_disk_usage.return_value = (2000000000, 999, 800000000)

        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage{query}")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"] == {
        "id": "media_test",
        "label": "media_test",
        "total_bytes": 2000000000,
        "used_bytes": 1200000000,
    }
    # Omitted entirely rather than empty, like every other node in the tree
    assert "children" not in result["data"]
    mock_structure.assert_not_called()
    mock_disk_usage.assert_called_once_with(active_mount.local_where)


async def test_disk_usage_api_mount_breakdown(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    active_mount: Mount,
):
    """Test a mount breakdown at depth 2.

    Depth means the same thing as it does for the system disk: level 1 is the
    labeled known paths, which a mount does not have, so a mount's own
    subdirectories start at level 2.
    """
    api_client, prefix = api_client_with_prefix

    with (
        patch.object(coresys.hardware.disk, "disk_usage_for_mount") as mock_disk_usage,
        patch.object(
            coresys.hardware.disk, "get_dir_structure_sizes"
        ) as mock_structure,
    ):
        mock_disk_usage.return_value = (2000000000, 999, 800000000)
        mock_structure.return_value = {
            "used_bytes": 1100000000,
            "children": [
                {"id": "movies", "label": "movies", "used_bytes": 900000000},
                {"id": "music", "label": "music", "used_bytes": 200000000},
            ],
        }

        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage?max_depth=2")

    assert resp.status == 200
    result = await resp.json()
    children = result["data"]["children"]

    # What the walk could not attribute is reported as "other", so a mount's
    # children add up to its used_bytes like every other node in the tree.
    assert children == [
        {"id": "movies", "label": "movies", "used_bytes": 900000000},
        {"id": "music", "label": "music", "used_bytes": 200000000},
        {"id": "other", "label": "Other", "used_bytes": 100000000},
    ]
    assert (
        sum(child["used_bytes"] for child in children) == (result["data"]["used_bytes"])
    )
    # check_oserror off: read errors from a mount walk must stay the mount's
    # problem instead of marking the whole system unhealthy
    mock_structure.assert_called_once_with(
        active_mount.local_where, 2, check_oserror=False
    )


@pytest.mark.parametrize(
    ("walked_bytes", "expect_children"),
    [(1200000000, True), (1300000000, False)],
    ids=["accounts-for-everything", "overshoots-the-filesystem"],
)
@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_mount_breakdown_without_remainder(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    walked_bytes: int,
    expect_children: bool,
    caplog: pytest.LogCaptureFixture,
):
    """Test an exact walk keeps its children and an overshooting walk drops them."""
    api_client, prefix = api_client_with_prefix

    with (
        patch.object(coresys.hardware.disk, "disk_usage_for_mount") as mock_disk_usage,
        patch.object(
            coresys.hardware.disk, "get_dir_structure_sizes"
        ) as mock_structure,
    ):
        # used = total - free = 1200000000
        mock_disk_usage.return_value = (2000000000, 999, 800000000)
        mock_structure.return_value = {
            "used_bytes": walked_bytes,
            "children": [
                {"id": "movies", "label": "movies", "used_bytes": walked_bytes},
            ],
        }

        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage?max_depth=2")

    assert resp.status == 200
    result = await resp.json()
    if expect_children:
        assert result["data"]["children"] == [
            {"id": "movies", "label": "movies", "used_bytes": walked_bytes},
        ]
        assert "Omitting the breakdown" not in caplog.text
    else:
        assert "children" not in result["data"]
        # Dropped data is not silent: leave a trace for user reports
        assert "Directory sizes of mount media_test" in caplog.text
        assert "Omitting the breakdown" in caplog.text
    # Either way the children never sum past used_bytes
    assert (
        sum(child["used_bytes"] for child in result["data"].get("children", []))
        <= result["data"]["used_bytes"]
    )


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_disk_usage_api_unknown_mount(
    api_client_with_prefix: tuple[TestClient, str],
):
    """Test requesting usage for a mount that does not exist."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/host/disks/nope/usage")

    assert resp.status == 404
    result = await resp.json()
    assert result["message"] == "No mount exists with name nope"
    assert result["error_key"] == "mount_not_found_error"
    assert result["extra_fields"] == {"name": "nope"}


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
@pytest.mark.parametrize(
    "stale_state",
    [UnitActiveState.INACTIVE, UnitActiveState.FAILED, None],
    ids=["dormant-trigger", "last-probe-failed", "state-unknown"],
)
async def test_disk_usage_api_probes_regardless_of_cached_state(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    stale_state: UnitActiveState | None,
):
    """Test usage comes from the probe, not cached mount state."""
    api_client, prefix = api_client_with_prefix
    _register_mount(coresys, "media_test", stale_state)

    with patch.object(coresys.hardware.disk, "disk_usage_for_mount") as mock_disk_usage:
        mock_disk_usage.return_value = (2000000000, 999, 800000000)
        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["used_bytes"] == 1200000000
    mock_disk_usage.assert_called_once()


@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_mount_timeout(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test a probe that never returns fails cleanly for that mount."""
    api_client, prefix = api_client_with_prefix

    def _never_returns(_):
        time.sleep(0.5)
        return (1, 1, 1)

    with (
        patch("supervisor.api.host.MOUNT_USAGE_TIMEOUT", 0.05),
        patch.object(
            coresys.hardware.disk, "disk_usage_for_mount", side_effect=_never_returns
        ),
    ):
        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage")

    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == "mount_usage_timeout_error"
    assert result["extra_fields"] == {"name": "media_test"}


@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_mount_unreachable(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test an unreachable mount reports an error rather than failing the API."""
    api_client, prefix = api_client_with_prefix

    with patch.object(
        coresys.hardware.disk,
        "disk_usage_for_mount",
        side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
    ):
        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage")

    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == "mount_usage_read_error"
    assert result["extra_fields"]["name"] == "media_test"
    assert "Host is down" in result["extra_fields"]["reason"]


@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_ghost_mount(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test a vanished mount is an error, not host-disk numbers."""
    api_client, prefix = api_client_with_prefix

    with (
        patch.object(coresys.hardware.disk, "disk_usage_for_mount", return_value=None),
        patch.object(
            coresys.hardware.disk, "get_dir_structure_sizes"
        ) as mock_structure,
    ):
        resp = await api_client.get(f"{prefix}/host/disks/media_test/usage?max_depth=2")

    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == "mount_usage_not_mounted_error"
    assert result["extra_fields"] == {"name": "media_test"}
    # A ghost is never walked either
    mock_structure.assert_not_called()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_mount_usage_caller_timeout_joins_same_probe(coresys: CoreSys):
    """Test a caller's timeout neither cancels nor orphans the shared probe.

    A probe killed by its own timeout would be dropped from the registry while
    its executor thread stays parked in the kernel, so the next request would
    stack a fresh thread against the same mount. The timeout therefore bounds
    only the caller's wait: the probe and its registry entry outlive slow
    callers, and later callers join the same probe.
    """
    api_host = APIHost()
    api_host.coresys = coresys
    mount = _register_mount(coresys, "media_test", UnitActiveState.ACTIVE)

    def _slow(_):
        time.sleep(0.4)
        return (2000000000, 999, 800000000)

    with patch.object(
        coresys.hardware.disk, "disk_usage_for_mount", side_effect=_slow
    ) as mock_usage:
        with (
            patch("supervisor.api.host.MOUNT_USAGE_TIMEOUT", 0.05),
            pytest.raises(
                MountUsageTimeoutError, match="Timed out reading storage usage"
            ),
        ):
            await api_host._mount_usage(mount, 0)

        # The probe survived its caller: still registered, still running
        assert ("media_test", 0) in api_host._mount_usage_probes

        # A later caller (with the real, generous timeout) joins that same
        # probe rather than starting another executor thread
        result = await api_host._mount_usage(mount, 0)

    assert result["used_bytes"] == 1200000000
    mock_usage.assert_called_once()
    # Completion popped the entry, so the next request starts fresh
    assert not api_host._mount_usage_probes


@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_mount_shares_in_flight_probe(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test concurrent requests for the same mount share one probe.

    A probe of an unreachable mount blocks until the kernel gives up, so
    stacking one executor thread per caller is what this guards against.
    """
    api_client, prefix = api_client_with_prefix

    def _slow(_):
        time.sleep(0.3)
        return (2000000000, 999, 800000000)

    with patch.object(
        coresys.hardware.disk, "disk_usage_for_mount", side_effect=_slow
    ) as mock_disk_usage:
        first, second = await asyncio.gather(
            api_client.get(f"{prefix}/host/disks/media_test/usage"),
            api_client.get(f"{prefix}/host/disks/media_test/usage"),
        )

    assert first.status == 200
    assert second.status == 200
    assert (await first.json())["data"] == (await second.json())["data"]
    mock_disk_usage.assert_called_once()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_mount_usage_abandoned_probe_retrieves_its_exception(coresys: CoreSys):
    """Test an abandoned failing probe is not reported as an unretrieved exception.

    The shield deliberately keeps a probe alive past the caller that started it,
    so a browser giving up on an unreachable mount leaves a probe that still
    fails later with nobody waiting on it. Left unretrieved, asyncio reports it
    with a traceback that reads like a supervisor fault rather than a mount that
    was never going to answer.
    """
    api_host = APIHost()
    api_host.coresys = coresys
    mount = _register_mount(coresys, "media_test", UnitActiveState.ACTIVE)

    reported: list[dict[str, Any]] = []
    loop = asyncio.get_running_loop()
    previous_handler = loop.get_exception_handler()
    loop.set_exception_handler(lambda _loop, context: reported.append(context))

    def _fails_slowly(_):
        time.sleep(0.2)
        raise OSError(errno.EHOSTDOWN, "Host is down")

    try:
        with patch.object(
            coresys.hardware.disk, "disk_usage_for_mount", side_effect=_fails_slowly
        ):
            waiter = asyncio.create_task(api_host._mount_usage(mount, 0))

            # Let the probe get going, then abandon it the way a disconnecting
            # client does
            await asyncio.sleep(0.05)
            waiter.cancel()
            with suppress(asyncio.CancelledError):
                await waiter

            # Give the orphaned probe time to fail, then force collection so an
            # unretrieved exception would be surfaced
            await asyncio.sleep(0.5)
            gc.collect()
            await asyncio.sleep(0)
    finally:
        loop.set_exception_handler(previous_handler)

    # Nothing at all should reach the loop exception handler: an unreachable
    # mount is an expected outcome, not a supervisor fault
    assert not reported
    # The entry is gone either way, so a later request starts a fresh probe
    assert not api_host._mount_usage_probes


@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_mount_depths_below_two_share_one_probe(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test concurrent callers at depths 0 and 1 share a single probe."""
    api_client, prefix = api_client_with_prefix

    def _slow(_):
        time.sleep(0.3)
        return (2000000000, 999, 800000000)

    with patch.object(
        coresys.hardware.disk, "disk_usage_for_mount", side_effect=_slow
    ) as mock_disk_usage:
        first, second = await asyncio.gather(
            api_client.get(f"{prefix}/host/disks/media_test/usage?max_depth=0"),
            api_client.get(f"{prefix}/host/disks/media_test/usage?max_depth=1"),
        )

    assert first.status == 200
    assert second.status == 200
    assert (await first.json())["data"] == (await second.json())["data"]
    mock_disk_usage.assert_called_once()


@pytest.mark.usefixtures("active_mount")
async def test_disk_usage_api_v1_mount_children_are_not_remapped(
    api_client: TestClient, coresys: CoreSys
):
    """Test a mount directory named apps_data keeps its name in v1 responses."""
    with (
        patch.object(coresys.hardware.disk, "disk_usage_for_mount") as mock_disk_usage,
        patch.object(
            coresys.hardware.disk, "get_dir_structure_sizes"
        ) as mock_structure,
    ):
        mock_disk_usage.return_value = (2000000000, 999, 800000000)
        mock_structure.return_value = {
            "used_bytes": 1200000000,
            "children": [
                {"id": "apps_data", "label": "apps_data", "used_bytes": 1200000000},
            ],
        }

        resp = await api_client.get("/host/disks/media_test/usage?max_depth=2")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["children"] == [
        {"id": "apps_data", "label": "apps_data", "used_bytes": 1200000000},
    ]


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_disk_usage_api_default_wins_over_mount_of_that_name(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test "default" always means the system disk.

    The mount name pattern permits a mount called "default", so the resolution
    order has to be documented and pinned: the reserved target wins.
    """
    api_client, prefix = api_client_with_prefix
    _register_mount(coresys, "default", UnitActiveState.ACTIVE)

    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)
        mock_dir_sizes.return_value = []

        resp = await api_client.get(f"{prefix}/host/disks/default/usage")

    assert resp.status == 200
    result = await resp.json()
    # The system disk, not the mount
    assert result["data"]["id"] == "root"
    assert result["data"]["label"] == "Root"
