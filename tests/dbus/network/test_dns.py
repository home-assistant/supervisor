"""Test DNS Manager object."""

from ipaddress import IPv4Address

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.network.configuration import DNSConfiguration
from supervisor.dbus.network.dns import NetworkManagerDNS

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.network_dns_manager import DnsManager as DnsManagerService


@pytest.fixture(name="dns_manager_service")
async def fixture_dns_manager_service(
    dbus_session_bus: MessageBus,
) -> DnsManagerService:
    """Mock DnsManager dbus service."""
    yield (await mock_dbus_services({"network_dns_manager": None}, dbus_session_bus))[
        "network_dns_manager"
    ]


async def test_dns(
    dns_manager_service: DnsManagerService, dbus_session_bus: MessageBus
):
    """Test dns manager."""
    dns_manager = NetworkManagerDNS()

    assert dns_manager.mode is None
    assert dns_manager.rc_manager is None

    await dns_manager.connect(dbus_session_bus)

    assert dns_manager.mode == "default"
    assert dns_manager.rc_manager == "file"
    assert dns_manager.configuration == [
        DNSConfiguration(
            [IPv4Address("192.168.30.1")], ["syshack.ch"], "eth0", 100, False
        )
    ]

    dns_manager_service.emit_properties_changed({"Mode": "test"})
    await dns_manager_service.ping()
    assert dns_manager.mode == "test"

    dns_manager_service.emit_properties_changed({}, ["Mode"])
    await dns_manager_service.ping()
    await dns_manager_service.ping()
    assert dns_manager.mode == "default"


async def test_dbus_dns_connect_error(
    dbus_session_bus: MessageBus, caplog: pytest.LogCaptureFixture
):
    """Test connecting to dns error."""
    dns_manager = NetworkManagerDNS()
    await dns_manager.connect(dbus_session_bus)
    assert "No DnsManager support on the host" in caplog.text
