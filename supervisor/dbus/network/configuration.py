"""NetworkConnection object4s for Network Manager."""
from typing import List


class NettworkProperties:
    """NettworkProperties object for Network Manager."""

    def __init__(self, properties: dict) -> None:
        """Initialize NettworkProperties object."""
        self._properties = properties


class NetworkAttributes(NettworkProperties):
    """NetworkAttributes object for Network Manager."""

    def __init__(self, object_path: str, properties: dict) -> None:
        """Initialize NetworkAttributes object."""
        super().__init__(properties)
        self.object_path = object_path


class AddressData(NettworkProperties):
    """AddressData object for Network Manager."""

    @property
    def address(self) -> str:
        """Return the address in the options."""
        return self._properties["address"]

    @property
    def prefix(self) -> int:
        """Return the prefix in the options."""
        return self._properties["prefix"]


class IpConfiguration(NetworkAttributes):
    """NetworkSettingsIPConfig object for Network Manager."""

    @property
    def gateway(self) -> str:
        """Return the gateway in the options."""
        return self._properties["Gateway"]

    @property
    def address_data(self) -> List[AddressData]:
        """Return the routers in the options."""
        return [AddressData(x) for x in self._properties["AddressData"]]


class DNSConfiguration(NettworkProperties):
    """NMI DnsManager configuration Object."""

    @property
    def nameservers(self) -> List[str]:
        """Return the nameservers."""
        return self._properties["nameservers"]

    @property
    def domains(self) -> List[str]:
        """Return the domains."""
        return self._properties["domains"]

    @property
    def interface(self) -> str:
        """Return the interface."""
        return self._properties["interface"]

    @property
    def priority(self) -> int:
        """Return the priority."""
        return self._properties["priority"]

    @property
    def vpn(self) -> bool:
        """Return vpn."""
        return self._properties["vpn"]


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
