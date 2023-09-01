"""Init file for Supervisor add-on Docker object."""
from __future__ import annotations

from collections.abc import Awaitable
from contextlib import suppress
from ipaddress import IPv4Address, ip_address
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from awesomeversion import AwesomeVersion
import docker
from docker.types import Mount
import requests

from ..addons.build import AddonBuild
from ..bus import EventListener
from ..const import (
    DOCKER_CPU_RUNTIME_ALLOCATION,
    MAP_ADDONS,
    MAP_BACKUP,
    MAP_CONFIG,
    MAP_MEDIA,
    MAP_SHARE,
    MAP_SSL,
    SECURITY_DISABLE,
    SECURITY_PROFILE,
    SYSTEMD_JOURNAL_PERSISTENT,
    SYSTEMD_JOURNAL_VOLATILE,
    BusEvent,
    CpuArch,
)
from ..coresys import CoreSys
from ..exceptions import (
    CoreDNSError,
    DBusError,
    DockerError,
    DockerJobError,
    DockerNotFound,
    HardwareNotFound,
)
from ..hardware.const import PolicyGroup
from ..hardware.data import Device
from ..jobs.const import JobCondition, JobExecutionLimit
from ..jobs.decorator import Job
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.sentry import capture_exception
from .const import (
    ENV_TIME,
    ENV_TOKEN,
    ENV_TOKEN_OLD,
    MOUNT_DBUS,
    MOUNT_DEV,
    MOUNT_DOCKER,
    MOUNT_UDEV,
    Capabilities,
    MountType,
    PropagationMode,
)
from .interface import DockerInterface

if TYPE_CHECKING:
    from ..addons.addon import Addon


_LOGGER: logging.Logger = logging.getLogger(__name__)

NO_ADDDRESS = ip_address("0.0.0.0")


class DockerAddon(DockerInterface):
    """Docker Supervisor wrapper for Home Assistant."""

    def __init__(self, coresys: CoreSys, addon: Addon):
        """Initialize Docker Home Assistant wrapper."""
        self.addon: Addon = addon
        super().__init__(coresys)

        self._hw_listener: EventListener | None = None

    @staticmethod
    def slug_to_name(slug: str) -> str:
        """Convert slug to container name."""
        return f"addon_{slug}"

    @property
    def image(self) -> str | None:
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
        return self.addon.version

    @property
    def arch(self) -> str:
        """Return arch of Docker image."""
        if self.addon.legacy:
            return self.sys_arch.default
        return super().arch

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return DockerAddon.slug_to_name(self.addon.slug)

    @property
    def environment(self) -> dict[str, str | None]:
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
            ENV_TIME: self.sys_timezone,
            ENV_TOKEN: self.addon.supervisor_token,
            ENV_TOKEN_OLD: self.addon.supervisor_token,
        }

    @property
    def cgroups_rules(self) -> list[str] | None:
        """Return a list of needed cgroups permission."""
        rules = set()

        # Attach correct cgroups for static devices
        for device_path in self.addon.static_devices:
            try:
                device = self.sys_hardware.get_by_path(device_path)
            except HardwareNotFound:
                _LOGGER.debug("Ignore static device path %s", device_path)
                continue

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
            return [self.sys_hardware.policy.get_full_access()]

        # Return None if no rules is present
        if rules:
            return list(rules)
        return None

    @property
    def ports(self) -> dict[str, str | int | None] | None:
        """Filter None from add-on ports."""
        if self.addon.host_network or not self.addon.ports:
            return None

        return {
            container_port: host_port
            for container_port, host_port in self.addon.ports.items()
            if host_port
        }

    @property
    def security_opt(self) -> list[str]:
        """Control security options."""
        security = super().security_opt

        # AppArmor
        if (
            not self.sys_host.apparmor.available
            or self.addon.apparmor == SECURITY_DISABLE
        ):
            security.append("apparmor=unconfined")
        elif self.addon.apparmor == SECURITY_PROFILE:
            security.append(f"apparmor={self.addon.slug}")

        return security

    @property
    def tmpfs(self) -> dict[str, str] | None:
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
    def network_mapping(self) -> dict[str, IPv4Address]:
        """Return hosts mapping."""
        return {
            "supervisor": self.sys_docker.network.supervisor,
            "hassio": self.sys_docker.network.supervisor,
        }

    @property
    def network_mode(self) -> str | None:
        """Return network mode for add-on."""
        if self.addon.host_network:
            return "host"
        return None

    @property
    def pid_mode(self) -> str | None:
        """Return PID mode for add-on."""
        if not self.addon.protected and self.addon.host_pid:
            return "host"
        return None

    @property
    def uts_mode(self) -> str | None:
        """Return UTS mode for add-on."""
        if self.addon.host_uts:
            return "host"
        return None

    @property
    def capabilities(self) -> list[Capabilities] | None:
        """Generate needed capabilities."""
        capabilities: set[Capabilities] = set(self.addon.privileged)

        # Need work with kernel modules
        if self.addon.with_kernel_modules:
            capabilities.add(Capabilities.SYS_MODULE)

        # Need schedule functions
        if self.addon.with_realtime:
            capabilities.add(Capabilities.SYS_NICE)

        # Return None if no capabilities is present
        if capabilities:
            return list(capabilities)
        return None

    @property
    def ulimits(self) -> list[docker.types.Ulimit] | None:
        """Generate ulimits for add-on."""
        limits: list[docker.types.Ulimit] = []

        # Need schedule functions
        if self.addon.with_realtime:
            limits.append(docker.types.Ulimit(name="rtprio", soft=90, hard=99))

            # Set available memory for memlock to 128MB
            mem = 128 * 1024 * 1024
            limits.append(docker.types.Ulimit(name="memlock", soft=mem, hard=mem))

        # Return None if no capabilities is present
        if limits:
            return limits
        return None

    @property
    def cpu_rt_runtime(self) -> int | None:
        """Limit CPU real-time runtime in microseconds."""
        if not self.sys_docker.info.support_cpu_realtime:
            return None

        # If need CPU RT
        if self.addon.with_realtime:
            return DOCKER_CPU_RUNTIME_ALLOCATION
        return None

    @property
    def mounts(self) -> list[Mount]:
        """Return mounts for container."""
        addon_mapping = self.addon.map_volumes

        mounts = [
            MOUNT_DEV,
            Mount(
                type=MountType.BIND,
                source=self.addon.path_extern_data.as_posix(),
                target="/data",
                read_only=False,
            ),
        ]

        # setup config mappings
        if MAP_CONFIG in addon_mapping:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_homeassistant.as_posix(),
                    target="/config",
                    read_only=addon_mapping[MAP_CONFIG],
                )
            )

        if MAP_SSL in addon_mapping:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_ssl.as_posix(),
                    target="/ssl",
                    read_only=addon_mapping[MAP_SSL],
                )
            )

        if MAP_ADDONS in addon_mapping:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_addons_local.as_posix(),
                    target="/addons",
                    read_only=addon_mapping[MAP_ADDONS],
                )
            )

        if MAP_BACKUP in addon_mapping:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_backup.as_posix(),
                    target="/backup",
                    read_only=addon_mapping[MAP_BACKUP],
                )
            )

        if MAP_SHARE in addon_mapping:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_share.as_posix(),
                    target="/share",
                    read_only=addon_mapping[MAP_SHARE],
                    propagation=PropagationMode.RSLAVE,
                )
            )

        if MAP_MEDIA in addon_mapping:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_media.as_posix(),
                    target="/media",
                    read_only=addon_mapping[MAP_MEDIA],
                    propagation=PropagationMode.RSLAVE,
                )
            )

        # Init other hardware mappings

        # GPIO support
        if self.addon.with_gpio and self.sys_hardware.helper.support_gpio:
            for gpio_path in ("/sys/class/gpio", "/sys/devices/platform/soc"):
                if not Path(gpio_path).exists():
                    continue
                mounts.append(
                    Mount(
                        type=MountType.BIND,
                        source=gpio_path,
                        target=gpio_path,
                        read_only=False,
                    )
                )

        # DeviceTree support
        if self.addon.with_devicetree:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source="/sys/firmware/devicetree/base",
                    target="/device-tree",
                    read_only=True,
                )
            )

        # Host udev support
        if self.addon.with_udev:
            mounts.append(MOUNT_UDEV)

        # Kernel Modules support
        if self.addon.with_kernel_modules:
            mounts.append(
                Mount(
                    type=MountType.BIND,
                    source="/lib/modules",
                    target="/lib/modules",
                    read_only=True,
                )
            )

        # Docker API support
        if not self.addon.protected and self.addon.access_docker_api:
            mounts.append(MOUNT_DOCKER)

        # Host D-Bus system
        if self.addon.host_dbus:
            mounts.append(MOUNT_DBUS)

        # Configuration Audio
        if self.addon.with_audio:
            mounts += [
                Mount(
                    type=MountType.BIND,
                    source=self.addon.path_extern_pulse.as_posix(),
                    target="/etc/pulse/client.conf",
                    read_only=True,
                ),
                Mount(
                    type=MountType.BIND,
                    source=self.sys_plugins.audio.path_extern_pulse.as_posix(),
                    target="/run/audio",
                    read_only=True,
                ),
                Mount(
                    type=MountType.BIND,
                    source=self.sys_plugins.audio.path_extern_asound.as_posix(),
                    target="/etc/asound.conf",
                    read_only=True,
                ),
            ]

        # System Journal access
        if self.addon.with_journald:
            mounts += [
                Mount(
                    type=MountType.BIND,
                    source=SYSTEMD_JOURNAL_PERSISTENT.as_posix(),
                    target=SYSTEMD_JOURNAL_PERSISTENT.as_posix(),
                    read_only=True,
                ),
                Mount(
                    type=MountType.BIND,
                    source=SYSTEMD_JOURNAL_VOLATILE.as_posix(),
                    target=SYSTEMD_JOURNAL_VOLATILE.as_posix(),
                    read_only=True,
                ),
            ]

        return mounts

    @Job(
        name="docker_addon_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        if await self.is_running():
            return

        # Security check
        if not self.addon.protected:
            _LOGGER.warning("%s running with disabled protected mode!", self.addon.name)

        # Cleanup
        await self.stop()

        # Don't set a hostname if no separate UTS namespace is used
        hostname = None if self.uts_mode else self.addon.hostname

        # Create & Run container
        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.run,
                self.image,
                tag=str(self.addon.version),
                name=self.name,
                hostname=hostname,
                detach=True,
                init=self.addon.default_init,
                stdin_open=self.addon.with_stdin,
                network_mode=self.network_mode,
                pid_mode=self.pid_mode,
                uts_mode=self.uts_mode,
                ports=self.ports,
                extra_hosts=self.network_mapping,
                device_cgroup_rules=self.cgroups_rules,
                cap_add=self.capabilities,
                ulimits=self.ulimits,
                cpu_rt_runtime=self.cpu_rt_runtime,
                security_opt=self.security_opt,
                environment=self.environment,
                mounts=self.mounts,
                tmpfs=self.tmpfs,
                oom_score_adj=200,
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
            await self.sys_plugins.dns.add_host(
                ipv4=self.ip_address, names=[self.addon.hostname]
            )
        except CoreDNSError as err:
            _LOGGER.warning("Can't update DNS for %s", self.name)
            capture_exception(err)

        # Hardware Access
        if self.addon.static_devices:
            self._hw_listener = self.sys_bus.register_event(
                BusEvent.HARDWARE_NEW_DEVICE, self._hardware_events
            )

    @Job(
        name="docker_addon_update",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def update(
        self, version: AwesomeVersion, image: str | None = None, latest: bool = False
    ) -> None:
        """Update a docker image."""
        image = image or self.image

        _LOGGER.info(
            "Updating image %s:%s to %s:%s", self.image, self.version, image, version
        )

        # Update docker image
        await self.install(
            version, image=image, latest=latest, need_build=self.addon.latest_need_build
        )

        # Stop container & cleanup
        with suppress(DockerError):
            await self.stop()

    @Job(
        name="docker_addon_install",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def install(
        self,
        version: AwesomeVersion,
        image: str | None = None,
        latest: bool = False,
        arch: CpuArch | None = None,
        *,
        need_build: bool | None = None,
    ) -> None:
        """Pull Docker image or build it."""
        if need_build is None and self.addon.need_build or need_build:
            await self._build(version)
        else:
            await super().install(version, image, latest, arch)

    async def _build(self, version: AwesomeVersion) -> None:
        """Build a Docker container."""
        build_env = AddonBuild(self.coresys, self.addon)
        if not build_env.is_valid:
            _LOGGER.error("Invalid build environment, can't build this add-on!")
            raise DockerError()

        _LOGGER.info("Starting build for %s:%s", self.image, version)
        try:
            image, log = await self.sys_run_in_executor(
                self.sys_docker.images.build,
                use_config_proxy=False,
                **build_env.get_docker_args(version),
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

    @Job(
        name="docker_addon_export_image",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    def export_image(self, tar_file: Path) -> Awaitable[None]:
        """Export current images into a tar file."""
        return self.sys_run_in_executor(
            self.sys_docker.export_image, self.image, self.version, tar_file
        )

    @Job(
        name="docker_addon_import_image",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def import_image(self, tar_file: Path) -> None:
        """Import a tar file as image."""
        docker_image = await self.sys_run_in_executor(
            self.sys_docker.import_image, tar_file
        )
        if docker_image:
            self._meta = docker_image.attrs
            _LOGGER.info("Importing image %s and version %s", tar_file, self.version)

            with suppress(DockerError):
                await self.cleanup()

    @Job(
        name="docker_addon_write_stdin",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def write_stdin(self, data: bytes) -> None:
        """Write to add-on stdin."""
        if not await self.is_running():
            raise DockerError()

        await self.sys_run_in_executor(self._write_stdin, data)

    def _write_stdin(self, data: bytes) -> None:
        """Write to add-on stdin.

        Need run inside executor.
        """
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

    @Job(
        name="docker_addon_stop",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def stop(self, remove_container: bool = True) -> None:
        """Stop/remove Docker container."""
        # DNS
        if self.ip_address != NO_ADDDRESS:
            try:
                await self.sys_plugins.dns.delete_host(self.addon.hostname)
            except CoreDNSError as err:
                _LOGGER.warning("Can't update DNS for %s", self.name)
                capture_exception(err)

        # Hardware
        if self._hw_listener:
            self.sys_bus.remove_listener(self._hw_listener)
            self._hw_listener = None

        await super().stop(remove_container)

    async def _validate_trust(
        self, image_id: str, image: str, version: AwesomeVersion
    ) -> None:
        """Validate trust of content."""
        if not self.addon.signed:
            return

        checksum = image_id.partition(":")[2]
        return await self.sys_security.verify_content(self.addon.codenotary, checksum)

    @Job(
        name="docker_addon_hardware_events",
        conditions=[JobCondition.OS_AGENT],
        limit=JobExecutionLimit.SINGLE_WAIT,
        internal=True,
    )
    async def _hardware_events(self, device: Device) -> None:
        """Process Hardware events for adjust device access."""
        if not any(
            device_path in (device.path, device.sysfs)
            for device_path in self.addon.static_devices
        ):
            return

        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.containers.get, self.name
            )
        except docker.errors.NotFound:
            self.sys_bus.remove_listener(self._hw_listener)
            self._hw_listener = None
            return
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't process Hardware Event on {self.name}: {err!s}", _LOGGER.error
            ) from err

        permission = self.sys_hardware.policy.get_cgroups_rule(device)
        try:
            await self.sys_dbus.agent.cgroup.add_devices_allowed(
                docker_container.id, permission
            )
            _LOGGER.info(
                "Added cgroup permissions '%s' for device %s to %s",
                permission,
                device.path,
                self.name,
            )
        except DBusError as err:
            raise DockerError(
                f"Can't set cgroup permission '{permission}' on the host for {self.name}",
                _LOGGER.error,
            ) from err
