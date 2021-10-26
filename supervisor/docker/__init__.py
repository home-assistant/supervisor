"""Init file for Supervisor Docker object."""
from contextlib import suppress
from ipaddress import IPv4Address
import logging
import os
from pathlib import Path
from typing import Any, Optional

import attr
from awesomeversion import AwesomeVersion, AwesomeVersionCompare
from docker import errors as docker_errors
from docker.api.client import APIClient
from docker.client import DockerClient
from docker.models.containers import Container, ContainerCollection
from docker.models.images import ImageCollection
from docker.models.networks import Network
import requests

from ..const import (
    ATTR_REGISTRIES,
    DNS_SUFFIX,
    DOCKER_NETWORK,
    ENV_SUPERVISOR_CPU_RT,
    FILE_HASSIO_DOCKER,
    SOCKET_DOCKER,
)
from ..exceptions import DockerAPIError, DockerError, DockerNotFound, DockerRequestError
from ..utils.common import FileConfiguration
from ..validate import SCHEMA_DOCKER_CONFIG
from .network import DockerNetwork

_LOGGER: logging.Logger = logging.getLogger(__name__)

MIN_SUPPORTED_DOCKER = "19.03.0"
DOCKER_NETWORK_HOST = "host"


@attr.s(frozen=True)
class CommandReturn:
    """Return object from command run."""

    exit_code: int = attr.ib()
    output: bytes = attr.ib()


@attr.s(frozen=True)
class DockerInfo:
    """Return docker information."""

    version: AwesomeVersion = attr.ib()
    storage: str = attr.ib()
    logging: str = attr.ib()

    @staticmethod
    def new(data: dict[str, Any]):
        """Create a object from docker info."""
        return DockerInfo(
            AwesomeVersion(data["ServerVersion"]), data["Driver"], data["LoggingDriver"]
        )

    @property
    def supported_version(self) -> bool:
        """Return true, if docker version is supported."""
        try:
            return self.version >= MIN_SUPPORTED_DOCKER
        except AwesomeVersionCompare:
            return False

    @property
    def support_cpu_realtime(self) -> bool:
        """Return true, if CONFIG_RT_GROUP_SCHED is loaded."""
        if not Path("/sys/fs/cgroup/cpu/cpu.rt_runtime_us").exists():
            return False
        return bool(os.environ.get(ENV_SUPERVISOR_CPU_RT, 0))


class DockerConfig(FileConfiguration):
    """Home Assistant core object for Docker configuration."""

    def __init__(self):
        """Initialize the JSON configuration."""
        super().__init__(FILE_HASSIO_DOCKER, SCHEMA_DOCKER_CONFIG)

    @property
    def registries(self) -> dict[str, Any]:
        """Return credentials for docker registries."""
        return self._data.get(ATTR_REGISTRIES, {})


class DockerAPI:
    """Docker Supervisor wrapper.

    This class is not AsyncIO safe!
    """

    def __init__(self):
        """Initialize Docker base wrapper."""
        self.docker: DockerClient = DockerClient(
            base_url=f"unix:/{str(SOCKET_DOCKER)}", version="auto", timeout=900
        )
        self.network: DockerNetwork = DockerNetwork(self.docker)
        self._info: DockerInfo = DockerInfo.new(self.docker.info())
        self.config: DockerConfig = DockerConfig()

    @property
    def images(self) -> ImageCollection:
        """Return API images."""
        return self.docker.images

    @property
    def containers(self) -> ContainerCollection:
        """Return API containers."""
        return self.docker.containers

    @property
    def api(self) -> APIClient:
        """Return API containers."""
        return self.docker.api

    @property
    def info(self) -> DockerInfo:
        """Return local docker info."""
        return self._info

    def run(
        self,
        image: str,
        tag: str = "latest",
        dns: bool = True,
        ipv4: Optional[IPv4Address] = None,
        **kwargs: Any,
    ) -> Container:
        """Create a Docker container and run it.

        Need run inside executor.
        """
        name: Optional[str] = kwargs.get("name")
        network_mode: Optional[str] = kwargs.get("network_mode")
        hostname: Optional[str] = kwargs.get("hostname")

        # Setup DNS
        if dns:
            kwargs["dns"] = [str(self.network.dns)]
            kwargs["dns_search"] = [DNS_SUFFIX]
            kwargs["domainname"] = DNS_SUFFIX

        # Setup network
        if not network_mode:
            kwargs["network"] = None

        # Create container
        try:
            container = self.docker.containers.create(
                f"{image}:{tag}", use_config_proxy=False, **kwargs
            )
        except docker_errors.NotFound as err:
            raise DockerNotFound(
                f"Image {image} not exists for {name}", _LOGGER.error
            ) from err
        except docker_errors.DockerException as err:
            raise DockerAPIError(
                f"Can't create container from {name}: {err}", _LOGGER.error
            ) from err
        except requests.RequestException as err:
            raise DockerRequestError(
                f"Dockerd connection issue for {name}: {err}", _LOGGER.error
            ) from err

        # Attach network
        if not network_mode:
            alias = [hostname] if hostname else None
            try:
                self.network.attach_container(container, alias=alias, ipv4=ipv4)
            except DockerError:
                _LOGGER.warning("Can't attach %s to hassio-network!", name)
            else:
                with suppress(DockerError):
                    self.network.detach_default_bridge(container)
        else:
            host_network: Network = self.docker.networks.get(DOCKER_NETWORK_HOST)

            # Check if container is register on host
            # https://github.com/moby/moby/issues/23302
            if name in (
                val.get("Name")
                for val in host_network.attrs.get("Containers", {}).values()
            ):
                with suppress(docker_errors.NotFound):
                    host_network.disconnect(name, force=True)

        # Run container
        try:
            container.start()
        except docker_errors.DockerException as err:
            raise DockerAPIError(f"Can't start {name}: {err}", _LOGGER.error) from err
        except requests.RequestException as err:
            raise DockerRequestError(
                f"Dockerd connection issue for {name}: {err}", _LOGGER.error
            ) from err

        # Update metadata
        with suppress(docker_errors.DockerException, requests.RequestException):
            container.reload()

        return container

    def run_command(
        self,
        image: str,
        tag: str = "latest",
        command: Optional[str] = None,
        **kwargs: Any,
    ) -> CommandReturn:
        """Create a temporary container and run command.

        Need run inside executor.
        """
        stdout = kwargs.get("stdout", True)
        stderr = kwargs.get("stderr", True)

        _LOGGER.info("Runing command '%s' on %s", command, image)
        container = None
        try:
            container = self.docker.containers.run(
                f"{image}:{tag}",
                command=command,
                network=self.network.name,
                use_config_proxy=False,
                **kwargs,
            )

            # wait until command is done
            result = container.wait()
            output = container.logs(stdout=stdout, stderr=stderr)

        except (docker_errors.DockerException, requests.RequestException) as err:
            raise DockerError(f"Can't execute command: {err}", _LOGGER.error) from err

        finally:
            # cleanup container
            if container:
                with suppress(docker_errors.DockerException, requests.RequestException):
                    container.remove(force=True)

        return CommandReturn(result.get("StatusCode"), output)

    def repair(self) -> None:
        """Repair local docker overlayfs2 issues."""

        _LOGGER.info("Prune stale containers")
        try:
            output = self.docker.api.prune_containers()
            _LOGGER.debug("Containers prune: %s", output)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for containers prune: %s", err)

        _LOGGER.info("Prune stale images")
        try:
            output = self.docker.api.prune_images(filters={"dangling": False})
            _LOGGER.debug("Images prune: %s", output)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for images prune: %s", err)

        _LOGGER.info("Prune stale builds")
        try:
            output = self.docker.api.prune_builds()
            _LOGGER.debug("Builds prune: %s", output)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for builds prune: %s", err)

        _LOGGER.info("Prune stale volumes")
        try:
            output = self.docker.api.prune_builds()
            _LOGGER.debug("Volumes prune: %s", output)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for volumes prune: %s", err)

        _LOGGER.info("Prune stale networks")
        try:
            output = self.docker.api.prune_networks()
            _LOGGER.debug("Networks prune: %s", output)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for networks prune: %s", err)

        _LOGGER.info("Fix stale container on hassio network")
        try:
            self.prune_networks(DOCKER_NETWORK)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for networks hassio prune: %s", err)

        _LOGGER.info("Fix stale container on host network")
        try:
            self.prune_networks(DOCKER_NETWORK_HOST)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for networks host prune: %s", err)

    def prune_networks(self, network_name: str) -> None:
        """Prune stale container from network.

        Fix: https://github.com/moby/moby/issues/23302
        """
        network: Network = self.docker.networks.get(network_name)

        for cid, data in network.attrs.get("Containers", {}).items():
            try:
                self.docker.containers.get(cid)
                continue
            except docker_errors.NotFound:
                _LOGGER.debug(
                    "Docker network %s is corrupt on container: %s", network_name, cid
                )
            except (docker_errors.DockerException, requests.RequestException):
                _LOGGER.warning(
                    "Docker fatal error on container %s on %s", cid, network_name
                )
                continue

            with suppress(docker_errors.DockerException, requests.RequestException):
                network.disconnect(data.get("Name", cid), force=True)
