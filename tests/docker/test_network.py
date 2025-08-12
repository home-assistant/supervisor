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
        self,
        raise_error: bool,
        containers: list[str],
        enableIPv6: bool,
        mtu: int | None = None,
    ) -> None:
        """Initialize a mock network."""
        self.raise_error = raise_error
        self.containers = [MockContainer(container) for container in containers or []]
        self.attrs = {
            DOCKER_ENABLEIPV6: enableIPv6,
            "Options": {"com.docker.network.driver.mtu": str(mtu)} if mtu else {},
        }

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
            return_value=MockNetwork(raise_error, containers, old_enable_ipv6, None),
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks.create",
            return_value=MockNetwork(raise_error, containers, new_enable_ipv6, None),
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


async def test_network_default_ipv6_for_new_installations():
    """Test that IPv6 is enabled by default when no user setting is provided (None)."""
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
            side_effect=docker.errors.NotFound("Network not found"),
        ),
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks.create",
            return_value=MockNetwork(False, None, True, None),
        ) as mock_create,
    ):
        # Pass None as enable_ipv6 to simulate no user setting
        network = (await DockerNetwork(MagicMock()).post_init(None)).network

        assert network is not None
        assert network.attrs.get(DOCKER_ENABLEIPV6) is True

        # Verify that create was called with IPv6 enabled by default
        expected_params = DOCKER_NETWORK_PARAMS.copy()
        expected_params[ATTR_ENABLE_IPV6] = True
        mock_create.assert_called_with(**expected_params)


async def test_network_mtu_recreation():
    """Test network recreation with different MTU settings."""
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
            return_value=MockNetwork(False, None, True, 1500),  # Old MTU 1500
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks.create",
            return_value=MockNetwork(False, None, True, 1450),  # New MTU 1450
        ) as mock_create,
    ):
        # Set new MTU to 1450
        network = (await DockerNetwork(MagicMock()).post_init(True, 1450)).network

        mock_get.assert_called_with(DOCKER_NETWORK)

        assert network is not None

        # Verify network was recreated with new MTU
        expected_params = DOCKER_NETWORK_PARAMS.copy()
        expected_params[ATTR_ENABLE_IPV6] = True
        expected_params["options"] = expected_params["options"].copy()
        expected_params["options"]["com.docker.network.driver.mtu"] = "1450"
        mock_create.assert_called_with(**expected_params)


async def test_network_mtu_no_change():
    """Test that network is not recreated when MTU hasn't changed."""
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
            return_value=MockNetwork(False, None, True, 1450),  # Existing MTU 1450
        ) as mock_get,
        patch(
            "supervisor.docker.network.DockerNetwork.docker.networks.create",
        ) as mock_create,
    ):
        # Set same MTU (1450)
        network = (await DockerNetwork(MagicMock()).post_init(True, 1450)).network

        mock_get.assert_called_with(DOCKER_NETWORK)

        # Verify network was NOT recreated since MTU is the same
        mock_create.assert_not_called()

        assert network is not None
