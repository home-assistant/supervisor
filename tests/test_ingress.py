"""Test ingress."""

from datetime import timedelta
from pathlib import Path
from unittest.mock import ANY, patch

from supervisor.const import IngressSessionData, IngressSessionDataUser
from supervisor.coresys import CoreSys
from supervisor.ingress import Ingress
from supervisor.utils.dt import utc_from_timestamp
from supervisor.utils.json import read_json_file


def test_session_handling(coresys: CoreSys):
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

    session_data = coresys.ingress.get_session_data(session)
    assert session_data is None


def test_session_handling_with_session_data(coresys: CoreSys):
    """Create and test session."""
    session = coresys.ingress.create_session(
        IngressSessionData(IngressSessionDataUser("some-id"))
    )

    assert session

    session_data = coresys.ingress.get_session_data(session)
    assert session_data.user.id == "some-id"


async def test_save_on_unload(coresys: CoreSys):
    """Test called save on unload."""
    coresys.ingress.create_session()
    await coresys.ingress.unload()

    assert coresys.ingress.save_data.called


async def test_dynamic_ports(coresys: CoreSys):
    """Test dyanmic port handling."""
    port_test1 = await coresys.ingress.get_dynamic_port("test1")

    assert port_test1
    assert coresys.ingress.save_data.called
    assert port_test1 == await coresys.ingress.get_dynamic_port("test1")

    port_test2 = await coresys.ingress.get_dynamic_port("test2")

    assert port_test2
    assert port_test2 != port_test1

    assert port_test2 > 62000
    assert port_test2 < 65500
    assert port_test1 > 62000
    assert port_test1 < 65500


async def test_ingress_save_data(coresys: CoreSys, tmp_supervisor_data: Path):
    """Test saving ingress data to file."""
    config_file = tmp_supervisor_data / "ingress.json"
    with patch("supervisor.ingress.FILE_HASSIO_INGRESS", new=config_file):
        ingress = await Ingress(coresys).load_config()
        session = ingress.create_session(
            IngressSessionData(IngressSessionDataUser("123", "Test", "test"))
        )
        await ingress.save_data()

    def get_config():
        assert config_file.exists()
        return read_json_file(config_file)

    assert await coresys.run_in_executor(get_config) == {
        "session": {session: ANY},
        "session_data": {
            session: {"user": {"id": "123", "displayname": "Test", "username": "test"}}
        },
        "ports": {},
    }


async def test_ingress_reload_ignore_none_data(coresys: CoreSys):
    """Test reloading ingress does not add None for session data and create errors."""
    session = coresys.ingress.create_session()
    assert session in coresys.ingress.sessions
    assert session not in coresys.ingress.sessions_data

    await coresys.ingress.reload()
    assert session in coresys.ingress.sessions
    assert session not in coresys.ingress.sessions_data
