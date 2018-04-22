"""Host function like audio/dbus/systemd."""

from .alsa import AlsaAudio  # noqa
from ..const import FEATURES_REBOOT, FEATURES_SHUTDOWN
from ..coresys import CoreSysAttributes


class HostManager(CoreSysAttributes):
    """Manage supported function from host."""

    def __init__(self, coresys):
        """Initialize Host manager."""
        self.coresys = coresys

    @property
    def supperted_features(self):
        """Return a list of supported host features."""
        features = []

        if self.sys_systemd.is_connected:
            features.extend([
                FEATURES_REBOOT,
                FEATURES_SHUTDOWN,
            ])

        return features

    async def load(self):
        """Load host functions."""
        await self.sys_systemd.connect()
