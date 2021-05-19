"""Host function like audio, D-Bus or systemd."""
from contextlib import suppress
from functools import lru_cache
import logging
from typing import List

from ..const import HostFeature
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError, PulseAudioError
from .apparmor import AppArmorControl
from .control import SystemControl
from .info import InfoCenter
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
    def features(self) -> List[HostFeature]:
        """Return a list of host features."""
        return self.supported_features()

    @lru_cache
    def supported_features(self) -> List[HostFeature]:
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

        if self.sys_hassos.available:
            features.append(HostFeature.HASSOS)

        return features

    async def reload(self):
        """Reload host functions."""
        if self.sys_dbus.hostname.is_connected:
            await self.info.update()

        if self.sys_dbus.systemd.is_connected:
            await self.services.update()

        if self.sys_dbus.network.is_connected:
            await self.network.update()

        with suppress(PulseAudioError):
            await self.sound.update()

        _LOGGER.info("Host information reload completed")
        self.supported_features.cache_clear()  # pylint: disable=no-member

    async def load(self):
        """Load host information."""
        with suppress(HassioError):
            await self.reload()

        # Load profile data
        try:
            await self.apparmor.load()
        except HassioError as err:
            _LOGGER.warning("Loading host AppArmor on start failed: %s", err)
