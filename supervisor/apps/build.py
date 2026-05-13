"""Supervisor app build environment."""

from __future__ import annotations

import base64
from functools import cached_property
import json
import logging
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Any, Self

from awesomeversion import AwesomeVersion
import voluptuous as vol

from ..const import (
    ATTR_ARGS,
    ATTR_BUILD_FROM,
    ATTR_LABELS,
    ATTR_PASSWORD,
    ATTR_SQUASH,
    ATTR_USERNAME,
    FILE_SUFFIX_CONFIGURATION,
    LABEL_ARCH,
    LABEL_DESCRIPTION,
    LABEL_NAME,
    LABEL_TYPE,
    LABEL_URL,
    LABEL_VERSION,
    META_APP,
    SOCKET_DOCKER,
    CpuArch,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.const import DOCKER_HUB, DOCKER_HUB_LEGACY, DockerMount, MountType
from ..docker.interface import MAP_ARCH
from ..exceptions import (
    AppBuildArchitectureNotSupportedError,
    AppBuildDockerfileMissingError,
    ConfigurationFileError,
    HassioArchNotFound,
)
from ..utils.common import find_one_filetype, read_json_or_yaml_file
from .validate import SCHEMA_BUILD_CONFIG

if TYPE_CHECKING:
    from .manager import AnyApp

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AppBuild(CoreSysAttributes):
    """Handle build options for apps."""

    def __init__(self, coresys: CoreSys, app: AnyApp, data: dict[str, Any]) -> None:
        """Initialize Supervisor app builder."""
        self.coresys: CoreSys = coresys
        self.app = app
        self._build_config: dict[str, Any] = data

    @classmethod
    async def create(cls, coresys: CoreSys, app: AnyApp) -> Self:
        """Create an AppBuild by reading the build configuration from disk."""
        data = await coresys.run_in_executor(cls._read_build_config, app)

        if data:
            _LOGGER.warning(
                "App %s uses build.yaml which is deprecated. "
                "Move build parameters into the Dockerfile directly.",
                app.slug,
            )

            if data[ATTR_SQUASH]:
                _LOGGER.warning(
                    "Ignoring squash build option for %s as Docker BuildKit"
                    " does not support it.",
                    app.slug,
                )

        return cls(coresys, app, data or {})

    @staticmethod
    def _read_build_config(app: AnyApp) -> dict[str, Any] | None:
        """Find and read the build configuration file.

        Must be run in executor.
        """
        try:
            build_file = find_one_filetype(
                app.path_location, "build", FILE_SUFFIX_CONFIGURATION
            )
        except ConfigurationFileError:
            # No build config file found, assuming modernized build
            return None

        try:
            raw = read_json_or_yaml_file(build_file)
            build_config = SCHEMA_BUILD_CONFIG(raw)
        except ConfigurationFileError as ex:
            _LOGGER.exception(
                "Error reading %s build config (%s), using defaults",
                app.slug,
                ex,
            )
            build_config = SCHEMA_BUILD_CONFIG({})
        except vol.Invalid as ex:
            _LOGGER.warning(
                "Error parsing %s build config (%s), using defaults", app.slug, ex
            )
            build_config = SCHEMA_BUILD_CONFIG({})

        # Default base image is passed in BUILD_FROM only when build.yaml is used
        # (this is legacy behavior - without build config, Dockerfile should specify it)
        if not build_config[ATTR_BUILD_FROM]:
            build_config[ATTR_BUILD_FROM] = "ghcr.io/home-assistant/base:latest"

        return build_config

    @cached_property
    def arch(self) -> CpuArch:
        """Return arch of the app."""
        return self.sys_arch.match([self.app.arch])

    @property
    def base_image(self) -> str | None:
        """Return base image for this app, or None to use Dockerfile default."""
        # No build config (otherwise default is coerced when reading the config)
        if not self._build_config.get(ATTR_BUILD_FROM):
            return None

        # Single base image in build config
        if isinstance(self._build_config[ATTR_BUILD_FROM], str):
            return self._build_config[ATTR_BUILD_FROM]

        # Dict - per-arch base images in build config
        if self.arch not in self._build_config[ATTR_BUILD_FROM]:
            raise HassioArchNotFound(
                f"App {self.app.slug} is not supported on {self.arch}"
            )
        return self._build_config[ATTR_BUILD_FROM][self.arch]

    @property
    def additional_args(self) -> dict[str, str]:
        """Return additional Docker build arguments."""
        return self._build_config.get(ATTR_ARGS, {})

    @property
    def additional_labels(self) -> dict[str, str]:
        """Return additional Docker labels."""
        return self._build_config.get(ATTR_LABELS, {})

    def get_dockerfile(self) -> Path:
        """Return Dockerfile path.

        Must be run in executor.
        """
        if self.app.path_location.joinpath(f"Dockerfile.{self.arch}").exists():
            return self.app.path_location.joinpath(f"Dockerfile.{self.arch}")
        return self.app.path_location.joinpath("Dockerfile")

    async def is_valid(self) -> None:
        """Return true if the build env is valid."""

        def build_is_valid() -> bool:
            return all(
                [
                    self.app.path_location.is_dir(),
                    self.get_dockerfile().is_file(),
                ]
            )

        try:
            if not await self.sys_run_in_executor(build_is_valid):
                raise AppBuildDockerfileMissingError(_LOGGER.error, app=self.app.slug)
        except HassioArchNotFound:
            raise AppBuildArchitectureNotSupportedError(
                _LOGGER.error,
                app=self.app.slug,
                app_arch_list=self.app.supported_arch,
                system_arch_list=[arch.value for arch in self.sys_arch.supported],
            ) from None

    def _registry_key(self, registry: str) -> str:
        """Return the Docker config.json key for a registry."""
        if registry in (DOCKER_HUB, DOCKER_HUB_LEGACY):
            return "https://index.docker.io/v1/"
        return registry

    def _registry_auth(self, registry: str) -> str:
        """Return base64-encoded auth string for a registry."""
        stored = self.sys_docker.config.registries[registry]
        return base64.b64encode(
            f"{stored[ATTR_USERNAME]}:{stored[ATTR_PASSWORD]}".encode()
        ).decode()

    def get_docker_config_json(self) -> str | None:
        """Generate Docker config.json content with all configured registry credentials.

        Returns a JSON string with registry credentials, or None if no registries
        are configured.
        """
        if not self.sys_docker.config.registries:
            return None

        auths = {
            self._registry_key(registry): {"auth": self._registry_auth(registry)}
            for registry in self.sys_docker.config.registries
        }
        return json.dumps({"auths": auths})

    def get_docker_args(
        self, version: AwesomeVersion, image_tag: str, docker_config_path: Path | None
    ) -> dict[str, Any]:
        """Create a dict with Docker run args."""
        dockerfile_path = self.get_dockerfile().relative_to(self.app.path_location)

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
            LABEL_VERSION: version,
            LABEL_ARCH: self.arch,
            LABEL_TYPE: META_APP,
            **self.additional_labels,
        }

        # Set name only if non-empty, could have been set in Dockerfile
        if name := self._fix_label("name"):
            labels[LABEL_NAME] = name

        # Set description only if non-empty, could have been set in Dockerfile
        if description := self._fix_label("description"):
            labels[LABEL_DESCRIPTION] = description

        if self.app.url:
            labels[LABEL_URL] = self.app.url

        for key, value in labels.items():
            build_cmd.extend(["--label", f"{key}={value}"])

        build_args = {
            "BUILD_VERSION": version,
            "BUILD_ARCH": self.arch,
            **self.additional_args,
        }

        if self.base_image is not None:
            build_args["BUILD_FROM"] = self.base_image

        for key, value in build_args.items():
            build_cmd.extend(["--build-arg", f"{key}={value}"])

        # The app path will be mounted from the host system
        app_extern_path = self.sys_config.local_to_extern_path(self.app.path_location)

        mounts = [
            DockerMount(
                type=MountType.BIND,
                source=SOCKET_DOCKER.as_posix(),
                target="/var/run/docker.sock",
                read_only=False,
            ),
            DockerMount(
                type=MountType.BIND,
                source=app_extern_path.as_posix(),
                target="/addon",
                read_only=True,
            ),
        ]

        # Mount Docker config with registry credentials if available
        if docker_config_path:
            docker_config_extern_path = self.sys_config.local_to_extern_path(
                docker_config_path
            )
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=docker_config_extern_path.as_posix(),
                    target="/root/.docker/config.json",
                    read_only=True,
                )
            )

        return {
            "command": build_cmd,
            "mounts": mounts,
            "working_dir": PurePath("/addon"),
        }

    def _fix_label(self, label_name: str) -> str:
        """Remove characters they are not supported."""
        label = getattr(self.app, label_name, "")
        return label.replace("'", "")
