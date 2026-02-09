"""Internal network manager for Supervisor."""

from contextlib import suppress
from http import HTTPStatus
from ipaddress import IPv4Address
import logging
from typing import Any, Self, cast

import aiodocker
from aiodocker.networks import DockerNetwork as AiodockerNetwork

from ..const import (
    ATTR_AUDIO,
    ATTR_CLI,
    ATTR_DNS,
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
DOCKER_OPTIONS = "Options"
DOCKER_ENABLE_IPV6_DEFAULT = True
DOCKER_NETWORK_PARAMS = {
    "Name": DOCKER_NETWORK,
    "Driver": DOCKER_NETWORK_DRIVER,
    "IPAM": {
        "Driver": "default",
        "Config": [
            {
                "Subnet": str(DOCKER_IPV6_NETWORK_MASK),
            },
            {
                "Subnet": str(DOCKER_IPV4_NETWORK_MASK),
                "Gateway": str(DOCKER_IPV4_NETWORK_MASK[1]),
                "IPRange": str(DOCKER_IPV4_NETWORK_RANGE),
            },
        ],
    },
    DOCKER_ENABLEIPV6: DOCKER_ENABLE_IPV6_DEFAULT,
    DOCKER_OPTIONS: {"com.docker.network.bridge.name": DOCKER_NETWORK},
}


class DockerNetwork:
    """Internal Supervisor Network."""

    def __init__(self, docker_client: aiodocker.Docker):
        """Initialize internal Supervisor network."""
        self.docker: aiodocker.Docker = docker_client
        self._network: AiodockerNetwork | None = None
        self._network_meta: dict[str, Any] | None = None

    async def post_init(
        self, enable_ipv6: bool | None = None, mtu: int | None = None
    ) -> Self:
        """Post init actions that must be done in event loop."""
        try:
            self._network = network = await self.docker.networks.get(DOCKER_NETWORK)
        except aiodocker.DockerError as err:
            # If network was not found, create it instead. Can skip further checks since it's new
            if err.status == HTTPStatus.NOT_FOUND:
                await self._create_supervisor_network(enable_ipv6, mtu)
                return self

            raise DockerError(
                f"Could not get network from Docker: {err!s}", _LOGGER.error
            ) from err

        # Cache metadata for network
        await self.reload()
        current_ipv6: bool = self.network_meta.get(DOCKER_ENABLEIPV6, False)
        current_mtu_str: str | None = self.network_meta.get(DOCKER_OPTIONS, {}).get(
            "com.docker.network.driver.mtu"
        )
        current_mtu = int(current_mtu_str) if current_mtu_str is not None else None

        # Check if we have explicitly provided settings that differ from what is set
        changes = []
        if enable_ipv6 is not None and current_ipv6 != enable_ipv6:
            changes.append("IPv4/IPv6 Dual-Stack" if enable_ipv6 else "IPv4-Only")
        if mtu is not None and current_mtu != mtu:
            changes.append(f"MTU {mtu}")

        if not changes:
            return self

        _LOGGER.info("Migrating Supervisor network to %s", ", ".join(changes))

        # System is considered running if any containers besides Supervisor and Observer are found
        # A reboot is required then, we won't disconnect those containers to remake network
        containers: dict[str, dict[str, Any]] = self.network_meta.get("Containers", {})
        system_running = containers and any(
            container.get("Name") not in (OBSERVER_DOCKER_NAME, SUPERVISOR_DOCKER_NAME)
            for container in containers.values()
        )
        if system_running:
            _LOGGER.warning(
                "System appears to be running, not applying Supervisor network change. "
                "Reboot your system to apply the change."
            )
            return self

        # Disconnect all containers in the network
        for c_id, meta in containers.items():
            try:
                await network.disconnect({"Container": c_id, "Force": True})
            except aiodocker.DockerError:
                _LOGGER.warning(
                    "Cannot apply Supervisor network changes because container %s "
                    "could not be disconnected. Reboot your system to apply change.",
                    meta.get("Name"),
                )
                return self

        # Remove the network
        try:
            await network.delete()
        except aiodocker.DockerError:
            _LOGGER.warning(
                "Cannot apply Supervisor network changes because Supervisor network "
                "could not be removed and recreated. Reboot your system to apply change."
            )
            return self

        # Recreate it with correct settings
        await self._create_supervisor_network(enable_ipv6, mtu)
        return self

    @property
    def name(self) -> str:
        """Return name of network."""
        return DOCKER_NETWORK

    @property
    def network(self) -> AiodockerNetwork:
        """Return docker network."""
        if not self._network:
            raise RuntimeError("Network not set!")
        return self._network

    @property
    def network_meta(self) -> dict[str, Any]:
        """Return docker network metadata."""
        if not self._network_meta:
            raise RuntimeError("Network metadata not set!")
        return self._network_meta

    @property
    def containers(self) -> dict[str, dict[str, Any]]:
        """Return metadata of connected containers to network."""
        return self.network_meta.get("Containers", {})

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

    async def _create_supervisor_network(
        self, enable_ipv6: bool | None = None, mtu: int | None = None
    ) -> None:
        """Create supervisor network."""
        network_params = DOCKER_NETWORK_PARAMS.copy()

        if enable_ipv6 is not None:
            network_params[DOCKER_ENABLEIPV6] = enable_ipv6

        # Copy options and add MTU if specified
        if mtu is not None:
            options = cast(dict[str, str], network_params[DOCKER_OPTIONS]).copy()
            options["com.docker.network.driver.mtu"] = str(mtu)
            network_params[DOCKER_OPTIONS] = options

        try:
            self._network = await self.docker.networks.create(network_params)
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't create Supervisor network: {err}", _LOGGER.error
            ) from err

        await self.reload()

        with suppress(DockerError):
            await self.attach_container_by_name(
                SUPERVISOR_DOCKER_NAME, [ATTR_SUPERVISOR], self.supervisor
            )

        with suppress(DockerError):
            await self.attach_container_by_name(
                OBSERVER_DOCKER_NAME, [ATTR_OBSERVER], self.observer
            )

        for name, ip in (
            (ATTR_CLI, self.cli),
            (ATTR_DNS, self.dns),
            (ATTR_AUDIO, self.audio),
        ):
            with suppress(DockerError):
                await self.attach_container_by_name(
                    f"{DOCKER_PREFIX}_{name}", [name], ip
                )

    async def reload(self) -> None:
        """Get and cache metadata for supervisor network."""
        try:
            self._network_meta = await self.network.show()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Could not get network metadata from Docker: {err!s}", _LOGGER.error
            ) from err

    async def attach_container(
        self,
        container_id: str,
        name: str | None,
        alias: list[str] | None = None,
        ipv4: IPv4Address | None = None,
    ) -> None:
        """Attach container to Supervisor network."""
        # Reload Network information
        with suppress(DockerError):
            await self.reload()

        # Check stale Network
        if name and name in (val.get("Name") for val in self.containers.values()):
            await self.stale_cleanup(name)

        # Attach Network
        endpoint_config: dict[str, Any] = {}
        if alias:
            endpoint_config["Aliases"] = alias
        if ipv4:
            endpoint_config["IPAMConfig"] = {"IPv4Address": str(ipv4)}

        try:
            await self.network.connect(
                {
                    "Container": container_id,
                    "EndpointConfig": endpoint_config,
                }
            )
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't connect {name or container_id} to Supervisor network: {err}",
                _LOGGER.error,
            ) from err

    async def attach_container_by_name(
        self, name: str, alias: list[str] | None = None, ipv4: IPv4Address | None = None
    ) -> None:
        """Attach container to Supervisor network."""
        try:
            container = await self.docker.containers.get(name)
        except aiodocker.DockerError as err:
            raise DockerError(f"Can't find {name}: {err}", _LOGGER.error) from err

        if container.id not in self.containers:
            await self.attach_container(container.id, name, alias, ipv4)

    async def detach_default_bridge(
        self, container_id: str, name: str | None = None
    ) -> None:
        """Detach default Docker bridge."""
        try:
            default_network = await self.docker.networks.get(DOCKER_NETWORK_DRIVER)
            await default_network.disconnect({"Container": container_id})
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                return
            raise DockerError(
                f"Can't disconnect {name or container_id} from default network: {err}",
                _LOGGER.warning,
            ) from err

    async def stale_cleanup(self, name: str) -> None:
        """Force remove a container from Network.

        Fix: https://github.com/moby/moby/issues/23302
        """
        try:
            await self.network.disconnect({"Container": name, "Force": True})
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't disconnect {name} from Supervisor network: {err}",
                _LOGGER.warning,
            ) from err
