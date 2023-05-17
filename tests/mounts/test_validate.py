"""Tests for mount manager validation."""

import pytest
from voluptuous import Invalid

from supervisor.mounts.validate import SCHEMA_MOUNT_CONFIG


async def test_valid_mounts():
    """Test valid mounts."""
    assert SCHEMA_MOUNT_CONFIG(
        {
            "name": "cifs_test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "test",
        }
    )

    assert SCHEMA_MOUNT_CONFIG(
        {
            "name": "nfs_test",
            "usage": "media",
            "type": "nfs",
            "server": "192.168.1.10",
            "path": "/data/media",
        }
    )


async def test_invalid_name():
    """Test name not a valid filename."""
    base = {
        "usage": "backup",
        "type": "cifs",
        "server": "test.local",
        "share": "test",
    }
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"name": "no spaces"} | base)

    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"name": "no_special_chars_@#"} | base)

    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"name": "no-dashes"} | base)

    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"name": "no/slashes"} | base)


async def test_no_bind_mounts():
    """Bind mount not a valid type."""
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG(
            {
                "name": "test",
                "usage": " backup",
                "type": "bind",
                "path": "/etc/ssl",
            }
        )


async def test_invalid_cifs():
    """Test invalid cifs mounts."""
    base = {
        "name": "test",
        "usage": "backup",
        "type": "cifs",
        "server": "test.local",
    }

    # Missing share
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG(base)

    # Path is for NFS
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"path": "backups"})

    # Username and password must be together
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"username": "admin"})


async def test_invalid_nfs():
    """Test invalid nfs mounts."""
    base = {
        "name": "test",
        "usage": "backup",
        "type": "nfs",
        "server": "test.local",
    }

    # Missing path
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG(base)

    # Share is for CIFS
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"share": "backups"})

    # Auth is for CIFS
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG({"username": "admin", "password": "password"})
