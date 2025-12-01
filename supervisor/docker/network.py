"""Internal network manager for Supervisor."""

import asyncio
from contextlib import suppress
from ipaddress import IPv4Address
import logging
from typing import Self, cast

import docker
from docker.models.containers import Container
from docker.models.networks import Network
import requests

from ..const import (
    ATTR_AUDIO,
    ATTR_CLI,
    ATTR_DNS,
    ATTR_ENABLE_IPV6,
    ATTR_OBSERVER,
    ATTR_SUPERVISOR,
    DOCKER_IPV4_NETWORK_MASK,
    DOCKER_IPV4_NETWORK_RANGE,
    DOCKER_IPV6_NETWORK_MASK,
    DOCKER_NETWORK,
    DOCKER_NETWORK_DRIVER,
    DOCKER_PREFIX,
    OBSERVER_DOCKER_NAME,
    SUPERVISOR_DOCKER_NAME,
)
from ..exceptions import DockerError

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOCKER_ENABLEIPV6 = "EnableIPv6"
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
    ATTR_ENABLE_IPV6: True,
    "options": {"com.docker.network.bridge.name": DOCKER_NETWORK},
}

DOCKER_ENABLE_IPV6_DEFAULT = True


class DockerNetwork:
    """Internal Supervisor Network.

    This class is not AsyncIO safe!
    """

    def __init__(self, docker_client: docker.DockerClient):
        """Initialize internal Supervisor network."""
        self.docker: docker.DockerClient = docker_client
        self._network: Network

    async def post_init(
        self, enable_ipv6: bool | None = None, mtu: int | None = None
    ) -> Self:
        """Post init actions that must be done in event loop."""
        self._network = await asyncio.get_running_loop().run_in_executor(
            None, self._get_network, enable_ipv6, mtu
        )
        return self

    @property
    def name(self) -> str:
        """Return name of network."""
        return DOCKER_NETWORK

    @property
    def network(self) -> Network:
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

    def _get_network(
        self, enable_ipv6: bool | None = None, mtu: int | None = None
    ) -> Network:
        """Get supervisor network."""
        try:
            if network := self.docker.networks.get(DOCKER_NETWORK):
                current_ipv6 = network.attrs.get(DOCKER_ENABLEIPV6, False)
                current_mtu = network.attrs.get("Options", {}).get(
                    "com.docker.network.driver.mtu"
                )
                current_mtu = int(current_mtu) if current_mtu else None

                # If the network exists and we don't have explicit settings,
                # simply stick with what we have.
                if (enable_ipv6 is None or current_ipv6 == enable_ipv6) and (
                    mtu is None or current_mtu == mtu
                ):
                    return network

                # We have explicit settings which differ from the current state.
                changes = []
                if enable_ipv6 is not None and current_ipv6 != enable_ipv6:
                    changes.append(
                        "IPv4/IPv6 Dual-Stack" if enable_ipv6 else "IPv4-Only"
                    )
                if mtu is not None and current_mtu != mtu:
                    changes.append(f"MTU {mtu}")

                if changes:
                    _LOGGER.info(
                        "Migrating Supervisor network to %s", ", ".join(changes)
                    )

                if (containers := network.containers) and (
                    containers_all := all(
                        container.name in (OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME)
                        for container in containers
                    )
                ):
                    for container in containers:
                        with suppress(
                            docker.errors.APIError,
                            docker.errors.DockerException,
                            requests.RequestException,
                        ):
                            network.disconnect(container, force=True)

                if not containers or containers_all:
                    try:
                        network.remove()
                    except docker.errors.APIError:
                        _LOGGER.warning("Failed to remove existing Supervisor network")
                        return network
                else:
                    _LOGGER.warning(
                        "System appears to be running, "
                        "not applying Supervisor network change. "
                        "Reboot your system to apply the change."
                    )
                    return network
        except docker.errors.NotFound:
            _LOGGER.info("Can't find Supervisor network, creating a new network")

        network_params = DOCKER_NETWORK_PARAMS.copy()
        network_params[ATTR_ENABLE_IPV6] = (
            DOCKER_ENABLE_IPV6_DEFAULT if enable_ipv6 is None else enable_ipv6
        )

        # Copy options and add MTU if specified
        if mtu is not None:
            options = cast(dict[str, str], network_params["options"]).copy()
            options["com.docker.network.driver.mtu"] = str(mtu)
            network_params["options"] = options

        try:
            self._network = self.docker.networks.create(**network_params)  # type: ignore
        except docker.errors.APIError as err:
            raise DockerError(
                f"Can't create Supervisor network: {err}", _LOGGER.error
            ) from err

        with suppress(DockerError):
            self.attach_container_by_name(
                SUPERVISOR_DOCKER_NAME, [ATTR_SUPERVISOR], self.supervisor
            )

        with suppress(DockerError):
            self.attach_container_by_name(
                OBSERVER_DOCKER_NAME, [ATTR_OBSERVER], self.observer
            )

        for name, ip in (
            (ATTR_CLI, self.cli),
            (ATTR_DNS, self.dns),
            (ATTR_AUDIO, self.audio),
        ):
            with suppress(DockerError):
                self.attach_container_by_name(f"{DOCKER_PREFIX}_{name}", [name], ip)

        return self._network

    def attach_container(
        self,
        container: Container,
        alias: list[str] | None = None,
        ipv4: IPv4Address | None = None,
    ) -> None:
        """Attach container to Supervisor network.

        Need run inside executor.
        """
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
            self.network.connect(
                container, aliases=alias, ipv4_address=str(ipv4) if ipv4 else None
            )
        except (
            docker.errors.NotFound,
            docker.errors.APIError,
            docker.errors.DockerException,
            requests.RequestException,
        ) as err:
            raise DockerError(
                f"Can't connect {container.name} to Supervisor network: {err}",
                _LOGGER.error,
            ) from err

    def attach_container_by_name(
        self,
        name: str,
        alias: list[str] | None = None,
        ipv4: IPv4Address | None = None,
    ) -> None:
        """Attach container to Supervisor network.

        Need run inside executor.
        """
        try:
            container = self.docker.containers.get(name)
        except (
            docker.errors.NotFound,
            docker.errors.APIError,
            docker.errors.DockerException,
            requests.RequestException,
        ) as err:
            raise DockerError(f"Can't find {name}: {err}", _LOGGER.error) from err

        if container.id not in self.containers:
            self.attach_container(container, alias, ipv4)

    def detach_default_bridge(self, container: Container) -> None:
        """Detach default Docker bridge.

        Need run inside executor.
        """
        try:
            default_network = self.docker.networks.get(DOCKER_NETWORK_DRIVER)
            default_network.disconnect(container)
        except docker.errors.NotFound:
            pass
        except (
            docker.errors.APIError,
            docker.errors.DockerException,
            requests.RequestException,
        ) as err:
            raise DockerError(
                f"Can't disconnect {container.name} from default network: {err}",
                _LOGGER.warning,
            ) from err

    def stale_cleanup(self, name: str) -> None:
        """Force remove a container from Network.

        Fix: https://github.com/moby/moby/issues/23302
        """
        try:
            self.network.disconnect(name, force=True)
        except (
            docker.errors.APIError,
            docker.errors.DockerException,
            requests.RequestException,
        ) as err:
            raise DockerError(
                f"Can't disconnect {name} from Supervisor network: {err}",
                _LOGGER.warning,
            ) from err
