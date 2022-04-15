"""Test DNS plugin."""
from pathlib import Path
from unittest.mock import AsyncMock, Mock, call, patch

from aiodns.error import DNSError
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.resolution.const import ContextType, IssueType


@pytest.fixture(name="docker_interface")
async def fixture_docker_interface() -> tuple[AsyncMock, AsyncMock]:
    """Mock docker interface methods."""
    # with patch("supervisor.docker.interface.DockerInterface.run"), patch("supervisor.docker.interface.DockerInterface.restart")
    with patch.object(DockerInterface, "run") as run, patch.object(
        DockerInterface, "restart"
    ) as restart:
        yield (run, restart)


@pytest.fixture(name="write_json")
async def fixture_write_json() -> Mock:
    """Mock json file writer."""
    with patch("supervisor.plugins.dns.write_json_file") as write_json_file:
        yield write_json_file


@pytest.fixture(name="dns_query")
async def fixture_dns_query() -> AsyncMock:
    """Mock aiodns query."""
    with patch(
        "supervisor.plugins.dns.aiodns.DNSResolver.query", new_callable=AsyncMock
    ) as dns_query:
        yield dns_query


@pytest.mark.parametrize("start", [True, False])
async def test_config_write(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
    dns_query: AsyncMock,
    start: bool,
):
    """Test config write on DNS start and restart."""
    assert len(coresys.resolution.issues) == 0
    assert coresys.plugins.dns.locals == ["dns://192.168.30.1"]
    coresys.plugins.dns.servers = ["dns://1.1.1.1", "dns://8.8.8.8"]

    if start:
        await coresys.plugins.dns.start()
        docker_interface[0].assert_called_once()
        docker_interface[1].assert_not_called()
    else:
        await coresys.plugins.dns.restart()
        docker_interface[0].assert_not_called()
        docker_interface[1].assert_called_once()

    write_json.assert_called_once_with(
        Path("/data/dns/coredns.json"),
        {
            "servers": ["dns://1.1.1.1", "dns://8.8.8.8"],
            "locals": ["dns://192.168.30.1"],
            "debug": False,
        },
    )
    assert dns_query.call_count == 6
    assert len(coresys.resolution.issues) == 0


async def test_dns_server_failure(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
    dns_query: AsyncMock,
):
    """Test issue created on DNS server failure."""
    assert len(coresys.resolution.issues) == 0
    assert coresys.plugins.dns.locals == ["dns://192.168.30.1"]

    dns_query.side_effect = DNSError()
    await coresys.plugins.dns.start()
    docker_interface[0].assert_called_once()
    docker_interface[1].assert_not_called()

    write_json.assert_called_once_with(
        Path("/data/dns/coredns.json"),
        {
            "servers": [],
            "locals": ["dns://192.168.30.1"],
            "debug": False,
        },
    )
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "A")

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type == IssueType.DNS_SERVER_FAILED
    assert coresys.resolution.issues[0].context == ContextType.DNS_SERVER
    assert coresys.resolution.issues[0].reference == "dns://192.168.30.1"

    # Ensure restart does not duplicate the issue
    dns_query.reset_mock()
    await coresys.plugins.dns.restart()

    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "A")
    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type == IssueType.DNS_SERVER_FAILED
    assert coresys.resolution.issues[0].context == ContextType.DNS_SERVER
    assert coresys.resolution.issues[0].reference == "dns://192.168.30.1"


@pytest.mark.parametrize(
    "error_code,error_message",
    [(1, "DNS server returned answer with no data"), (4, "Domain name not found")],
)
async def test_dns_server_ipv6_behavior(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
    dns_query: AsyncMock,
    error_code: int,
    error_message: str,
):
    """Test DNS server handling ipv6 incorrectly creates issue."""
    assert len(coresys.resolution.issues) == 0
    assert coresys.plugins.dns.locals == ["dns://192.168.30.1"]

    dns_query.side_effect = [
        None,
        DNSError(error_code, error_message),
    ]
    await coresys.plugins.dns.start()

    write_json.assert_called_once_with(
        Path("/data/dns/coredns.json"),
        {
            "servers": [],
            "locals": ["dns://192.168.30.1"],
            "debug": False,
        },
    )
    docker_interface[0].assert_called_once()
    docker_interface[1].assert_not_called()
    assert dns_query.call_count == 2
    assert dns_query.call_args_list == [
        call("_checkdns.home-assistant.io", "A"),
        call("_checkdns.home-assistant.io", "AAAA"),
    ]

    if error_code == 1:
        assert len(coresys.resolution.issues) == 0
    else:
        assert len(coresys.resolution.issues) == 1
        assert coresys.resolution.issues[0].type == IssueType.DNS_SERVER_IPV6_ERROR
        assert coresys.resolution.issues[0].context == ContextType.DNS_SERVER
        assert coresys.resolution.issues[0].reference == "dns://192.168.30.1"
