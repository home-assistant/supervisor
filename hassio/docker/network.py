"""Internal network manager for Hass.io."""
from ipaddress import IPv4Address
import logging
from typing import List, Optional

import docker

from ..const import DOCKER_NETWORK, DOCKER_NETWORK_MASK, DOCKER_NETWORK_RANGE
from ..exceptions import DockerAPIError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DockerNetwork:
    """Internal Hass.io Network.

    This class is not AsyncIO safe!
    """

    def __init__(self, docker_client: docker.DockerClient):
        """Initialize internal Hass.io network."""
        self.docker: docker.DockerClient = docker_client
        self.network: docker.models.networks.Network = self._get_network()

    @property
    def name(self) -> str:
        """Return name of network."""
        return DOCKER_NETWORK

    @property
    def containers(self) -> List[docker.models.containers.Container]:
        """Return of connected containers from network."""
        return self.network.containers

    @property
    def gateway(self) -> IPv4Address:
        """Return gateway of the network."""
        return DOCKER_NETWORK_MASK[1]

    @property
    def supervisor(self) -> IPv4Address:
        """Return supervisor of the network."""
        return DOCKER_NETWORK_MASK[2]

    @property
    def dns(self) -> IPv4Address:
        """Return dns of the network."""
        return DOCKER_NETWORK_MASK[3]

    def _get_network(self) -> docker.models.networks.Network:
        """Get HassIO network."""
        try:
            return self.docker.networks.get(DOCKER_NETWORK)
        except docker.errors.NotFound:
            _LOGGER.info("Can't find Hass.io network, create new network")

        ipam_pool = docker.types.IPAMPool(
            subnet=str(DOCKER_NETWORK_MASK),
            gateway=str(self.gateway),
            iprange=str(DOCKER_NETWORK_RANGE),
        )

        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        return self.docker.networks.create(
            DOCKER_NETWORK,
            driver="bridge",
            ipam=ipam_config,
            enable_ipv6=False,
            options={"com.docker.network.bridge.name": DOCKER_NETWORK},
        )

    def attach_container(
        self,
        container: docker.models.containers.Container,
        alias: Optional[List[str]] = None,
        ipv4: Optional[IPv4Address] = None,
    ) -> None:
        """Attach container to Hass.io network.

        Need run inside executor.
        """
        ipv4 = str(ipv4) if ipv4 else None

        try:
            self.network.connect(container, aliases=alias, ipv4_address=ipv4)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't link container to hassio-net: %s", err)
            raise DockerAPIError() from None

        self.network.reload()

    def detach_default_bridge(
        self, container: docker.models.containers.Container
    ) -> None:
        """Detach default Docker bridge.

        Need run inside executor.
        """
        try:
            default_network = self.docker.networks.get("bridge")
            default_network.disconnect(container)

        except docker.errors.NotFound:
            return

        except docker.errors.APIError as err:
            _LOGGER.warning("Can't disconnect container from default: %s", err)
            raise DockerAPIError() from None
