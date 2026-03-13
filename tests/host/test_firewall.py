"""Test host firewall manager."""

import asyncio
from unittest.mock import patch

from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import StartUnitMode
from supervisor.host.firewall import (
    BIN_SH,
    FIREWALL_SERVICE,
    IP6TABLES_CMD,
    IPTABLES_CMD,
    FirewallManager,
)
from supervisor.resolution.const import UnsupportedReason

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService

GATEWAY_IPV4 = "172.30.32.1"
GATEWAY_IPV6 = "fd0c:ac1e:2100::1"


@pytest.fixture(name="systemd_service")
async def fixture_systemd_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> SystemdService:
    """Return systemd service mock."""
    yield all_dbus_services["systemd"]


@pytest.fixture(name="systemd_unit_service")
async def fixture_systemd_unit_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> SystemdUnitService:
    """Return systemd unit service mock."""
    yield all_dbus_services["systemd_unit"]


async def test_apply_gateway_firewall_rules(
    coresys: CoreSys,
    systemd_service: SystemdService,
    systemd_unit_service: SystemdUnitService,
):
    """Test gateway firewall rules are applied."""
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()
    systemd_unit_service.active_state = "inactive"

    await coresys.host.firewall.apply_gateway_firewall_rules()

    assert (
        UnsupportedReason.DOCKER_GATEWAY_UNPROTECTED
        not in coresys.resolution.unsupported
    )
    assert len(systemd_service.StartTransientUnit.calls) == 1
    call = systemd_service.StartTransientUnit.calls[0]
    assert call[0] == FIREWALL_SERVICE
    assert call[1] == StartUnitMode.REPLACE


async def test_apply_gateway_firewall_rules_exec_start_rules(coresys: CoreSys):
    """Test correct iptables rules are generated."""
    entries = FirewallManager._build_exec_start()

    # 4 entries: 2 per IP version (DROP + ACCEPT)
    assert len(entries) == 4

    # IPv4 DROP rule
    assert entries[0].binary == BIN_SH
    assert entries[0].argv == [
        BIN_SH,
        "-c",
        f"{IPTABLES_CMD} -t raw -C PREROUTING ! -i hassio -d {GATEWAY_IPV4}"
        f" -j DROP 2>/dev/null"
        f" || {IPTABLES_CMD} -t raw -I PREROUTING ! -i hassio -d {GATEWAY_IPV4}"
        f" -j DROP",
    ]
    assert entries[0].ignore_failure is False

    # IPv4 ACCEPT rule
    assert entries[1].binary == BIN_SH
    assert entries[1].argv == [
        BIN_SH,
        "-c",
        f"{IPTABLES_CMD} -t raw -C PREROUTING -i lo -d {GATEWAY_IPV4}"
        f" -j ACCEPT 2>/dev/null"
        f" || {IPTABLES_CMD} -t raw -I PREROUTING -i lo -d {GATEWAY_IPV4}"
        f" -j ACCEPT",
    ]
    assert entries[1].ignore_failure is False

    # IPv6 DROP rule
    assert entries[2].binary == BIN_SH
    assert entries[2].argv == [
        BIN_SH,
        "-c",
        f"{IP6TABLES_CMD} -t raw -C PREROUTING ! -i hassio -d {GATEWAY_IPV6}"
        f" -j DROP 2>/dev/null"
        f" || {IP6TABLES_CMD} -t raw -I PREROUTING ! -i hassio -d {GATEWAY_IPV6}"
        f" -j DROP",
    ]
    assert entries[2].ignore_failure is False

    # IPv6 ACCEPT rule
    assert entries[3].binary == BIN_SH
    assert entries[3].argv == [
        BIN_SH,
        "-c",
        f"{IP6TABLES_CMD} -t raw -C PREROUTING -i lo -d {GATEWAY_IPV6}"
        f" -j ACCEPT 2>/dev/null"
        f" || {IP6TABLES_CMD} -t raw -I PREROUTING -i lo -d {GATEWAY_IPV6}"
        f" -j ACCEPT",
    ]
    assert entries[3].ignore_failure is False


async def test_apply_gateway_firewall_rules_systemd_not_connected(
    coresys: CoreSys, systemd_service: SystemdService
):
    """Test unsupported reason added when systemd is not available."""
    systemd_service.StartTransientUnit.calls.clear()

    with patch.object(
        type(coresys.dbus.systemd),
        "is_connected",
        new_callable=lambda: property(lambda self: False),
    ):
        await coresys.host.firewall.apply_gateway_firewall_rules()

    assert (
        UnsupportedReason.DOCKER_GATEWAY_UNPROTECTED in coresys.resolution.unsupported
    )
    assert len(systemd_service.StartTransientUnit.calls) == 0


async def test_apply_gateway_firewall_rules_dbus_error(
    coresys: CoreSys, systemd_service: SystemdService
):
    """Test unsupported reason added when transient unit fails."""
    systemd_service.response_start_transient_unit = DBusError(
        ErrorType.SERVICE_ERROR, "test error"
    )

    await coresys.host.firewall.apply_gateway_firewall_rules()

    assert (
        UnsupportedReason.DOCKER_GATEWAY_UNPROTECTED in coresys.resolution.unsupported
    )


async def test_apply_gateway_firewall_rules_resets_failed_unit(
    coresys: CoreSys,
    systemd_service: SystemdService,
    systemd_unit_service: SystemdUnitService,
):
    """Test that previous failed unit is reset before applying."""
    systemd_service.ResetFailedUnit.calls.clear()
    systemd_unit_service.active_state = "inactive"

    await coresys.host.firewall.apply_gateway_firewall_rules()

    assert len(systemd_service.ResetFailedUnit.calls) == 1
    assert systemd_service.ResetFailedUnit.calls[0] == (FIREWALL_SERVICE,)


async def test_apply_gateway_firewall_rules_properties(
    coresys: CoreSys,
    systemd_service: SystemdService,
    systemd_unit_service: SystemdUnitService,
):
    """Test transient unit has correct properties."""
    systemd_service.StartTransientUnit.calls.clear()
    systemd_unit_service.active_state = "inactive"

    await coresys.host.firewall.apply_gateway_firewall_rules()

    call = systemd_service.StartTransientUnit.calls[0]
    properties = {prop[0]: prop[1] for prop in call[2]}

    assert properties["Description"].value == "Supervisor gateway firewall rules"
    assert properties["Type"].value == "oneshot"
    assert properties["ExecStart"].signature == "a(sasb)"
    assert len(properties["ExecStart"].value) == 4


async def test_apply_gateway_firewall_rules_unit_failed(
    coresys: CoreSys,
    systemd_service: SystemdService,
    systemd_unit_service: SystemdUnitService,
):
    """Test unsupported reason added when firewall unit fails."""
    systemd_unit_service.active_state = "failed"

    await coresys.host.firewall.apply_gateway_firewall_rules()

    assert (
        UnsupportedReason.DOCKER_GATEWAY_UNPROTECTED in coresys.resolution.unsupported
    )


async def test_apply_gateway_firewall_rules_unit_failed_via_signal(
    coresys: CoreSys,
    systemd_service: SystemdService,
    systemd_unit_service: SystemdUnitService,
):
    """Test failure detected via property change signal when unit is still activating."""
    systemd_unit_service.active_state = "activating"

    task = asyncio.create_task(coresys.host.firewall.apply_gateway_firewall_rules())
    await asyncio.sleep(0.1)
    systemd_unit_service.emit_properties_changed({"ActiveState": "failed"})
    await task

    assert (
        UnsupportedReason.DOCKER_GATEWAY_UNPROTECTED in coresys.resolution.unsupported
    )
