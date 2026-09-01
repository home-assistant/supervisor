"""Tests for mount manager validation."""

import pytest
from voluptuous import Invalid

from supervisor.api.mounts import SCHEMA_MOUNT_CONFIG
from supervisor.mounts.validate import SCHEMA_MOUNTS_CONFIG

DISK_UUID = "d2f4a6c8-3b5e-4079-8a1c-6e9d2f4b7a30"


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


async def test_valid_disk_mounts():
    """Test valid disk mounts."""
    # A device path is how a user picks a disk to begin with
    assert SCHEMA_MOUNT_CONFIG(
        {
            "name": "disk_by_device",
            "usage": "media",
            "type": "disk",
            "device": "/dev/sdc1",
        }
    )

    # A uuid identifies a disk that has been resolved before
    assert SCHEMA_MOUNT_CONFIG(
        {
            "name": "disk_by_uuid",
            "usage": "backup",
            "type": "disk",
            "uuid": DISK_UUID,
        }
    )


async def test_api_disk_mount_cannot_set_filesystem():
    """Test the API schema does not let a caller supply filesystem.

    Resolving the device is what runs the mountable-device guard, and a mount
    only resolves when it does not already know its filesystem. Accepting one
    here would skip resolution and so skip every guard rail.
    """
    config = SCHEMA_MOUNT_CONFIG(
        {
            "name": "disk_test",
            "usage": "media",
            "type": "disk",
            "uuid": DISK_UUID,
            "filesystem": "ext4",
        }
    )

    # Dropped rather than rejected, so that reading a mount from GET /mounts
    # and writing it back with PUT keeps working
    assert "filesystem" not in config


async def test_mounts_config_keeps_persisted_filesystem():
    """Test the file schema keeps filesystem so reloads need no UDisks2."""
    config = SCHEMA_MOUNTS_CONFIG(
        {
            "mounts": [
                {
                    "name": "disk_test",
                    "usage": "media",
                    "type": "disk",
                    "uuid": DISK_UUID,
                    "filesystem": "ext4",
                }
            ]
        }
    )

    assert config["mounts"][0]["filesystem"] == "ext4"


async def test_mounts_config_tolerates_unsupported_filesystem():
    """Test an unsupported persisted filesystem does not invalidate the file.

    FileConfiguration resets invalid configuration to default, so rejecting the
    value here would discard every configured mount, network ones included. It
    is rejected at mount time instead, costing only that one mount.
    """
    config = SCHEMA_MOUNTS_CONFIG(
        {
            "mounts": [
                {
                    "name": "cifs_test",
                    "usage": "backup",
                    "type": "cifs",
                    "server": "test.local",
                    "share": "test",
                },
                {
                    "name": "disk_test",
                    "usage": "media",
                    "type": "disk",
                    "uuid": DISK_UUID,
                    "filesystem": "reiserfs",
                },
            ]
        }
    )

    assert len(config["mounts"]) == 2
    assert config["mounts"][1]["filesystem"] == "reiserfs"


async def test_invalid_disk():
    """Test invalid disk mounts."""
    base = {"name": "test", "usage": "media", "type": "disk"}

    # Both identifiers together are valid, so a candidates entry can be
    # posted back as-is
    assert SCHEMA_MOUNT_CONFIG(
        base
        | {
            "device": "/dev/sdc1",
            "uuid": "d2f4a6c8-3b5e-4079-8a1c-6e9d2f4b7a30",
        }
    )

    # One of the two is required
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG(base)

    # A filesystem on its own does not identify a device
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG(base | {"filesystem": "ext4"})


async def test_mounts_config_requires_uuid():
    """Test a persisted disk mount must carry the uuid it was resolved to."""
    base = {"name": "disk_test", "usage": "media", "type": "disk"}

    with pytest.raises(Invalid):
        SCHEMA_MOUNTS_CONFIG({"mounts": [base]})

    # device is API input only and cannot stand in for the uuid
    with pytest.raises(Invalid):
        SCHEMA_MOUNTS_CONFIG({"mounts": [base | {"device": "/dev/sdc1"}]})


async def test_invalid_read_only_disk_backup_mount():
    """Test a disk mount used for backups cannot be read only."""
    with pytest.raises(Invalid):
        SCHEMA_MOUNT_CONFIG(
            {
                "name": "test",
                "usage": "backup",
                "type": "disk",
                "device": "/dev/sdc1",
                "read_only": True,
            }
        )
