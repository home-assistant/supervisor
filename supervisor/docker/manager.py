"""Manager for Supervisor Docker."""

import asyncio
from contextlib import suppress
from functools import partial
from ipaddress import IPv4Address
import logging
import os
from pathlib import Path
from typing import Any, Final, Self, cast

import attr
from awesomeversion import AwesomeVersion, AwesomeVersionCompareException
from docker import errors as docker_errors
from docker.api.client import APIClient
from docker.client import DockerClient
from docker.errors import DockerException, ImageNotFound, NotFound
from docker.models.containers import Container, ContainerCollection
from docker.models.images import Image, ImageCollection
from docker.models.networks import Network
from docker.types.daemon import CancellableStream
import requests

from ..const import (
    ATTR_REGISTRIES,
    DNS_SUFFIX,
    DOCKER_NETWORK,
    ENV_SUPERVISOR_CPU_RT,
    FILE_HASSIO_DOCKER,
    SOCKET_DOCKER,
)
from ..coresys import CoreSys
from ..exceptions import DockerAPIError, DockerError, DockerNotFound, DockerRequestError
from ..utils.common import FileConfiguration
from ..validate import SCHEMA_DOCKER_CONFIG
from .const import LABEL_MANAGED
from .monitor import DockerMonitor
from .network import DockerNetwork

_LOGGER: logging.Logger = logging.getLogger(__name__)

MIN_SUPPORTED_DOCKER: Final = AwesomeVersion("20.10.1")
DOCKER_NETWORK_HOST: Final = "host"


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
    cgroup: str = attr.ib()

    @staticmethod
    def new(data: dict[str, Any]):
        """Create a object from docker info."""
        return DockerInfo(
            AwesomeVersion(data.get("ServerVersion", "0.0.0")),
            data.get("Driver", "unknown"),
            data.get("LoggingDriver", "unknown"),
            data.get("CgroupVersion", "1"),
        )

    @property
    def supported_version(self) -> bool:
        """Return true, if docker version is supported."""
        try:
            return self.version >= MIN_SUPPORTED_DOCKER
        except AwesomeVersionCompareException:
            return False

    @property
    def support_cpu_realtime(self) -> bool:
        """Return true, if CONFIG_RT_GROUP_SCHED is loaded."""
        if not Path("/sys/fs/cgroup/cpu/cpu.rt_runtime_us").exists():
            return False
        return bool(os.environ.get(ENV_SUPERVISOR_CPU_RT) == "1")


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

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self._docker: DockerClient | None = None
        self._network: DockerNetwork | None = None
        self._info: DockerInfo | None = None
        self.config: DockerConfig = DockerConfig()
        self._monitor: DockerMonitor = DockerMonitor(coresys)

    async def post_init(self) -> Self:
        """Post init actions that must be done in event loop."""
        self._docker = await asyncio.get_running_loop().run_in_executor(
            None,
            partial(
                DockerClient,
                base_url=f"unix:/{str(SOCKET_DOCKER)}",
                version="auto",
                timeout=900,
            ),
        )
        self._network = DockerNetwork(self._docker)
        self._info = DockerInfo.new(self.docker.info())
        await self.config.read_data()
        return self

    @property
    def docker(self) -> DockerClient:
        """Get docker API client."""
        if not self._docker:
            raise RuntimeError("Docker API Client not initialized!")
        return self._docker

    @property
    def network(self) -> DockerNetwork:
        """Get Docker network."""
        if not self._network:
            raise RuntimeError("Docker Network not initialized!")
        return self._network

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
        if not self._info:
            raise RuntimeError("Docker Info not initialized!")
        return self._info

    @property
    def events(self) -> CancellableStream:
        """Return docker event stream."""
        return self.docker.events(decode=True)

    @property
    def monitor(self) -> DockerMonitor:
        """Return docker events monitor."""
        return self._monitor

    async def load(self) -> None:
        """Start docker events monitor."""
        await self.monitor.load()

    async def unload(self) -> None:
        """Stop docker events monitor."""
        await self.monitor.unload()

    def run(
        self,
        image: str,
        tag: str = "latest",
        dns: bool = True,
        ipv4: IPv4Address | None = None,
        **kwargs: Any,
    ) -> Container:
        """Create a Docker container and run it.

        Need run inside executor.
        """
        name: str | None = kwargs.get("name")
        network_mode: str | None = kwargs.get("network_mode")
        hostname: str | None = kwargs.get("hostname")

        if "labels" not in kwargs:
            kwargs["labels"] = {}
        elif isinstance(kwargs["labels"], list):
            kwargs["labels"] = dict.fromkeys(kwargs["labels"], "")

        kwargs["labels"][LABEL_MANAGED] = ""

        # Setup DNS
        if dns:
            kwargs["dns"] = [str(self.network.dns)]
            kwargs["dns_search"] = [DNS_SUFFIX]
            # CoreDNS forward plug-in fails in ~6s, then fallback triggers.
            # However, the default timeout of glibc and musl is 5s. Increase
            # default timeout to make sure CoreDNS fallback is working
            # on first query.
            kwargs["dns_opt"] = ["timeout:10"]
            if hostname:
                kwargs["domainname"] = DNS_SUFFIX

        # Setup network
        if not network_mode:
            kwargs["network"] = None

        # Create container
        try:
            container = self.containers.create(
                f"{image}:{tag}", use_config_proxy=False, **kwargs
            )
        except docker_errors.NotFound as err:
            raise DockerNotFound(
                f"Image {image}:{tag} does not exist for {name}", _LOGGER.error
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
            if name and name in (
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
        command: str | None = None,
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

    def container_is_initialized(
        self, name: str, image: str, version: AwesomeVersion
    ) -> bool:
        """Return True if docker container exists in good state and is built from expected image."""
        try:
            docker_container = self.containers.get(name)
            docker_image = self.images.get(f"{image}:{version}")
        except NotFound:
            return False
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # Check the image is correct and state is good
        return (
            docker_container.image is not None
            and docker_container.image.id == docker_image.id
            and docker_container.status in ("exited", "running", "created")
        )

    def stop_container(
        self, name: str, timeout: int, remove_container: bool = True
    ) -> None:
        """Stop/remove Docker container."""
        try:
            docker_container: Container = self.containers.get(name)
        except NotFound:
            raise DockerNotFound() from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        if docker_container.status == "running":
            _LOGGER.info("Stopping %s application", name)
            with suppress(DockerException, requests.RequestException):
                docker_container.stop(timeout=timeout)

        if remove_container:
            with suppress(DockerException, requests.RequestException):
                _LOGGER.info("Cleaning %s application", name)
                docker_container.remove(force=True)

    def start_container(self, name: str) -> None:
        """Start Docker container."""
        try:
            docker_container: Container = self.containers.get(name)
        except NotFound:
            raise DockerNotFound(
                f"{name} not found for starting up", _LOGGER.error
            ) from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Could not get {name} for starting up", _LOGGER.error
            ) from err

        _LOGGER.info("Starting %s", name)
        try:
            docker_container.start()
        except (DockerException, requests.RequestException) as err:
            raise DockerError(f"Can't start {name}: {err}", _LOGGER.error) from err

    def restart_container(self, name: str, timeout: int) -> None:
        """Restart docker container."""
        try:
            container: Container = self.containers.get(name)
        except NotFound:
            raise DockerNotFound() from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        _LOGGER.info("Restarting %s", name)
        try:
            container.restart(timeout=timeout)
        except (DockerException, requests.RequestException) as err:
            raise DockerError(f"Can't restart {name}: {err}", _LOGGER.warning) from err

    def container_logs(self, name: str, tail: int = 100) -> bytes:
        """Return Docker logs of container."""
        try:
            docker_container: Container = self.containers.get(name)
        except NotFound:
            raise DockerNotFound() from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        try:
            return docker_container.logs(tail=tail, stdout=True, stderr=True)
        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't grep logs from {name}: {err}", _LOGGER.warning
            ) from err

    def container_stats(self, name: str) -> dict[str, Any]:
        """Read and return stats from container."""
        try:
            docker_container: Container = self.containers.get(name)
        except NotFound:
            raise DockerNotFound() from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # container is not running
        if docker_container.status != "running":
            raise DockerError(f"Container {name} is not running", _LOGGER.error)

        try:
            return docker_container.stats(stream=False)
        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't read stats from {name}: {err}", _LOGGER.error
            ) from err

    def container_run_inside(self, name: str, command: str) -> CommandReturn:
        """Execute a command inside Docker container."""
        try:
            docker_container: Container = self.containers.get(name)
        except NotFound:
            raise DockerNotFound() from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # Execute
        try:
            code, output = docker_container.exec_run(command)
        except (DockerException, requests.RequestException) as err:
            raise DockerError() from err

        return CommandReturn(code, output)

    def remove_image(
        self, image: str, version: AwesomeVersion, latest: bool = True
    ) -> None:
        """Remove a Docker image by version and latest."""
        try:
            if latest:
                _LOGGER.info("Removing image %s with latest", image)
                with suppress(ImageNotFound):
                    self.images.remove(image=f"{image}:latest", force=True)

            _LOGGER.info("Removing image %s with %s", image, version)
            with suppress(ImageNotFound):
                self.images.remove(image=f"{image}:{version!s}", force=True)

        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't remove image {image}: {err}", _LOGGER.warning
            ) from err

    def import_image(self, tar_file: Path) -> Image | None:
        """Import a tar file as image."""
        try:
            with tar_file.open("rb") as read_tar:
                docker_image_list: list[Image] = self.images.load(read_tar)  # type: ignore

            if len(docker_image_list) != 1:
                _LOGGER.warning(
                    "Unexpected image count %d while importing image from tar",
                    len(docker_image_list),
                )
                return None
            return docker_image_list[0]
        except (DockerException, OSError) as err:
            raise DockerError(
                f"Can't import image from tar: {err}", _LOGGER.error
            ) from err

    def export_image(self, image: str, version: AwesomeVersion, tar_file: Path) -> None:
        """Export current images into a tar file."""
        try:
            docker_image = self.api.get_image(f"{image}:{version}")
        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't fetch image {image}: {err}", _LOGGER.error
            ) from err

        _LOGGER.info("Export image %s to %s", image, tar_file)
        try:
            with tar_file.open("wb") as write_tar:
                for chunk in docker_image:
                    write_tar.write(chunk)
        except (OSError, requests.RequestException) as err:
            raise DockerError(
                f"Can't write tar file {tar_file}: {err}", _LOGGER.error
            ) from err

        _LOGGER.info("Export image %s done", image)

    def cleanup_old_images(
        self,
        current_image: str,
        current_version: AwesomeVersion,
        old_images: set[str] | None = None,
        *,
        keep_images: set[str] | None = None,
    ) -> None:
        """Clean up old versions of an image."""
        image = f"{current_image}:{current_version!s}"
        try:
            keep = {cast(str, self.images.get(image).id)}
        except ImageNotFound:
            raise DockerNotFound(
                f"{current_image} not found for cleanup", _LOGGER.warning
            ) from None
        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't get {current_image} for cleanup", _LOGGER.warning
            ) from err

        if keep_images:
            keep_images -= {image}
            try:
                for image in keep_images:
                    # If its not found, no need to preserve it from getting removed
                    with suppress(ImageNotFound):
                        keep.add(cast(str, self.images.get(image).id))
            except (DockerException, requests.RequestException) as err:
                raise DockerError(
                    f"Failed to get one or more images from {keep} during cleanup",
                    _LOGGER.warning,
                ) from err

        # Cleanup old and current
        image_names = list(
            old_images | {current_image} if old_images else {current_image}
        )
        try:
            # This API accepts a list of image names. Tested and confirmed working on docker==7.1.0
            # Its typing does say only `str` though. Bit concerning, could an update break this?
            images_list = self.images.list(name=image_names)  # type: ignore
        except (DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Corrupt docker overlayfs found: {err}", _LOGGER.warning
            ) from err

        for docker_image in images_list:
            if docker_image.id in keep:
                continue

            with suppress(DockerException, requests.RequestException):
                _LOGGER.info("Cleanup images: %s", docker_image.tags)
                self.images.remove(docker_image.id, force=True)
