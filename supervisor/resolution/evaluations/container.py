"""Evaluation class for container."""
import logging
from typing import Any

from docker.errors import DockerException
from requests import RequestException

from ...const import CoreState
from ...coresys import CoreSys
from ..const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)
from .base import EvaluateBase

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOCKER_IMAGE_DENYLIST = [
    "watchtower",
    "ouroboros",
]


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateContainer(coresys)


class EvaluateContainer(EvaluateBase):
    """Evaluate container."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        super().__init__(coresys)
        self.coresys = coresys
        self._images = set()

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CONTAINER

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return f"Found images: {self._images} which are not supported, remove these from the host!"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    @property
    def known_images(self) -> set[str]:
        """Return a set of all known images."""
        return {
            self.sys_homeassistant.image,
            self.sys_supervisor.image,
            *(plugin.image for plugin in self.sys_plugins.all_plugins),
            *(addon.image for addon in self.sys_addons.installed),
        }

    async def evaluate(self) -> None:
        """Run evaluation."""
        self.sys_resolution.evaluate.cached_images.clear()
        self._images.clear()

        for image in await self.sys_run_in_executor(self._get_images):
            for tag in image.tags:
                self.sys_resolution.evaluate.cached_images.add(tag)

                # Evalue system
                image_name = tag.partition(":")[0]
                if image_name not in self.known_images:
                    self._images.add(image_name)
                    if any(
                        image_name.split("/")[-1].startswith(deny_name)
                        for deny_name in DOCKER_IMAGE_DENYLIST
                    ):
                        _LOGGER.error(
                            "Found image in deny-list '%s' on the host", image_name
                        )
                        self.sys_resolution.unhealthy = UnhealthyReason.DOCKER

        return len(self._images) != 0

    def _get_images(self) -> list[Any]:
        """Return a list of images."""
        images = []

        try:
            images = [
                container.image for container in self.sys_docker.containers.list()
            ]
        except (DockerException, RequestException) as err:
            _LOGGER.error("Corrupt docker overlayfs detect: %s", err)
            self.sys_resolution.create_issue(
                IssueType.CORRUPT_DOCKER,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_REPAIR],
            )

        return images
