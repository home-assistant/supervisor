"""Host function like audio/dbus/systemd."""

from .alsa import AlsaAudio
from .power import PowerControl
from ..const import FEATURES_REBOOT, FEATURES_SHUTDOWN
from ..coresys import CoreSysAttributes


class HostManager(CoreSysAttributes):
    """Manage supported function from host."""

    def __init__(self, coresys):
        """Initialize Host manager."""
        self.coresys = coresys
        self._alsa = AlsaAudio(coresys)
        self._power = PowerControl(coresys)

    @property
    def alsa(self):
        """Return host ALSA handler."""
        return self._alsa

    @property
    def power(self):
        """Return host power handler."""
        return self._power

    @property
    def supperted_features(self):
        """Return a list of supported host features."""
        features = []

        if self.sys_dbus.systemd.is_connected:
            features.extend([
                FEATURES_REBOOT,
                FEATURES_SHUTDOWN,
            ])

        return features

    async def load(self):
        """Load host functions."""
        pass

    async def reload(self):
        """Reload host information."""
        pass
