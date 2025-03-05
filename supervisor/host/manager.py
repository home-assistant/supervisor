"""Host function like audio, D-Bus or systemd."""

from contextlib import suppress
from functools import lru_cache
import logging
from typing import Self

from awesomeversion import AwesomeVersion

from ..const import BusEvent
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError, HostLogError, PulseAudioError
from ..hardware.const import PolicyGroup
from ..hardware.data import Device
from .apparmor import AppArmorControl
from .const import HostFeature
from .control import SystemControl
from .info import InfoCenter
from .logs import LogsControl
from .network import NetworkManager
from .services import ServiceManager
from .sound import SoundControl

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HostManager(CoreSysAttributes):
    """Manage supported function from host."""

    def __init__(self, coresys: CoreSys):
        """Initialize Host manager."""
        self.coresys: CoreSys = coresys

        self._apparmor: AppArmorControl = AppArmorControl(coresys)
        self._control: SystemControl = SystemControl(coresys)
        self._info: InfoCenter = InfoCenter(coresys)
        self._services: ServiceManager = ServiceManager(coresys)
        self._network: NetworkManager = NetworkManager(coresys)
        self._sound: SoundControl = SoundControl(coresys)
        self._logs: LogsControl = LogsControl(coresys)

    async def post_init(self) -> Self:
        """Post init actions that must occur in event loop."""
        await self._logs.post_init()
        return self

    @property
    def apparmor(self) -> AppArmorControl:
        """Return host AppArmor handler."""
        return self._apparmor

    @property
    def control(self) -> SystemControl:
        """Return host control handler."""
        return self._control

    @property
    def info(self) -> InfoCenter:
        """Return host info handler."""
        return self._info

    @property
    def services(self) -> ServiceManager:
        """Return host services handler."""
        return self._services

    @property
    def network(self) -> NetworkManager:
        """Return host NetworkManager handler."""
        return self._network

    @property
    def sound(self) -> SoundControl:
        """Return host PulseAudio control."""
        return self._sound

    @property
    def logs(self) -> LogsControl:
        """Return host logs handler."""
        return self._logs

    @property
    def features(self) -> list[HostFeature]:
        """Return a list of host features."""
        return self.supported_features()

    @lru_cache(maxsize=128)
    def supported_features(self) -> list[HostFeature]:
        """Return a list of supported host features."""
        features = []

        if self.sys_dbus.systemd.is_connected:
            features.extend(
                [HostFeature.REBOOT, HostFeature.SHUTDOWN, HostFeature.SERVICES]
            )

        if self.sys_dbus.network.is_connected and self.sys_dbus.network.interfaces:
            features.append(HostFeature.NETWORK)

        if self.sys_dbus.hostname.is_connected:
            features.append(HostFeature.HOSTNAME)

        if self.sys_dbus.timedate.is_connected:
            features.append(HostFeature.TIMEDATE)

        if self.sys_dbus.agent.is_connected:
            features.append(HostFeature.OS_AGENT)

        if self.sys_os.available:
            features.append(HostFeature.HAOS)

        if self.sys_dbus.resolved.is_connected:
            features.append(HostFeature.RESOLVED)

        if self.logs.available:
            features.append(HostFeature.JOURNAL)

        if self.sys_dbus.udisks2.is_connected:
            features.append(HostFeature.DISK)

        # Support added in OS10. Propagation mode changed on mount in 10.2 to support this
        if (
            self.sys_dbus.systemd.is_connected
            and self.sys_supervisor.instance.host_mounts_available
            and (
                not self.sys_os.available
                or self.sys_os.version >= AwesomeVersion("10.2")
            )
        ):
            features.append(HostFeature.MOUNT)

        return features

    async def reload(self):
        """Reload host functions."""
        await self.info.update()
        await self.sys_os.reload()

        if self.sys_dbus.systemd.is_connected:
            await self.services.update()

        if self.sys_dbus.network.is_connected:
            await self.network.update()

        if self.sys_dbus.agent.is_connected:
            await self.sys_dbus.agent.update()

        if self.sys_dbus.udisks2.is_connected:
            await self.sys_dbus.udisks2.update()

        with suppress(PulseAudioError):
            await self.sound.update()

        _LOGGER.info("Host information reload completed")
        self.supported_features.cache_clear()  # pylint: disable=no-member

    async def load(self):
        """Load host information."""
        with suppress(HassioError):
            if self.sys_dbus.systemd.is_connected:
                await self.services.update()

            with suppress(PulseAudioError):
                await self.sound.update()

            with suppress(HostLogError):
                await self.logs.load()

            await self.network.load()

        # Register for events
        self.sys_bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, self._hardware_events)
        self.sys_bus.register_event(
            BusEvent.HARDWARE_REMOVE_DEVICE, self._hardware_events
        )

        # Load profile data
        try:
            await self.apparmor.load()
        except HassioError as err:
            _LOGGER.warning("Loading host AppArmor on start failed: %s", err)

    async def _hardware_events(self, device: Device) -> None:
        """Process hardware requests."""
        if self.sys_hardware.policy.is_match_cgroup(PolicyGroup.AUDIO, device):
            await self.sound.update(reload_pulse=True)
