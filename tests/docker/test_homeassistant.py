"""Test Home Assistant container."""

from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import ANY, patch

from awesomeversion import AwesomeVersion
from docker.types import Mount

from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.manager import DockerAPI
from supervisor.homeassistant.const import LANDINGPAGE


async def test_homeassistant_start(
    coresys: CoreSys, tmp_supervisor_data: Path, path_extern
):
    """Test starting homeassistant."""
    coresys.homeassistant.version = AwesomeVersion("2023.8.1")

    with patch.object(DockerAPI, "run") as run, patch.object(
        DockerHomeAssistant, "is_running", side_effect=[False, False, True]
    ), patch("supervisor.homeassistant.core.asyncio.sleep"):
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
        }
        assert run.call_args.kwargs["mounts"] == [
            Mount(type="bind", source="/dev", target="/dev", read_only=True),
            Mount(type="bind", source="/run/dbus", target="/run/dbus", read_only=True),
            Mount(type="bind", source="/run/udev", target="/run/udev", read_only=True),
            Mount(
                type="bind",
                source=coresys.config.path_extern_homeassistant.as_posix(),
                target="/config",
                read_only=False,
            ),
            Mount(
                type="bind",
                source=coresys.config.path_extern_ssl.as_posix(),
                target="/ssl",
                read_only=True,
            ),
            Mount(
                type="bind",
                source=coresys.config.path_extern_share.as_posix(),
                target="/share",
                read_only=False,
                propagation="rslave",
            ),
            Mount(
                type="bind",
                source=coresys.config.path_extern_media.as_posix(),
                target="/media",
                read_only=False,
                propagation="rslave",
            ),
            Mount(
                type="bind",
                source=coresys.homeassistant.path_extern_pulse.as_posix(),
                target="/etc/pulse/client.conf",
                read_only=True,
            ),
            Mount(
                type="bind",
                source=coresys.plugins.audio.path_extern_pulse.as_posix(),
                target="/run/audio",
                read_only=True,
            ),
            Mount(
                type="bind",
                source=coresys.plugins.audio.path_extern_asound.as_posix(),
                target="/etc/asound.conf",
                read_only=True,
            ),
            Mount(
                type="bind",
                source="/etc/machine-id",
                target="/etc/machine-id",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs


async def test_landingpage_start(
    coresys: CoreSys, tmp_supervisor_data: Path, path_extern
):
    """Test starting landingpage."""
    coresys.homeassistant.version = LANDINGPAGE

    with patch.object(DockerAPI, "run") as run, patch.object(
        DockerHomeAssistant, "is_running", return_value=False
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
        }
        assert run.call_args.kwargs["mounts"] == [
            Mount(type="bind", source="/dev", target="/dev", read_only=True),
            Mount(type="bind", source="/run/dbus", target="/run/dbus", read_only=True),
            Mount(type="bind", source="/run/udev", target="/run/udev", read_only=True),
            Mount(
                type="bind",
                source=coresys.config.path_extern_homeassistant.as_posix(),
                target="/config",
                read_only=False,
            ),
            Mount(
                type="bind",
                source="/etc/machine-id",
                target="/etc/machine-id",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs
