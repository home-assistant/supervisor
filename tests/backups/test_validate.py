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
