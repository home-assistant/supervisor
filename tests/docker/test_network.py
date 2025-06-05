"""Test Internal network manager for Supervisor."""

from unittest.mock import MagicMock, PropertyMock, patch

import docker
import pytest

from supervisor.const import (
    ATTR_ENABLE_IPV6,
    DOCKER_NETWORK,
    OBSERVER_DOCKER_NAME,
    SUPERVISOR_DOCKER_NAME,
)
from supervisor.docker.network import (
    DOCKER_ENABLEIPV6,
    DOCKER_NETWORK_PARAMS,
    DockerNetwork,
)


class MockContainer:
    """Mock implementation of a Docker container."""

    def __init__(self, name: str) -> None:
        """Initialize a mock container."""
        self.name = name


class MockNetwork:
    """Mock implementation of internal network."""

    def __init__(
        self, raise_error: bool, containers: list[str], enableIPv6: bool
    ) -> None:
        """Initialize a mock network."""
        self.raise_error = raise_error
        self.containers = [MockContainer(container) for container in containers or []]
        self.attrs = {DOCKER_ENABLEIPV6: enableIPv6}

    def remove(self) -> None:
        """Simulate a network removal."""
        if self.raise_error:
            raise docker.errors.APIError("Simulated removal error")

    def reload(self, *args, **kwargs) -> None:
        """Simulate a network reload."""

    def connect(self, *args, **kwargs) -> None:
        """Simulate a network connection."""

    def disconnect(self, *args, **kwargs) -> None:
        """Simulate a network disconnection."""


@pytest.mark.parametrize(
    ("raise_error", "containers", f"old_{ATTR_ENABLE_IPV6}", f"new_{ATTR_ENABLE_IPV6}"),
    [
        (False, [OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME], False, True),
        (False, [OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME], True, False),
        (False, ["test_container"], False, True),
        (False, None, False, True),
        (True, None, False, True),
        (False, None, True, True),
    ],
)
async def test_network_recreation(
    raise_error: bool,
    containers: list[str] | None,
    old_enable_ipv6: bool,
    new_enable_ipv6: bool,
):
    """Test network recreation with IPv6 enabled/disabled."""

    with (
        patch(
            "supervisor.docker.network.DockerNetwork.docker",
            new_callable=PropertyMock,
            return_value=MagicMock(),
            create=True,
        ),
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks",
            new_callable=PropertyMock,
            return_value=MagicMock(),
            create=True,
        ),
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks.get",
            return_value=MockNetwork(raise_error, containers, old_enable_ipv6),
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks.create",
            return_value=MockNetwork(raise_error, containers, new_enable_ipv6),
        ) as mock_create,
    ):
        network = (await DockerNetwork(MagicMock()).post_init(new_enable_ipv6)).network

        mock_get.assert_called_with(DOCKER_NETWORK)

        assert network is not None
        assert network.attrs.get(DOCKER_ENABLEIPV6) is (
            new_enable_ipv6
            if not raise_error and (not containers or len(containers) > 1)
            else old_enable_ipv6
        )

        if (
            not raise_error and (not containers or len(containers) > 1)
        ) and old_enable_ipv6 != new_enable_ipv6:
            network_params = DOCKER_NETWORK_PARAMS.copy()
            network_params[ATTR_ENABLE_IPV6] = new_enable_ipv6

            mock_create.assert_called_with(**network_params)
