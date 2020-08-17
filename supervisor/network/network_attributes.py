"""Common NetworkAttributes object for Network Manager."""


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
