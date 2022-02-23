"""Util add-ons functions."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ..const import ROLE_ADMIN, ROLE_MANAGER, SECURITY_DISABLE, SECURITY_PROFILE
from ..docker.const import Capabilities

if TYPE_CHECKING:
    from .model import AddonModel

_LOGGER: logging.Logger = logging.getLogger(__name__)


def rating_security(addon: AddonModel) -> int:
    """Return 1-8 for security rating.

    1 = not secure
    8 = high secure
    """
    rating = 5

    # AppArmor
    if addon.apparmor == SECURITY_DISABLE:
        rating += -1
    elif addon.apparmor == SECURITY_PROFILE:
        rating += 1

    # Home Assistant Login & Ingress
    if addon.with_ingress:
        rating += 2
    elif addon.access_auth_api:
        rating += 1

    # Signed
    if addon.signed:
        rating += 1

    # Privileged options
    if (
        any(
            privilege in addon.privileged
            for privilege in (
                Capabilities.NET_ADMIN,
                Capabilities.SYS_ADMIN,
                Capabilities.SYS_RAWIO,
                Capabilities.SYS_PTRACE,
                Capabilities.SYS_MODULE,
                Capabilities.DAC_READ_SEARCH,
            )
        )
        or addon.with_kernel_modules
    ):
        rating += -1

    # API Supervisor role
    if addon.hassio_role == ROLE_MANAGER:
        rating += -1
    elif addon.hassio_role == ROLE_ADMIN:
        rating += -2

    # Not secure Networking
    if addon.host_network:
        rating += -1

    # Insecure PID namespace
    if addon.host_pid:
        rating += -2

    # Docker Access & full Access
    if addon.access_docker_api or addon.with_full_access:
        rating = 1

    return max(min(8, rating), 1)


async def remove_data(folder: Path) -> None:
    """Remove folder and reset privileged."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "rm", "-rf", str(folder), stdout=asyncio.subprocess.DEVNULL
        )

        _, error_msg = await proc.communicate()
    except OSError as err:
        error_msg = str(err)
    else:
        if proc.returncode == 0:
            return

    _LOGGER.error("Can't remove Add-on Data: %s", error_msg)
