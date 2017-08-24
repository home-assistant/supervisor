"""Internal network manager for HassIO."""
import logging

import docker

from ..const import DOCKER_NETWORK_MASK, DOCKER_NETWORK, DOCKER_NETWORK_RANGE

_LOGGER = logging.getLogger(__name__)


class DockerNetwork(object):
    """Internal HassIO Network."""

    def __init__(self, dock):
        """Initialize internal hassio network."""
        self.docker = dock
        self.network = self._get_network()

    @property
    def name(self):
        """Return name of network."""
        return DOCKER_NETWORK

    @property
    def gateway(self):
        """Return gateway of the network."""
        return DOCKER_NETWORK_MASK[1]

    @property
    def supervisor(self):
        """Return supervisor of the network."""
        return DOCKER_NETWORK_MASK[2]

    def _get_network(self):
        """Get HassIO network."""
        try:
            return self.docker.networks.get(DOCKER_NETWORK)
        except docker.errors.NotFound:
            _LOGGER.info("Can't find HassIO network, create new network")

        ipam_pool = docker.types.IPAMPool(
            subnet=str(DOCKER_NETWORK_MASK),
            gateway=str(self.gateway),
            iprange=str(DOCKER_NETWORK_RANGE)
        )

        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        return self.docker.networks.create(
            DOCKER_NETWORK, driver='bridge', ipam=ipam_config, options={
                "com.docker.network.bridge.name": DOCKER_NETWORK,
            })

    def attach_container(self, container, alias=None, ipv4=None):
        """Attach container to hassio network.

        Need run inside executor.
        """
        ipv4 = str(ipv4) if ipv4 else ""

        try:
            self.network.connect(container, aliases=alias, ipv4_address=ipv4)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't link container to hassio-net -> %s", err)
            return False

        self.network.reload()
        return True

    def container_mapped(self, container):
        """Return True if a container is already mapped to network."""
        container_list = set(i_cont.id for i_cont in self.network.containers)
        return container.id in container_list
