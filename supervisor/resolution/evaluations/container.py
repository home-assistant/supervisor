"""Evaluation class for container."""
import logging
from typing import Any, List

from docker.errors import DockerException
from requests import RequestException

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOCKER_IMAGE_DENYLIST = [
    "watchtower",
    "ouroboros",
]


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
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP, CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        self._images.clear()
        for image in await self.sys_run_in_executor(self._get_images):
            for tag in image.tags:
                image_name = tag.partition(":")[0].split("/")[-1]
                if (
                    any(
                        image_name.startswith(deny_name)
                        for deny_name in DOCKER_IMAGE_DENYLIST
                    )
                    and image_name not in self._images
                ):
                    self._images.add(image_name)
        return len(self._images) != 0

    def _get_images(self) -> List[Any]:
        """Return a list of images."""
        images = []

        try:
            images = self.sys_docker.images.list()
        except (DockerException, RequestException) as err:
            _LOGGER.error("Corrupt docker overlayfs detect: %s", err)

        return images
