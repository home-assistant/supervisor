"""Supervisor add-on build environment."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict

from awesomeversion import AwesomeVersion

from ..const import (
    ATTR_ARGS,
    ATTR_BUILD_FROM,
    ATTR_SQUASH,
    FILE_SUFFIX_CONFIGURATION,
    META_ADDON,
)
from ..coresys import CoreSys, CoreSysAttributes
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

        super().__init__(
            find_one_filetype(
                self.addon.path_location, "build", FILE_SUFFIX_CONFIGURATION
            ),
            SCHEMA_BUILD_CONFIG,
        )

    def save_data(self):
        """Ignore save function."""
        raise RuntimeError()

    @property
    def base_image(self) -> str:
        """Return base image for this add-on."""
        return self._data[ATTR_BUILD_FROM].get(
            self.sys_arch.default, f"homeassistant/{self.sys_arch.default}-base:latest"
        )

    @property
    def squash(self) -> bool:
        """Return True or False if squash is active."""
        return self._data[ATTR_SQUASH]

    @property
    def additional_args(self) -> Dict[str, str]:
        """Return additional Docker build arguments."""
        return self._data[ATTR_ARGS]

    @property
    def is_valid(self) -> bool:
        """Return true if the build env is valid."""
        return all(
            [
                self.addon.path_location.is_dir(),
                Path(self.addon.path_location, "Dockerfile").is_file(),
            ]
        )

    def get_docker_args(self, version: AwesomeVersion):
        """Create a dict with Docker build arguments."""
        args = {
            "path": str(self.addon.path_location),
            "tag": f"{self.addon.image}:{version!s}",
            "pull": True,
            "forcerm": True,
            "squash": self.squash,
            "labels": {
                "io.hass.version": version,
                "io.hass.arch": self.sys_arch.default,
                "io.hass.type": META_ADDON,
                "io.hass.name": self._fix_label("name"),
                "io.hass.description": self._fix_label("description"),
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
