"""Host function like audio, D-Bus or systemd."""
from contextlib import suppress
import logging

from .alsa import AlsaAudio
from .apparmor import AppArmorControl
from .control import SystemControl
from .info import InfoCenter
from .services import ServiceManager
from ..const import (
    FEATURES_REBOOT,
    FEATURES_SHUTDOWN,
    FEATURES_HOSTNAME,
    FEATURES_SERVICES,
    FEATURES_HASSOS,
)
from ..coresys import CoreSysAttributes
from ..exceptions import HassioError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HostManager(CoreSysAttributes):
    """Manage supported function from host."""

    def __init__(self, coresys):
        """Initialize Host manager."""
        self.coresys = coresys
        self._alsa = AlsaAudio(coresys)
        self._apparmor = AppArmorControl(coresys)
        self._control = SystemControl(coresys)
        self._info = InfoCenter(coresys)
        self._services = ServiceManager(coresys)

    @property
    def alsa(self):
        """Return host ALSA handler."""
        return self._alsa

    @property
    def apparmor(self):
        """Return host AppArmor handler."""
        return self._apparmor

    @property
    def control(self):
        """Return host control handler."""
        return self._control

    @property
    def info(self):
        """Return host info handler."""
        return self._info

    @property
    def services(self):
        """Return host services handler."""
        return self._services

    @property
    def supperted_features(self):
        """Return a list of supported host features."""
        features = []

        if self.sys_dbus.systemd.is_connected:
            features.extend([FEATURES_REBOOT, FEATURES_SHUTDOWN, FEATURES_SERVICES])

        if self.sys_dbus.hostname.is_connected:
            features.append(FEATURES_HOSTNAME)

        if self.sys_hassos.available:
            features.append(FEATURES_HASSOS)

        return features

    async def reload(self):
        """Reload host functions."""
        if self.sys_dbus.hostname.is_connected:
            await self.info.update()

        if self.sys_dbus.systemd.is_connected:
            await self.services.update()

    async def load(self):
        """Load host information."""
        with suppress(HassioError):
            await self.reload()

        # Load profile data
        try:
            await self.apparmor.load()
        except HassioError as err:
            _LOGGER.waring("Load host AppArmor on start fails: %s", err)
