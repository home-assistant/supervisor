"""External physical network management for app network isolation.

Apps with host networking can be assigned an isolated endpoint on a physical
host interface instead (macvlan/ipvlan Docker networks). The Docker engine
allows only one such network per parent interface, so networks are a shared
resource managed here and referenced by the apps using them.
"""

from contextlib import suppress
from http import HTTPStatus
from ipaddress import IPv4Address, IPv4Interface, IPv4Network
import logging
from typing import Any, Final

import aiodocker
from awesomeversion import AwesomeVersion, AwesomeVersionCompareException

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DockerError
from ..host.configuration import Interface
from ..host.const import InterfaceType
from .const import LABEL_MANAGED, ExtraNetworkEndpoint, NetworkIsolationConfig

_LOGGER: logging.Logger = logging.getLogger(__name__)

# GwPriority on endpoints requires Docker API 1.48
MIN_EXTERNAL_NETWORK_DOCKER: Final = AwesomeVersion("28.0.0")

# Make the physical network win the default route over the internal
# NAT-ed hassio network (which uses the default priority of 0).
EXTERNAL_NETWORK_GW_PRIORITY: Final = 100

DOCKER_PARENT_INTERFACE: Final = "parent"


class DockerExternalNetworks(CoreSysAttributes):
    """Manage Docker networks attached to physical host interfaces."""

    def __init__(self, coresys: CoreSys):
        """Initialize external networks manager."""
        self.coresys: CoreSys = coresys

    @property
    def available(self) -> bool:
        """Return True if the Docker engine supports external networks."""
        try:
            return self.sys_docker.info.version >= MIN_EXTERNAL_NETWORK_DOCKER
        except AwesomeVersionCompareException:
            return False

    @staticmethod
    def network_name(config: NetworkIsolationConfig) -> str:
        """Return the Docker network name for an isolation config."""
        return f"hassio-{config.driver}-{config.interface}"

    @staticmethod
    def mac_from_ip(ipv4: IPv4Address) -> str:
        """Return a stable, locally administered MAC address for an IPv4.

        Same derivation Docker used for macvlan endpoints before engine 28
        switched to random MACs per endpoint creation. Pinning it keeps the
        app's MAC stable across container recreations so users can rely on
        it in router/firewall rules.
        """
        return "02:42:" + ":".join(f"{octet:02x}" for octet in ipv4.packed)

    @staticmethod
    def capable_interface(interface: Interface) -> bool:
        """Return True if a host interface can host an external network."""
        return (
            interface.type == InterfaceType.ETHERNET
            and interface.connected
            and DockerExternalNetworks.interface_subnet(interface) is not None
        )

    @staticmethod
    def interface_subnet(interface: Interface) -> IPv4Network | None:
        """Return the IPv4 subnet of a host interface, if any."""
        if not interface.ipv4:
            return None
        for address in interface.ipv4.address:
            if isinstance(address, IPv4Interface):
                return address.network
        return None

    @staticmethod
    def _interface_ip(interface: Interface) -> IPv4Address | None:
        """Return the host's own IPv4 address on the interface, if any."""
        if not interface.ipv4:
            return None
        for address in interface.ipv4.address:
            if isinstance(address, IPv4Interface):
                return address.ip
        return None

    def _network_params(
        self, config: NetworkIsolationConfig, interface: Interface
    ) -> dict[str, Any]:
        """Return Docker network create parameters for an isolation config."""
        subnet = self.interface_subnet(interface)
        if subnet is None:
            raise DockerError(
                f"Host interface {interface.name} has no IPv4 subnet", _LOGGER.error
            )

        ipam_config: dict[str, Any] = {"Subnet": str(subnet)}
        if interface.ipv4 and isinstance(interface.ipv4.gateway, IPv4Address):
            ipam_config["Gateway"] = str(interface.ipv4.gateway)
        if host_ip := self._interface_ip(interface):
            # Reserve the host's own address so Docker IPAM can never assign it
            ipam_config["AuxiliaryAddresses"] = {"host": str(host_ip)}

        return {
            "Name": self.network_name(config),
            "Driver": config.driver.value,
            "IPAM": {"Driver": "default", "Config": [ipam_config]},
            "EnableIPv6": False,
            "Options": {DOCKER_PARENT_INTERFACE: interface.name},
            "Labels": {LABEL_MANAGED: ""},
        }

    @staticmethod
    def _network_matches(meta: dict[str, Any], params: dict[str, Any]) -> bool:
        """Return True if an existing network matches the wanted parameters."""
        if meta.get("Driver") != params["Driver"]:
            return False
        if (
            meta.get("Options", {}).get(DOCKER_PARENT_INTERFACE)
            != params["Options"][DOCKER_PARENT_INTERFACE]
        ):
            return False

        wanted_ipam: dict[str, Any] = params["IPAM"]["Config"][0]
        current_ipam_configs = meta.get("IPAM", {}).get("Config") or [{}]
        current_ipam: dict[str, Any] = current_ipam_configs[0]
        return current_ipam.get("Subnet") == wanted_ipam["Subnet"] and current_ipam.get(
            "Gateway"
        ) == wanted_ipam.get("Gateway")

    async def ensure(self, config: NetworkIsolationConfig) -> str:
        """Ensure the Docker network for an isolation config exists.

        Returns the network name. Raises HostNetworkNotFound if the parent
        interface is gone and DockerError if the network cannot be created
        or drifted from the host interface configuration while still in use.
        """
        interface = self.sys_host.network.get(config.interface)
        if not self.capable_interface(interface):
            raise DockerError(
                f"Host interface {config.interface} must be a connected ethernet "
                "interface with IPv4 to host an external network",
                _LOGGER.error,
            )

        params = self._network_params(config, interface)
        name: str = params["Name"]

        try:
            network = await self.sys_docker.docker.networks.get(name)
            meta = await network.show()
        except aiodocker.DockerError as err:
            if err.status != HTTPStatus.NOT_FOUND:
                raise DockerError(
                    f"Can't inspect external network {name}: {err}", _LOGGER.error
                ) from err
            await self._create(params)
            return name

        if self._network_matches(meta, params):
            return name

        # The host interface configuration changed since the network was
        # created. Recreate it unless containers are still attached.
        if meta.get("Containers"):
            raise DockerError(
                f"External network {name} no longer matches the configuration of "
                f"host interface {config.interface} but still has containers "
                "attached. Stop the apps using it to recreate the network.",
                _LOGGER.error,
            )

        _LOGGER.info(
            "Recreating external network %s for changed host interface %s",
            name,
            config.interface,
        )
        try:
            await network.delete()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't remove outdated external network {name}: {err}", _LOGGER.error
            ) from err
        await self._create(params)
        return name

    async def _create(self, params: dict[str, Any]) -> None:
        """Create an external network."""
        _LOGGER.info(
            "Creating external network %s on host interface %s",
            params["Name"],
            params["Options"][DOCKER_PARENT_INTERFACE],
        )
        try:
            await self.sys_docker.docker.networks.create(params)
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't create external network {params['Name']}: {err}", _LOGGER.error
            ) from err

    async def connect_container(
        self, container_id: str, name: str | None, endpoint: ExtraNetworkEndpoint
    ) -> None:
        """Connect a container to an external network endpoint."""
        try:
            network = await self.sys_docker.docker.networks.get(endpoint.network)
            meta = await network.show()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't get external network {endpoint.network}: {err}", _LOGGER.error
            ) from err

        # Clean up stale endpoint of a previous container with the same name
        # Fix: https://github.com/moby/moby/issues/23302
        if name and name in (
            val.get("Name") for val in meta.get("Containers", {}).values()
        ):
            with suppress(aiodocker.DockerError):
                await network.disconnect({"Container": name, "Force": True})

        endpoint_config: dict[str, Any] = {
            "IPAMConfig": {"IPv4Address": str(endpoint.ipv4)},
            "GwPriority": endpoint.gw_priority,
        }
        if endpoint.mac:
            endpoint_config["MacAddress"] = endpoint.mac
        try:
            await network.connect(
                {"Container": container_id, "EndpointConfig": endpoint_config}
            )
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't connect {name or container_id} to external network "
                f"{endpoint.network}: {err}",
                _LOGGER.error,
            ) from err

    async def gc(self) -> None:
        """Remove external networks no installed app references.

        Networks with containers still attached are skipped; removal is
        retried on the next garbage collection.
        """
        used = {
            self.network_name(config)
            for app in self.sys_apps.installed
            if (config := app.network_isolation)
        }

        try:
            networks = await self.sys_docker.docker.networks.list(
                filters={"label": LABEL_MANAGED}
            )
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't list external networks: {err}", _LOGGER.warning
            ) from err

        for meta in networks:
            name = meta.get("Name", "")
            if name in used or not name.startswith("hassio-"):
                continue

            _LOGGER.info("Removing unused external network %s", name)
            try:
                network = await self.sys_docker.docker.networks.get(name)
                await network.delete()
            except aiodocker.DockerError as err:
                _LOGGER.warning("Can't remove external network %s: %s", name, err)
