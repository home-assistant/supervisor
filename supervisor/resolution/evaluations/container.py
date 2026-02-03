"""Evaluation class for container."""

import asyncio
import logging

import aiodocker

from ...const import CoreState
from ...coresys import CoreSys
from ...docker.const import ADDON_BUILDER_IMAGE
from ..const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)
from .base import EvaluateBase

_LOGGER: logging.Logger = logging.getLogger(__name__)

UNHEALTHY_IMAGES = [
    "watchtower",
    "ouroboros",
    "portainer",
]
IGNORE_IMAGES = ["sha256"]


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateContainer(coresys)


class EvaluateContainer(EvaluateBase):
    """Evaluate container."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        super().__init__(coresys)
        self.coresys = coresys
        self._images: set[str] = set()

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SOFTWARE

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Found unsupported images: {self._images}"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    @property
    def known_images(self) -> set[str]:
        """Return a set of all known images."""
        return {
            self.sys_homeassistant.image,
            self.sys_supervisor.image or self.sys_supervisor.default_image,
            *(plugin.image for plugin in self.sys_plugins.all_plugins if plugin.image),
            *(addon.image for addon in self.sys_addons.installed if addon.image),
            ADDON_BUILDER_IMAGE,
        }

    async def evaluate(self) -> bool:
        """Run evaluation."""
        self.sys_resolution.evaluate.cached_images.clear()
        self._images.clear()

        try:
            containers = await self.sys_docker.containers.list()
            containers_metadata = await asyncio.gather(*[c.show() for c in containers])
        except aiodocker.DockerError as err:
            _LOGGER.error("Corrupt docker overlayfs detect: %s", err)
            self.sys_resolution.create_issue(
                IssueType.CORRUPT_DOCKER,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_REPAIR],
            )
            return False

        images = {
            image
            for container in containers_metadata
            if (config := container.get("Config")) is not None
            and (image := config.get("Image")) is not None
        }
        for image in images:
            self.sys_resolution.evaluate.cached_images.add(image)

            image_name = image.partition(":")[0]
            if image_name not in IGNORE_IMAGES and image_name not in self.known_images:
                self._images.add(image_name)
                if any(
                    image_name.split("/")[-1].startswith(unhealthy)
                    for unhealthy in UNHEALTHY_IMAGES
                ):
                    _LOGGER.error(
                        "Found image in unhealthy image list '%s' on the host",
                        image_name,
                    )
                    self.sys_resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)

        return len(self._images) != 0
