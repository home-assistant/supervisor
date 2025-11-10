"""Supervisor add-on build environment."""

from __future__ import annotations

import base64
from functools import cached_property
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from awesomeversion import AwesomeVersion

from ..const import (
    ATTR_ARGS,
    ATTR_BUILD_FROM,
    ATTR_LABELS,
    ATTR_PASSWORD,
    ATTR_SQUASH,
    ATTR_USERNAME,
    FILE_SUFFIX_CONFIGURATION,
    META_ADDON,
    SOCKET_DOCKER,
    CpuArch,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.const import DOCKER_HUB, DOCKER_HUB_LEGACY
from ..docker.interface import MAP_ARCH
from ..exceptions import (
    AddonBuildArchitectureNotSupportedError,
    AddonBuildDockerfileMissingError,
    ConfigurationFileError,
    HassioArchNotFound,
)
from ..utils.common import FileConfiguration, find_one_filetype
from .validate import SCHEMA_BUILD_CONFIG

if TYPE_CHECKING:
    from .manager import AnyAddon

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AddonBuild(FileConfiguration, CoreSysAttributes):
    """Handle build options for add-ons."""

    def __init__(self, coresys: CoreSys, addon: AnyAddon) -> None:
        """Initialize Supervisor add-on builder."""
        self.coresys: CoreSys = coresys
        self.addon = addon

        # Search for build file later in executor
        super().__init__(None, SCHEMA_BUILD_CONFIG)

    def _get_build_file(self) -> Path:
        """Get build file.

        Must be run in executor.
        """
        try:
            return find_one_filetype(
                self.addon.path_location, "build", FILE_SUFFIX_CONFIGURATION
            )
        except ConfigurationFileError:
            return self.addon.path_location / "build.json"

    async def read_data(self) -> None:
        """Load data from file."""
        if not self._file:
            self._file = await self.sys_run_in_executor(self._get_build_file)

        await super().read_data()

    async def save_data(self):
        """Ignore save function."""
        raise RuntimeError()

    @cached_property
    def arch(self) -> CpuArch:
        """Return arch of the add-on."""
        return self.sys_arch.match([self.addon.arch])

    @property
    def base_image(self) -> str:
        """Return base image for this add-on."""
        if not self._data[ATTR_BUILD_FROM]:
            return f"ghcr.io/home-assistant/{self.sys_arch.default}-base:latest"

        if isinstance(self._data[ATTR_BUILD_FROM], str):
            return self._data[ATTR_BUILD_FROM]

        # Evaluate correct base image
        if self.arch not in self._data[ATTR_BUILD_FROM]:
            raise HassioArchNotFound(
                f"Add-on {self.addon.slug} is not supported on {self.arch}"
            )
        return self._data[ATTR_BUILD_FROM][self.arch]

    @property
    def squash(self) -> bool:
        """Return True or False if squash is active."""
        return self._data[ATTR_SQUASH]

    @property
    def additional_args(self) -> dict[str, str]:
        """Return additional Docker build arguments."""
        return self._data[ATTR_ARGS]

    @property
    def additional_labels(self) -> dict[str, str]:
        """Return additional Docker labels."""
        return self._data[ATTR_LABELS]

    def get_dockerfile(self) -> Path:
        """Return Dockerfile path.

        Must be run in executor.
        """
        if self.addon.path_location.joinpath(f"Dockerfile.{self.arch}").exists():
            return self.addon.path_location.joinpath(f"Dockerfile.{self.arch}")
        return self.addon.path_location.joinpath("Dockerfile")

    async def is_valid(self) -> None:
        """Return true if the build env is valid."""

        def build_is_valid() -> bool:
            return all(
                [
                    self.addon.path_location.is_dir(),
                    self.get_dockerfile().is_file(),
                ]
            )

        try:
            if not await self.sys_run_in_executor(build_is_valid):
                raise AddonBuildDockerfileMissingError(
                    _LOGGER.error, addon=self.addon.slug
                )
        except HassioArchNotFound:
            raise AddonBuildArchitectureNotSupportedError(
                _LOGGER.error,
                addon=self.addon.slug,
                addon_arch_list=self.addon.supported_arch,
                system_arch_list=self.sys_arch.supported,
            ) from None

    def get_docker_config_json(self) -> str | None:
        """Generate Docker config.json content with registry credentials for base image.

        Returns a JSON string with registry credentials for the base image's registry,
        or None if no matching registry is configured.

        Raises:
            HassioArchNotFound: If the add-on is not supported on the current architecture.

        """
        # Early return before accessing base_image to avoid unnecessary arch lookup
        if not self.sys_docker.config.registries:
            return None

        registry = self.sys_docker.config.get_registry_for_image(self.base_image)
        if not registry:
            return None

        stored = self.sys_docker.config.registries[registry]
        username = stored[ATTR_USERNAME]
        password = stored[ATTR_PASSWORD]

        # Docker config.json uses base64-encoded "username:password" for auth
        auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()

        # Use the actual registry URL for the key
        # Docker Hub uses "https://index.docker.io/v1/" as the key
        # Support both docker.io (official) and hub.docker.com (legacy)
        registry_key = (
            "https://index.docker.io/v1/"
            if registry in (DOCKER_HUB, DOCKER_HUB_LEGACY)
            else registry
        )

        config = {"auths": {registry_key: {"auth": auth_string}}}

        return json.dumps(config)

    def get_docker_args(
        self, version: AwesomeVersion, image_tag: str, docker_config_path: Path | None
    ) -> dict[str, Any]:
        """Create a dict with Docker run args."""
        dockerfile_path = self.get_dockerfile().relative_to(self.addon.path_location)

        build_cmd = [
            "docker",
            "buildx",
            "build",
            ".",
            "--tag",
            image_tag,
            "--file",
            str(dockerfile_path),
            "--platform",
            MAP_ARCH[self.arch],
            "--pull",
        ]

        labels = {
            "io.hass.version": version,
            "io.hass.arch": self.arch,
            "io.hass.type": META_ADDON,
            "io.hass.name": self._fix_label("name"),
            "io.hass.description": self._fix_label("description"),
            **self.additional_labels,
        }

        if self.addon.url:
            labels["io.hass.url"] = self.addon.url

        for key, value in labels.items():
            build_cmd.extend(["--label", f"{key}={value}"])

        build_args = {
            "BUILD_FROM": self.base_image,
            "BUILD_VERSION": version,
            "BUILD_ARCH": self.sys_arch.default,
            **self.additional_args,
        }

        for key, value in build_args.items():
            build_cmd.extend(["--build-arg", f"{key}={value}"])

        # The addon path will be mounted from the host system
        addon_extern_path = self.sys_config.local_to_extern_path(
            self.addon.path_location
        )

        volumes = {
            SOCKET_DOCKER: {"bind": "/var/run/docker.sock", "mode": "rw"},
            addon_extern_path: {"bind": "/addon", "mode": "ro"},
        }

        # Mount Docker config with registry credentials if available
        if docker_config_path:
            docker_config_extern_path = self.sys_config.local_to_extern_path(
                docker_config_path
            )
            volumes[docker_config_extern_path] = {
                "bind": "/root/.docker/config.json",
                "mode": "ro",
            }

        return {
            "command": build_cmd,
            "volumes": volumes,
            "working_dir": "/addon",
        }

    def _fix_label(self, label_name: str) -> str:
        """Remove characters they are not supported."""
        label = getattr(self.addon, label_name, "")
        return label.replace("'", "")
