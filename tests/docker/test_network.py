"""Test Internal network manager for Supervisor."""

from http import HTTPStatus
from unittest.mock import MagicMock

import aiodocker
from aiodocker.networks import DockerNetwork as AiodockerNetwork
import pytest

from supervisor.const import (
    DOCKER_NETWORK,
    OBSERVER_DOCKER_NAME,
    SUPERVISOR_DOCKER_NAME,
)
from supervisor.docker.manager import DockerAPI
from supervisor.docker.network import (
    DOCKER_ENABLEIPV6,
    DOCKER_NETWORK_PARAMS,
    DockerNetwork,
)


@pytest.mark.parametrize(
    (
        "delete_error",
        "disconnect_error",
        "containers",
        "old_enable_ipv6",
        "new_enable_ipv6",
        "create_expected",
    ),
    [
        (None, None, [OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME], False, True, True),
        (None, None, [OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME], True, False, True),
        (None, None, ["test_container"], False, True, False),
        (None, None, [], False, True, True),
        (
            None,
            aiodocker.DockerError(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"message": "Simulated disconnect error"},
            ),
            [OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME],
            False,
            True,
            False,
        ),
        (
            aiodocker.DockerError(
                HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "Simulated removal error"}
            ),
            None,
            [],
            False,
            True,
            False,
        ),
        (None, None, [], True, True, False),
    ],
)
async def test_network_recreation(
    docker: DockerAPI,
    delete_error: aiodocker.DockerError | None,
    disconnect_error: aiodocker.DockerError | None,
    containers: list[str],
    old_enable_ipv6: bool,
    new_enable_ipv6: bool,
    create_expected: bool,
):
    """Test network recreation with IPv6 enabled/disabled."""
    docker.docker.networks.get.return_value = mock_network = MagicMock(
        spec=AiodockerNetwork, id="test123"
    )
    mock_network.show.return_value = {
        "Containers": {name: {"Id": name, "Name": name} for name in containers},
        DOCKER_ENABLEIPV6: old_enable_ipv6,
    }
    mock_network.delete.side_effect = delete_error
    mock_network.disconnect.side_effect = disconnect_error
    docker.docker.networks.create.return_value = mock_new_network = MagicMock(
        spec=AiodockerNetwork, id="test123"
    )
    mock_new_network.show.return_value = {
        "Containers": {},
        DOCKER_ENABLEIPV6: new_enable_ipv6,
    }

    docker_network = await DockerNetwork(docker.docker).post_init(new_enable_ipv6)
    docker.docker.networks.get.assert_called_with(DOCKER_NETWORK)

    assert docker_network.network
    assert docker_network.network_meta

    if not create_expected:
        assert docker_network.network_meta[DOCKER_ENABLEIPV6] is old_enable_ipv6
        docker.docker.networks.create.assert_not_called()
    else:
        assert docker_network.network_meta[DOCKER_ENABLEIPV6] is new_enable_ipv6
        docker.docker.networks.create.assert_called_once_with(
            DOCKER_NETWORK_PARAMS | {DOCKER_ENABLEIPV6: new_enable_ipv6}
        )


async def test_network_default_ipv6_for_new_installations(docker: DockerAPI):
    """Test that IPv6 is enabled by default when no user setting is provided (None)."""
    docker.docker.networks.get.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "Network not found"}
    )
    docker.docker.networks.create.return_value = mock_network = MagicMock(
        spec=AiodockerNetwork, id="test123"
    )
    mock_network.show.return_value = {"Containers": {}, DOCKER_ENABLEIPV6: True}

    # Pass None as enable_ipv6 to simulate no user setting
    docker_network = await DockerNetwork(docker.docker).post_init(None)

    assert docker_network.network
    assert docker_network.network_meta
    assert docker_network.network_meta[DOCKER_ENABLEIPV6] is True

    # Verify that create was called with IPv6 enabled by default
    docker.docker.networks.create.assert_called_with(
        DOCKER_NETWORK_PARAMS | {DOCKER_ENABLEIPV6: True}
    )


async def test_network_mtu_recreation(docker: DockerAPI):
    """Test network recreation with different MTU settings."""
    docker.docker.networks.get.return_value = mock_network = MagicMock(
        spec=AiodockerNetwork, id="test123"
    )
    mock_network.show.return_value = {
        DOCKER_ENABLEIPV6: False,
        "Containers": {},
        "Options": {"com.docker.network.driver.mtu": "1500"},
    }
    docker.docker.networks.create.return_value = mock_new_network = MagicMock(
        spec=AiodockerNetwork, id="test123"
    )
    mock_new_network.show.return_value = {
        DOCKER_ENABLEIPV6: True,
        "Containers": {},
        "Options": {"com.docker.network.driver.mtu": "1450"},
    }

    # Set new MTU to 1450
    docker_network = await DockerNetwork(docker.docker).post_init(True, 1450)

    docker.docker.networks.get.assert_called_with(DOCKER_NETWORK)
    assert docker_network.network
    assert docker_network.network_meta
    assert docker_network.network_meta[DOCKER_ENABLEIPV6] is True
    assert (
        docker_network.network_meta["Options"]["com.docker.network.driver.mtu"]
        == "1450"
    )

    # Verify network was recreated with new MTU
    expected_options = DOCKER_NETWORK_PARAMS["Options"] | {
        "com.docker.network.driver.mtu": "1450"
    }
    docker.docker.networks.create.assert_called_with(
        DOCKER_NETWORK_PARAMS | {DOCKER_ENABLEIPV6: True, "Options": expected_options}
    )


async def test_network_mtu_no_change(docker: DockerAPI):
    """Test that network is not recreated when MTU hasn't changed."""
    docker.docker.networks.get.return_value = mock_network = MagicMock(
        spec=AiodockerNetwork, id="test123"
    )
    mock_network.show.return_value = {
        DOCKER_ENABLEIPV6: True,
        "Containers": {},
        "Options": {"com.docker.network.driver.mtu": "1450"},
    }

    # Set same MTU (1450)
    docker_network = await DockerNetwork(docker.docker).post_init(True, 1450)

    docker.docker.networks.get.assert_called_with(DOCKER_NETWORK)
    assert docker_network.network
    assert docker_network.network_meta
    assert docker_network.network_meta[DOCKER_ENABLEIPV6] is True
    assert (
        docker_network.network_meta["Options"]["com.docker.network.driver.mtu"]
        == "1450"
    )

    # Verify network was NOT recreated since MTU is the same
    docker.docker.networks.create.assert_not_called()
