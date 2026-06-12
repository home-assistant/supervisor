"""Test app network isolation setting."""

from ipaddress import IPv4Address

import pytest
import voluptuous as vol

from supervisor.apps import validate as vd
from supervisor.apps.app import App
from supervisor.apps.utils import rating_security
from supervisor.const import (
    ATTR_DRIVER,
    ATTR_HOST_NETWORK,
    ATTR_INTERFACE,
    ATTR_IPV4,
    ATTR_NETWORK_ISOLATION,
)
from supervisor.coresys import CoreSys
from supervisor.docker.const import ExternalNetworkDriver, NetworkIsolationConfig

from ..const import TEST_INTERFACE_ETH_NAME

TEST_CONFIG = NetworkIsolationConfig(
    driver=ExternalNetworkDriver.MACVLAN,
    interface=TEST_INTERFACE_ETH_NAME,
    ipv4=IPv4Address("192.168.2.50"),
)


def test_schema_defaults_to_macvlan():
    """Test network isolation schema applies macvlan driver default."""
    data = vd.SCHEMA_NETWORK_ISOLATION(
        {ATTR_INTERFACE: TEST_INTERFACE_ETH_NAME, ATTR_IPV4: "192.168.2.50"}
    )

    assert data[ATTR_DRIVER] == ExternalNetworkDriver.MACVLAN
    assert data[ATTR_IPV4] == "192.168.2.50"


@pytest.mark.parametrize(
    "config",
    [
        {ATTR_INTERFACE: TEST_INTERFACE_ETH_NAME, ATTR_IPV4: "not-an-ip"},
        {ATTR_INTERFACE: TEST_INTERFACE_ETH_NAME, ATTR_IPV4: "fd00::1"},
        {ATTR_INTERFACE: TEST_INTERFACE_ETH_NAME},
        {ATTR_IPV4: "192.168.2.50"},
        {
            ATTR_INTERFACE: TEST_INTERFACE_ETH_NAME,
            ATTR_IPV4: "192.168.2.50",
            ATTR_DRIVER: "bridge",
        },
    ],
)
def test_schema_invalid(config: dict[str, str]):
    """Test invalid network isolation configurations are rejected."""
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_NETWORK_ISOLATION(config)


async def test_network_isolation_persistence(coresys: CoreSys, install_app_ssh: App):
    """Test network isolation setting round-trips through persisted data."""
    assert install_app_ssh.network_isolation is None

    install_app_ssh.network_isolation = TEST_CONFIG
    assert install_app_ssh.persist[ATTR_NETWORK_ISOLATION] == {
        ATTR_DRIVER: "macvlan",
        ATTR_INTERFACE: TEST_INTERFACE_ETH_NAME,
        ATTR_IPV4: "192.168.2.50",
    }
    assert install_app_ssh.network_isolation == TEST_CONFIG

    install_app_ssh.network_isolation = None
    assert install_app_ssh.network_isolation is None
    assert ATTR_NETWORK_ISOLATION not in install_app_ssh.persist


async def test_rating_security_with_isolation(coresys: CoreSys, install_app_ssh: App):
    """Test host network rating penalty is not applied with isolation."""
    install_app_ssh.data[ATTR_HOST_NETWORK] = True
    host_network_rating = rating_security(install_app_ssh)

    install_app_ssh.network_isolation = TEST_CONFIG
    assert rating_security(install_app_ssh) == host_network_rating + 1
