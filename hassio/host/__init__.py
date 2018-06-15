"""Host function like audio/dbus/systemd."""

from .alsa import AlsaAudio
from .control import SystemControl
from .info import InfoCenter
from .service import ServiceManager
from ..const import (
    FEATURES_REBOOT, FEATURES_SHUTDOWN, FEATURES_HOSTNAME, FEATURES_SERVICES)
from ..coresys import CoreSysAttributes


class HostManager(CoreSysAttributes):
    """Manage supported function from host."""

    def __init__(self, coresys):
        """Initialize Host manager."""
        self.coresys = coresys
        self._alsa = AlsaAudio(coresys)
        self._control = SystemControl(coresys)
        self._info = InfoCenter(coresys)
        self._service = ServiceManager(coresys)

    @property
    def alsa(self):
        """Return host ALSA handler."""
        return self._alsa

    @property
    def control(self):
        """Return host control handler."""
        return self._control

    @property
    def info(self):
        """Return host info handler."""
        return self._info

    @property
    def service(self):
        """Return host service handler."""
        return self._service

    @property
    def supperted_features(self):
        """Return a list of supported host features."""
        features = []

        if self.sys_dbus.systemd.is_connected:
            features.extend([
                FEATURES_REBOOT,
                FEATURES_SHUTDOWN,
                FEATURES_SERVICES,
            ])

        if self.sys_dbus.hostname.is_connected:
            features.append(FEATURES_HOSTNAME)

        return features

    async def load(self):
        """Load host functions."""
        if self.sys_dbus.hostname.is_connected:
            await self.info.update()

        if self.sys_dbus.systemd.is_connected:
            await self.service.update()

    def reload(self):
        """Reload host information."""
        return self.load()
