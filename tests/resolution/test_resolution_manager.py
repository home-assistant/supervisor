"""Tests for resolution manager."""


from supervisor.coresys import CoreSys
from supervisor.resolution.const import UnsupportedReason


def test_properies(coresys: CoreSys):
    """Test resolution manager properties."""

    assert coresys.core.supported

    coresys.resolution.unsupported = UnsupportedReason.OS
    assert not coresys.core.supported
