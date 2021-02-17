"""Init file for Supervisor add-on Docker object."""
from __future__ import annotations

from contextlib import suppress
from ipaddress import IPv4Address, ip_address
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Dict, List, Optional, Set, Union

from awesomeversion import AwesomeVersion
import docker
import requests

from ..addons.build import AddonBuild
from ..const import (
    ENV_TIME,
    ENV_TOKEN,
    ENV_TOKEN_HASSIO,
    MAP_ADDONS,
    MAP_BACKUP,
    MAP_CONFIG,
    MAP_MEDIA,
    MAP_SHARE,
    MAP_SSL,
    SECURITY_DISABLE,
    SECURITY_PROFILE,
)
from ..coresys import CoreSys
from ..exceptions import CoreDNSError, DockerError, DockerNotFound, HardwareNotFound
from ..hardware.const import PolicyGroup
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils import process_lock
from .const import Capabilities
from .interface import DockerInterface

if TYPE_CHECKING:
    from ..addons.addon import Addon


_LOGGER: logging.Logger = logging.getLogger(__name__)

NO_ADDDRESS = ip_address("0.0.0.0")


class DockerAddon(DockerInterface):
    """Docker Supervisor wrapper for Home Assistant."""

    def __init__(self, coresys: CoreSys, addon: Addon):
        """Initialize Docker Home Assistant wrapper."""
        super().__init__(coresys)
        self.addon = addon

    @property
    def image(self) -> Optional[str]:
        """Return name of Docker image."""
        return self.addon.image

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP address of this container."""
        if self.addon.host_network:
            return self.sys_docker.network.gateway

        # Extract IP-Address
        try:
            return ip_address(
                self._meta["NetworkSettings"]["Networks"]["hassio"]["IPAddress"]
            )
        except (KeyError, TypeError, ValueError):
            return NO_ADDDRESS

    @property
    def timeout(self) -> int:
        """Return timeout for Docker actions."""
        return self.addon.timeout

    @property
    def version(self) -> AwesomeVersion:
        """Return version of Docker image."""
        if self.addon.legacy:
            return self.addon.version
        return super().version

    @property
    def arch(self) -> str:
        """Return arch of Docker image."""
        if self.addon.legacy:
            return self.sys_arch.default
        return super().arch

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return f"addon_{self.addon.slug}"

    @property
    def environment(self) -> Dict[str, Optional[str]]:
        """Return environment for Docker add-on."""
        addon_env = self.addon.environment or {}

        # Provide options for legacy add-ons
        if self.addon.legacy:
            for key, value in self.addon.options.items():
                if isinstance(value, (int, str)):
                    addon_env[key] = value
                else:
                    _LOGGER.warning("Can not set nested option %s as Docker env", key)

        return {
            **addon_env,
            ENV_TIME: self.sys_config.timezone,
            ENV_TOKEN: self.addon.supervisor_token,
            ENV_TOKEN_HASSIO: self.addon.supervisor_token,
        }

    @property
    def cgroups_rules(self) -> Optional[List[str]]:
        """Return a list of needed cgroups permission."""
        rules = set()

        # Attach correct cgroups for static devices
        for device_path in self.addon.static_devices:
            try:
                device = self.sys_hardware.get_by_path(device_path)
            except HardwareNotFound:
                _LOGGER.debug("Ignore static device path %s", device_path)

            # Check access
            if not self.sys_hardware.policy.allowed_for_access(device):
                _LOGGER.error(
                    "Add-on %s try to access to blocked device %s!",
                    self.addon.name,
                    device.name,
                )
                continue
            rules.add(self.sys_hardware.policy.get_cgroups_rule(device))

        # Attach correct cgroups for devices
        for device in self.addon.devices:
            if not self.sys_hardware.policy.allowed_for_access(device):
                _LOGGER.error(
                    "Add-on %s try to access to blocked device %s!",
                    self.addon.name,
                    device.name,
                )
                continue
            rules.add(self.sys_hardware.policy.get_cgroups_rule(device))

        # Video
        if self.addon.with_video:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.VIDEO))

        # GPIO
        if self.addon.with_gpio:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.GPIO))

        # UART
        if self.addon.with_uart:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.UART))

        # USB
        if self.addon.with_usb:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.USB))

        # Full Access
        if not self.addon.protected and self.addon.with_full_access:
            rules = set(self.sys_hardware.policy.get_full_access())

        # Return None if no rules is present
        if rules:
            return list(rules)
        return None

    @property
    def ports(self) -> Optional[Dict[str, Union[str, int, None]]]:
        """Filter None from add-on ports."""
        if self.addon.host_network or not self.addon.ports:
            return None

        return {
            container_port: host_port
            for container_port, host_port in self.addon.ports.items()
            if host_port
        }

    @property
    def security_opt(self) -> List[str]:
        """Control security options."""
        security = []

        # AppArmor
        apparmor = self.sys_host.apparmor.available
        if not apparmor or self.addon.apparmor == SECURITY_DISABLE:
            security.append("apparmor:unconfined")
        elif self.addon.apparmor == SECURITY_PROFILE:
            security.append(f"apparmor={self.addon.slug}")

        # Disable Seccomp / We don't support it official and it
        # causes problems on some types of host systems.
        security.append("seccomp=unconfined")

        return security

    @property
    def tmpfs(self) -> Optional[Dict[str, str]]:
        """Return tmpfs for Docker add-on."""
        tmpfs = {}

        if self.addon.with_tmpfs:
            tmpfs["/tmp"] = ""

        if not self.addon.host_ipc:
            tmpfs["/dev/shm"] = ""

        # Return None if no tmpfs is present
        if tmpfs:
            return tmpfs
        return None

    @property
    def network_mapping(self) -> Dict[str, IPv4Address]:
        """Return hosts mapping."""
        return {
            "supervisor": self.sys_docker.network.supervisor,
            "hassio": self.sys_docker.network.supervisor,
        }

    @property
    def network_mode(self) -> Optional[str]:
        """Return network mode for add-on."""
        if self.addon.host_network:
            return "host"
        return None

    @property
    def pid_mode(self) -> Optional[str]:
        """Return PID mode for add-on."""
        if not self.addon.protected and self.addon.host_pid:
            return "host"
        return None

    @property
    def capabilities(self) -> Optional[List[str]]:
        """Generate needed capabilities."""
        capabilities: Set[Capabilities] = set(self.addon.privileged)

        # Need work with kernel modules
        if self.addon.with_kernel_modules:
            capabilities.add(Capabilities.SYS_MODULE)

        # Return None if no capabilities is present
        if capabilities:
            return [cap.value for cap in capabilities]
        return None

    @property
    def volumes(self) -> Dict[str, Dict[str, str]]:
        """Generate volumes for mappings."""
        addon_mapping = self.addon.map_volumes

        volumes = {
            "/dev": {"bind": "/dev", "mode": "ro"},
            str(self.addon.path_extern_data): {"bind": "/data", "mode": "rw"},
        }

        # setup config mappings
        if MAP_CONFIG in addon_mapping:
            volumes.update(
                {
                    str(self.sys_config.path_extern_homeassistant): {
                        "bind": "/config",
                        "mode": addon_mapping[MAP_CONFIG],
                    }
                }
            )

        if MAP_SSL in addon_mapping:
            volumes.update(
                {
                    str(self.sys_config.path_extern_ssl): {
                        "bind": "/ssl",
                        "mode": addon_mapping[MAP_SSL],
                    }
                }
            )

        if MAP_ADDONS in addon_mapping:
            volumes.update(
                {
                    str(self.sys_config.path_extern_addons_local): {
                        "bind": "/addons",
                        "mode": addon_mapping[MAP_ADDONS],
                    }
                }
            )

        if MAP_BACKUP in addon_mapping:
            volumes.update(
                {
                    str(self.sys_config.path_extern_backup): {
                        "bind": "/backup",
                        "mode": addon_mapping[MAP_BACKUP],
                    }
                }
            )

        if MAP_SHARE in addon_mapping:
            volumes.update(
                {
                    str(self.sys_config.path_extern_share): {
                        "bind": "/share",
                        "mode": addon_mapping[MAP_SHARE],
                    }
                }
            )

        if MAP_MEDIA in addon_mapping:
            volumes.update(
                {
                    str(self.sys_config.path_extern_media): {
                        "bind": "/media",
                        "mode": addon_mapping[MAP_MEDIA],
                    }
                }
            )

        # Init other hardware mappings

        # GPIO support
        if self.addon.with_gpio and self.sys_hardware.helper.support_gpio:
            for gpio_path in ("/sys/class/gpio", "/sys/devices/platform/soc"):
                if not Path(gpio_path).exists():
                    continue
                volumes.update({gpio_path: {"bind": gpio_path, "mode": "rw"}})

        # DeviceTree support
        if self.addon.with_devicetree:
            volumes.update(
                {
                    "/sys/firmware/devicetree/base": {
                        "bind": "/device-tree",
                        "mode": "ro",
                    }
                }
            )

        # Host udev support
        if self.addon.with_udev:
            volumes.update({"/run/udev": {"bind": "/run/udev", "mode": "ro"}})

        # Kernel Modules support
        if self.addon.with_kernel_modules:
            volumes.update({"/lib/modules": {"bind": "/lib/modules", "mode": "ro"}})

        # Docker API support
        if not self.addon.protected and self.addon.access_docker_api:
            volumes.update(
                {"/run/docker.sock": {"bind": "/run/docker.sock", "mode": "ro"}}
            )

        # Host D-Bus system
        if self.addon.host_dbus:
            volumes.update({"/run/dbus": {"bind": "/run/dbus", "mode": "ro"}})

        # Configuration Audio
        if self.addon.with_audio:
            volumes.update(
                {
                    str(self.addon.path_extern_pulse): {
                        "bind": "/etc/pulse/client.conf",
                        "mode": "ro",
                    },
                    str(self.sys_plugins.audio.path_extern_pulse): {
                        "bind": "/run/audio",
                        "mode": "ro",
                    },
                    str(self.sys_plugins.audio.path_extern_asound): {
                        "bind": "/etc/asound.conf",
                        "mode": "ro",
                    },
                }
            )

        return volumes

    def _run(self) -> None:
        """Run Docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # Security check
        if not self.addon.protected:
            _LOGGER.warning("%s running with disabled protected mode!", self.addon.name)

        # Cleanup
        self._stop()

        # Create & Run container
        try:
            docker_container = self.sys_docker.run(
                self.image,
                tag=str(self.addon.version),
                name=self.name,
                hostname=self.addon.hostname,
                detach=True,
                init=self.addon.default_init,
                stdin_open=self.addon.with_stdin,
                network_mode=self.network_mode,
                pid_mode=self.pid_mode,
                ports=self.ports,
                extra_hosts=self.network_mapping,
                device_cgroup_rules=self.cgroups_rules,
                cap_add=self.capabilities,
                security_opt=self.security_opt,
                environment=self.environment,
                volumes=self.volumes,
                tmpfs=self.tmpfs,
            )
        except DockerNotFound:
            self.sys_resolution.create_issue(
                IssueType.MISSING_IMAGE,
                ContextType.ADDON,
                reference=self.addon.slug,
                suggestions=[SuggestionType.EXECUTE_REPAIR],
            )
            raise

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Starting Docker add-on %s with version %s", self.image, self.version
        )

        # Write data to DNS server
        try:
            self.sys_plugins.dns.add_host(
                ipv4=self.ip_address, names=[self.addon.hostname]
            )
        except CoreDNSError as err:
            _LOGGER.warning("Can't update DNS for %s", self.name)
            self.sys_capture_exception(err)

    def _install(
        self, version: AwesomeVersion, image: Optional[str] = None, latest: bool = False
    ) -> None:
        """Pull Docker image or build it.

        Need run inside executor.
        """
        if self.addon.need_build:
            self._build(version)
        else:
            super()._install(version, image, latest)

    def _build(self, version: AwesomeVersion) -> None:
        """Build a Docker container.

        Need run inside executor.
        """
        build_env = AddonBuild(self.coresys, self.addon)
        if not build_env.is_valid:
            _LOGGER.error("Invalid build envoirement, can't build this add-on!")
            raise DockerError()

        _LOGGER.info("Starting build for %s:%s", self.image, version)
        try:
            image, log = self.sys_docker.images.build(
                use_config_proxy=False, **build_env.get_docker_args(version)
            )

            _LOGGER.debug("Build %s:%s done: %s", self.image, version, log)

            # Update meta data
            self._meta = image.attrs

        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Can't build %s:%s: %s", self.image, version, err)
            if hasattr(err, "build_log"):
                log = "\n".join(
                    [
                        x["stream"]
                        for x in err.build_log  # pylint: disable=no-member
                        if isinstance(x, dict) and "stream" in x
                    ]
                )
                _LOGGER.error("Build log: \n%s", log)
            raise DockerError() from err

        _LOGGER.info("Build %s:%s done", self.image, version)

    @process_lock
    def export_image(self, tar_file: Path) -> Awaitable[None]:
        """Export current images into a tar file."""
        return self.sys_run_in_executor(self._export_image, tar_file)

    def _export_image(self, tar_file: Path) -> None:
        """Export current images into a tar file.

        Need run inside executor.
        """
        try:
            image = self.sys_docker.api.get_image(f"{self.image}:{self.version}")
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Can't fetch image %s: %s", self.image, err)
            raise DockerError() from err

        _LOGGER.info("Export image %s to %s", self.image, tar_file)
        try:
            with tar_file.open("wb") as write_tar:
                for chunk in image:
                    write_tar.write(chunk)
        except (OSError, requests.RequestException) as err:
            _LOGGER.error("Can't write tar file %s: %s", tar_file, err)
            raise DockerError() from err

        _LOGGER.info("Export image %s done", self.image)

    @process_lock
    def import_image(self, tar_file: Path) -> Awaitable[None]:
        """Import a tar file as image."""
        return self.sys_run_in_executor(self._import_image, tar_file)

    def _import_image(self, tar_file: Path) -> None:
        """Import a tar file as image.

        Need run inside executor.
        """
        try:
            with tar_file.open("rb") as read_tar:
                self.sys_docker.api.load_image(read_tar, quiet=True)

            docker_image = self.sys_docker.images.get(f"{self.image}:{self.version}")
        except (docker.errors.DockerException, OSError) as err:
            _LOGGER.error("Can't import image %s: %s", self.image, err)
            raise DockerError() from err

        self._meta = docker_image.attrs
        _LOGGER.info("Importing image %s and version %s", tar_file, self.version)

        with suppress(DockerError):
            self._cleanup()

    @process_lock
    def write_stdin(self, data: bytes) -> Awaitable[None]:
        """Write to add-on stdin."""
        return self.sys_run_in_executor(self._write_stdin, data)

    def _write_stdin(self, data: bytes) -> None:
        """Write to add-on stdin.

        Need run inside executor.
        """
        if not self._is_running():
            raise DockerError()

        try:
            # Load needed docker objects
            container = self.sys_docker.containers.get(self.name)
            socket = container.attach_socket(params={"stdin": 1, "stream": 1})
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Can't attach to %s stdin: %s", self.name, err)
            raise DockerError() from err

        try:
            # Write to stdin
            data += b"\n"
            os.write(socket.fileno(), data)
            socket.close()
        except OSError as err:
            _LOGGER.error("Can't write to %s stdin: %s", self.name, err)
            raise DockerError() from err

    def _stop(self, remove_container=True) -> None:
        """Stop/remove Docker container.

        Need run inside executor.
        """
        if self.ip_address != NO_ADDDRESS:
            try:
                self.sys_plugins.dns.delete_host(self.addon.hostname)
            except CoreDNSError as err:
                _LOGGER.warning("Can't update DNS for %s", self.name)
                self.sys_capture_exception(err)
        super()._stop(remove_container)
