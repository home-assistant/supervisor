"""Test external network manager."""

from http import HTTPStatus
from ipaddress import IPv4Address
from unittest.mock import MagicMock

import aiodocker
from aiodocker.networks import DockerNetwork as AiodockerNetwork
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.const import (
    ExternalNetworkDriver,
    ExtraNetworkEndpoint,
    NetworkIsolationConfig,
)
from supervisor.docker.external_network import DockerExternalNetworks
from supervisor.exceptions import DockerError, HostNetworkNotFound

from ..const import TEST_INTERFACE_ETH_NAME

TEST_CONFIG = NetworkIsolationConfig(
    driver=ExternalNetworkDriver.MACVLAN,
    interface=TEST_INTERFACE_ETH_NAME,
    ipv4=IPv4Address("192.168.2.50"),
)

TEST_NETWORK_NAME = f"hassio-macvlan-{TEST_INTERFACE_ETH_NAME}"

# Derived from the eth0 mock of the NetworkManager D-Bus service
EXPECTED_NETWORK_PARAMS = {
    "Name": TEST_NETWORK_NAME,
    "Driver": "macvlan",
    "IPAM": {
        "Driver": "default",
        "Config": [
            {
                "Subnet": "192.168.2.0/24",
                "Gateway": "192.168.2.1",
                "AuxiliaryAddresses": {"host": "192.168.2.148"},
            }
        ],
    },
    "EnableIPv6": True,
    "Options": {"parent": TEST_INTERFACE_ETH_NAME},
    "Labels": {"supervisor_managed": ""},
}

EXPECTED_ENDPOINT_SYSCTLS = {
    "com.docker.network.endpoint.sysctls": (
        "net.ipv6.conf.IFNAME.accept_ra=2,"
        "net.ipv6.conf.IFNAME.accept_ra_rt_info_max_plen=64"
    )
}


async def test_ensure_creates_network(coresys: CoreSys):
    """Test network is created from host interface configuration."""
    coresys.docker.docker.networks.reset_mock()
    coresys.docker.docker.networks.get.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "not found"}
    )

    name = await coresys.docker.external_networks.ensure(TEST_CONFIG)

    assert name == TEST_NETWORK_NAME
    coresys.docker.docker.networks.create.assert_called_once_with(
        EXPECTED_NETWORK_PARAMS
    )


async def test_ensure_keeps_matching_network(coresys: CoreSys):
    """Test existing matching network is kept."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    # The engine lists its auto-allocated IPv6 ULA in the IPAM config
    network.show.return_value = EXPECTED_NETWORK_PARAMS | {
        "IPAM": {
            "Driver": "default",
            "Config": [
                {"Subnet": "fd61:6c69:6e74:6f6e::/64"},
                *EXPECTED_NETWORK_PARAMS["IPAM"]["Config"],
            ],
        },
        "Containers": {},
    }
    coresys.docker.docker.networks.get.return_value = network

    assert await coresys.docker.external_networks.ensure(TEST_CONFIG) == (
        TEST_NETWORK_NAME
    )

    coresys.docker.docker.networks.create.assert_not_called()
    network.delete.assert_not_called()


async def test_ensure_recreates_drifted_network(coresys: CoreSys):
    """Test network with outdated host interface configuration is recreated."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    network.show.return_value = EXPECTED_NETWORK_PARAMS | {
        "IPAM": {
            "Driver": "default",
            "Config": [{"Subnet": "10.1.0.0/24", "Gateway": "10.1.0.1"}],
        },
        "Containers": {},
    }
    coresys.docker.docker.networks.get.return_value = network

    assert await coresys.docker.external_networks.ensure(TEST_CONFIG) == (
        TEST_NETWORK_NAME
    )

    network.delete.assert_called_once()
    coresys.docker.docker.networks.create.assert_called_once_with(
        EXPECTED_NETWORK_PARAMS
    )


async def test_ensure_drifted_network_in_use(coresys: CoreSys):
    """Test drifted network with attached containers raises."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    network.show.return_value = EXPECTED_NETWORK_PARAMS | {
        "IPAM": {
            "Driver": "default",
            "Config": [{"Subnet": "10.1.0.0/24", "Gateway": "10.1.0.1"}],
        },
        "Containers": {"abc123": {"Name": "addon_other"}},
    }
    coresys.docker.docker.networks.get.return_value = network

    with pytest.raises(DockerError):
        await coresys.docker.external_networks.ensure(TEST_CONFIG)

    network.delete.assert_not_called()
    coresys.docker.docker.networks.create.assert_not_called()


async def test_ensure_recreates_ipv4_only_network(coresys: CoreSys):
    """Test network without IPv6 (pre-SLAAC support) is recreated."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    network.show.return_value = EXPECTED_NETWORK_PARAMS | {
        "EnableIPv6": False,
        "Containers": {},
    }
    coresys.docker.docker.networks.get.return_value = network

    assert await coresys.docker.external_networks.ensure(TEST_CONFIG) == (
        TEST_NETWORK_NAME
    )

    network.delete.assert_called_once()
    coresys.docker.docker.networks.create.assert_called_once_with(
        EXPECTED_NETWORK_PARAMS
    )


async def test_ensure_interface_missing(coresys: CoreSys):
    """Test missing host interface raises."""
    with pytest.raises(HostNetworkNotFound):
        await coresys.docker.external_networks.ensure(
            NetworkIsolationConfig(
                driver=ExternalNetworkDriver.MACVLAN,
                interface="eth42",
                ipv4=IPv4Address("192.168.2.50"),
            )
        )


async def test_connect_container(coresys: CoreSys):
    """Test connecting a container to an external network endpoint."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    network.show.return_value = EXPECTED_NETWORK_PARAMS | {"Containers": {}}
    coresys.docker.docker.networks.get.return_value = network

    await coresys.docker.external_networks.connect_container(
        "abc123",
        "addon_test",
        ExtraNetworkEndpoint(
            network=TEST_NETWORK_NAME,
            ipv4=IPv4Address("192.168.2.50"),
            mac="02:42:c0:a8:02:32",
            gw_priority=100,
        ),
    )

    network.connect.assert_called_once_with(
        {
            "Container": "abc123",
            "EndpointConfig": {
                "IPAMConfig": {"IPv4Address": "192.168.2.50"},
                "GwPriority": 100,
                "DriverOpts": EXPECTED_ENDPOINT_SYSCTLS,
                "MacAddress": "02:42:c0:a8:02:32",
            },
        }
    )


def test_mac_from_ip():
    """Test stable MAC address derivation from IPv4."""
    assert (
        DockerExternalNetworks.mac_from_ip(IPv4Address("192.168.2.50"))
        == "02:42:c0:a8:02:32"
    )
    assert (
        DockerExternalNetworks.mac_from_ip(IPv4Address("10.0.0.1"))
        == "02:42:0a:00:00:01"
    )


async def test_connect_container_stale_endpoint_cleanup(coresys: CoreSys):
    """Test stale endpoint of previous container with same name is removed."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    network.show.return_value = EXPECTED_NETWORK_PARAMS | {
        "Containers": {"old123": {"Name": "addon_test"}}
    }
    coresys.docker.docker.networks.get.return_value = network

    await coresys.docker.external_networks.connect_container(
        "abc123",
        "addon_test",
        ExtraNetworkEndpoint(
            network=TEST_NETWORK_NAME, ipv4=IPv4Address("192.168.2.50")
        ),
    )

    network.disconnect.assert_called_once_with(
        {"Container": "addon_test", "Force": True}
    )
    network.connect.assert_called_once()


async def test_gc_removes_unreferenced_network(coresys: CoreSys):
    """Test garbage collection removes networks without app references."""
    coresys.docker.docker.networks.reset_mock()
    network = MagicMock(spec=AiodockerNetwork)
    coresys.docker.docker.networks.list.return_value = [
        {"Name": TEST_NETWORK_NAME},
        {"Name": "some-user-network"},
    ]
    coresys.docker.docker.networks.get.return_value = network

    await coresys.docker.external_networks.gc()

    coresys.docker.docker.networks.get.assert_called_once_with(TEST_NETWORK_NAME)
    network.delete.assert_called_once()
