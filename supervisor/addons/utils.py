"""Util add-ons functions."""

from __future__ import annotations

import logging
from pathlib import Path
import subprocess
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
                Capabilities.BPF,
                Capabilities.CHECKPOINT_RESTORE,
                Capabilities.DAC_READ_SEARCH,
                Capabilities.NET_ADMIN,
                Capabilities.NET_RAW,
                Capabilities.PERFMON,
                Capabilities.SYS_ADMIN,
                Capabilities.SYS_MODULE,
                Capabilities.SYS_PTRACE,
                Capabilities.SYS_RAWIO,
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

    # UTS host namespace allows to set hostname only with SYS_ADMIN
    if addon.host_uts and Capabilities.SYS_ADMIN in addon.privileged:
        rating += -1

    # Docker Access & full Access
    if addon.access_docker_api or addon.with_full_access:
        rating = 1

    return max(min(8, rating), 1)


def remove_data(folder: Path) -> None:
    """Remove folder and reset privileged.

    Must be run in executor.
    """
    try:
        subprocess.run(
            ["rm", "-rf", str(folder)], stdout=subprocess.DEVNULL, text=True, check=True
        )
    except OSError as err:
        error_msg = str(err)
    except subprocess.CalledProcessError as procerr:
        error_msg = procerr.stderr.strip()
    else:
        return

    _LOGGER.error("Can't remove Add-on Data: %s", error_msg)
