"""Test ingress."""
from datetime import timedelta

from supervisor.utils.dt import utc_from_timestamp


def test_session_handling(coresys):
    """Create and test session."""
    session = coresys.ingress.create_session()
    validate = coresys.ingress.sessions[session]

    assert session
    assert validate

    assert coresys.ingress.validate_session(session)
    assert coresys.ingress.sessions[session] != validate

    not_valid = utc_from_timestamp(validate) - timedelta(minutes=20)
    coresys.ingress.sessions[session] = not_valid.timestamp()
    assert not coresys.ingress.validate_session(session)
    assert not coresys.ingress.validate_session("invalid session")


async def test_save_on_unload(coresys):
    """Test called save on unload."""
    coresys.ingress.create_session()
    await coresys.ingress.unload()

    assert coresys.ingress.save_data.called


def test_dynamic_ports(coresys):
    """Test dyanmic port handling."""
    port_test1 = coresys.ingress.get_dynamic_port("test1")

    assert port_test1
    assert coresys.ingress.save_data.called
    assert port_test1 == coresys.ingress.get_dynamic_port("test1")

    port_test2 = coresys.ingress.get_dynamic_port("test2")

    assert port_test2
    assert port_test2 != port_test1

    assert port_test2 > 62000
    assert port_test2 < 65500
    assert port_test1 > 62000
    assert port_test1 < 65500
