"""Test Host API."""

from collections.abc import AsyncGenerator
from unittest.mock import ANY, MagicMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.resolved import Resolved
from supervisor.homeassistant.api import APIState
from supervisor.host.const import LogFormat, LogFormatter
from supervisor.host.control import SystemControl

from tests.dbus_service_mocks.base import DBusServiceMock
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
    coresys.host.sys_dbus.udisks2.is_connected = False

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
    assert "disk" not in result["data"]["features"]

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

    coresys.host.sys_dbus.udisks2.is_connected = True
    coresys.host.supported_features.cache_clear()
    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert "disk" in result["data"]["features"]


async def test_api_llmnr_mdns_info(api_client: TestClient, coresys_disk_info: CoreSys):
    """Test llmnr and mdns details in info."""
    coresys = coresys_disk_info
    # pylint: disable=protected-access
    coresys.host.sys_dbus._resolved = Resolved()
    # pylint: enable=protected-access

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["broadcast_llmnr"] is None
    assert result["data"]["broadcast_mdns"] is None
    assert result["data"]["llmnr_hostname"] is None

    await coresys.dbus.resolved.connect(coresys.dbus.bus)

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["broadcast_llmnr"] is True
    assert result["data"]["broadcast_mdns"] is False
    assert result["data"]["llmnr_hostname"] == "homeassistant"


async def test_api_boot_ids_info(api_client: TestClient, journald_logs: MagicMock):
    """Test getting boot IDs."""
    resp = await api_client.get("/host/logs/boots")
    result = await resp.json()
    assert result["data"] == {"boots": {"0": "ccc", "-1": "bbb", "-2": "aaa"}}


async def test_api_identifiers_info(api_client: TestClient, journald_logs: MagicMock):
    """Test getting syslog identifiers."""
    resp = await api_client.get("/host/logs/identifiers")
    result = await resp.json()
    assert result["data"] == {
        "identifiers": ["hassio_supervisor", "hassos-config", "kernel"]
    }


async def test_api_virtualization_info(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    coresys_disk_info: CoreSys,
):
    """Test getting virtualization info."""
    systemd_service: SystemdService = all_dbus_services["systemd"]

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["virtualization"] == ""

    systemd_service.virtualization = "vmware"
    await coresys_disk_info.dbus.systemd.update()

    resp = await api_client.get("/host/info")
    result = await resp.json()
    assert result["data"]["virtualization"] == "vmware"


async def test_advanced_logs(
    api_client: TestClient, coresys: CoreSys, journald_logs: MagicMock
):
    """Test advanced logging API entries with identifier and custom boot."""
    await api_client.get("/host/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    identifier = "dropbear"
    await api_client.get(f"/host/logs/identifiers/{identifier}")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": identifier},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
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
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get(f"/host/logs/boots/{bootid}/identifiers/{identifier}")
    journald_logs.assert_called_once_with(
        params={"_BOOT_ID": bootid, "SYSLOG_IDENTIFIER": identifier},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    headers = {"Range": "entries=:-19:10"}
    await api_client.get("/host/logs", headers=headers)
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=headers["Range"],
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/follow")
    journald_logs.assert_called_once_with(
        params={
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
            "follow": "",
        },
        range_header=DEFAULT_RANGE_FOLLOW,
        accept=LogFormat.JOURNAL,
    )

    # Host logs don't have a /latest endpoint
    resp = await api_client.get("/host/logs/latest")
    assert resp.status == 404


async def test_advaced_logs_query_parameters(
    api_client: TestClient,
    coresys: CoreSys,
    journald_logs: MagicMock,
    journal_logs_reader: MagicMock,
):
    """Test advanced logging API entries controlled by query parameters."""
    # Check lines query parameter
    await api_client.get("/host/logs?lines=53")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header="entries=:-52:53",
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    # Check verbose logs formatter via query parameter
    await api_client.get("/host/logs?verbose")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers},
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, LogFormatter.VERBOSE)

    journal_logs_reader.reset_mock()
    journald_logs.reset_mock()

    # Query parameters should take precedence over headers
    await api_client.get(
        "/host/logs?lines=53&verbose",
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
    journal_logs_reader.assert_called_with(ANY, LogFormatter.VERBOSE)


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
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/boots/-2")
    journald_logs.assert_called_once_with(
        params={
            "_BOOT_ID": "aaa",
            "SYSLOG_IDENTIFIER": coresys.host.logs.default_identifiers,
        },
        range_header=DEFAULT_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    await api_client.get("/host/logs/boots/2")
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
    api_client: TestClient,
    coresys: CoreSys,
    journal_logs_reader: MagicMock,
):
    """Test advanced logs formatters varying on Accept header."""

    await api_client.get("/host/logs")
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.VERBOSE)

    journal_logs_reader.reset_mock()

    headers = {"Accept": "text/x-log"}
    await api_client.get("/host/logs", headers=headers)
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.VERBOSE)

    journal_logs_reader.reset_mock()

    await api_client.get("/host/logs/identifiers/test")
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.PLAIN)

    journal_logs_reader.reset_mock()

    headers = {"Accept": "text/x-log"}
    await api_client.get("/host/logs/identifiers/test", headers=headers)
    journal_logs_reader.assert_called_once_with(ANY, LogFormatter.VERBOSE)


async def test_advanced_logs_errors(coresys: CoreSys, api_client: TestClient):
    """Test advanced logging API errors."""
    with patch("supervisor.host.logs.SYSTEMD_JOURNAL_GATEWAYD_SOCKET") as socket:
        socket.is_socket.return_value = False
        await coresys.host.logs.post_init()
        resp = await api_client.get("/host/logs")
        assert resp.content_type == "text/plain"
        assert resp.status == 400
        content = await resp.text()
        assert content == "No systemd-journal-gatewayd Unix socket available"

    headers = {"Accept": "application/json"}
    resp = await api_client.get("/host/logs", headers=headers)
    assert resp.content_type == "text/plain"
    assert resp.status == 400
    content = await resp.text()
    assert (
        content
        == "Invalid content type requested. Only text/plain and text/x-log supported for now."
    )


async def test_disk_usage_api(api_client: TestClient, coresys: CoreSys):
    """Test disk usage API endpoint."""
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
                "id": "addons_data",
                "label": "Addons Data",
                "used_bytes": 100000000,
                "children": [
                    {"id": "addon1", "label": "addon1", "used_bytes": 50000000}
                ],
            },
            {
                "id": "addons_config",
                "label": "Addons Config",
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
        resp = await api_client.get("/host/disks/default/usage")
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
        assert children[1]["id"] == "addons_data"
        assert children[2]["id"] == "addons_config"
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
        assert paths_dict["addons_data"] == coresys.config.path_addons_data
        assert paths_dict["addons_config"] == coresys.config.path_addon_configs
        assert paths_dict["media"] == coresys.config.path_media
        assert paths_dict["share"] == coresys.config.path_share
        assert paths_dict["backup"] == coresys.config.path_backup
        assert paths_dict["ssl"] == coresys.config.path_ssl
        assert paths_dict["homeassistant"] == coresys.config.path_homeassistant


async def test_disk_usage_api_with_custom_depth(
    api_client: TestClient, coresys: CoreSys
):
    """Test disk usage API endpoint with custom max_depth parameter."""
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)

        # Mock deeper directory structure
        mock_dir_sizes.return_value = [
            {
                "id": "addons_data",
                "label": "Addons Data",
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
                "id": "addons_config",
                "label": "Addons Config",
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
        resp = await api_client.get("/host/disks/default/usage?max_depth=2")
        assert resp.status == 200
        result = await resp.json()
        assert result["data"]["used_bytes"] == 500000000
        assert result["data"]["children"]

        # Verify max_depth=2 was passed to get_dir_sizes
        assert mock_dir_sizes.call_count == 1
        call_args = mock_dir_sizes.call_args
        assert call_args[0][1] == 2  # max_depth parameter


async def test_disk_usage_api_invalid_depth(api_client: TestClient, coresys: CoreSys):
    """Test disk usage API endpoint with invalid max_depth parameter."""
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)
        mock_dir_sizes.return_value = [
            {
                "id": "addons_data",
                "label": "Addons Data",
                "used_bytes": 100000000,
            },
            {
                "id": "addons_config",
                "label": "Addons Config",
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
        resp = await api_client.get("/host/disks/default/usage?max_depth=invalid")
        assert resp.status == 200
        result = await resp.json()
        assert result["data"]["used_bytes"] == 500000000
        assert result["data"]["children"]

        # Should default to max_depth=1 when invalid value is provided
        assert mock_dir_sizes.call_count == 1
        call_args = mock_dir_sizes.call_args
        assert call_args[0][1] == 1  # Should default to 1


async def test_disk_usage_api_empty_directories(
    api_client: TestClient, coresys: CoreSys
):
    """Test disk usage API endpoint with empty directories."""
    with (
        patch.object(coresys.hardware.disk, "disk_usage") as mock_disk_usage,
        patch.object(coresys.hardware.disk, "get_dir_sizes") as mock_dir_sizes,
    ):
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)

        # Mock empty directory structures (no children)
        mock_dir_sizes.return_value = [
            {
                "id": "addons_data",
                "label": "Addons Data",
                "used_bytes": 0,
            },
            {
                "id": "addons_config",
                "label": "Addons Config",
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

        resp = await api_client.get("/host/disks/default/usage")
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


@pytest.mark.parametrize("action", ["reboot", "shutdown"])
async def test_migration_blocks_shutdown(
    api_client: TestClient,
    coresys: CoreSys,
    action: str,
):
    """Test that an offline db migration in progress stops users from shuting down or rebooting system."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    resp = await api_client.post(f"/host/{action}")
    assert resp.status == 503
    result = await resp.json()
    assert (
        result["message"]
        == "Home Assistant offline database migration in progress, please wait until complete before shutting down host"
    )


async def test_force_reboot_during_migration(api_client: TestClient, coresys: CoreSys):
    """Test force option reboots even during a migration."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(SystemControl, "reboot") as reboot:
        await api_client.post("/host/reboot", json={"force": True})
        reboot.assert_called_once()


async def test_force_shutdown_during_migration(
    api_client: TestClient, coresys: CoreSys
):
    """Test force option shutdown even during a migration."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(SystemControl, "shutdown") as shutdown:
        await api_client.post("/host/shutdown", json={"force": True})
        shutdown.assert_called_once()
