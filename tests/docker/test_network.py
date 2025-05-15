"""Test Internal network manager for Supervisor."""

from unittest.mock import MagicMock, patch

from supervisor.const import DOCKER_NETWORK
from supervisor.docker.network import DOCKER_NETWORK_PARAMS, DockerNetwork


class MockNetwork:
    """Mock implementation of internal network."""

    def __init__(self, enableIPv6: bool) -> None:
        """Initialize a mock network."""
        self.attrs = {"EnableIPv6": enableIPv6}

    def remove(self) -> None:
        """Simulate a network removal."""


async def test_network_recreate_as_ipv6():
    """Test network recreation with IPv6 enabled when the existing network lacks IPv6 support."""

    with (
        patch(
            "supervisor.docker.network.DockerNetwork._get",
            return_value=MockNetwork(False),
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork._create",
            return_value=MockNetwork(True),
        ) as mock_create,
    ):
        network = DockerNetwork(MagicMock()).network

        assert network is not None
        assert network.attrs.get("EnableIPv6", False) is True

        mock_get.assert_called_with(DOCKER_NETWORK)

        mock_create.assert_called_with(**DOCKER_NETWORK_PARAMS)
