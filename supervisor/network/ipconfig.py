"""NetworkConnection object4s for Network Manager."""
from typing import List

from .network_attributes import NettworkProperties, NetworkAttributes


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


class NetworkSettingsIPConfig(NetworkAttributes):
    """NetworkSettingsIPConfig object for Network Manager."""

    @property
    def gateway(self) -> str:
        """Return the gateway in the options."""
        return self._properties["Gateway"]

    @property
    def address_data(self) -> List[AddressData]:
        """Return the routers in the options."""
        return [AddressData(x) for x in self._properties["AddressData"]]
