"""Check dbus-next implementation."""
from dbus_next.signature import Variant

from supervisor.coresys import CoreSys
from supervisor.utils.dbus_next import DBus, _remove_dbus_signature


def test_remove_dbus_signature():
    """Check D-Bus signature clean-up."""
    test = _remove_dbus_signature(Variant("s", "Value"))
    assert isinstance(test, str)
    assert test == "Value"

    test_dict = _remove_dbus_signature({"Key": Variant("s", "Value")})
    assert isinstance(test_dict["Key"], str)
    assert test_dict["Key"] == "Value"

    test_dict = _remove_dbus_signature([Variant("s", "Value")])
    assert isinstance(test_dict[0], str)
    assert test_dict[0] == "Value"


async def test_dbus_prepare_args(coresys: CoreSys):
    """Check D-Bus dynamic argument builder."""
    dbus = DBus("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
    signature, args = dbus._prepare_args(
        True, 1, 1.0, "Value", ("a{sv}", {"Key": "Value"})
    )
    assert signature == "bidsa{sv}"
