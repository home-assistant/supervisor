"""Test backups API."""

from unittest.mock import patch

from supervisor.backups.backup import Backup
from supervisor.coresys import CoreSys


async def test_info(api_client, coresys: CoreSys, mock_full_backup: Backup):
    """Test info endpoint."""
    resp = await api_client.get("/backups/info")
    result = await resp.json()
    assert result["data"]["auto_backup"] is False
    assert result["data"]["days_until_stale"] == 30
    assert result["data"]["max_full_backups"] == 2
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "test"
    assert result["data"]["backups"][0]["content"]["homeassistant"] is True
    assert len(result["data"]["backups"][0]["content"]["addons"]) == 1
    assert result["data"]["backups"][0]["content"]["addons"][0] == "local_ssh"


async def test_list(api_client, coresys: CoreSys, mock_full_backup: Backup):
    """Test list endpoint."""
    resp = await api_client.get("/backups")
    result = await resp.json()
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "test"
    assert result["data"]["backups"][0]["content"]["homeassistant"] is True
    assert len(result["data"]["backups"][0]["content"]["addons"]) == 1
    assert result["data"]["backups"][0]["content"]["addons"][0] == "local_ssh"


async def test_options(api_client, coresys: CoreSys):
    """Test options endpoint."""
    assert coresys.backups.auto_backup is False
    assert coresys.backups.days_until_stale == 30
    assert coresys.backups.max_full_backups == 2

    with patch.object(type(coresys.backups), "save_data") as save_data:
        await api_client.post(
            "/backups/options",
            json={
                "auto_backup": True,
                "days_until_stale": 10,
                "max_full_backups": 5,
            },
        )
        save_data.assert_called_once()

    assert coresys.backups.auto_backup is True
    assert coresys.backups.days_until_stale == 10
    assert coresys.backups.max_full_backups == 5
