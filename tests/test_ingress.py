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
    ("user", "expected"),
    [
        pytest.param({"id": "1", "is_owner": True}, True, id="owner"),
        pytest.param(
            {"id": "1", "is_active": True, "group_ids": ["system-admin"]},
            True,
            id="active_admin_group",
        ),
        pytest.param(
            {"id": "1", "is_active": False, "group_ids": ["system-admin"]},
            False,
            id="inactive_admin_group",
        ),
        pytest.param(
            {"id": "1", "is_active": True, "group_ids": ["system-users"]},
            False,
            id="users_group",
        ),
        pytest.param({"id": "1"}, False, id="no_groups"),
    ],
)
def test_user_is_admin(user: dict[str, Any], expected: bool) -> None:
    """Test admin role derivation matches Core's definition."""
    assert HomeAssistantUser.from_dict(user).is_admin is expected


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


async def test_ingress_save_data(coresys: CoreSys, tmp_supervisor_data: Path):
    """Test saving ingress session data to file."""
    config_file = tmp_supervisor_data / "ingress.json"
    with patch("supervisor.ingress.FILE_HASSIO_INGRESS", new=config_file):
        ingress = await Ingress(coresys).load_config()
        session = ingress.create_session(
            IngressSessionData(HomeAssistantUser("123", name="Test", username="test"))
        )
        await ingress.save_data()

    def get_config():
        assert config_file.exists()
        return read_json_file(config_file)

    assert await coresys.run_in_executor(get_config) == {
        "session": {session: ANY},
        "session_data": {
            session: {"user": {"id": "123", "name": "Test", "username": "test"}}
        },
        "ports": {},
    }


async def test_ingress_load_drops_sessions_without_data(
    coresys: CoreSys, tmp_supervisor_data: Path
):
    """Test loading drops sessions without user data."""
    config_file = tmp_supervisor_data / "ingress.json"
    with_user = "a" * 128
    without_user = "b" * 128
    config_file.write_text(
        json.dumps(
            {
                "session": {with_user: 9999999999.0, without_user: 9999999999.0},
                "session_data": {with_user: {"user": {"id": "123"}}},
                "ports": {},
            }
        )
    )

    with patch("supervisor.ingress.FILE_HASSIO_INGRESS", new=config_file):
        ingress = await Ingress(coresys).load_config()
        await ingress.load()

    assert without_user not in ingress.sessions
    assert ingress.get_session_data(with_user) == IngressSessionData(
        HomeAssistantUser("123")
    )


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


async def test_ingress_reload_drops_sessions_without_data(coresys: CoreSys):
    """Test reloading ingress drops sessions that carry no user data."""
    session = coresys.ingress.create_session()
    assert session in coresys.ingress.sessions
    assert session not in coresys.ingress.sessions_data

    await coresys.ingress.reload()
    assert session not in coresys.ingress.sessions
