"""Internal network manager for Supervisor."""
from contextlib import suppress
from ipaddress import IPv4Address
import logging
from typing import Optional

import docker
import requests

from ..const import DOCKER_NETWORK, DOCKER_NETWORK_MASK, DOCKER_NETWORK_RANGE
from ..exceptions import DockerError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DockerNetwork:
    """Internal Supervisor Network.

    This class is not AsyncIO safe!
    """

    def __init__(self, docker_client: docker.DockerClient):
        """Initialize internal Supervisor network."""
        self.docker: docker.DockerClient = docker_client
        self.network: docker.models.networks.Network = self._get_network()

    @property
    def name(self) -> str:
        """Return name of network."""
        return DOCKER_NETWORK

    @property
    def containers(self) -> list[docker.models.containers.Container]:
        """Return of connected containers from network."""
        containers: list[docker.models.containers.Container] = []
        for cid, _ in self.network.attrs.get("Containers", {}).items():
            try:
                containers.append(self.docker.containers.get(cid))
            except docker.errors.NotFound:
                _LOGGER.warning("Docker network is corrupt! %s", cid)
            except (docker.errors.DockerException, requests.RequestException) as err:
                _LOGGER.error("Unknown error with container lookup %s", err)

        return containers

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

    @property
    def audio(self) -> IPv4Address:
        """Return audio of the network."""
        return DOCKER_NETWORK_MASK[4]

    @property
    def cli(self) -> IPv4Address:
        """Return cli of the network."""
        return DOCKER_NETWORK_MASK[5]

    @property
    def observer(self) -> IPv4Address:
        """Return observer of the network."""
        return DOCKER_NETWORK_MASK[6]

    def _get_network(self) -> docker.models.networks.Network:
        """Get supervisor network."""
        try:
            return self.docker.networks.get(DOCKER_NETWORK)
        except docker.errors.NotFound:
            _LOGGER.info("Can't find Supervisor network, creating a new network")

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
        alias: Optional[list[str]] = None,
        ipv4: Optional[IPv4Address] = None,
    ) -> None:
        """Attach container to Supervisor network.

        Need run inside executor.
        """
        ipv4_address = str(ipv4) if ipv4 else None

        # Reload Network information
        with suppress(docker.errors.DockerException, requests.RequestException):
            self.network.reload()

        # Check stale Network
        if container.name in (
            val.get("Name") for val in self.network.attrs.get("Containers", {}).values()
        ):
            self.stale_cleanup(container.name)

        # Attach Network
        try:
            self.network.connect(container, aliases=alias, ipv4_address=ipv4_address)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't link container to hassio-net: %s", err)
            raise DockerError() from err

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
            raise DockerError() from err

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
