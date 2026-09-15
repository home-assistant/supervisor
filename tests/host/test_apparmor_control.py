"""Test host apparmor control."""

import errno
from pathlib import Path
from unittest.mock import PropertyMock, patch

from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    APIError,
    HostAppArmorError,
    HostAppArmorLoadProfileError,
)
from supervisor.host.const import HostFeature

from tests.dbus_service_mocks.agent_apparmor import AppArmor as AppArmorService
from tests.dbus_service_mocks.base import DBusServiceMock


async def test_load_profile_error(coresys: CoreSys):
    """Test error loading apparmor profile."""
    test_path = Path("test")
    with (
        patch("supervisor.host.apparmor.validate_profile"),
        patch(
            "supervisor.host.apparmor.shutil.copyfile", side_effect=(err := OSError())
        ),
    ):
        err.errno = errno.EBUSY
        with pytest.raises(HostAppArmorError):
            await coresys.host.apparmor.load_profile("test", test_path)
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with pytest.raises(HostAppArmorError):
            await coresys.host.apparmor.load_profile("test", test_path)
        assert coresys.core.healthy is False


async def test_load_profile_os_agent_rejected(
    coresys: CoreSys, os_agent_services: dict[str, DBusServiceMock], path_extern
):
    """A parser rejection from the OS Agent is an expected error carrying its reason."""
    apparmor_service: AppArmorService = os_agent_services["agent_apparmor"]
    apparmor_service.response_load_profile = DBusError(
        ErrorType.FAILED,
        "profile file '/mnt/data/supervisor/apparmor/test' defines unexpected profile 'docker-default'",
    )

    with (
        patch("supervisor.host.apparmor.validate_profile"),
        patch("supervisor.host.apparmor.shutil.copyfile"),
        patch.object(
            type(coresys.host),
            "features",
            new=PropertyMock(return_value=[HostFeature.OS_AGENT]),
        ),
        pytest.raises(HostAppArmorLoadProfileError) as excinfo,
    ):
        await coresys.host.apparmor.load_profile("test", Path("test"))

    err = excinfo.value
    assert isinstance(err, HostAppArmorError)
    assert isinstance(err, APIError)
    assert (
        str(err)
        == "Can't load profile test: profile file '/mnt/data/supervisor/apparmor/test' defines unexpected profile 'docker-default'"
    )
    assert err.error_key == "host_apparmor_load_profile_error"
    assert err.extra_fields == {
        "profile_name": "test",
        "reason": "profile file '/mnt/data/supervisor/apparmor/test' defines unexpected profile 'docker-default'",
    }


async def test_remove_profile_error(coresys: CoreSys, path_extern):
    """Test error removing apparmor profile."""
    coresys.host.apparmor._profiles.add("test")  # pylint: disable=protected-access
    with patch("supervisor.host.apparmor.Path.unlink", side_effect=(err := OSError())):
        err.errno = errno.EBUSY
        with pytest.raises(HostAppArmorError):
            await coresys.host.apparmor.remove_profile("test")
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with pytest.raises(HostAppArmorError):
            await coresys.host.apparmor.remove_profile("test")
        assert coresys.core.healthy is False


def test_backup_profile_error(coresys: CoreSys, path_extern):
    """Test error while backing up apparmor profile."""
    test_path = Path("test")
    coresys.host.apparmor._profiles.add("test")  # pylint: disable=protected-access
    with patch(
        "supervisor.host.apparmor.shutil.copyfile", side_effect=(err := OSError())
    ):
        err.errno = errno.EBUSY
        with pytest.raises(HostAppArmorError):
            coresys.host.apparmor.backup_profile("test", test_path)
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with pytest.raises(HostAppArmorError):
            coresys.host.apparmor.backup_profile("test", test_path)
        assert coresys.core.healthy is False


async def test_remove_profile_unload_error(
    coresys: CoreSys, os_agent_services: dict[str, DBusServiceMock], path_extern
):
    """Removing a profile deletes the file even if the OS Agent refuses to unload it."""
    apparmor_service: AppArmorService = os_agent_services["agent_apparmor"]
    apparmor_service.response_unload_profile = DBusError(
        ErrorType.FAILED,
        "profile file '/mnt/data/supervisor/apparmor/test' defines unexpected profile 'docker-default'",
    )

    coresys.config.path_apparmor.mkdir(parents=True, exist_ok=True)
    profile_file = coresys.config.path_apparmor / "test"
    profile_file.write_text("profile test {}", encoding="utf-8")
    coresys.host.apparmor._profiles.add("test")  # pylint: disable=protected-access

    with patch.object(
        type(coresys.host),
        "features",
        new=PropertyMock(return_value=[HostFeature.OS_AGENT]),
    ):
        await coresys.host.apparmor.remove_profile("test")

    assert not profile_file.exists()
    assert not coresys.host.apparmor.exists("test")


async def test_load_profile_rejected_cleanup(
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    path_extern,
    tmp_path: Path,
):
    """A load rejected by the OS Agent leaves no profile file behind."""
    apparmor_service: AppArmorService = os_agent_services["agent_apparmor"]
    apparmor_service.response_load_profile = DBusError(
        ErrorType.FAILED,
        "profile file '/mnt/data/supervisor/apparmor/test' defines unexpected profile 'docker-default'",
    )

    coresys.config.path_apparmor.mkdir(parents=True, exist_ok=True)
    source_file = tmp_path / "apparmor.txt"
    source_file.write_text("profile test {}", encoding="utf-8")
    dest_file = coresys.config.path_apparmor / "test"

    with (
        patch("supervisor.host.apparmor.validate_profile"),
        patch.object(
            type(coresys.host),
            "features",
            new=PropertyMock(return_value=[HostFeature.OS_AGENT]),
        ),
        pytest.raises(HostAppArmorLoadProfileError),
    ):
        await coresys.host.apparmor.load_profile("test", source_file)

    assert not dest_file.exists()
    assert not coresys.host.apparmor.exists("test")
