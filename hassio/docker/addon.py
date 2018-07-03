"""Init file for HassIO addon docker object."""
import logging
import os

import docker
import requests

from .interface import DockerInterface
from ..addons.build import AddonBuild
from ..const import (
    MAP_CONFIG, MAP_SSL, MAP_ADDONS, MAP_BACKUP, MAP_SHARE, ENV_TOKEN,
    ENV_TIME, SECURITY_PROFILE, SECURITY_DISABLE)
from ..utils import process_lock

_LOGGER = logging.getLogger(__name__)

AUDIO_DEVICE = "/dev/snd:/dev/snd:rwm"


class DockerAddon(DockerInterface):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, coresys, slug):
        """Initialize docker homeassistant wrapper."""
        super().__init__(coresys)
        self._id = slug

    @property
    def addon(self):
        """Return addon of docker image."""
        return self.sys_addons.get(self._id)

    @property
    def image(self):
        """Return name of docker image."""
        return self.addon.image

    @property
    def timeout(self):
        """Return timeout for docker actions."""
        return self.addon.timeout

    @property
    def version(self):
        """Return version of docker image."""
        if not self.addon.legacy:
            return super().version
        return self.addon.version_installed

    @property
    def arch(self):
        """Return arch of docker image."""
        if not self.addon.legacy:
            return super().arch
        return self.sys_arch

    @property
    def name(self):
        """Return name of docker container."""
        return "addon_{}".format(self.addon.slug)

    @property
    def ipc(self):
        """Return the IPC namespace."""
        if self.addon.host_ipc:
            return 'host'
        return None

    @property
    def hostname(self):
        """Return slug/id of addon."""
        return self.addon.slug.replace('_', '-')

    @property
    def environment(self):
        """Return environment for docker add-on."""
        addon_env = self.addon.environment or {}

        # Need audio settings
        if self.addon.with_audio:
            addon_env.update({
                'ALSA_OUTPUT': self.addon.audio_output,
                'ALSA_INPUT': self.addon.audio_input,
            })

        return {
            **addon_env,
            ENV_TIME: self.sys_config.timezone,
            ENV_TOKEN: self.addon.uuid,
        }

    @property
    def devices(self):
        """Return needed devices."""
        devices = self.addon.devices or []

        # Use audio devices
        if self.addon.with_audio and AUDIO_DEVICE not in devices:
            devices.append(AUDIO_DEVICE)

        # Auto mapping UART devices
        if self.addon.auto_uart:
            for device in self.sys_hardware.serial_devices:
                devices.append(f"{device}:{device}:rwm")

        # Return None if no devices is present
        return devices or None

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
    def security_opt(self):
        """Controlling security opt."""
        security = []

        # AppArmor
        apparmor = self.sys_host.apparmor.available
        if not apparmor or self.addon.apparmor == SECURITY_DISABLE:
            security.append("apparmor:unconfined")
        elif self.addon.apparmor == SECURITY_PROFILE:
            security.append(f"apparmor={self.addon.slug}")

        # Disable Seccomp / We don't support it official and it
        # make troubles on some kind of host systems.
        security.append("seccomp=unconfined")

        return security

    @property
    def tmpfs(self):
        """Return tmpfs for docker add-on."""
        options = self.addon.tmpfs
        if options:
            return {"/tmpfs": f"{options}"}
        return None

    @property
    def network_mapping(self):
        """Return hosts mapping."""
        return {
            'homeassistant': self.sys_docker.network.gateway,
            'hassio': self.sys_docker.network.supervisor,
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
                'bind': "/data", 'mode': 'rw'
            }}

        addon_mapping = self.addon.map_volumes

        # setup config mappings
        if MAP_CONFIG in addon_mapping:
            volumes.update({
                str(self.sys_config.path_extern_config): {
                    'bind': "/config", 'mode': addon_mapping[MAP_CONFIG]
                }})

        if MAP_SSL in addon_mapping:
            volumes.update({
                str(self.sys_config.path_extern_ssl): {
                    'bind': "/ssl", 'mode': addon_mapping[MAP_SSL]
                }})

        if MAP_ADDONS in addon_mapping:
            volumes.update({
                str(self.sys_config.path_extern_addons_local): {
                    'bind': "/addons", 'mode': addon_mapping[MAP_ADDONS]
                }})

        if MAP_BACKUP in addon_mapping:
            volumes.update({
                str(self.sys_config.path_extern_backup): {
                    'bind': "/backup", 'mode': addon_mapping[MAP_BACKUP]
                }})

        if MAP_SHARE in addon_mapping:
            volumes.update({
                str(self.sys_config.path_extern_share): {
                    'bind': "/share", 'mode': addon_mapping[MAP_SHARE]
                }})

        # Init other hardware mappings

        # GPIO support
        if self.addon.with_gpio:
            volumes.update({
                "/sys/class/gpio": {
                    'bind': "/sys/class/gpio", 'mode': 'rw'
                },
                "/sys/devices/platform/soc": {
                    'bind': "/sys/devices/platform/soc", 'mode': 'rw'
                },
            })

        # DeviceTree support
        if self.addon.with_devicetree:
            volumes.update({
                "/sys/firmware/devicetree": {
                    'bind': "/sys/firmware/devicetree", 'mode': 'ro'
                },
            })

        # Host dbus system
        if self.addon.host_dbus:
            volumes.update({
                "/var/run/dbus": {
                    'bind': "/var/run/dbus", 'mode': 'rw'
                }})

        # ALSA configuration
        if self.addon.with_audio:
            volumes.update({
                str(self.addon.path_extern_asound): {
                    'bind': "/etc/asound.conf", 'mode': 'ro'
                }})

        return volumes

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return True

        # cleanup
        self._stop()

        ret = self.sys_docker.run(
            self.image,
            name=self.name,
            hostname=self.hostname,
            detach=True,
            init=True,
            ipc_mode=self.ipc,
            stdin_open=self.addon.with_stdin,
            network_mode=self.network_mode,
            ports=self.ports,
            extra_hosts=self.network_mapping,
            devices=self.devices,
            cap_add=self.addon.privileged,
            security_opt=self.security_opt,
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
        build_env = AddonBuild(self.coresys, self._id)

        _LOGGER.info("Start build %s:%s", self.image, tag)
        try:
            image, log = self.sys_docker.images.build(
                **build_env.get_docker_args(tag))

            _LOGGER.debug("Build %s:%s done: %s", self.image, tag, log)
            image.tag(self.image, tag='latest')

            # Update meta data
            self._meta = image.attrs

        except (docker.errors.DockerException) as err:
            _LOGGER.error("Can't build %s:%s: %s", self.image, tag, err)
            return False

        _LOGGER.info("Build %s:%s done", self.image, tag)
        return True

    @process_lock
    def export_image(self, path):
        """Export current images into a tar file."""
        return self.sys_run_in_executor(self._export_image, path)

    def _export_image(self, tar_file):
        """Export current images into a tar file.

        Need run inside executor.
        """
        try:
            image = self.sys_docker.api.get_image(self.image)
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't fetch image %s: %s", self.image, err)
            return False

        _LOGGER.info("Export image %s to %s", self.image, tar_file)
        try:
            with tar_file.open("wb") as write_tar:
                for chunk in image:
                    write_tar.write(chunk)
        except (OSError, requests.exceptions.ReadTimeout) as err:
            _LOGGER.error("Can't write tar file %s: %s", tar_file, err)
            return False

        _LOGGER.info("Export image %s done", self.image)
        return True

    @process_lock
    def import_image(self, path, tag):
        """Import a tar file as image."""
        return self.sys_run_in_executor(self._import_image, path, tag)

    def _import_image(self, tar_file, tag):
        """Import a tar file as image.

        Need run inside executor.
        """
        try:
            with tar_file.open("rb") as read_tar:
                self.sys_docker.api.load_image(read_tar, quiet=True)

            image = self.sys_docker.images.get(self.image)
            image.tag(self.image, tag=tag)
        except (docker.errors.DockerException, OSError) as err:
            _LOGGER.error("Can't import image %s: %s", self.image, err)
            return False

        _LOGGER.info("Import image %s and tag %s", tar_file, tag)
        self._meta = image.attrs
        self._cleanup()
        return True

    @process_lock
    def write_stdin(self, data):
        """Write to add-on stdin."""
        return self.sys_run_in_executor(self._write_stdin, data)

    def _write_stdin(self, data):
        """Write to add-on stdin.

        Need run inside executor.
        """
        if not self._is_running():
            return False

        try:
            # load needed docker objects
            container = self.sys_docker.containers.get(self.name)
            socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't attach to %s stdin: %s", self.name, err)
            return False

        try:
            # write to stdin
            data += b"\n"
            os.write(socket.fileno(), data)
            socket.close()
        except OSError as err:
            _LOGGER.error("Can't write to %s stdin: %s", self.name, err)
            return False

        return True
