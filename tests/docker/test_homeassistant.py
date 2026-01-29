"""Test Home Assistant container."""

from ipaddress import IPv4Address
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
            "SUPERVISOR": IPv4Address("172.30.32.2"),
            "HASSIO": IPv4Address("172.30.32.2"),
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
            "SUPERVISOR": IPv4Address("172.30.32.2"),
            "HASSIO": IPv4Address("172.30.32.2"),
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
