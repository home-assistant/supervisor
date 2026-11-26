"""Test Home Assistant container."""

import asyncio
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any
from unittest.mock import ANY, patch

from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.const import (
    DockerMount,
    MountBindOptions,
    MountType,
    PropagationMode,
)
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import HomeAssistantAPIError
from supervisor.homeassistant.const import LANDINGPAGE

from . import DEV_MOUNT


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_homeassistant_start(coresys: CoreSys, container: DockerContainer):
    """Test starting homeassistant."""
    coresys.homeassistant.version = AwesomeVersion("2023.8.1")

    with (
        patch.object(DockerAPI, "run", return_value=container.show.return_value) as run,
        patch.object(
            DockerHomeAssistant, "is_running", side_effect=[False, False, True]
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep"),
    ):
        await coresys.homeassistant.core.start()

        run.assert_called_once()
        assert run.call_args.kwargs["name"] == "homeassistant"
        assert run.call_args.kwargs["hostname"] == "homeassistant"
        assert run.call_args.kwargs["privileged"] is True
        assert run.call_args.kwargs["oom_score_adj"] == -300
        assert run.call_args.kwargs["device_cgroup_rules"]
        assert run.call_args.kwargs["extra_hosts"] == {
            "supervisor": IPv4Address("172.30.32.2"),
            "observer": IPv4Address("172.30.32.6"),
        }
        assert run.call_args.kwargs["environment"] == {
            "SUPERVISOR": "172.30.32.2",
            "HASSIO": "172.30.32.2",
            "TZ": ANY,
            "SUPERVISOR_TOKEN": ANY,
            "HASSIO_TOKEN": ANY,
            # no "HA_DUPLICATE_LOG_FILE"
        }
        assert run.call_args.kwargs["mounts"] == [
            DEV_MOUNT,
            DockerMount(
                type=MountType.BIND,
                source="/run/dbus",
                target="/run/dbus",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/run/udev",
                target="/run/udev",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_homeassistant.as_posix(),
                target="/config",
                read_only=False,
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_ssl.as_posix(),
                target="/ssl",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_share.as_posix(),
                target="/share",
                read_only=False,
                bind_options=MountBindOptions(propagation=PropagationMode.RSLAVE),
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_media.as_posix(),
                target="/media",
                read_only=False,
                bind_options=MountBindOptions(propagation=PropagationMode.RSLAVE),
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.homeassistant.path_extern_pulse.as_posix(),
                target="/etc/pulse/client.conf",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.plugins.audio.path_extern_pulse.as_posix(),
                target="/run/audio",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.plugins.audio.path_extern_asound.as_posix(),
                target="/etc/asound.conf",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/etc/machine-id",
                target="/etc/machine-id",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_homeassistant_start_with_duplicate_log_file(
    coresys: CoreSys, container: DockerContainer
):
    """Test starting homeassistant with duplicate_log_file enabled."""
    coresys.homeassistant.version = AwesomeVersion("2025.12.0")
    coresys.homeassistant.duplicate_log_file = True

    with (
        patch.object(DockerAPI, "run", return_value=container.show.return_value) as run,
        patch.object(
            DockerHomeAssistant, "is_running", side_effect=[False, False, True]
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep"),
    ):
        await coresys.homeassistant.core.start()

        run.assert_called_once()
        env = run.call_args.kwargs["environment"]
        assert "HA_DUPLICATE_LOG_FILE" in env
        assert env["HA_DUPLICATE_LOG_FILE"] == "1"


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_homeassistant_start_with_unix_socket(
    coresys: CoreSys, container: DockerContainer, tmp_run_dir: Path
):
    """Test starting homeassistant with its socket folders for supported version."""
    coresys.homeassistant.version = AwesomeVersion("2026.4.0")
    run_dirs_at_run: list[bool] = []

    def run_dirs_state() -> list[bool]:
        return [
            (tmp_run_dir / "core").is_dir(),
            (tmp_run_dir / "supervisor" / "core").is_dir(),
        ]

    async def check_run_dirs(*args: Any, **kwargs: Any) -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        run_dirs_at_run.extend(await loop.run_in_executor(None, run_dirs_state))
        return container.show.return_value

    with (
        patch.object(DockerAPI, "run", side_effect=check_run_dirs) as run,
        patch.object(
            DockerHomeAssistant, "is_running", side_effect=[False, False, True]
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep"),
    ):
        await coresys.homeassistant.core.start()

        run.assert_called_once()
        assert run_dirs_at_run == [True, True]
        env = run.call_args.kwargs["environment"]
        assert env["SUPERVISOR_CORE_API_SOCKET"] == "/run/supervisor/core/core.sock"
        assert env["SUPERVISOR_SOCKET"] == "/run/supervisor/api/supervisor.sock"
        mounts = run.call_args.kwargs["mounts"]
        assert (
            DockerMount(
                type=MountType.BIND,
                source="/run/supervisor/core",
                target="/run/supervisor/core",
                read_only=False,
            )
            in mounts
        )
        assert (
            DockerMount(
                type=MountType.BIND,
                source="/run/supervisor/supervisor/core",
                target="/run/supervisor/api",
                read_only=True,
            )
            in mounts
        )
        assert not [mount for mount in mounts if mount.target == "/run/supervisor"]


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_landingpage_start(coresys: CoreSys, container: DockerContainer):
    """Test starting landingpage."""
    coresys.homeassistant.version = LANDINGPAGE

    with (
        patch.object(DockerAPI, "run", return_value=container.show.return_value) as run,
        patch.object(DockerHomeAssistant, "is_running", return_value=False),
    ):
        await coresys.homeassistant.core.start()

        run.assert_called_once()
        assert run.call_args.kwargs["name"] == "homeassistant"
        assert run.call_args.kwargs["hostname"] == "homeassistant"
        assert run.call_args.kwargs["privileged"] is False
        assert run.call_args.kwargs["oom_score_adj"] == -300
        assert not run.call_args.kwargs["device_cgroup_rules"]
        assert run.call_args.kwargs["extra_hosts"] == {
            "supervisor": IPv4Address("172.30.32.2"),
            "observer": IPv4Address("172.30.32.6"),
        }
        assert run.call_args.kwargs["environment"] == {
            "SUPERVISOR": "172.30.32.2",
            "HASSIO": "172.30.32.2",
            "TZ": ANY,
            "SUPERVISOR_TOKEN": ANY,
            "HASSIO_TOKEN": ANY,
            # no "HA_DUPLICATE_LOG_FILE"
        }
        assert run.call_args.kwargs["mounts"] == [
            DEV_MOUNT,
            DockerMount(
                type=MountType.BIND,
                source="/run/dbus",
                target="/run/dbus",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/run/udev",
                target="/run/udev",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_homeassistant.as_posix(),
                target="/config",
                read_only=False,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/etc/machine-id",
                target="/etc/machine-id",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs


async def test_version_landingpage_from_type_label(
    coresys: CoreSys, container: DockerContainer
):
    """Test landingpage image resolves to LANDINGPAGE despite a real version label."""
    container.show.return_value["Config"] = {
        "Labels": {
            "io.hass.type": "landingpage",
            "io.hass.version": "2026.06.3",
        }
    }
    await coresys.homeassistant.core.instance.attach(AwesomeVersion("2026.06.3"))

    assert coresys.homeassistant.core.instance.version == LANDINGPAGE


async def test_version_core_from_version_label(
    coresys: CoreSys, container: DockerContainer
):
    """Test non-landingpage image resolves to the io.hass.version label value."""
    container.show.return_value["Config"] = {
        "Labels": {
            "io.hass.type": "homeassistant",
            "io.hass.version": "2026.06.3",
        }
    }
    await coresys.homeassistant.core.instance.attach(AwesomeVersion("2026.06.3"))

    assert coresys.homeassistant.core.instance.version == AwesomeVersion("2026.06.3")


async def test_timeout(coresys: CoreSys, container: DockerContainer):
    """Test timeout for set from S6_SERVICES_GRACETIME."""
    assert coresys.homeassistant.core.instance.timeout == 260

    # Env missing, remain at default
    await coresys.homeassistant.core.instance.attach(AwesomeVersion("2024.3.0"))
    assert coresys.homeassistant.core.instance.timeout == 260

    # Set a mock value for env in attrs, see that it changes
    container.show.return_value["Config"] = {
        "Env": [
            "SUPERVISOR=172.30.32.2",
            "HASSIO=172.30.32.2",
            "TZ=America/New_York",
            "SUPERVISOR_TOKEN=abc123",
            "HASSIO_TOKEN=abc123",
            "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "LANG=C.UTF-8",
            "S6_BEHAVIOUR_IF_STAGE2_FAILS=2",
            "S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0",
            "S6_CMD_WAIT_FOR_SERVICES=1",
            "S6_SERVICES_READYTIME=50",
            "S6_SERVICES_GRACETIME=300000",
        ]
    }
    await coresys.homeassistant.core.instance.attach(AwesomeVersion("2024.3.0"))
    assert coresys.homeassistant.core.instance.timeout == 320


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_run_after_stop_uses_new_socket_path(
    coresys: CoreSys, container: DockerContainer
):
    """Test a Core container replacing a stopped one is reached on its own socket."""
    coresys.homeassistant.version = AwesomeVersion("2026.4.0")
    api = coresys.homeassistant.api
    instance = coresys.homeassistant.core.instance
    container.show.return_value |= {
        "Id": "old",
        "Config": {"Env": ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core.sock"]},
    }
    await instance.attach(AwesomeVersion("2026.4.0"))
    await instance.stop(remove_container=False)

    # A request while Core is stopped still targets the existing container
    old_session = api.session
    assert old_session.connector.path == str(coresys.config.path_run / "core.sock")

    new_container = {
        "Id": "new",
        "Config": {
            "Env": ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core/core.sock"]
        },
    }
    with (
        patch.object(DockerAPI, "run", return_value=new_container),
        patch.object(DockerHomeAssistant, "is_running", return_value=False),
    ):
        await instance.run()

    try:
        assert old_session.closed
        assert api.session.connector.path == str(
            coresys.config.path_run / "core" / "core.sock"
        )
    finally:
        await api.close()


async def test_stop_and_remove_unbinds_core_api(
    coresys: CoreSys, container: DockerContainer
):
    """Test removing the Core container leaves nothing to connect to."""
    coresys.homeassistant.version = AwesomeVersion("2026.4.0")
    api = coresys.homeassistant.api
    instance = coresys.homeassistant.core.instance
    container.show.return_value |= {"Id": "old", "Config": {"Env": []}}
    await instance.attach(AwesomeVersion("2026.4.0"))
    assert api.use_unix_socket is False

    await instance.stop()

    with pytest.raises(HomeAssistantAPIError, match="Core container is not running"):
        _ = api.use_unix_socket


async def test_inspect_binds_core_api(coresys: CoreSys, container: DockerContainer):
    """Test inspecting the Core container catches up on a missed attach or run."""
    coresys.homeassistant.version = AwesomeVersion("2026.4.0")
    api = coresys.homeassistant.api
    container.show.return_value |= {
        "Id": "abc123",
        "Config": {
            "Env": ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core/core.sock"]
        },
    }
    with pytest.raises(HomeAssistantAPIError, match="Core container is not running"):
        _ = api.use_unix_socket

    await coresys.homeassistant.core.instance.is_running()

    assert api.core_socket_path == coresys.config.path_run / "core" / "core.sock"


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_outdated_inspect_keeps_core_api_binding(coresys: CoreSys):
    """Test an inspect from before a new container was run does not rebind."""
    coresys.homeassistant.version = AwesomeVersion("2026.4.0")
    api = coresys.homeassistant.api
    instance = coresys.homeassistant.core.instance
    old_container = {
        "Id": "old",
        "Config": {"Env": ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core.sock"]},
        "State": {"Status": "exited", "ExitCode": 0},
    }
    new_container = {
        "Id": "new",
        "Config": {
            "Env": ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core/core.sock"]
        },
    }

    async def inspect_during_run() -> dict[str, Any]:
        with (
            patch.object(DockerAPI, "run", return_value=new_container),
            patch.object(DockerHomeAssistant, "is_running", return_value=False),
        ):
            await instance.run()
        return old_container

    with patch.object(instance, "_inspect_container", side_effect=inspect_during_run):
        await instance.current_state()

    assert api.core_socket_path == coresys.config.path_run / "core" / "core.sock"


async def test_overtaken_inspect_keeps_core_api_binding(coresys: CoreSys):
    """Test an inspect which a later one overtook does not rebind."""
    coresys.homeassistant.version = AwesomeVersion("2026.4.0")
    api = coresys.homeassistant.api
    instance = coresys.homeassistant.core.instance
    container = {
        "Id": "abc123",
        "Config": {
            "Env": ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core/core.sock"]
        },
        "State": {"Status": "running"},
    }
    first_inspect_started = asyncio.Event()
    second_inspect_done = asyncio.Event()

    async def missing_then_found() -> dict[str, Any] | None:
        if first_inspect_started.is_set():
            return container
        first_inspect_started.set()
        await second_inspect_done.wait()
        return None

    with patch.object(instance, "_inspect_container", side_effect=missing_then_found):
        first_inspect = asyncio.create_task(instance.current_state())
        await first_inspect_started.wait()
        await instance.current_state()
        second_inspect_done.set()
        await first_inspect

    assert api.core_socket_path == coresys.config.path_run / "core" / "core.sock"
