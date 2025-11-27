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
        if backend not in ("overlayfs", "overlay2"):
            raise DBusError(
                ErrorType.FAILED,
                f"unsupported driver: {backend} (only 'overlayfs' and 'overlay2' are supported)",
            )
