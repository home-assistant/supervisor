"""Check dbus-next implementation."""
from dbus_next.signature import Variant

from supervisor.utils.dbus import DBus


def test_remove_dbus_signature():
    """Check D-Bus signature clean-up."""
    test = DBus.remove_dbus_signature(Variant("s", "Value"))
    assert isinstance(test, str)
    assert test == "Value"

    test_dict = DBus.remove_dbus_signature({"Key": Variant("s", "Value")})
    assert isinstance(test_dict["Key"], str)
    assert test_dict["Key"] == "Value"

    test_dict = DBus.remove_dbus_signature([Variant("s", "Value")])
    assert isinstance(test_dict[0], str)
    assert test_dict[0] == "Value"
