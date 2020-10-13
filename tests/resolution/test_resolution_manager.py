"""Tests for resolution manager."""


from supervisor.const import UnsupportedReason
from supervisor.coresys import CoreSys


def test_properies(coresys: CoreSys):
    """Test resolution manager properties."""

    assert coresys.core.supported

    coresys.resolution.unsupported = UnsupportedReason.OS
    assert not coresys.core.supported
