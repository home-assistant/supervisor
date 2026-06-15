"""Test check for app network isolation endpoints."""

# pylint: disable=import-error,protected-access
from ipaddress import IPv4Address

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.const import ExternalNetworkDriver, NetworkIsolationConfig
from supervisor.resolution.checks.app_network_isolation import CheckAppNetworkIsolation
from supervisor.resolution.const import ContextType, IssueType

from tests.const import TEST_INTERFACE_ETH_NAME


class FakeApp:
    """Fake App for tests."""

    slug = "my_test"
    is_installed = True
    network_isolation: NetworkIsolationConfig | None = None


def _config(interface: str, address: str) -> NetworkIsolationConfig:
    """Create an isolation config."""
    return NetworkIsolationConfig(
        driver=ExternalNetworkDriver.MACVLAN,
        interface=interface,
        ipv4=IPv4Address(address),
    )


async def test_base(coresys: CoreSys):
    """Test check basics."""
    check = CheckAppNetworkIsolation(coresys)
    assert check.slug == "app_network_isolation"
    assert check.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    check = CheckAppNetworkIsolation(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app

    # No isolation assigned
    await check.run_check()
    assert len(coresys.resolution.issues) == 0

    # Valid endpoint on existing interface
    app.network_isolation = _config(TEST_INTERFACE_ETH_NAME, "192.168.2.50")
    await check.run_check()
    assert len(coresys.resolution.issues) == 0

    # Interface is gone
    app.network_isolation = _config("eth42", "192.168.2.50")
    await check.run_check()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type == IssueType.NETWORK_ISOLATION_FAILED
    assert coresys.resolution.issues[0].context == ContextType.ADDON
    assert coresys.resolution.issues[0].reference == app.slug


async def test_approve(coresys: CoreSys):
    """Test check approval."""
    check = CheckAppNetworkIsolation(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app

    # Address no longer within the interface subnet
    app.network_isolation = _config(TEST_INTERFACE_ETH_NAME, "10.0.0.5")
    assert await check.approve_check(reference=app.slug)

    # Back to a valid configuration
    app.network_isolation = _config(TEST_INTERFACE_ETH_NAME, "192.168.2.50")
    assert not await check.approve_check(reference=app.slug)

    # Isolation removed
    app.network_isolation = None
    assert not await check.approve_check(reference=app.slug)

    # App uninstalled
    coresys.apps.local.pop(app.slug)
    assert not await check.approve_check(reference=app.slug)
