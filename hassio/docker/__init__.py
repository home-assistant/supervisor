"""Init file for Hass.io Docker object."""
import logging
from contextlib import suppress
from typing import Any, Dict, Optional

import attr
import docker

from ..const import SOCKET_DOCKER
from ..exceptions import DockerAPIError
from .network import DockerNetwork

_LOGGER = logging.getLogger(__name__)


@attr.s(frozen=True)
class CommandReturn:
    """Return object from command run."""

    exit_code: int = attr.ib()
    output: bytes = attr.ib()


class DockerAPI:
    """Docker Hass.io wrapper.

    This class is not AsyncIO safe!
    """

    def __init__(self):
        """Initialize Docker base wrapper."""
        self.docker: docker.DockerClient = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)), version="auto", timeout=900
        )
        self.network: DockerNetwork = DockerNetwork(self.docker)

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

    def run(
        self, image: str, **kwargs: Dict[str, Any]
    ) -> docker.models.containers.Container:
        """"Create a Docker container and run it.

        Need run inside executor.
        """
        name = kwargs.get("name", image)
        network_mode = kwargs.get("network_mode")
        hostname = kwargs.get("hostname")

        # Setup network
        kwargs["dns_search"] = ["."]
        if network_mode:
            kwargs["dns"] = [str(self.network.supervisor)]
            kwargs["dns_opt"] = ["ndots:0"]
        else:
            kwargs["network"] = None

        # Create container
        try:
            container = self.docker.containers.create(
                image, use_config_proxy=False, **kwargs
            )
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't create container from %s: %s", name, err)
            raise DockerAPIError() from None

        # Attach network
        if not network_mode:
            alias = [hostname] if hostname else None
            try:
                self.network.attach_container(container, alias=alias)
            except DockerAPIError:
                _LOGGER.warning("Can't attach %s to hassio-net!", name)
            else:
                with suppress(DockerAPIError):
                    self.network.detach_default_bridge(container)

        # Run container
        try:
            container.start()
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't start %s: %s", name, err)
            raise DockerAPIError() from None

        # Update metadata
        with suppress(docker.errors.DockerException):
            container.reload()

        return container

    def run_command(
        self, image: str, command: Optional[str] = None, **kwargs: Dict[str, Any]
    ) -> CommandReturn:
        """Create a temporary container and run command.

        Need run inside executor.
        """
        stdout = kwargs.get("stdout", True)
        stderr = kwargs.get("stderr", True)

        _LOGGER.info("Run command '%s' on %s", command, image)
        try:
            container = self.docker.containers.run(
                image,
                command=command,
                network=self.network.name,
                use_config_proxy=False,
                **kwargs
            )

            # wait until command is done
            result = container.wait()
            output = container.logs(stdout=stdout, stderr=stderr)

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't execute command: %s", err)
            raise DockerAPIError() from None

        finally:
            # cleanup container
            with suppress(docker.errors.DockerException):
                container.remove(force=True)

        return CommandReturn(result.get("StatusCode"), output)
