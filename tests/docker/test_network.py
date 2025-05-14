"""Test Internal network manager for Supervisor."""

from unittest.mock import MagicMock, patch

from docker.types import IPAMConfig, IPAMPool

from supervisor.const import (
    DOCKER_IPV4_NETWORK_MASK,
    DOCKER_IPV4_NETWORK_RANGE,
    DOCKER_IPV6_NETWORK_MASK,
    DOCKER_NETWORK,
    DOCKER_NETWORK_DRIVER,
)
from supervisor.docker.network import DockerNetwork


class MockNetwork(dict):
    """Mock implementation of Docker internal network."""

    def remove(self):
        """Simulate a network removal."""


async def test_network_recreate_as_ipv6():
    """Test network recreation with IPv6 enabled when the existing network lacks IPv6 support."""

    with (
        patch(
            "supervisor.docker.network.DockerNetwork.get",
            return_value=MockNetwork(EnableIPv6=False),
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork.create",
            return_value=True,
        ) as mock_create,
    ):
        assert DockerNetwork(MagicMock()).network is True

        mock_get.assert_called_with(DOCKER_NETWORK)

        mock_create.assert_called_with(
            name=DOCKER_NETWORK,
            driver=DOCKER_NETWORK_DRIVER,
            ipam=IPAMConfig(
                pool_configs=[
                    IPAMPool(subnet=str(DOCKER_IPV6_NETWORK_MASK)),
                    IPAMPool(
                        subnet=str(DOCKER_IPV4_NETWORK_MASK),
                        gateway=str(DOCKER_IPV4_NETWORK_MASK[1]),
                        iprange=str(DOCKER_IPV4_NETWORK_RANGE),
                    ),
                ]
            ),
            enable_ipv6=True,
            options={"com.docker.network.bridge.name": DOCKER_NETWORK},
        )
