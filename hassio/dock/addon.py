"""Init file for HassIO addon docker object."""
import logging
import os

import docker
import requests

from .interface import DockerInterface
from .util import docker_process
from ..addons.build import AddonBuild
from ..const import (
    MAP_CONFIG, MAP_SSL, MAP_ADDONS, MAP_BACKUP, MAP_SHARE)

_LOGGER = logging.getLogger(__name__)

AUDIO_DEVICE = "/dev/snd:/dev/snd:rwm"


class DockerAddon(DockerInterface):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, api, addon):
        """Initialize docker homeassistant wrapper."""
        super().__init__(
            config, loop, api, image=addon.image, timeout=addon.timeout)
        self.addon = addon

    def process_metadata(self, metadata, force=False):
        """Use addon data instead meta data with legacy."""
        if not self.addon.legacy:
            return super().process_metadata(metadata, force=force)

        # set meta data
        if not self.version or force:
            if force:  # called on install/update/build
                self.version = self.addon.last_version
            else:
                self.version = self.addon.version_installed

        if not self.arch:
            self.arch = self.config.arch

    @property
    def name(self):
        """Return name of docker container."""
        return "addon_{}".format(self.addon.slug)

    @property
    def hostname(self):
        """Return slug/id of addon."""
        return self.addon.slug.replace('_', '-')

    @property
    def environment(self):
        """Return environment for docker add-on."""
        addon_env = self.addon.environment or {}
        if self.addon.with_audio:
            addon_env.update({
                'ALSA_OUTPUT': self.addon.audio_output,
                'ALSA_INPUT': self.addon.audio_input,
            })

        return {
            **addon_env,
            'TZ': self.config.timezone,
        }

    @property
    def devices(self):
        """Return needed devices."""
        devices = self.addon.devices or []

        # use audio devices
        if self.addon.with_audio and AUDIO_DEVICE not in devices:
            devices.append(AUDIO_DEVICE)

        # Return None if no devices is present
        if devices:
            return devices
        return None

    @property
    def ports(self):
        """Filter None from addon ports."""
        if not self.addon.ports:
            return None

        return {
            container_port: host_port
            for container_port, host_port in self.addon.ports.items()
            if host_port
        }

    @property
    def tmpfs(self):
        """Return tmpfs for docker add-on."""
        options = self.addon.tmpfs
        if options:
            return {"/tmpfs": "{}".format(options)}
        return None

    @property
    def network_mapping(self):
        """Return hosts mapping."""
        return {
            'homeassistant': self.docker.network.gateway,
            'hassio': self.docker.network.supervisor,
        }

    @property
    def network_mode(self):
        """Return network mode for addon."""
        if self.addon.host_network:
            return 'host'
        return None

    @property
    def volumes(self):
        """Generate volumes for mappings."""
        volumes = {
            str(self.addon.path_extern_data): {
                'bind': '/data', 'mode': 'rw'
            }}

        addon_mapping = self.addon.map_volumes

        # setup config mappings
        if MAP_CONFIG in addon_mapping:
            volumes.update({
                str(self.config.path_extern_config): {
                    'bind': '/config', 'mode': addon_mapping[MAP_CONFIG]
                }})

        if MAP_SSL in addon_mapping:
            volumes.update({
                str(self.config.path_extern_ssl): {
                    'bind': '/ssl', 'mode': addon_mapping[MAP_SSL]
                }})

        if MAP_ADDONS in addon_mapping:
            volumes.update({
                str(self.config.path_extern_addons_local): {
                    'bind': '/addons', 'mode': addon_mapping[MAP_ADDONS]
                }})

        if MAP_BACKUP in addon_mapping:
            volumes.update({
                str(self.config.path_extern_backup): {
                    'bind': '/backup', 'mode': addon_mapping[MAP_BACKUP]
                }})

        if MAP_SHARE in addon_mapping:
            volumes.update({
                str(self.config.path_extern_share): {
                    'bind': '/share', 'mode': addon_mapping[MAP_SHARE]
                }})

        # init other hardware mappings
        if self.addon.with_gpio:
            volumes.update({
                '/sys/class/gpio': {
                    'bind': '/sys/class/gpio', 'mode': "rw"
                },
                '/sys/devices/platform/soc': {
                    'bind': '/sys/devices/platform/soc', 'mode': "rw"
                },
            })

        return volumes

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return True

        # cleanup
        self._stop()

        # write config
        if not self.addon.write_options():
            return False

        ret = self.docker.run(
            self.image,
            name=self.name,
            hostname=self.hostname,
            detach=True,
            init=True,
            stdin_open=self.addon.with_stdin,
            network_mode=self.network_mode,
            ports=self.ports,
            extra_hosts=self.network_mapping,
            devices=self.devices,
            cap_add=self.addon.privileged,
            environment=self.environment,
            volumes=self.volumes,
            tmpfs=self.tmpfs
        )

        if ret:
            _LOGGER.info("Start docker addon %s with version %s",
                         self.image, self.version)

        return ret

    def _install(self, tag):
        """Pull docker image or build it.

        Need run inside executor.
        """
        if self.addon.need_build:
            return self._build(tag)

        return super()._install(tag)

    def _build(self, tag):
        """Build a docker container.

        Need run inside executor.
        """
        build_env = AddonBuild(self.config, self.addon)

        _LOGGER.info("Start build %s:%s", self.image, tag)
        try:
            image = self.docker.images.build(**build_env.get_docker_args(tag))

            image.tag(self.image, tag='latest')
            self.process_metadata(image.attrs, force=True)

        except (docker.errors.DockerException) as err:
            _LOGGER.error("Can't build %s:%s -> %s", self.image, tag, err)
            return False

        _LOGGER.info("Build %s:%s done", self.image, tag)
        return True

    @docker_process
    def export_image(self, path):
        """Export current images into a tar file."""
        return self.loop.run_in_executor(None, self._export_image, path)

    def _export_image(self, tar_file):
        """Export current images into a tar file.

        Need run inside executor.
        """
        try:
            image = self.docker.api.get_image(self.image)
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't fetch image %s -> %s", self.image, err)
            return False

        try:
            with tar_file.open("wb") as write_tar:
                for chunk in image.stream():
                    write_tar.write(chunk)
        except (OSError, requests.exceptions.ReadTimeout) as err:
            _LOGGER.error("Can't write tar file %s -> %s", tar_file, err)
            return False

        _LOGGER.info("Export image %s to %s", self.image, tar_file)
        return True

    @docker_process
    def import_image(self, path, tag):
        """Import a tar file as image."""
        return self.loop.run_in_executor(None, self._import_image, path, tag)

    def _import_image(self, tar_file, tag):
        """Import a tar file as image.

        Need run inside executor.
        """
        try:
            with tar_file.open("rb") as read_tar:
                self.docker.api.load_image(read_tar)

            image = self.docker.images.get(self.image)
            image.tag(self.image, tag=tag)
        except (docker.errors.DockerException, OSError) as err:
            _LOGGER.error("Can't import image %s -> %s", self.image, err)
            return False

        _LOGGER.info("Import image %s and tag %s", tar_file, tag)
        self.process_metadata(image.attrs, force=True)
        self._cleanup()
        return True

    def _restart(self):
        """Restart docker container.

        Addons prepare some thing on start and that is normaly not repeatable.
        Need run inside executor.
        """
        self._stop()
        return self._run()

    @docker_process
    def write_stdin(self, data):
        """Write to add-on stdin."""
        return self.loop.run_in_executor(None, self._write_stdin, data)

    def _write_stdin(self, data):
        """Write to add-on stdin.

        Need run inside executor.
        """
        if not self._is_running():
            return False

        try:
            # load needed docker objects
            container = self.docker.containers.get(self.name)
            socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't attach to %s stdin -> %s", self.name, err)
            return False

        try:
            # write to stdin
            data += b"\n"
            os.write(socket.fileno(), data)
            socket.close()
        except OSError as err:
            _LOGGER.error("Can't write to %s stdin -> %s", self.name, err)
            return False

        return True
