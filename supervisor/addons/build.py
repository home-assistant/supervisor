"""Supervisor add-on build environment."""
from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from awesomeversion import AwesomeVersion

from ..const import (
    ATTR_ARGS,
    ATTR_BUILD_FROM,
    ATTR_LABELS,
    ATTR_SQUASH,
    FILE_SUFFIX_CONFIGURATION,
    META_ADDON,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.interface import MAP_ARCH
from ..exceptions import ConfigurationFileError, HassioArchNotFound
from ..utils.common import FileConfiguration, find_one_filetype
from .validate import SCHEMA_BUILD_CONFIG

if TYPE_CHECKING:
    from . import AnyAddon


class AddonBuild(FileConfiguration, CoreSysAttributes):
    """Handle build options for add-ons."""

    def __init__(self, coresys: CoreSys, addon: AnyAddon) -> None:
        """Initialize Supervisor add-on builder."""
        self.coresys: CoreSys = coresys
        self.addon = addon

        try:
            build_file = find_one_filetype(
                self.addon.path_location, "build", FILE_SUFFIX_CONFIGURATION
            )
        except ConfigurationFileError:
            build_file = self.addon.path_location / "build.json"

        super().__init__(build_file, SCHEMA_BUILD_CONFIG)

    def save_data(self):
        """Ignore save function."""
        raise RuntimeError()

    @cached_property
    def arch(self) -> str:
        """Return arch of the add-on."""
        return self.sys_arch.match(self.addon.arch)

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
    def dockerfile(self) -> Path:
        """Return Dockerfile path."""
        if self.addon.path_location.joinpath(f"Dockerfile.{self.arch}").exists():
            return self.addon.path_location.joinpath(f"Dockerfile.{self.arch}")
        return self.addon.path_location.joinpath("Dockerfile")

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

    @property
    def is_valid(self) -> bool:
        """Return true if the build env is valid."""
        try:
            return all(
                [
                    self.addon.path_location.is_dir(),
                    self.dockerfile.is_file(),
                ]
            )
        except HassioArchNotFound:
            return False

    def get_docker_args(self, version: AwesomeVersion):
        """Create a dict with Docker build arguments."""
        args = {
            "path": str(self.addon.path_location),
            "tag": f"{self.addon.image}:{version!s}",
            "dockerfile": str(self.dockerfile),
            "pull": True,
            "forcerm": not self.sys_dev,
            "squash": self.squash,
            "platform": MAP_ARCH[self.arch],
            "labels": {
                "io.hass.version": version,
                "io.hass.arch": self.arch,
                "io.hass.type": META_ADDON,
                "io.hass.name": self._fix_label("name"),
                "io.hass.description": self._fix_label("description"),
                **self.additional_labels,
            },
            "buildargs": {
                "BUILD_FROM": self.base_image,
                "BUILD_VERSION": version,
                "BUILD_ARCH": self.sys_arch.default,
                **self.additional_args,
            },
        }

        if self.addon.url:
            args["labels"]["io.hass.url"] = self.addon.url

        return args

    def _fix_label(self, label_name: str) -> str:
        """Remove characters they are not supported."""
        label = getattr(self.addon, label_name, "")
        return label.replace("'", "")
