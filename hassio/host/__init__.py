"""Host function like audio/dbus/systemd."""

from .alsa import AlsaAudio
from .power import PowerControl
from .local import LocalCenter
from ..const import FEATURES_REBOOT, FEATURES_SHUTDOWN, FEATURES_HOSTNAME
from ..coresys import CoreSysAttributes


class HostManager(CoreSysAttributes):
    """Manage supported function from host."""

    def __init__(self, coresys):
        """Initialize Host manager."""
        self.coresys = coresys
        self._alsa = AlsaAudio(coresys)
        self._power = PowerControl(coresys)
        self._local = LocalCenter(coresys)

    @property
    def alsa(self):
        """Return host ALSA handler."""
        return self._alsa

    @property
    def power(self):
        """Return host power handler."""
        return self._power

    @property
    def local(self):
        """Return host local handler."""
        return self._local

    @property
    def supperted_features(self):
        """Return a list of supported host features."""
        features = []

        if self.sys_dbus.systemd.is_connected:
            features.extend([
                FEATURES_REBOOT,
                FEATURES_SHUTDOWN,
            ])

        if self.sys_dbus.hostname.is_connected:
            features.append(FEATURES_HOSTNAME)

        return features

    async def load(self):
        """Load host functions."""
        if self.sys_dbus.hostname.is_connected:
            await self.local.update()

    def reload(self):
        """Reload host information."""
        return self.load()
