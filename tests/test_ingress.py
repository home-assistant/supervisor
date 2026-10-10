"""Test ingress."""

from datetime import timedelta
import json
from pathlib import Path
from typing import Any
from unittest.mock import ANY, patch

import pytest
import time_machine

from supervisor.const import HomeAssistantUser, IngressSessionData
from supervisor.coresys import CoreSys
from supervisor.ingress import Ingress
from supervisor.utils.dt import utc_from_timestamp, utcnow
from supervisor.utils.json import read_json_file


def test_session_handling(coresys: CoreSys):
    """Create and test session."""
    session = coresys.ingress.create_session()
    validate = coresys.ingress.sessions[session]

    assert session
    assert validate

    assert coresys.ingress.validate_session(session)
    assert coresys.ingress.sessions[session] >= validate

    not_valid = utc_from_timestamp(validate) - timedelta(minutes=20)
    coresys.ingress.sessions[session] = not_valid.timestamp()
    assert not coresys.ingress.validate_session(session)
    assert not coresys.ingress.validate_session("invalid session")

    session_data = coresys.ingress.get_session_data(session)
    assert session_data is None


def test_session_validation_sliding_expiry(coresys: CoreSys):
    """Test validating a session extends expiry from now, not cumulatively."""
    start = utcnow()
    with time_machine.travel(start, tick=False):
        session = coresys.ingress.create_session()
        for _ in range(100):
            assert coresys.ingress.validate_session(session)

        assert coresys.ingress.sessions[session] == (
            (start + timedelta(minutes=15)).timestamp()
        )

    later = start + timedelta(minutes=10)
    with time_machine.travel(later, tick=False):
        assert coresys.ingress.validate_session(session)
        assert coresys.ingress.sessions[session] == (
            (later + timedelta(minutes=15)).timestamp()
        )

    with time_machine.travel(later + timedelta(minutes=16), tick=False):
        assert not coresys.ingress.validate_session(session)


def test_session_validation_malformed_timestamp(coresys: CoreSys):
    """Test a malformed session timestamp is reset to a float timestamp."""
    session = coresys.ingress.create_session()
    coresys.ingress.sessions[session] = 1e20

    start = utcnow()
    with time_machine.travel(start, tick=False):
        assert coresys.ingress.validate_session(session)
        assert coresys.ingress.sessions[session] == (
            (start + timedelta(minutes=15)).timestamp()
        )


def test_session_handling_with_session_data(coresys: CoreSys):
    """Create and test session."""
    session = coresys.ingress.create_session(
        IngressSessionData(HomeAssistantUser("some-id"))
    )

    assert session

    session_data = coresys.ingress.get_session_data(session)
    assert session_data.user.id == "some-id"


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {"user": {"id": "123", "name": "Test", "username": "test"}},
            IngressSessionData(
                HomeAssistantUser("123", name="Test", username="test"), admin=True
            ),
            id="legacy_without_admin_flag",
        ),
        pytest.param(
            {"admin": False},
            IngressSessionData(None, admin=False),
            id="admin_flag_without_user",
        ),
        pytest.param(
            {"admin": False, "user": {"id": "123", "name": None, "username": None}},
            IngressSessionData(HomeAssistantUser("123"), admin=False),
            id="admin_flag_with_user",
        ),
    ],
)
def test_session_data_from_dict(
    data: dict[str, Any], expected: IngressSessionData
) -> None:
    """Test deserializing ingress session data."""
    assert IngressSessionData.from_dict(data) == expected


async def test_save_on_unload(coresys: CoreSys):
    """Test called save on unload."""
    coresys.ingress.create_session()
    await coresys.ingress.unload()

    assert coresys.ingress.save_data.called


async def test_dynamic_ports(coresys: CoreSys):
    """Test dynamic port handling."""
    port_test1 = await coresys.ingress.get_dynamic_port("test1")

    assert port_test1
    assert coresys.ingress.save_data.called
    assert port_test1 == await coresys.ingress.get_dynamic_port("test1")

    port_test2 = await coresys.ingress.get_dynamic_port("test2")

    assert port_test2
    assert port_test2 != port_test1

    assert port_test2 >= 62000
    assert port_test2 <= 65500
    assert port_test1 >= 62000
    assert port_test1 <= 65500


@pytest.mark.parametrize(
    ("session_data", "expected"),
    [
        pytest.param(
            IngressSessionData(HomeAssistantUser("123", name="Test", username="test")),
            {
                "admin": True,
                "user": {"id": "123", "name": "Test", "username": "test"},
            },
            id="admin_with_user",
        ),
        pytest.param(
            IngressSessionData(
                HomeAssistantUser("123", name="Test", username="test"), admin=False
            ),
            {
                "admin": False,
                "user": {"id": "123", "name": "Test", "username": "test"},
            },
            id="non_admin_with_user",
        ),
        pytest.param(
            IngressSessionData(None, admin=False),
            {"admin": False},
            id="non_admin_without_user",
        ),
    ],
)
async def test_ingress_save_data(
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    session_data: IngressSessionData,
    expected: dict[str, Any],
):
    """Test saving ingress session data to file and loading it back."""
    config_file = tmp_supervisor_data / "ingress.json"
    with patch("supervisor.ingress.FILE_HASSIO_INGRESS", new=config_file):
        ingress = await Ingress(coresys).load_config()
        session = ingress.create_session(session_data)
        await ingress.save_data()

        reloaded = await Ingress(coresys).load_config()

    def get_config():
        assert config_file.exists()
        return read_json_file(config_file)

    assert await coresys.run_in_executor(get_config) == {
        "session": {session: ANY},
        "session_data": {session: expected},
        "ports": {},
    }
    assert reloaded.get_session_data(session) == session_data


async def test_ingress_load_legacy_displayname(
    coresys: CoreSys, tmp_supervisor_data: Path
):
    """Test loading session data with legacy 'displayname' key."""
    config_file = tmp_supervisor_data / "ingress.json"
    session_token = "a" * 128

    config_file.write_text(
        json.dumps(
            {
                "session": {session_token: 9999999999.0},
                "session_data": {
                    session_token: {
                        "user": {
                            "id": "456",
                            "displayname": "Legacy Name",
                            "username": "legacy",
                        }
                    }
                },
                "ports": {},
            }
        )
    )

    with patch("supervisor.ingress.FILE_HASSIO_INGRESS", new=config_file):
        ingress = await Ingress(coresys).load_config()

    session_data = ingress.get_session_data(session_token)
    assert session_data is not None
    assert session_data.user.id == "456"
    assert session_data.user.name == "Legacy Name"
    assert session_data.user.username == "legacy"


async def test_ingress_reload_ignore_none_data(coresys: CoreSys):
    """Test reloading ingress does not add None for session data and create errors."""
    session = coresys.ingress.create_session()
    assert session in coresys.ingress.sessions
    assert session not in coresys.ingress.sessions_data

    await coresys.ingress.reload()
    assert session in coresys.ingress.sessions
    assert session not in coresys.ingress.sessions_data
