"""Test ingress."""
from datetime import timedelta

from hassio.utils.dt import utc_from_timestamp


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
