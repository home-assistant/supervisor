"""Init file for Supervisor Docker object."""
from contextlib import suppress
from ipaddress import IPv4Address
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import attr
import docker
from packaging import version as pkg_version
import requests

from ..const import (
    ATTR_REGISTRIES,
    DNS_SUFFIX,
    DOCKER_IMAGE_DENYLIST,
    DOCKER_NETWORK,
    FILE_HASSIO_DOCKER,
    SOCKET_DOCKER,
)
from ..exceptions import DockerAPIError, DockerError, DockerNotFound, DockerRequestError
from ..utils.json import JsonConfig
from ..validate import SCHEMA_DOCKER_CONFIG
from .network import DockerNetwork

_LOGGER: logging.Logger = logging.getLogger(__name__)

MIN_SUPPORTED_DOCKER = "19.03.0"


@attr.s(frozen=True)
class CommandReturn:
    """Return object from command run."""

    exit_code: int = attr.ib()
    output: bytes = attr.ib()


@attr.s(frozen=True)
class DockerInfo:
    """Return docker information."""

    version: str = attr.ib()
    storage: str = attr.ib()
    logging: str = attr.ib()

    @staticmethod
    def new(data: Dict[str, Any]):
        """Create a object from docker info."""
        return DockerInfo(data["ServerVersion"], data["Driver"], data["LoggingDriver"])

    @property
    def supported_version(self) -> bool:
        """Return true, if docker version is supported."""
        version_local = pkg_version.parse(self.version)
        version_min = pkg_version.parse(MIN_SUPPORTED_DOCKER)

        return version_local >= version_min

    @property
    def inside_lxc(self) -> bool:
        """Return True if the docker run inside lxc."""
        return Path("/dev/lxd/sock").exists()

    def check_requirements(self) -> None:
        """Show wrong configurations."""
        if self.storage != "overlay2":
            _LOGGER.error("Docker storage driver %s is not supported!", self.storage)

        if self.logging != "journald":
            _LOGGER.error("Docker logging driver %s is not supported!", self.logging)

        return self.storage != "overlay2" or self.logging != "journald"


class DockerConfig(JsonConfig):
    """Home Assistant core object for Docker configuration."""

    def __init__(self):
        """Initialize the JSON configuration."""
        super().__init__(FILE_HASSIO_DOCKER, SCHEMA_DOCKER_CONFIG)

    @property
    def registries(self) -> Dict[str, Any]:
        """Return credentials for docker registries."""
        return self._data.get(ATTR_REGISTRIES, {})


class DockerAPI:
    """Docker Supervisor wrapper.

    This class is not AsyncIO safe!
    """

    def __init__(self):
        """Initialize Docker base wrapper."""
        self.docker: docker.DockerClient = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)), version="auto", timeout=900
        )
        self.network: DockerNetwork = DockerNetwork(self.docker)
        self._info: DockerInfo = DockerInfo.new(self.docker.info())
        self.config: DockerConfig = DockerConfig()

    @property
    def images(self) -> docker.models.images.ImageCollection:
        """Return API images."""
        return self.docker.images

    @property
    def containers(self) -> docker.models.containers.ContainerCollection:
        """Return API containers."""
        return self.docker.containers

    @property
    def api(self) -> docker.APIClient:
        """Return API containers."""
        return self.docker.api

    @property
    def info(self) -> DockerInfo:
        """Return local docker info."""
        return self._info

    def run(
        self,
        image: str,
        version: str = "latest",
        dns: bool = True,
        ipv4: Optional[IPv4Address] = None,
        **kwargs: Any,
    ) -> docker.models.containers.Container:
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
                f"{image}:{version}", use_config_proxy=False, **kwargs
            )
        except docker.errors.NotFound as err:
            _LOGGER.error("Image %s not exists for %s", image, name)
            raise DockerNotFound() from err
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't create container from %s: %s", name, err)
            raise DockerAPIError() from err
        except requests.RequestException as err:
            _LOGGER.error("Dockerd connection issue for %s: %s", name, err)
            raise DockerRequestError() from err

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
            host_network: docker.models.networks.Network = self.docker.networks.get(
                "host"
            )

            # Check if container is register on host
            if name in (
                val.get("Name")
                for val in host_network.attrs.get("Containers", {}).values()
            ):
                host_network.disconnect(name, force=True)

        # Run container
        try:
            container.start()
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't start %s: %s", name, err)
            raise DockerAPIError() from err
        except requests.RequestException as err:
            _LOGGER.error("Dockerd connection issue for %s: %s", name, err)
            raise DockerRequestError() from err

        # Update metadata
        with suppress(docker.errors.DockerException, requests.RequestException):
            container.reload()

        return container

    def run_command(
        self,
        image: str,
        version: str = "latest",
        command: Optional[str] = None,
        **kwargs: Any,
    ) -> CommandReturn:
        """Create a temporary container and run command.

        Need run inside executor.
        """
        stdout = kwargs.get("stdout", True)
        stderr = kwargs.get("stderr", True)

        _LOGGER.info("Runing command '%s' on %s", command, image)
        try:
            container = self.docker.containers.run(
                f"{image}:{version}",
                command=command,
                network=self.network.name,
                use_config_proxy=False,
                **kwargs,
            )

            # wait until command is done
            result = container.wait()
            output = container.logs(stdout=stdout, stderr=stderr)

        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Can't execute command: %s", err)
            raise DockerError() from err

        finally:
            # cleanup container
            with suppress(docker.errors.DockerException, requests.RequestException):
                container.remove(force=True)

        return CommandReturn(result.get("StatusCode"), output)

    def repair(self) -> None:
        """Repair local docker overlayfs2 issues."""

        _LOGGER.info("Prune stale containers")
        try:
            output = self.docker.api.prune_containers()
            _LOGGER.debug("Containers prune: %s", output)
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for containers prune: %s", err)

        _LOGGER.info("Prune stale images")
        try:
            output = self.docker.api.prune_images(filters={"dangling": False})
            _LOGGER.debug("Images prune: %s", output)
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for images prune: %s", err)

        _LOGGER.info("Prune stale builds")
        try:
            output = self.docker.api.prune_builds()
            _LOGGER.debug("Builds prune: %s", output)
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for builds prune: %s", err)

        _LOGGER.info("Prune stale volumes")
        try:
            output = self.docker.api.prune_builds()
            _LOGGER.debug("Volumes prune: %s", output)
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for volumes prune: %s", err)

        _LOGGER.info("Prune stale networks")
        try:
            output = self.docker.api.prune_networks()
            _LOGGER.debug("Networks prune: %s", output)
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for networks prune: %s", err)

        _LOGGER.info("Fix stale container on hassio network")
        try:
            self.prune_networks(DOCKER_NETWORK)
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for networks prune: %s", err)

        _LOGGER.info("Fix stale container on hassio network")
        try:
            self.prune_networks("host")
        except docker.errors.APIError as err:
            _LOGGER.warning("Error for networks prune: %s", err)

    def prune_networks(self, network_name: str) -> None:
        """Prune stale container from network."""
        network: docker.models.networks.Network = self.docker.networks.get(network_name)

        for cid, data in network.attrs.get("Containers", {}):
            try:
                self.docker.containers.get(cid)
                continue
            except docker.errors.NotFound:
                _LOGGER.debug(
                    "Docker network %s is corrupt on container: %s", network_name, cid
                )
            except (docker.errors.DockerException, requests.RequestException):
                _LOGGER.warning(
                    "Docker fatal error on container %s on %s", cid, network_name
                )
                continue

            with suppress(docker.errors.DockerException, requests.RequestException):
                network.disconnect(data.get("Name", cid), force=True)

    def check_denylist_images(self) -> bool:
        """Return a boolean if the host has images in the denylist."""
        denied_images = set()

        try:
            for image in self.images.list():
                for tag in image.tags:
                    image_name = tag.split(":")[0]
                    if (
                        image_name in DOCKER_IMAGE_DENYLIST
                        and image_name not in denied_images
                    ):
                        denied_images.add(image_name)
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Corrupt docker overlayfs detect: %s", err)
            raise DockerError() from err

        if not denied_images:
            return False

        _LOGGER.error(
            "Found images: '%s' which are not supported, remove these from the host!",
            ", ".join(denied_images),
        )
        return True
