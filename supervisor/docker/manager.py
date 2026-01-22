"""Manager for Supervisor Docker."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from http import HTTPStatus
from ipaddress import IPv4Address
import json
import logging
import os
from pathlib import Path, PurePath
import re
from typing import Any, Final, Literal, Self, cast

import aiodocker
from aiodocker.containers import DockerContainer, DockerContainers
from aiodocker.images import DockerImages
from aiodocker.types import JSONObject
from aiohttp import ClientSession, ClientTimeout, UnixConnector
import attr
from awesomeversion import AwesomeVersion, AwesomeVersionCompareException
from docker import errors as docker_errors
from docker.api.client import APIClient
from docker.client import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network
from docker.types.daemon import CancellableStream
import requests

from ..const import (
    ATTR_ENABLE_IPV6,
    ATTR_MTU,
    ATTR_REGISTRIES,
    DNS_SUFFIX,
    DOCKER_NETWORK,
    ENV_SUPERVISOR_CPU_RT,
    FILE_HASSIO_DOCKER,
    SOCKET_DOCKER,
    BusEvent,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    DockerAPIError,
    DockerError,
    DockerNoSpaceOnDevice,
    DockerNotFound,
    DockerRequestError,
)
from ..utils.common import FileConfiguration
from ..validate import SCHEMA_DOCKER_CONFIG
from .const import (
    DOCKER_HUB,
    DOCKER_HUB_LEGACY,
    LABEL_MANAGED,
    Capabilities,
    DockerMount,
    MountType,
    RestartPolicy,
    Ulimit,
)
from .monitor import DockerMonitor
from .network import DockerNetwork
from .utils import get_registry_from_image

_LOGGER: logging.Logger = logging.getLogger(__name__)

MIN_SUPPORTED_DOCKER: Final = AwesomeVersion("24.0.0")
DOCKER_NETWORK_HOST: Final = "host"
RE_IMPORT_IMAGE_STREAM = re.compile(r"(^Loaded image ID: |^Loaded image: )(.+)$")


@dataclass(slots=True, frozen=True)
class ExecReturn:
    """Return object from exec run."""

    exit_code: int
    output: bytes


@dataclass(slots=True, frozen=True)
class CommandReturn:
    """Return object from command run."""

    exit_code: int
    log: list[str]


@attr.s(frozen=True)
class DockerInfo:
    """Return docker information."""

    version: AwesomeVersion = attr.ib()
    storage: str = attr.ib()
    logging: str = attr.ib()
    cgroup: str = attr.ib()
    support_cpu_realtime: bool = attr.ib()

    @staticmethod
    async def new(data: dict[str, Any]) -> DockerInfo:
        """Create a object from docker info."""
        # Check if CONFIG_RT_GROUP_SCHED is loaded (blocking I/O in executor)
        cpu_rt_file_exists = await asyncio.get_running_loop().run_in_executor(
            None, Path("/sys/fs/cgroup/cpu/cpu.rt_runtime_us").exists
        )
        cpu_rt_supported = (
            cpu_rt_file_exists and os.environ.get(ENV_SUPERVISOR_CPU_RT) == "1"
        )

        return DockerInfo(
            AwesomeVersion(data.get("ServerVersion", "0.0.0")),
            data.get("Driver", "unknown"),
            data.get("LoggingDriver", "unknown"),
            data.get("CgroupVersion", "1"),
            cpu_rt_supported,
        )

    @property
    def supported_version(self) -> bool:
        """Return true, if docker version is supported."""
        try:
            return self.version >= MIN_SUPPORTED_DOCKER
        except AwesomeVersionCompareException:
            return False


@dataclass(frozen=True, slots=True)
class PullProgressDetail:
    """Progress detail information for pull.

    Documentation lacking but both of these seem to be in bytes when populated.

    Containerd-snapshot update - When leveraging this new feature, this information
    becomes useless to us while extracting. It simply tells elapsed time using
    current and units.
    """

    current: int | None = None
    total: int | None = None
    units: str | None = None

    @classmethod
    def from_pull_log_dict(cls, value: dict[str, int]) -> PullProgressDetail:
        """Convert pull progress log dictionary into instance."""
        return cls(current=value.get("current"), total=value.get("total"))


@dataclass(frozen=True, slots=True)
class PullLogEntry:
    """Details for a entry in pull log.

    Not seeing documentation on this structure. Notes from exploration:
    1. All entries have status except errors
    2. Nearly all (but not all) entries have an id
    3. Most entries have progress but it may be empty string and dictionary
    4. Status is not an enum. It includes dynamic data like the image name
    5. Progress is what you see in the CLI. It's for humans, progressDetail is for machines

    Omitted field - errorDetail. It seems to be a dictionary with one field "message" that
    exactly matches "error". As that is redundant, skipping for now.
    """

    job_id: str  # Not part of the docker object. Used to link  log entries to supervisor jobs
    id: str | None = None
    status: str | None = None
    progress: str | None = None
    progress_detail: PullProgressDetail | None = None
    error: str | None = None

    @classmethod
    def from_pull_log_dict(cls, job_id: str, value: dict[str, Any]) -> PullLogEntry:
        """Convert pull progress log dictionary into instance."""
        return cls(
            job_id=job_id,
            id=value.get("id"),
            status=value.get("status"),
            progress=value.get("progress"),
            progress_detail=PullProgressDetail.from_pull_log_dict(
                value["progressDetail"]
            )
            if "progressDetail" in value
            else None,
            error=value.get("error"),
        )

    @property
    def exception(self) -> DockerError:
        """Converts error message into a raisable exception. Raises RuntimeError if there is no error."""
        if not self.error:
            raise RuntimeError("No error to convert to exception!")
        if self.error.endswith("no space left on device"):
            return DockerNoSpaceOnDevice(_LOGGER.error)
        return DockerError(self.error, _LOGGER.error)


class DockerConfig(FileConfiguration):
    """Home Assistant core object for Docker configuration."""

    def __init__(self):
        """Initialize the JSON configuration."""
        super().__init__(FILE_HASSIO_DOCKER, SCHEMA_DOCKER_CONFIG)

    @property
    def enable_ipv6(self) -> bool | None:
        """Return IPv6 configuration for docker network."""
        return self._data.get(ATTR_ENABLE_IPV6, None)

    @enable_ipv6.setter
    def enable_ipv6(self, value: bool | None) -> None:
        """Set IPv6 configuration for docker network."""
        self._data[ATTR_ENABLE_IPV6] = value

    @property
    def mtu(self) -> int | None:
        """Return MTU configuration for docker network."""
        return self._data.get(ATTR_MTU)

    @mtu.setter
    def mtu(self, value: int | None) -> None:
        """Set MTU configuration for docker network."""
        self._data[ATTR_MTU] = value

    @property
    def registries(self) -> dict[str, Any]:
        """Return credentials for docker registries."""
        return self._data.get(ATTR_REGISTRIES, {})

    def get_registry_for_image(self, image: str) -> str | None:
        """Return the registry name if credentials are available for the image.

        Matches the image against configured registries and returns the registry
        name if found, or None if no matching credentials are configured.

        Uses Docker's domain detection logic from:
        vendor/github.com/distribution/reference/normalize.go
        """
        if not self.registries:
            return None

        # Check if image uses a custom registry (e.g., ghcr.io/org/image)
        registry = get_registry_from_image(image)
        if registry:
            if registry in self.registries:
                return registry
        else:
            # No registry prefix means Docker Hub
            # Support both docker.io (official) and hub.docker.com (legacy)
            if DOCKER_HUB in self.registries:
                return DOCKER_HUB
            if DOCKER_HUB_LEGACY in self.registries:
                return DOCKER_HUB_LEGACY

        return None


class DockerAPI(CoreSysAttributes):
    """Docker Supervisor wrapper.

    This class is not AsyncIO safe!
    """

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys = coresys
        # We keep both until we can fully refactor to aiodocker
        self._dockerpy: DockerClient | None = None
        self.docker: aiodocker.Docker = aiodocker.Docker(
            url="unix://localhost",  # dummy hostname for URL composition
            connector=(connector := UnixConnector(SOCKET_DOCKER.as_posix())),
            session=ClientSession(connector=connector, timeout=ClientTimeout(900)),
            api_version="auto",
        )

        self._network: DockerNetwork | None = None
        self._info: DockerInfo | None = None
        self.config: DockerConfig = DockerConfig()
        self._monitor: DockerMonitor = DockerMonitor(coresys)

    async def post_init(self) -> Self:
        """Post init actions that must be done in event loop."""
        self._dockerpy = await asyncio.get_running_loop().run_in_executor(
            None,
            partial(
                DockerClient,
                base_url=f"unix:/{SOCKET_DOCKER.as_posix()}",
                version="auto",
                timeout=900,
            ),
        )
        self._info = await DockerInfo.new(self.dockerpy.info())
        await self.config.read_data()
        self._network = await DockerNetwork(self.dockerpy).post_init(
            self.config.enable_ipv6, self.config.mtu
        )
        return self

    @property
    def dockerpy(self) -> DockerClient:
        """Get docker API client."""
        if not self._dockerpy:
            raise RuntimeError("Docker API Client not initialized!")
        return self._dockerpy

    @property
    def network(self) -> DockerNetwork:
        """Get Docker network."""
        if not self._network:
            raise RuntimeError("Docker Network not initialized!")
        return self._network

    @property
    def images(self) -> DockerImages:
        """Return API images."""
        return self.docker.images

    @property
    def containers(self) -> DockerContainers:
        """Return API containers."""
        return self.docker.containers

    @property
    def api(self) -> APIClient:
        """Return API containers."""
        return self.dockerpy.api

    @property
    def info(self) -> DockerInfo:
        """Return local docker info."""
        if not self._info:
            raise RuntimeError("Docker Info not initialized!")
        return self._info

    @property
    def events(self) -> CancellableStream:
        """Return docker event stream."""
        return self.dockerpy.events(decode=True)

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

    def _create_container_config(
        self,
        image: str,
        *,
        tag: str = "latest",
        dns: bool = True,
        init: bool = False,
        hostname: str | None = None,
        detach: bool = True,
        security_opt: list[str] | None = None,
        restart_policy: dict[str, RestartPolicy] | None = None,
        extra_hosts: dict[str, IPv4Address] | None = None,
        environment: dict[str, str | None] | None = None,
        mounts: list[DockerMount] | None = None,
        ports: dict[str, str | int | None] | None = None,
        oom_score_adj: int | None = None,
        network_mode: str | None = None,
        privileged: bool = False,
        device_cgroup_rules: list[str] | None = None,
        tmpfs: dict[str, str] | None = None,
        entrypoint: list[str] | None = None,
        cap_add: list[Capabilities] | None = None,
        ulimits: list[Ulimit] | None = None,
        cpu_rt_runtime: int | None = None,
        stdin_open: bool = False,
        pid_mode: str | None = None,
        uts_mode: str | None = None,
        command: list[str] | None = None,
        networking_config: dict[str, Any] | None = None,
        working_dir: PurePath | None = None,
    ) -> JSONObject:
        """Map kwargs to create container config.

        This only covers the docker options we currently use. It is not intended
        to be exhaustive as its dockerpy equivalent was. We'll add to it as we
        make use of new feature.
        """
        # Set up host dependent config for container
        host_config: dict[str, Any] = {
            "NetworkMode": network_mode if network_mode else "default",
            "Init": init,
            "Privileged": privileged,
        }
        if security_opt:
            host_config["SecurityOpt"] = security_opt
        if restart_policy:
            host_config["RestartPolicy"] = restart_policy
        if extra_hosts:
            host_config["ExtraHosts"] = [f"{k}:{v}" for k, v in extra_hosts.items()]
        if mounts:
            host_config["Mounts"] = [mount.to_dict() for mount in mounts]
        if oom_score_adj is not None:
            host_config["OomScoreAdj"] = oom_score_adj
        if device_cgroup_rules:
            host_config["DeviceCgroupRules"] = device_cgroup_rules
        if tmpfs:
            host_config["Tmpfs"] = tmpfs
        if cap_add:
            host_config["CapAdd"] = cap_add
        if cpu_rt_runtime is not None:
            host_config["CPURealtimeRuntime"] = cpu_rt_runtime
        if pid_mode:
            host_config["PidMode"] = pid_mode
        if uts_mode:
            host_config["UtsMode"] = uts_mode
        if ulimits:
            host_config["Ulimits"] = [limit.to_dict() for limit in ulimits]

        # Full container config
        config: dict[str, Any] = {
            "Image": f"{image}:{tag}",
            "Labels": {LABEL_MANAGED: ""},
            "OpenStdin": stdin_open,
            "StdinOnce": not detach and stdin_open,
            "AttachStdin": not detach and stdin_open,
            "AttachStdout": not detach,
            "AttachStderr": not detach,
            "HostConfig": host_config,
        }
        if hostname:
            config["Hostname"] = hostname
        if environment:
            config["Env"] = [
                env if val is None else f"{env}={val}"
                for env, val in environment.items()
            ]
        if entrypoint:
            config["Entrypoint"] = entrypoint
        if command:
            config["Cmd"] = command
        if networking_config:
            config["NetworkingConfig"] = networking_config
        if working_dir:
            config["WorkingDir"] = working_dir.as_posix()

        # Set up networking
        if dns:
            host_config["Dns"] = [str(self.network.dns)]
            host_config["DnsSearch"] = [DNS_SUFFIX]
            # CoreDNS forward plug-in fails in ~6s, then fallback triggers.
            # However, the default timeout of glibc and musl is 5s. Increase
            # default timeout to make sure CoreDNS fallback is working
            # on first query.
            host_config["DnsOptions"] = ["timeout:10"]
            if hostname:
                config["Domainname"] = DNS_SUFFIX

        # Setup ports
        if ports:
            port_bindings = {
                port if "/" in port else f"{port}/tcp": [
                    {"HostIp": "", "HostPort": str(host_port) if host_port else ""}
                ]
                for port, host_port in ports.items()
            }
            config["ExposedPorts"] = {port: {} for port in port_bindings}
            host_config["PortBindings"] = port_bindings

        return config

    async def _run(
        self,
        image: str,
        *,
        name: str | None = None,
        tag: str = "latest",
        hostname: str | None = None,
        mounts: list[DockerMount] | None = None,
        network_mode: str | None = None,
        networking_config: dict[str, Any] | None = None,
        ipv4: IPv4Address | None = None,
        skip_cidfile: bool = False,
        **kwargs,
    ) -> DockerContainer:
        """Create a Docker container and run it."""
        if not image or not tag:
            raise ValueError("image and tag cannot be an empty string!")

        cidfile_path: Path | None = None
        if name and not skip_cidfile:
            # Setup cidfile and bind mount it
            cidfile_path = self.coresys.config.path_cid_files / f"{name}.cid"

            def create_cidfile() -> None:
                # Remove the file/directory if it exists e.g. as a leftover from unclean shutdown
                # Note: Can be a directory if Docker auto-started container with restart policy
                # before Supervisor could write the CID file
                with suppress(OSError):
                    if cidfile_path.is_dir():
                        cidfile_path.rmdir()
                    elif cidfile_path.is_file():
                        cidfile_path.unlink(missing_ok=True)

                # Create empty CID file before adding it to volumes to prevent Docker
                # from creating it as a directory if container auto-starts
                cidfile_path.touch()

            await self.sys_run_in_executor(create_cidfile)

            # Bind mount to /run/cid in container
            extern_cidfile_path = (
                self.coresys.config.path_extern_cid_files / f"{name}.cid"
            )
            cid_mount = DockerMount(
                type=MountType.BIND,
                source=extern_cidfile_path.as_posix(),
                target="/run/cid",
                read_only=True,
            )
            if mounts is None:
                mounts = [cid_mount]
            else:
                mounts = [*mounts, cid_mount]

        # Create container
        config = self._create_container_config(
            image,
            tag=tag,
            hostname=hostname,
            mounts=mounts,
            network_mode=network_mode,
            **kwargs,
        )
        try:
            container = await self.containers.create(config, name=name)
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                raise DockerNotFound(
                    f"Image {image}:{tag} does not exist", _LOGGER.error
                ) from err
            raise DockerAPIError(
                f"Can't create container from {image}:{tag}: {err}", _LOGGER.error
            ) from err

        # Store container id in cidfile
        def setup_cidfile(cidfile_path: Path) -> None:
            # Write cidfile
            with cidfile_path.open("w", encoding="ascii") as cidfile:
                cidfile.write(str(container.id))

        if cidfile_path:
            await self.sys_run_in_executor(setup_cidfile, cidfile_path)

        # Setup network
        def setup_network(network_mode: Literal["host"] | None) -> None:
            # Attach network
            if network_mode:
                alias = [hostname] if hostname else None
                try:
                    self.network.attach_container(
                        container.id, name, alias=alias, ipv4=ipv4
                    )
                except DockerError:
                    _LOGGER.warning(
                        "Can't attach %s to hassio-network!", name or container.id
                    )
                else:
                    with suppress(DockerError):
                        self.network.detach_default_bridge(container.id, name)
            else:
                host_network: Network = self.dockerpy.networks.get(DOCKER_NETWORK_HOST)

                # Check if container is register on host
                # https://github.com/moby/moby/issues/23302
                if name and name in (
                    val.get("Name")
                    for val in host_network.attrs.get("Containers", {}).values()
                ):
                    with suppress(docker_errors.NotFound):
                        host_network.disconnect(name, force=True)

        if not networking_config and network_mode in ("host", None):
            await self.sys_run_in_executor(setup_network, network_mode)

        # Run container
        try:
            await container.start()
        except aiodocker.DockerError as err:
            raise DockerAPIError(
                f"Can't start {name or container.id}: {err}", _LOGGER.error
            ) from err

        return container

    async def run(
        self, image: str, *, name: str, tag: str = "latest", **kwargs
    ) -> dict[str, Any]:
        """Create and run a container from provided config, returning its inspect metadata."""
        container = await self._run(image, name=name, tag=tag, **kwargs)

        # Get container metadata after the container is started
        try:
            container_attrs = await container.show()
        except aiodocker.DockerError as err:
            raise DockerAPIError(
                f"Can't inspect started container {name}: {err}", _LOGGER.error
            ) from err
        except requests.RequestException as err:
            raise DockerRequestError(
                f"Dockerd connection issue for {name}: {err}", _LOGGER.error
            ) from err

        return container_attrs

    async def run_command(
        self,
        image: str,
        command: list[str],
        tag: str = "latest",
        stdout: bool = True,
        stderr: bool = True,
        **kwargs: Any,
    ) -> CommandReturn:
        """Create a temporary container and run command, returning its output."""
        _LOGGER.info("Runing command '%s' on %s:%s", command, image, tag)
        container: DockerContainer | None = None
        try:
            container = await self._run(
                image,
                tag=tag,
                command=command,
                detach=True,
                network_mode=self.network.name,
                networking_config={self.network.name: None},
                skip_cidfile=True,
                **kwargs,
            )

            # wait until command is done
            result = await container.wait()
            log = await container.log(stdout=stdout, stderr=stderr, follow=False)

        except (DockerError, aiodocker.DockerError) as err:
            raise DockerError(f"Can't execute command: {err}", _LOGGER.error) from err

        finally:
            # cleanup container
            if container:
                with suppress(aiodocker.DockerError):
                    await container.delete(force=True, v=True)

        return CommandReturn(result["StatusCode"], log)

    async def pull_image(
        self,
        job_id: str,
        repository: str,
        tag: str = "latest",
        platform: str | None = None,
        auth: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Pull the specified image and return it.

        This mimics the high level API of images.pull but provides better error handling by raising
        based on a docker error on pull. Whereas the high level API ignores all errors on pull and
        raises only if the get fails afterwards. Additionally it fires progress reports for the pull
        on the bus so listeners can use that to update status for users.
        """
        # Use timeout=None to disable timeout for pull operations, matching docker-py behavior.
        # aiodocker converts None to ClientTimeout(total=None) which disables the timeout.
        async for e in self.images.pull(
            repository, tag=tag, platform=platform, auth=auth, stream=True, timeout=None
        ):
            entry = PullLogEntry.from_pull_log_dict(job_id, e)
            if entry.error:
                raise entry.exception
            await asyncio.gather(
                *self.sys_bus.fire_event(BusEvent.DOCKER_IMAGE_PULL_UPDATE, entry)
            )

        sep = "@" if tag.startswith("sha256:") else ":"
        return await self.images.inspect(f"{repository}{sep}{tag}")

    async def repair(self) -> None:
        """Repair local docker overlayfs2 issues."""

        def repair_docker_blocking():
            _LOGGER.info("Prune stale containers")
            try:
                output = self.dockerpy.api.prune_containers()
                _LOGGER.debug("Containers prune: %s", output)
            except docker_errors.APIError as err:
                _LOGGER.warning("Error for containers prune: %s", err)

            _LOGGER.info("Prune stale images")
            try:
                output = self.dockerpy.api.prune_images(filters={"dangling": False})
                _LOGGER.debug("Images prune: %s", output)
            except docker_errors.APIError as err:
                _LOGGER.warning("Error for images prune: %s", err)

            _LOGGER.info("Prune stale builds")
            try:
                output = self.dockerpy.api.prune_builds()
                _LOGGER.debug("Builds prune: %s", output)
            except docker_errors.APIError as err:
                _LOGGER.warning("Error for builds prune: %s", err)

            _LOGGER.info("Prune stale volumes")
            try:
                output = self.dockerpy.api.prune_volumes()
                _LOGGER.debug("Volumes prune: %s", output)
            except docker_errors.APIError as err:
                _LOGGER.warning("Error for volumes prune: %s", err)

            _LOGGER.info("Prune stale networks")
            try:
                output = self.dockerpy.api.prune_networks()
                _LOGGER.debug("Networks prune: %s", output)
            except docker_errors.APIError as err:
                _LOGGER.warning("Error for networks prune: %s", err)

        await self.sys_run_in_executor(repair_docker_blocking)

        _LOGGER.info("Fix stale container on hassio network")
        try:
            await self.prune_networks(DOCKER_NETWORK)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for networks hassio prune: %s", err)

        _LOGGER.info("Fix stale container on host network")
        try:
            await self.prune_networks(DOCKER_NETWORK_HOST)
        except docker_errors.APIError as err:
            _LOGGER.warning("Error for networks host prune: %s", err)

    async def prune_networks(self, network_name: str) -> None:
        """Prune stale container from network.

        Fix: https://github.com/moby/moby/issues/23302
        """
        network: Network = await self.sys_run_in_executor(
            self.dockerpy.networks.get, network_name
        )
        corrupt_containers: list[str] = []

        for cid, data in network.attrs.get("Containers", {}).items():
            try:
                await self.containers.get(cid)
                continue
            except aiodocker.DockerError as err:
                if err.status != HTTPStatus.NOT_FOUND:
                    _LOGGER.warning(
                        "Docker fatal error on container %s on %s: %s",
                        cid,
                        network_name,
                        err,
                    )
                    continue

                _LOGGER.debug(
                    "Docker network %s is corrupt on container: %s", network_name, cid
                )
                corrupt_containers.append(data.get("Name", cid))

        def disconnect_corrupt_containers():
            for name in corrupt_containers:
                with suppress(docker_errors.DockerException, requests.RequestException):
                    network.disconnect(name, force=True)

        await self.sys_run_in_executor(disconnect_corrupt_containers)

    async def container_is_initialized(
        self, name: str, image: str, version: AwesomeVersion
    ) -> bool:
        """Return True if docker container exists in good state and is built from expected image."""
        try:
            docker_container = await self.containers.get(name)
            container_metadata = await docker_container.show()
            docker_image = await self.images.inspect(f"{image}:{version}")
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                return False
            raise DockerError(
                f"Could not get container {name} or image {image}:{version} to check state: {err!s}",
                _LOGGER.error,
            ) from err

        # Check the image is correct and state is good
        metadata_image = container_metadata.get("ImageID", container_metadata["Image"])
        status = container_metadata["State"]["Status"]
        return metadata_image == docker_image["Id"] and status in (
            "exited",
            "running",
            "created",
        )

    async def stop_container(
        self, name: str, timeout: int, remove_container: bool = True
    ) -> None:
        """Stop/remove Docker container."""
        try:
            docker_container = await self.containers.get(name)
            container_metadata = await docker_container.show()
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                # Generally suppressed so we don't log this
                raise DockerNotFound() from None
            raise DockerError(
                f"Could not get container {name} for stopping: {err!s}",
                _LOGGER.error,
            ) from err

        if container_metadata["State"]["Status"] == "running":
            _LOGGER.info("Stopping %s application", name)
            with suppress(aiodocker.DockerError):
                await docker_container.stop(timeout=timeout)

        if remove_container:
            with suppress(aiodocker.DockerError):
                _LOGGER.info("Cleaning %s application", name)
                await docker_container.delete(force=True, v=True)

            cidfile_path = self.coresys.config.path_cid_files / f"{name}.cid"
            with suppress(OSError):
                await self.sys_run_in_executor(cidfile_path.unlink, missing_ok=True)

    async def start_container(self, name: str) -> None:
        """Start Docker container."""
        try:
            docker_container = await self.containers.get(name)
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                raise DockerNotFound(
                    f"{name} not found for starting up", _LOGGER.error
                ) from None
            raise DockerError(
                f"Could not get {name} for starting up", _LOGGER.error
            ) from err

        _LOGGER.info("Starting %s", name)
        try:
            await docker_container.start()
        except aiodocker.DockerError as err:
            raise DockerError(f"Can't start {name}: {err}", _LOGGER.error) from err

    async def restart_container(self, name: str, timeout: int) -> None:
        """Restart docker container."""
        try:
            container = await self.containers.get(name)
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                raise DockerNotFound(
                    f"Container {name} not found for restarting", _LOGGER.warning
                ) from None
            raise DockerError(
                f"Could not get container {name} for restarting: {err!s}", _LOGGER.error
            ) from err

        _LOGGER.info("Restarting %s", name)
        try:
            await container.restart(timeout=timeout)
        except aiodocker.DockerError as err:
            raise DockerError(f"Can't restart {name}: {err}", _LOGGER.warning) from err

    def container_logs(self, name: str, tail: int = 100) -> bytes:
        """Return Docker logs of container.

        Must be run in executor.
        """
        # Remains on docker py for now because aiodocker doesn't seem to have a way to get
        # the raw binary of the logs. Only provides list[str] or AsyncIterator[str] options.
        try:
            docker_container: Container = self.dockerpy.containers.get(name)
        except docker_errors.NotFound:
            raise DockerNotFound(
                f"Container {name} not found for logs", _LOGGER.warning
            ) from None
        except (docker_errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Could not get container {name} for logs: {err!s}", _LOGGER.error
            ) from err

        try:
            return docker_container.logs(tail=tail, stdout=True, stderr=True)
        except (docker_errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't grep logs from {name}: {err}", _LOGGER.warning
            ) from err

    async def container_stats(self, name: str) -> dict[str, Any]:
        """Read and return stats from container."""
        try:
            docker_container = await self.containers.get(name)
            container_metadata = await docker_container.show()
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                raise DockerNotFound(
                    f"Container {name} not found for stats", _LOGGER.warning
                ) from None
            raise DockerError(
                f"Could not inspect container '{name}': {err!s}", _LOGGER.error
            ) from err

        # container is not running
        if container_metadata["State"]["Status"] != "running":
            raise DockerError(f"Container {name} is not running", _LOGGER.error)

        try:
            stats = await docker_container.stats(stream=False)
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't read stats from {name}: {err}", _LOGGER.error
            ) from err

        if not stats:
            raise DockerError(f"Could not get stats for {name}", _LOGGER.error)
        return stats[-1]

    async def container_run_inside(self, name: str, command: str) -> ExecReturn:
        """Execute a command inside Docker container."""
        try:
            docker_container = await self.containers.get(name)
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                raise DockerNotFound(
                    f"Container {name} not found for running command", _LOGGER.warning
                ) from None
            raise DockerError(
                f"Can't get container {name} to run command: {err!s}"
            ) from err

        # Execute
        try:
            docker_exec = await docker_container.exec(command)
            output = await docker_exec.start(detach=True)
            exec_metadata = await docker_exec.inspect()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't run command in container {name}: {err!s}"
            ) from err

        return ExecReturn(exec_metadata["ExitCode"], output)

    async def remove_image(
        self, image: str, version: AwesomeVersion, latest: bool = True
    ) -> None:
        """Remove a Docker image by version and latest."""
        try:
            if latest:
                _LOGGER.info("Removing image %s with latest", image)
                try:
                    await self.images.delete(f"{image}:latest", force=True)
                except aiodocker.DockerError as err:
                    if err.status != HTTPStatus.NOT_FOUND:
                        raise

            _LOGGER.info("Removing image %s with %s", image, version)
            try:
                await self.images.delete(f"{image}:{version!s}", force=True)
            except aiodocker.DockerError as err:
                if err.status != HTTPStatus.NOT_FOUND:
                    raise

        except (aiodocker.DockerError, requests.RequestException) as err:
            raise DockerError(
                f"Can't remove image {image}: {err}", _LOGGER.warning
            ) from err

    async def import_image(self, tar_file: Path) -> dict[str, Any] | None:
        """Import a tar file as image."""
        try:
            with tar_file.open("rb") as read_tar:
                resp: list[dict[str, Any]] = await self.images.import_image(read_tar)
        except (aiodocker.DockerError, OSError) as err:
            raise DockerError(
                f"Can't import image from tar: {err}", _LOGGER.error
            ) from err

        docker_image_list: list[str] = []
        for chunk in resp:
            if "errorDetail" in chunk:
                raise DockerError(
                    f"Can't import image from tar: {chunk['errorDetail']['message']}",
                    _LOGGER.error,
                )
            if "stream" in chunk:
                if match := RE_IMPORT_IMAGE_STREAM.search(chunk["stream"]):
                    docker_image_list.append(match.group(2))

        if len(docker_image_list) != 1:
            _LOGGER.warning(
                "Unexpected image count %d while importing image from tar",
                len(docker_image_list),
            )
            return None

        try:
            return await self.images.inspect(docker_image_list[0])
        except (aiodocker.DockerError, requests.RequestException) as err:
            raise DockerError(
                f"Could not inspect imported image due to: {err!s}", _LOGGER.error
            ) from err

    def export_image(self, image: str, version: AwesomeVersion, tar_file: Path) -> None:
        """Export current images into a tar file."""
        try:
            docker_image = self.api.get_image(f"{image}:{version}")
        except (docker_errors.DockerException, requests.RequestException) as err:
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

    async def cleanup_old_images(
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
            try:
                image_attr = await self.images.inspect(image)
            except aiodocker.DockerError as err:
                if err.status == HTTPStatus.NOT_FOUND:
                    raise DockerNotFound(
                        f"{current_image} not found for cleanup", _LOGGER.warning
                    ) from None
                raise
        except (aiodocker.DockerError, requests.RequestException) as err:
            raise DockerError(
                f"Can't get {current_image} for cleanup", _LOGGER.warning
            ) from err
        keep = {cast(str, image_attr["Id"])}

        if keep_images:
            keep_images -= {image}
            results = await asyncio.gather(
                *[self.images.inspect(image) for image in keep_images],
                return_exceptions=True,
            )
            for result in results:
                # If its not found, no need to preserve it from getting removed
                if (
                    isinstance(result, aiodocker.DockerError)
                    and result.status == HTTPStatus.NOT_FOUND
                ):
                    continue
                if isinstance(result, BaseException):
                    raise DockerError(
                        f"Failed to get one or more images from {keep} during cleanup",
                        _LOGGER.warning,
                    ) from result
                keep.add(cast(str, result["Id"]))

        # Cleanup old and current
        image_names = list(
            old_images | {current_image} if old_images else {current_image}
        )
        try:
            images_list = await self.images.list(
                filters=json.dumps({"reference": image_names})
            )
        except (aiodocker.DockerError, requests.RequestException) as err:
            raise DockerError(
                f"Corrupt docker overlayfs found: {err}", _LOGGER.warning
            ) from err

        for docker_image in images_list:
            if docker_image["Id"] in keep:
                continue

            with suppress(aiodocker.DockerError, requests.RequestException):
                _LOGGER.info("Cleanup images: %s", docker_image["RepoTags"])
                await self.images.delete(docker_image["Id"], force=True)
