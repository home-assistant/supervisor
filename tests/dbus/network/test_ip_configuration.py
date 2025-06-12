"""Test Network Manager IP configuration object."""

from ipaddress import IPv4Address, IPv6Address

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.network.ip_configuration import IpConfiguration

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.network_ip4config import IP4Config as IP4ConfigService
from tests.dbus_service_mocks.network_ip6config import IP6Config as IP6ConfigService


@pytest.fixture(name="ip4config_service")
async def fixture_ip4config_service(dbus_session_bus: MessageBus) -> IP4ConfigService:
    """Mock IP4Config service."""
    yield (await mock_dbus_services({"network_ip4config": None}, dbus_session_bus))[
        "network_ip4config"
    ]


@pytest.fixture(name="ip6config_service")
async def fixture_ip6config_service(dbus_session_bus: MessageBus) -> IP4ConfigService:
    """Mock IP6Config service."""
    yield (await mock_dbus_services({"network_ip6config": None}, dbus_session_bus))[
        "network_ip6config"
    ]


async def test_ipv4_configuration(
    ip4config_service: IP4ConfigService, dbus_session_bus: MessageBus
):
    """Test IPv4 configuration object."""
    ip4 = IpConfiguration("/org/freedesktop/NetworkManager/IP4Config/1")

    assert ip4.gateway is None
    assert ip4.nameservers is None

    await ip4.connect(dbus_session_bus)

    assert ip4.gateway == IPv4Address("192.168.2.1")
    assert ip4.nameservers == [IPv4Address("192.168.2.2")]

    ip4config_service.emit_properties_changed({"Gateway": "192.168.100.1"})
    await ip4config_service.ping()
    assert ip4.gateway == IPv4Address("192.168.100.1")

    ip4config_service.emit_properties_changed({}, ["Gateway"])
    await ip4config_service.ping()
    await ip4config_service.ping()
    assert ip4.gateway == IPv4Address("192.168.2.1")


async def test_ipv6_configuration(
    ip6config_service: IP6ConfigService, dbus_session_bus: MessageBus
):
    """Test IPv6 configuration object."""
    ip6 = IpConfiguration("/org/freedesktop/NetworkManager/IP6Config/1", ip4=False)

    assert ip6.gateway is None
    assert ip6.nameservers is None

    await ip6.connect(dbus_session_bus)

    assert ip6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")
    assert ip6.nameservers == [
        IPv6Address("2001:1620:2777:1::10"),
        IPv6Address("2001:1620:2777:2::20"),
    ]

    ip6config_service.emit_properties_changed({"Gateway": "2001:1620:2777:1::10"})
    await ip6config_service.ping()
    assert ip6.gateway == IPv6Address("2001:1620:2777:1::10")

    ip6config_service.emit_properties_changed({}, ["Gateway"])
    await ip6config_service.ping()
    await ip6config_service.ping()
    assert ip6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")


async def test_gateway_empty_string(
    ip4config_service: IP4ConfigService, dbus_session_bus: MessageBus
):
    """Test empty string in gateway returns None."""
    ip4 = IpConfiguration("/org/freedesktop/NetworkManager/IP4Config/1", ip4=True)
    await ip4.connect(dbus_session_bus)

    ip4config_service.emit_properties_changed({"Gateway": ""})
    await ip4config_service.ping()
    assert ip4.gateway is None
