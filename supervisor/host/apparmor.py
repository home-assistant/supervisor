"""AppArmor control for host."""
from __future__ import annotations

import logging
from pathlib import Path
import shutil

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DBusError, HostAppArmorError
from ..resolution.const import UnsupportedReason
from ..utils.apparmor import validate_profile
from .const import HostFeature

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AppArmorControl(CoreSysAttributes):
    """Handle host AppArmor controls."""

    def __init__(self, coresys: CoreSys):
        """Initialize host power handling."""
        self.coresys: CoreSys = coresys
        self._profiles: set[str] = set()

    @property
    def available(self) -> bool:
        """Return True if AppArmor is available on host."""
        return (
            HostFeature.OS_AGENT in self.sys_host.features
            and UnsupportedReason.APPARMOR not in self.sys_resolution.unsupported
        )

    @property
    def version(self) -> AwesomeVersion | None:
        """Return hosts AppArmor Version."""
        return self.sys_dbus.agent.apparmor.version

    def exists(self, profile_name: str) -> bool:
        """Return True if a profile exists."""
        return profile_name in self._profiles

    def _get_profile(self, profile_name: str) -> Path:
        """Get a profile from AppArmor store."""
        if profile_name not in self._profiles:
            raise HostAppArmorError(
                f"Can't find {profile_name} for removing", _LOGGER.error
            )
        return Path(self.sys_config.path_apparmor, profile_name)

    async def load(self) -> None:
        """Load available profiles."""
        for content in self.sys_config.path_apparmor.iterdir():
            if not content.is_file():
                continue
            self._profiles.add(content.name)

        _LOGGER.info("Loading AppArmor Profiles: %s", self._profiles)

        # Load profiles
        if self.available:
            for profile_name in self._profiles:
                try:
                    await self._load_profile(profile_name)
                except HostAppArmorError:
                    pass
        else:
            _LOGGER.warning("AppArmor is not enabled on host")

    async def load_profile(self, profile_name: str, profile_file: Path) -> None:
        """Load/Update a new/exists profile into AppArmor."""
        if not validate_profile(profile_name, profile_file):
            raise HostAppArmorError(
                f"AppArmor profile '{profile_name}' is not valid", _LOGGER.error
            )

        # Copy to AppArmor folder
        dest_profile: Path = Path(self.sys_config.path_apparmor, profile_name)
        try:
            await self.sys_run_in_executor(shutil.copyfile, profile_file, dest_profile)
        except OSError as err:
            raise HostAppArmorError(
                f"Can't copy {profile_file}: {err}", _LOGGER.error
            ) from err

        # Load profiles
        _LOGGER.info("Adding/updating AppArmor profile: %s", profile_name)
        self._profiles.add(profile_name)
        if not self.available:
            return

        await self._load_profile(profile_name)

    async def remove_profile(self, profile_name: str) -> None:
        """Remove a AppArmor profile."""
        profile_file: Path = self._get_profile(profile_name)

        # Unload if apparmor is enabled
        if self.available:
            await self._unload_profile(profile_name)

        try:
            await self.sys_run_in_executor(profile_file.unlink)
        except OSError as err:
            raise HostAppArmorError(
                f"Can't remove profile: {err}", _LOGGER.error
            ) from err

        _LOGGER.info("Removing AppArmor profile: %s", profile_name)
        self._profiles.remove(profile_name)

    async def backup_profile(self, profile_name: str, backup_file: Path) -> None:
        """Backup A profile into a new file."""
        profile_file: Path = self._get_profile(profile_name)

        try:
            await self.sys_run_in_executor(shutil.copy, profile_file, backup_file)
        except OSError as err:
            raise HostAppArmorError(
                f"Can't backup profile {profile_name}: {err}", _LOGGER.error
            ) from err

    async def _load_profile(self, profile_name: str) -> None:
        """Load a profile on the host."""
        try:
            await self.sys_dbus.agent.apparmor.load_profile(
                self.sys_config.path_extern_apparmor.joinpath(profile_name),
                self.sys_config.path_apparmor_cache,
            )
        except DBusError as err:
            raise HostAppArmorError(
                f"Can't load profile {profile_name}: {err!s}", _LOGGER.error
            ) from err

    async def _unload_profile(self, profile_name: str) -> None:
        """Unload a profile on the host."""
        try:
            await self.sys_dbus.agent.apparmor.unload_profile(
                self.sys_config.path_extern_apparmor.joinpath(profile_name),
                self.sys_config.path_apparmor_cache,
            )
        except DBusError as err:
            raise HostAppArmorError(
                f"Can't unload profile {profile_name}: {err!s}", _LOGGER.error
            ) from err
