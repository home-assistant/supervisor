"""Test host apparmor control."""

import errno
from pathlib import Path
from unittest.mock import patch

from pytest import raises

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostAppArmorError


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
        with raises(HostAppArmorError):
            await coresys.host.apparmor.load_profile("test", test_path)
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with raises(HostAppArmorError):
            await coresys.host.apparmor.load_profile("test", test_path)
        assert coresys.core.healthy is False


async def test_remove_profile_error(coresys: CoreSys, path_extern):
    """Test error removing apparmor profile."""
    coresys.host.apparmor._profiles.add("test")  # pylint: disable=protected-access
    with patch("supervisor.host.apparmor.Path.unlink", side_effect=(err := OSError())):
        err.errno = errno.EBUSY
        with raises(HostAppArmorError):
            await coresys.host.apparmor.remove_profile("test")
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with raises(HostAppArmorError):
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
        with raises(HostAppArmorError):
            coresys.host.apparmor.backup_profile("test", test_path)
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with raises(HostAppArmorError):
            coresys.host.apparmor.backup_profile("test", test_path)
        assert coresys.core.healthy is False
