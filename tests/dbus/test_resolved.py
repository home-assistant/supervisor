"""Test systemd-resolved dbus interface."""

from socket import AF_INET6, inet_aton, inet_pton
from unittest.mock import patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import (
    DNSOverTLSEnabled,
    DNSSECValidation,
    DNSStubListenerEnabled,
    MulticastProtocolEnabled,
    ResolvConfMode,
)

DNS_IP_FIELDS = [
    "DNS",
    "DNSEx",
    "FallbackDNS",
    "FallbackDNSEx",
    "CurrentDNSServer",
    "CurrentDNSServerEx",
]


@pytest.fixture(name="coresys_ip_bytes")
async def fixture_coresys_ip_bytes(coresys: CoreSys) -> CoreSys:
    """Coresys with ip addresses correctly mocked as bytes."""
    get_properties = coresys.dbus.network.dbus.get_properties

    async def mock_get_properties(dbus_obj, interface):
        reply = await get_properties(interface)

        for field in DNS_IP_FIELDS:
            if field in reply and len(reply[field]) > 0:
                if isinstance(reply[field][0], list):
                    for entry in reply[field]:
                        entry[2] = bytes(entry[2])
                else:
                    reply[field][2] = bytes(reply[field][2])

        return reply

    with patch("supervisor.utils.dbus.DBus.get_properties", new=mock_get_properties):
        yield coresys


async def test_dbus_resolved_info(coresys_ip_bytes: CoreSys):
    """Test systemd-resolved dbus connection."""
    coresys = coresys_ip_bytes

    assert coresys.dbus.resolved.dns is None

    await coresys.dbus.resolved.connect(coresys.dbus.bus)
    await coresys.dbus.resolved.update()

    assert coresys.dbus.resolved.llmnr_hostname == "homeassistant"
    assert coresys.dbus.resolved.llmnr == MulticastProtocolEnabled.YES
    assert coresys.dbus.resolved.multicast_dns == MulticastProtocolEnabled.RESOLVE
    assert coresys.dbus.resolved.dns_over_tls == DNSOverTLSEnabled.NO

    assert len(coresys.dbus.resolved.dns) == 2
    assert coresys.dbus.resolved.dns[0] == [0, 2, inet_aton("127.0.0.1")]
    assert coresys.dbus.resolved.dns[1] == [0, 10, inet_pton(AF_INET6, "::1")]
    assert len(coresys.dbus.resolved.dns_ex) == 2
    assert coresys.dbus.resolved.dns_ex[0] == [0, 2, inet_aton("127.0.0.1"), 0, ""]
    assert coresys.dbus.resolved.dns_ex[1] == [0, 10, inet_pton(AF_INET6, "::1"), 0, ""]

    assert len(coresys.dbus.resolved.fallback_dns) == 2
    assert coresys.dbus.resolved.fallback_dns[0] == [0, 2, inet_aton("1.1.1.1")]
    assert coresys.dbus.resolved.fallback_dns[1] == [
        0,
        10,
        inet_pton(AF_INET6, "2606:4700:4700::1111"),
    ]
    assert len(coresys.dbus.resolved.fallback_dns_ex) == 2
    assert coresys.dbus.resolved.fallback_dns_ex[0] == [
        0,
        2,
        inet_aton("1.1.1.1"),
        0,
        "cloudflare-dns.com",
    ]
    assert coresys.dbus.resolved.fallback_dns_ex[1] == [
        0,
        10,
        inet_pton(AF_INET6, "2606:4700:4700::1111"),
        0,
        "cloudflare-dns.com",
    ]

    assert coresys.dbus.resolved.current_dns_server == [0, 2, inet_aton("127.0.0.1")]
    assert coresys.dbus.resolved.current_dns_server_ex == [
        0,
        2,
        inet_aton("127.0.0.1"),
        0,
        "",
    ]

    assert len(coresys.dbus.resolved.domains) == 1
    assert coresys.dbus.resolved.domains[0] == [0, "local.hass.io", False]

    assert coresys.dbus.resolved.transaction_statistics == [0, 100000]
    assert coresys.dbus.resolved.cache_statistics == [10, 50000, 10000]
    assert coresys.dbus.resolved.dnssec == DNSSECValidation.NO
    assert coresys.dbus.resolved.dnssec_statistics == [0, 0, 0, 0]
    assert coresys.dbus.resolved.dnssec_supported is False
    assert coresys.dbus.resolved.dnssec_negative_trust_anchors == [
        "168.192.in-addr.arpa",
        "local",
    ]
    assert coresys.dbus.resolved.dns_stub_listener == DNSStubListenerEnabled.NO
    assert coresys.dbus.resolved.resolv_conf_mode == ResolvConfMode.FOREIGN
