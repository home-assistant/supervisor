"""Mock of OS Agent System dbus service."""

from dbus_fast import DBusError, ErrorType

from .base import DBusServiceMock, dbus_method

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return System()


class System(DBusServiceMock):
    """System mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/System
    """

    object_path = "/io/hass/os/System"
    interface = "io.hass.os.System"
    response_schedule_wipe_device: bool | DBusError = True
    response_migrate_docker_storage_driver: None | DBusError = None
    response_add_ssh_auth_key: None | DBusError = None
    response_clear_ssh_auth_keys: None | DBusError = None

    @dbus_method()
    def ScheduleWipeDevice(self) -> "b":
        """Schedule wipe device."""
        if isinstance(self.response_schedule_wipe_device, DBusError):
            raise self.response_schedule_wipe_device  # pylint: disable=raising-bad-type
        return self.response_schedule_wipe_device

    @dbus_method()
    def MigrateDockerStorageDriver(self, backend: "s") -> None:
        """Migrate Docker storage driver."""
        if isinstance(self.response_migrate_docker_storage_driver, DBusError):
            raise self.response_migrate_docker_storage_driver  # pylint: disable=raising-bad-type
        if backend != "overlayfs":
            raise DBusError(
                ErrorType.FAILED,
                f"unsupported driver: {backend} (only 'overlayfs' is currently supported)",
            )

    @dbus_method()
    def AddSSHAuthKey(self, key: "s") -> None:
        """Add SSH authorized key."""
        if isinstance(self.response_add_ssh_auth_key, DBusError):
            raise self.response_add_ssh_auth_key  # pylint: disable=raising-bad-type

    @dbus_method()
    def ClearSSHAuthKeys(self) -> None:
        """Clear SSH authorized keys."""
        if isinstance(self.response_clear_ssh_auth_keys, DBusError):
            raise self.response_clear_ssh_auth_keys  # pylint: disable=raising-bad-type
