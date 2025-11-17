"""Test systemd-resolved dbus interface."""
# pylint: disable=import-error

from socket import AF_INET6, inet_aton, inet_pton

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import (
    DNSOverTLSEnabled,
    DNSSECValidation,
    DNSStubListenerEnabled,
    MulticastProtocolEnabled,
    ResolvConfMode,
)
from supervisor.dbus.resolved import Resolved

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.resolved import Resolved as ResolvedService


@pytest.fixture(name="resolved_service")
async def fixture_resolved_service(dbus_session_bus: MessageBus) -> ResolvedService:
    """Mock resolved dbus service."""
    yield (await mock_dbus_services({"resolved": None}, dbus_session_bus))["resolved"]


async def test_dbus_resolved_info(
    resolved_service: ResolvedService, dbus_session_bus: MessageBus
):
    """Test systemd-resolved dbus connection."""
    resolved = Resolved()

    assert resolved.dns is None

    await resolved.connect(dbus_session_bus)

    assert resolved.llmnr_hostname == "homeassistant"
    assert resolved.llmnr == MulticastProtocolEnabled.YES
    assert resolved.multicast_dns == MulticastProtocolEnabled.RESOLVE
    assert resolved.dns_over_tls == DNSOverTLSEnabled.NO

    assert len(resolved.dns) == 2
    assert resolved.dns[0] == (0, 2, inet_aton("127.0.0.1"))
    assert resolved.dns[1] == (0, 10, inet_pton(AF_INET6, "::1"))
    assert len(resolved.dns_ex) == 2
    assert resolved.dns_ex[0] == (0, 2, inet_aton("127.0.0.1"), 0, "")
    assert resolved.dns_ex[1] == (0, 10, inet_pton(AF_INET6, "::1"), 0, "")

    assert len(resolved.fallback_dns) == 2
    assert resolved.fallback_dns[0] == (0, 2, inet_aton("1.1.1.1"))
    assert resolved.fallback_dns[1] == (
        0,
        10,
        inet_pton(AF_INET6, "2606:4700:4700::1111"),
    )
    assert len(resolved.fallback_dns_ex) == 2
    assert resolved.fallback_dns_ex[0] == (
        0,
        2,
        inet_aton("1.1.1.1"),
        0,
        "cloudflare-dns.com",
    )
    assert resolved.fallback_dns_ex[1] == (
        0,
        10,
        inet_pton(AF_INET6, "2606:4700:4700::1111"),
        0,
        "cloudflare-dns.com",
    )

    assert resolved.current_dns_server == (0, 2, inet_aton("127.0.0.1"))
    assert resolved.current_dns_server_ex == (
        0,
        2,
        inet_aton("127.0.0.1"),
        0,
        "",
    )

    assert len(resolved.domains) == 1
    assert resolved.domains[0] == (0, "local.hass.io", False)

    assert resolved.transaction_statistics == (0, 100000)
    assert resolved.cache_statistics == (10, 50000, 10000)
    assert resolved.dnssec == DNSSECValidation.NO
    assert resolved.dnssec_statistics == (0, 0, 0, 0)
    assert resolved.dnssec_supported is False
    assert resolved.dnssec_negative_trust_anchors == [
        "168.192.in-addr.arpa",
        "local",
    ]
    assert resolved.dns_stub_listener == DNSStubListenerEnabled.NO
    assert resolved.resolv_conf_mode == ResolvConfMode.FOREIGN

    resolved_service.emit_properties_changed({"LLMNRHostname": "test"})
    await resolved_service.ping()
    assert resolved.llmnr_hostname == "test"

    resolved_service.emit_properties_changed({}, ["LLMNRHostname"])
    await resolved_service.ping()
    await resolved_service.ping()  # To process the follow-up get all properties call
    assert resolved.llmnr_hostname == "homeassistant"


async def test_dbus_resolved_connect_error(
    dbus_session_bus: MessageBus, caplog: pytest.LogCaptureFixture
):
    """Test connecting to resolved error."""
    resolved = Resolved()
    await resolved.connect(dbus_session_bus)
    assert "Host has no systemd-resolved support" in caplog.text
