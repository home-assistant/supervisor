"""Internal network manager for Supervisor."""

from contextlib import suppress
from ipaddress import IPv4Address
import logging
from typing import Any

import docker
import requests

from ..const import (
    DOCKER_IPV4_NETWORK_MASK,
    DOCKER_IPV4_NETWORK_RANGE,
    DOCKER_IPV6_NETWORK_MASK,
    DOCKER_NETWORK,
    DOCKER_NETWORK_DRIVER,
)
from ..exceptions import DockerError

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOCKER_NETWORK_PARAMS = {
    "name": DOCKER_NETWORK,
    "driver": DOCKER_NETWORK_DRIVER,
    "ipam": docker.types.IPAMConfig(
        pool_configs=[
            docker.types.IPAMPool(subnet=str(DOCKER_IPV6_NETWORK_MASK)),
            docker.types.IPAMPool(
                subnet=str(DOCKER_IPV4_NETWORK_MASK),
                gateway=str(DOCKER_IPV4_NETWORK_MASK[1]),
                iprange=str(DOCKER_IPV4_NETWORK_RANGE),
            ),
        ]
    ),
    "enable_ipv6": True,
    "options": {"com.docker.network.bridge.name": DOCKER_NETWORK},
}


class DockerNetwork:
    """Internal Supervisor Network.

    This class is not AsyncIO safe!
    """

    def __init__(self, docker_client: docker.DockerClient):
        """Initialize internal Supervisor network."""
        self.docker: docker.DockerClient = docker_client
        self._network: docker.models.networks.Network = self._get_network()

    @property
    def name(self) -> str:
        """Return name of network."""
        return DOCKER_NETWORK

    @property
    def network(self) -> docker.models.networks.Network:
        """Return docker network."""
        return self._network

    @property
    def containers(self) -> list[str]:
        """Return of connected containers from network."""
        return list(self.network.attrs.get("Containers", {}).keys())

    @property
    def gateway(self) -> IPv4Address:
        """Return gateway of the network."""
        return DOCKER_IPV4_NETWORK_MASK[1]

    @property
    def supervisor(self) -> IPv4Address:
        """Return supervisor of the network."""
        return DOCKER_IPV4_NETWORK_MASK[2]

    @property
    def dns(self) -> IPv4Address:
        """Return dns of the network."""
        return DOCKER_IPV4_NETWORK_MASK[3]

    @property
    def audio(self) -> IPv4Address:
        """Return audio of the network."""
        return DOCKER_IPV4_NETWORK_MASK[4]

    @property
    def cli(self) -> IPv4Address:
        """Return cli of the network."""
        return DOCKER_IPV4_NETWORK_MASK[5]

    @property
    def observer(self) -> IPv4Address:
        """Return observer of the network."""
        return DOCKER_IPV4_NETWORK_MASK[6]

    def _get(self, network_id: str) -> docker.models.networks.Network:
        """Get a network by ID."""
        return self.docker.networks.get(network_id)

    def _create(self, **kwargs: Any) -> docker.models.networks.Network:
        """Create a new network."""
        return self.docker.networks.create(**kwargs)

    def _get_network(self) -> docker.models.networks.Network:
        """Get supervisor network."""
        try:
            if (network := self._get(DOCKER_NETWORK)).attrs.get("EnableIPv6", False):
                return network
            network.remove()
            _LOGGER.info("Migrating Supervisor network to IPv4/IPv6 Dual Stack")
        except docker.errors.NotFound:
            _LOGGER.info("Can't find Supervisor network, creating a new network")

        return self._create(**DOCKER_NETWORK_PARAMS)

    def attach_container(
        self,
        container: docker.models.containers.Container,
        alias: list[str] | None = None,
        ipv4: IPv4Address | None = None,
    ) -> None:
        """Attach container to Supervisor network.

        Need run inside executor.
        """
        ipv4_address = str(ipv4) if ipv4 else None

        # Reload Network information
        with suppress(docker.errors.DockerException, requests.RequestException):
            self.network.reload()

        # Check stale Network
        if container.name and container.name in (
            val.get("Name") for val in self.network.attrs.get("Containers", {}).values()
        ):
            self.stale_cleanup(container.name)

        # Attach Network
        try:
            self.network.connect(container, aliases=alias, ipv4_address=ipv4_address)
        except docker.errors.APIError as err:
            raise DockerError(
                f"Can't link container to hassio-net: {err}", _LOGGER.error
            ) from err

    def detach_default_bridge(
        self, container: docker.models.containers.Container
    ) -> None:
        """Detach default Docker bridge.

        Need run inside executor.
        """
        try:
            default_network = self.docker.networks.get(DOCKER_NETWORK_DRIVER)
            default_network.disconnect(container)

        except docker.errors.NotFound:
            return

        except docker.errors.APIError as err:
            raise DockerError(
                f"Can't disconnect container from default: {err}", _LOGGER.warning
            ) from err

    def stale_cleanup(self, container_name: str):
        """Remove force a container from Network.

        Fix: https://github.com/moby/moby/issues/23302
        """
        try:
            self.network.disconnect(container_name, force=True)
        except docker.errors.NotFound:
            pass
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err
