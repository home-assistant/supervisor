"""Test host firewall manager."""

from unittest.mock import patch

import pytest

from supervisor.const import DOCKER_IPV4_NETWORK_MASK, DOCKER_IPV6_NETWORK_MASK
from supervisor.coresys import CoreSys
from supervisor.dbus.const import StartUnitMode
from supervisor.host.firewall import (
    FIREWALL_SERVICE,
    IP6TABLES_CMD,
    IPTABLES_CMD,
    SHELL_CMD,
    FirewallManager,
)

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


@pytest.fixture(name="systemd_service")
async def fixture_systemd_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> SystemdService:
    """Return systemd service mock."""
    yield all_dbus_services["systemd"]


async def test_apply_gateway_protection(
    coresys: CoreSys, systemd_service: SystemdService
):
    """Test gateway protection rules are applied."""
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()

    await coresys.host.firewall.apply_gateway_protection()

    assert len(systemd_service.StartTransientUnit.calls) == 1
    call = systemd_service.StartTransientUnit.calls[0]
    assert call[0] == FIREWALL_SERVICE
    assert call[1] == StartUnitMode.REPLACE


async def test_apply_gateway_protection_exec_start_rules(coresys: CoreSys):
    """Test correct iptables rules are generated."""
    entries = FirewallManager._build_exec_start()

    gateway_ipv4 = str(DOCKER_IPV4_NETWORK_MASK[1])
    gateway_ipv6 = str(DOCKER_IPV6_NETWORK_MASK[1])

    # 4 entries: 2 per IP version (DROP + ACCEPT)
    assert len(entries) == 4

    # IPv4 DROP rule
    binary, argv, ignore = entries[0]
    assert binary == SHELL_CMD
    assert (
        f"{IPTABLES_CMD} -t raw -C PREROUTING ! -i hassio -d {gateway_ipv4} -j DROP"
        in argv[2]
    )
    assert (
        f"{IPTABLES_CMD} -t raw -I PREROUTING ! -i hassio -d {gateway_ipv4} -j DROP"
        in argv[2]
    )
    assert ignore is False

    # IPv4 ACCEPT rule
    binary, argv, ignore = entries[1]
    assert binary == SHELL_CMD
    assert (
        f"{IPTABLES_CMD} -t raw -C PREROUTING -i lo -d {gateway_ipv4} -j ACCEPT"
        in argv[2]
    )
    assert (
        f"{IPTABLES_CMD} -t raw -I PREROUTING -i lo -d {gateway_ipv4} -j ACCEPT"
        in argv[2]
    )
    assert ignore is False

    # IPv6 DROP rule
    binary, argv, ignore = entries[2]
    assert binary == SHELL_CMD
    assert (
        f"{IP6TABLES_CMD} -t raw -C PREROUTING ! -i hassio -d {gateway_ipv6} -j DROP"
        in argv[2]
    )
    assert (
        f"{IP6TABLES_CMD} -t raw -I PREROUTING ! -i hassio -d {gateway_ipv6} -j DROP"
        in argv[2]
    )
    assert ignore is False

    # IPv6 ACCEPT rule
    binary, argv, ignore = entries[3]
    assert binary == SHELL_CMD
    assert (
        f"{IP6TABLES_CMD} -t raw -C PREROUTING -i lo -d {gateway_ipv6} -j ACCEPT"
        in argv[2]
    )
    assert (
        f"{IP6TABLES_CMD} -t raw -I PREROUTING -i lo -d {gateway_ipv6} -j ACCEPT"
        in argv[2]
    )
    assert ignore is False


async def test_apply_gateway_protection_systemd_not_connected(
    coresys: CoreSys, systemd_service: SystemdService
):
    """Test graceful handling when systemd is not available."""
    systemd_service.StartTransientUnit.calls.clear()

    with patch.object(
        type(coresys.dbus.systemd),
        "is_connected",
        new_callable=lambda: property(lambda self: False),
    ):
        await coresys.host.firewall.apply_gateway_protection()

    assert len(systemd_service.StartTransientUnit.calls) == 0


async def test_apply_gateway_protection_resets_failed_unit(
    coresys: CoreSys, systemd_service: SystemdService
):
    """Test that previous failed unit is reset before applying."""
    systemd_service.ResetFailedUnit.calls.clear()

    await coresys.host.firewall.apply_gateway_protection()

    assert len(systemd_service.ResetFailedUnit.calls) == 1
    assert systemd_service.ResetFailedUnit.calls[0] == (FIREWALL_SERVICE,)


async def test_apply_gateway_protection_properties(
    coresys: CoreSys, systemd_service: SystemdService
):
    """Test transient unit has correct properties."""
    systemd_service.StartTransientUnit.calls.clear()

    await coresys.host.firewall.apply_gateway_protection()

    call = systemd_service.StartTransientUnit.calls[0]
    properties = {prop[0]: prop[1] for prop in call[2]}

    assert properties["Description"].value == "Supervisor gateway firewall protection"
    assert properties["Type"].value == "oneshot"
    assert properties["ExecStart"].signature == "a(sasb)"
    assert len(properties["ExecStart"].value) == 4
