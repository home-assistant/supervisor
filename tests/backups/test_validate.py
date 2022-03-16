"""Test Backup schema validation."""

from supervisor.backups import validate

VALID_DEFAULT = {
    validate.ATTR_NAME: "Test Backup",
    validate.ATTR_SLUG: "test",
    validate.ATTR_DATE: "2021-12-01 00:00:00",
}


def test_v1_homeassistant_migration():
    """Test v1 homeassistant validation migration."""

    data = validate.SCHEMA_BACKUP(
        {
            **VALID_DEFAULT,
            **{
                validate.ATTR_HOMEASSISTANT: {validate.ATTR_VERSION: None},
                validate.ATTR_TYPE: validate.BackupType.PARTIAL,
            },
        }
    )

    assert data[validate.ATTR_HOMEASSISTANT] is None


def test_v1_folder_migration():
    """Test v1 folder validation migration."""
    data = validate.SCHEMA_BACKUP(
        {
            **VALID_DEFAULT,
            **{
                validate.ATTR_TYPE: validate.BackupType.PARTIAL,
                validate.ATTR_FOLDERS: [
                    validate.FOLDER_ADDONS,
                    validate.ATTR_HOMEASSISTANT,
                ],
            },
        }
    )

    assert data[validate.ATTR_FOLDERS] == [validate.FOLDER_ADDONS]


def test_v1_protected():
    """Test v1 protection migration."""
    data = validate.SCHEMA_BACKUP(
        {
            **VALID_DEFAULT,
            **{
                validate.ATTR_PROTECTED: 8,
                validate.ATTR_TYPE: validate.BackupType.FULL,
            },
        }
    )

    assert data[validate.ATTR_PROTECTED] is True
