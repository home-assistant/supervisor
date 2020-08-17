"""NetworkConnection object4s for Network Manager."""
from .network_attributes import NetworkAttributes


class NetworkSettings(NetworkAttributes):
    """NetworkSettings object for Network Manager."""

    @property
    def flags(self) -> int:
        """
        Return the flags for the setting.

        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMSettingsConnectionFlags
        """
        return self._properties["Flags"]

    @property
    def unsaved(self) -> bool:
        """Return a boolean if the settings is saved or not."""
        return self._properties["Unsaved"]

    @property
    def filename(self) -> str:
        """Return the filename for the setting."""
        return self._properties["Filename"]
