"""Init file for Supervisor app Docker object."""

from __future__ import annotations

from contextlib import suppress
from http import HTTPStatus
from ipaddress import IPv4Address
import logging
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING, Any, Literal, cast

import aiodocker
from attr import evolve
from awesomeversion import AwesomeVersion

from ..addons.build import AppBuild
from ..addons.const import MappingType
from ..bus import EventListener
from ..const import (
    DOCKER_CPU_RUNTIME_ALLOCATION,
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
    DockerBuildError,
    DockerError,
    DockerJobError,
    DockerNotFound,
    HardwareNotFound,
)
from ..hardware.const import PolicyGroup
from ..hardware.data import Device
from ..jobs.const import JobConcurrency, JobCondition
from ..jobs.decorator import Job
from ..resolution.const import CGROUP_V2_VERSION, ContextType, IssueType, SuggestionType
from ..utils.sentry import async_capture_exception
from .const import (
    ADDON_BUILDER_IMAGE,
    ENV_TIME,
    ENV_TOKEN,
    ENV_TOKEN_OLD,
    MOUNT_DBUS,
    MOUNT_DEV,
    MOUNT_DOCKER,
    MOUNT_UDEV,
    PATH_ALL_ADDON_CONFIGS,
    PATH_BACKUP,
    PATH_HOMEASSISTANT_CONFIG,
    PATH_HOMEASSISTANT_CONFIG_LEGACY,
    PATH_LOCAL_ADDONS,
    PATH_MEDIA,
    PATH_PRIVATE_DATA,
    PATH_PUBLIC_CONFIG,
    PATH_SHARE,
    PATH_SSL,
    Capabilities,
    DockerMount,
    MountBindOptions,
    MountType,
    PropagationMode,
    Ulimit,
)
from .interface import DockerInterface

if TYPE_CHECKING:
    from ..addons.addon import App


_LOGGER: logging.Logger = logging.getLogger(__name__)

NO_ADDDRESS = IPv4Address("0.0.0.0")


class DockerApp(DockerInterface):
    """Docker Supervisor wrapper for Home Assistant."""

    def __init__(self, coresys: CoreSys, app: App):
        """Initialize Docker Home Assistant wrapper."""
        self.app: App = app
        super().__init__(coresys)

        self._hw_listener: EventListener | None = None

    @staticmethod
    def slug_to_name(slug: str) -> str:
        """Convert slug to container name."""
        return f"addon_{slug}"

    @property
    def image(self) -> str | None:
        """Return name of Docker image."""
        return self.app.image

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP address of this container."""
        if self.app.host_network:
            return self.sys_docker.network.gateway
        if not self._meta:
            return NO_ADDDRESS

        # Extract IP-Address
        try:
            return IPv4Address(
                self._meta["NetworkSettings"]["Networks"]["hassio"]["IPAddress"]
            )
        except KeyError, TypeError, ValueError:
            return NO_ADDDRESS

    @property
    def timeout(self) -> int:
        """Return timeout for Docker actions."""
        return self.app.timeout

    @property
    def version(self) -> AwesomeVersion:
        """Return version of Docker image."""
        return self.app.version

    @property
    def arch(self) -> str | None:
        """Return arch of Docker image."""
        if self.app.legacy:
            return str(self.sys_arch.default)
        return super().arch

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return DockerApp.slug_to_name(self.app.slug)

    @property
    def environment(self) -> dict[str, str | int | None]:
        """Return environment for Docker app."""
        app_env = cast(dict[str, str | int | None], self.app.environment or {})

        # Provide options for legacy apps
        if self.app.legacy:
            for key, value in self.app.options.items():
                if isinstance(value, (int, str)):
                    app_env[key] = value
                else:
                    _LOGGER.warning("Can not set nested option %s as Docker env", key)

        return {
            **app_env,
            ENV_TIME: self.sys_timezone,
            ENV_TOKEN: self.app.supervisor_token,
            ENV_TOKEN_OLD: self.app.supervisor_token,
        }

    @property
    def cgroups_rules(self) -> list[str] | None:
        """Return a list of needed cgroups permission."""
        rules = set()

        # Attach correct cgroups for static devices
        for device_path in self.app.static_devices:
            try:
                device = self.sys_hardware.get_by_path(device_path)
            except HardwareNotFound:
                _LOGGER.debug("Ignore static device path %s", device_path)
                continue

            # Check access
            if not self.sys_hardware.policy.allowed_for_access(device):
                _LOGGER.error(
                    "App %s tried to access blocked device %s!",
                    self.app.name,
                    device.name,
                )
                continue
            rules.add(self.sys_hardware.policy.get_cgroups_rule(device))

        # Attach correct cgroups for devices
        for device in self.app.devices:
            if not self.sys_hardware.policy.allowed_for_access(device):
                _LOGGER.error(
                    "App %s tried to access blocked device %s!",
                    self.app.name,
                    device.name,
                )
                continue
            rules.add(self.sys_hardware.policy.get_cgroups_rule(device))

        # Video
        if self.app.with_video:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.VIDEO))

        # GPIO
        if self.app.with_gpio:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.GPIO))

        # UART
        if self.app.with_uart:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.UART))

        # USB
        if self.app.with_usb:
            rules.update(self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.USB))

        # Full Access
        if not self.app.protected and self.app.with_full_access:
            return [self.sys_hardware.policy.get_full_access()]

        # Return None if no rules is present
        if rules:
            return list(rules)
        return None

    @property
    def ports(self) -> dict[str, str | int | None] | None:
        """Filter None from app ports."""
        if self.app.host_network or not self.app.ports:
            return None

        return {
            container_port: host_port
            for container_port, host_port in self.app.ports.items()
            if host_port
        }

    @property
    def security_opt(self) -> list[str]:
        """Control security options."""
        security = super().security_opt

        # AppArmor
        if (
            not self.sys_host.apparmor.available
            or self.app.apparmor == SECURITY_DISABLE
        ):
            security.append("apparmor=unconfined")
        elif self.app.apparmor == SECURITY_PROFILE:
            security.append(f"apparmor={self.app.slug}")

        return security

    @property
    def tmpfs(self) -> dict[str, str] | None:
        """Return tmpfs for Docker app."""
        tmpfs = {}

        if self.app.with_tmpfs:
            tmpfs["/tmp"] = ""  # noqa: S108

        if not self.app.host_ipc:
            tmpfs["/dev/shm"] = ""  # noqa: S108

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
    def network_mode(self) -> Literal["host"] | None:
        """Return network mode for app."""
        if self.app.host_network:
            return "host"
        return None

    @property
    def pid_mode(self) -> str | None:
        """Return PID mode for app."""
        if not self.app.protected and self.app.host_pid:
            return "host"
        return None

    @property
    def uts_mode(self) -> str | None:
        """Return UTS mode for app."""
        if self.app.host_uts:
            return "host"
        return None

    @property
    def capabilities(self) -> list[Capabilities] | None:
        """Generate needed capabilities."""
        capabilities: set[Capabilities] = set(self.app.privileged)

        # Need work with kernel modules
        if self.app.with_kernel_modules:
            capabilities.add(Capabilities.SYS_MODULE)

        # Need schedule functions
        if self.app.with_realtime:
            capabilities.add(Capabilities.SYS_NICE)

        # Return None if no capabilities is present
        if capabilities:
            return list(capabilities)
        return None

    @property
    def ulimits(self) -> list[Ulimit] | None:
        """Generate ulimits for app."""
        limits: list[Ulimit] = []

        # Need schedule functions
        if self.app.with_realtime:
            limits.append(Ulimit(name="rtprio", soft=90, hard=99))

            # Set available memory for memlock to 128MB
            mem = 128 * 1024 * 1024
            limits.append(Ulimit(name="memlock", soft=mem, hard=mem))

        # Add configurable ulimits from app config
        for name, config in self.app.ulimits.items():
            if isinstance(config, int):
                # Simple format: both soft and hard limits are the same
                limits.append(Ulimit(name=name, soft=config, hard=config))
            elif isinstance(config, dict):
                # Detailed format: both soft and hard limits are mandatory
                soft = config["soft"]
                hard = config["hard"]
                limits.append(Ulimit(name=name, soft=soft, hard=hard))

        # Return None if no ulimits are present
        if limits:
            return limits
        return None

    @property
    def cpu_rt_runtime(self) -> int | None:
        """Limit CPU real-time runtime in microseconds."""
        if not self.sys_docker.info.support_cpu_realtime:
            return None

        # If need CPU RT
        if self.app.with_realtime:
            return DOCKER_CPU_RUNTIME_ALLOCATION
        return None

    @property
    def mounts(self) -> list[DockerMount]:
        """Return mounts for container."""
        app_mapping = self.app.map_volumes

        target_data_path: str | None = None
        if MappingType.DATA in app_mapping:
            target_data_path = app_mapping[MappingType.DATA].path

        mounts = [
            MOUNT_DEV,
            DockerMount(
                type=MountType.BIND,
                source=self.app.path_extern_data.as_posix(),
                target=target_data_path or PATH_PRIVATE_DATA.as_posix(),
                read_only=False,
            ),
        ]

        # setup config mappings
        if MappingType.CONFIG in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_homeassistant.as_posix(),
                    target=app_mapping[MappingType.CONFIG].path
                    or PATH_HOMEASSISTANT_CONFIG_LEGACY.as_posix(),
                    read_only=app_mapping[MappingType.CONFIG].read_only,
                )
            )

        else:
            # Map app's public config folder if not using deprecated config option
            if self.app.app_config_used:
                mounts.append(
                    DockerMount(
                        type=MountType.BIND,
                        source=self.app.path_extern_config.as_posix(),
                        target=app_mapping[MappingType.ADDON_CONFIG].path
                        or PATH_PUBLIC_CONFIG.as_posix(),
                        read_only=app_mapping[MappingType.ADDON_CONFIG].read_only,
                    )
                )

            # Map Home Assistant config in new way
            if MappingType.HOMEASSISTANT_CONFIG in app_mapping:
                mounts.append(
                    DockerMount(
                        type=MountType.BIND,
                        source=self.sys_config.path_extern_homeassistant.as_posix(),
                        target=app_mapping[MappingType.HOMEASSISTANT_CONFIG].path
                        or PATH_HOMEASSISTANT_CONFIG.as_posix(),
                        read_only=app_mapping[
                            MappingType.HOMEASSISTANT_CONFIG
                        ].read_only,
                    )
                )

        if MappingType.ALL_ADDON_CONFIGS in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_app_configs.as_posix(),
                    target=app_mapping[MappingType.ALL_ADDON_CONFIGS].path
                    or PATH_ALL_ADDON_CONFIGS.as_posix(),
                    read_only=app_mapping[MappingType.ALL_ADDON_CONFIGS].read_only,
                )
            )

        if MappingType.SSL in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_ssl.as_posix(),
                    target=app_mapping[MappingType.SSL].path or PATH_SSL.as_posix(),
                    read_only=app_mapping[MappingType.SSL].read_only,
                )
            )

        if MappingType.ADDONS in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_apps_local.as_posix(),
                    target=app_mapping[MappingType.ADDONS].path
                    or PATH_LOCAL_ADDONS.as_posix(),
                    read_only=app_mapping[MappingType.ADDONS].read_only,
                )
            )

        if MappingType.BACKUP in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_backup.as_posix(),
                    target=app_mapping[MappingType.BACKUP].path
                    or PATH_BACKUP.as_posix(),
                    read_only=app_mapping[MappingType.BACKUP].read_only,
                )
            )

        if MappingType.SHARE in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_share.as_posix(),
                    target=app_mapping[MappingType.SHARE].path or PATH_SHARE.as_posix(),
                    read_only=app_mapping[MappingType.SHARE].read_only,
                    bind_options=MountBindOptions(propagation=PropagationMode.RSLAVE),
                )
            )

        if MappingType.MEDIA in app_mapping:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_media.as_posix(),
                    target=app_mapping[MappingType.MEDIA].path or PATH_MEDIA.as_posix(),
                    read_only=app_mapping[MappingType.MEDIA].read_only,
                    bind_options=MountBindOptions(propagation=PropagationMode.RSLAVE),
                )
            )

        # Init other hardware mappings

        # GPIO support
        if self.app.with_gpio and self.sys_hardware.helper.support_gpio:
            for gpio_path in ("/sys/class/gpio", "/sys/devices/platform/soc"):
                if not Path(gpio_path).exists():
                    continue
                mounts.append(
                    DockerMount(
                        type=MountType.BIND,
                        source=gpio_path,
                        target=gpio_path,
                        read_only=False,
                    )
                )

        # DeviceTree support
        if self.app.with_devicetree:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source="/sys/firmware/devicetree/base",
                    target="/device-tree",
                    read_only=True,
                )
            )

        # Host udev support
        if self.app.with_udev:
            mounts.append(MOUNT_UDEV)

        # Kernel Modules support
        if self.app.with_kernel_modules:
            mounts.append(
                DockerMount(
                    type=MountType.BIND,
                    source="/lib/modules",
                    target="/lib/modules",
                    read_only=True,
                )
            )

        # Docker API support
        if not self.app.protected and self.app.access_docker_api:
            mounts.append(MOUNT_DOCKER)

        # Host D-Bus system
        if self.app.host_dbus:
            mounts.append(MOUNT_DBUS)

        # Configuration Audio
        if self.app.with_audio:
            mounts += [
                DockerMount(
                    type=MountType.BIND,
                    source=self.app.path_extern_pulse.as_posix(),
                    target="/etc/pulse/client.conf",
                    read_only=True,
                ),
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_plugins.audio.path_extern_pulse.as_posix(),
                    target="/run/audio",
                    read_only=True,
                ),
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_plugins.audio.path_extern_asound.as_posix(),
                    target="/etc/asound.conf",
                    read_only=True,
                ),
            ]

        # System Journal access
        if self.app.with_journald:
            mounts += [
                DockerMount(
                    type=MountType.BIND,
                    source=SYSTEMD_JOURNAL_PERSISTENT.as_posix(),
                    target=SYSTEMD_JOURNAL_PERSISTENT.as_posix(),
                    read_only=True,
                ),
                DockerMount(
                    type=MountType.BIND,
                    source=SYSTEMD_JOURNAL_VOLATILE.as_posix(),
                    target=SYSTEMD_JOURNAL_VOLATILE.as_posix(),
                    read_only=True,
                ),
            ]

        return mounts

    @Job(
        name="docker_addon_run",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def run(self) -> None:
        """Run Docker image."""
        # Security check
        if not self.app.protected:
            _LOGGER.warning("%s running with disabled protected mode!", self.app.name)

        # Don't set a hostname if no separate UTS namespace is used
        hostname = None if self.uts_mode else self.app.hostname

        # Create & Run container
        try:
            await self._run(
                tag=str(self.app.version),
                name=self.name,
                hostname=hostname,
                detach=True,
                init=self.app.default_init,
                stdin_open=self.app.with_stdin,
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
                reference=self.app.slug,
                suggestions=[SuggestionType.EXECUTE_REPAIR],
            )
            raise

        _LOGGER.info("Starting Docker app %s with version %s", self.image, self.version)

        # Write data to DNS server
        try:
            await self.sys_plugins.dns.add_host(
                ipv4=self.ip_address, names=[self.app.hostname]
            )
        except CoreDNSError as err:
            _LOGGER.warning("Can't update DNS for %s", self.name)
            await async_capture_exception(err)

        # Hardware Access
        if self.app.static_devices:
            self._hw_listener = self.sys_bus.register_event(
                BusEvent.HARDWARE_NEW_DEVICE, self._hardware_events
            )

    @Job(
        name="docker_addon_update",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def update(
        self,
        version: AwesomeVersion,
        image: str | None = None,
        latest: bool = False,
        arch: CpuArch | None = None,
    ) -> None:
        """Update a docker image."""
        image = image or self.image

        _LOGGER.info(
            "Updating image %s:%s to %s:%s", self.image, self.version, image, version
        )

        # Update docker image
        await self.install(
            version,
            image=image,
            latest=latest,
            arch=arch,
            need_build=self.app.latest_need_build,
        )

    @Job(
        name="docker_addon_install",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
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
        if need_build is None and self.app.need_build or need_build:
            await self._build(version, image)
        else:
            await super().install(version, image, latest, arch)

    async def _build(self, version: AwesomeVersion, image: str | None = None) -> None:
        """Build a Docker container."""
        build_env = await AppBuild.create(self.coresys, self.app)
        # Check if the build environment is valid, raises if not
        await build_env.is_valid()

        _LOGGER.info("Starting build for %s:%s", self.image, version)

        app_image_tag = f"{image or self.app.image}:{version!s}"

        docker_version = self.sys_docker.info.version
        builder_version_tag = (
            f"{docker_version.major}.{docker_version.minor}.{docker_version.micro}-cli"
        )

        builder_name = f"addon_builder_{self.app.slug}"

        # Remove dangling builder container if it exists by any chance
        # E.g. because of an abrupt host shutdown/reboot during a build
        try:
            container = await self.sys_docker.containers.get(builder_name)
            await container.delete(force=True, v=True)
        except aiodocker.DockerError as err:
            if err.status != HTTPStatus.NOT_FOUND:
                raise DockerBuildError(
                    f"Can't clean up existing builder container: {err!s}", _LOGGER.error
                ) from err

        # Generate Docker config with registry credentials for base image if needed
        docker_config_content = build_env.get_docker_config_json()
        temp_dir: tempfile.TemporaryDirectory | None = None

        try:

            def pre_build_setup() -> tuple[
                tempfile.TemporaryDirectory | None, dict[str, Any]
            ]:
                docker_config_path: Path | None = None
                temp_dir: tempfile.TemporaryDirectory | None = None
                if docker_config_content:
                    # Create temporary directory for docker config
                    temp_dir = tempfile.TemporaryDirectory(
                        prefix="hassio_build_", dir=self.sys_config.path_tmp
                    )
                    docker_config_path = Path(temp_dir.name) / "config.json"
                    docker_config_path.write_text(
                        docker_config_content, encoding="utf-8"
                    )
                    _LOGGER.debug(
                        "Created temporary Docker config for build at %s",
                        docker_config_path,
                    )

                return (
                    temp_dir,
                    build_env.get_docker_args(
                        version, app_image_tag, docker_config_path
                    ),
                )

            temp_dir, build_args = await self.sys_run_in_executor(pre_build_setup)

            result = await self.sys_docker.run_command(
                ADDON_BUILDER_IMAGE,
                tag=builder_version_tag,
                name=builder_name,
                **build_args,
            )
        except DockerError as err:
            raise DockerBuildError(
                f"Can't build {self.image}:{version}: {err!s}", _LOGGER.error
            ) from err
        finally:
            # Clean up temporary directory
            if temp_dir:
                await self.sys_run_in_executor(temp_dir.cleanup)

        logs = "".join(result.log)
        if result.exit_code != 0:
            raise DockerBuildError(
                f"Docker build failed for {app_image_tag} (exit code {result.exit_code}). Build output:\n{logs}",
                _LOGGER.error,
            )

        _LOGGER.debug("Build %s:%s done: %s", self.image, version, logs)

        try:
            # Update meta data
            self._meta = await self.sys_docker.images.inspect(app_image_tag)
        except aiodocker.DockerError as err:
            raise DockerBuildError(
                f"Can't get image metadata for {app_image_tag} after build: {err!s}"
            ) from err

        _LOGGER.info("Build %s:%s done", self.image, version)

        # Clean up old add-on builder images from previous Docker versions.
        # Done here after build because cleanup_old_images needs the current
        # image to exist, and the builder image is only pulled on first build
        # (in run_command) after a Docker engine update.
        with suppress(DockerError):
            await self.sys_docker.cleanup_old_images(
                ADDON_BUILDER_IMAGE, AwesomeVersion(builder_version_tag)
            )

    async def export_image(self, tar_file: Path) -> None:
        """Export current images into a tar file."""
        if not self.image:
            raise RuntimeError("Cannot export without image!")
        await self.sys_docker.export_image(self.image, self.version, tar_file)

    @Job(
        name="docker_addon_import_image",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def import_image(self, tar_file: Path) -> None:
        """Import a tar file as image."""
        if docker_image := await self.sys_docker.import_image(tar_file):
            self._meta = docker_image
            _LOGGER.info("Importing image %s and version %s", tar_file, self.version)

            with suppress(DockerError):
                await self.cleanup()

    @Job(name="docker_addon_cleanup", concurrency=JobConcurrency.GROUP_QUEUE)
    async def cleanup(
        self,
        old_image: str | None = None,
        image: str | None = None,
        version: AwesomeVersion | None = None,
    ) -> None:
        """Check if old version exists and cleanup other versions of image not in use."""
        if not (use_image := image or self.image):
            raise DockerError("Cannot determine image from metadata!", _LOGGER.error)
        if not (use_version := version or self.version):
            raise DockerError("Cannot determine version from metadata!", _LOGGER.error)

        await self.sys_docker.cleanup_old_images(
            use_image,
            use_version,
            {old_image} if old_image else None,
            keep_images={
                f"{app.image}:{app.version}"
                for app in self.sys_apps.installed
                if app.slug != self.app.slug
                and app.image
                and app.image in {old_image, use_image}
            },
        )

    @Job(
        name="docker_addon_write_stdin",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def write_stdin(self, data: bytes) -> None:
        """Write to app stdin."""
        try:
            # Load needed docker objects
            container = await self.sys_docker.containers.get(self.name)
            socket = container.attach(stdin=True)
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't attach to {self.name} stdin: {err!s}", _LOGGER.error
            ) from err

        try:
            await socket.write_in(data + b"\n")
            await socket.close()
        # Seems to raise very generic exceptions like RuntimeError or AssertionError
        # So we catch all exceptions and re-raise them as DockerError
        except Exception as err:
            raise DockerError(
                f"Can't write to {self.name} stdin: {err!s}", _LOGGER.error
            ) from err

    @Job(
        name="docker_addon_stop",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def stop(self, remove_container: bool = True) -> None:
        """Stop/remove Docker container."""
        # DNS
        if self.ip_address != NO_ADDDRESS:
            try:
                await self.sys_plugins.dns.delete_host(self.app.hostname)
            except CoreDNSError as err:
                _LOGGER.warning("Can't update DNS for %s", self.name)
                await async_capture_exception(err)

        # Hardware
        if self._hw_listener:
            self.sys_bus.remove_listener(self._hw_listener)
            self._hw_listener = None

        await super().stop(remove_container)

        # If there is a device access issue and the container is removed, clear it
        if remove_container and (
            issue := self.sys_resolution.get_issue_if_present(
                self.app.device_access_missing_issue
            )
        ):
            self.sys_resolution.dismiss_issue(issue)

    @Job(
        name="docker_addon_hardware_events",
        conditions=[JobCondition.OS_AGENT],
        internal=True,
        concurrency=JobConcurrency.QUEUE,
    )
    async def _hardware_events(self, device: Device) -> None:
        """Process Hardware events for adjust device access."""
        if not any(
            device_path in (device.path, device.sysfs)
            for device_path in self.app.static_devices
        ):
            return

        try:
            docker_container = await self.sys_docker.containers.get(self.name)
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.NOT_FOUND:
                if self._hw_listener:
                    self.sys_bus.remove_listener(self._hw_listener)
                self._hw_listener = None
                return
            raise DockerError(
                f"Can't process Hardware Event on {self.name}: {err!s}", _LOGGER.error
            ) from err

        if (
            self.sys_docker.info.cgroup == CGROUP_V2_VERSION
            and not self.sys_os.available
        ):
            self.sys_resolution.add_issue(
                evolve(self.app.device_access_missing_issue),
                suggestions=[SuggestionType.EXECUTE_RESTART],
            )
            return

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
