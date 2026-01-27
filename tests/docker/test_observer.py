"""Test Observer plugin container."""

from ipaddress import IPv4Address, ip_network
from unittest.mock import patch

from aiodocker.containers import DockerContainer

from supervisor.coresys import CoreSys
from supervisor.docker.const import DockerMount, MountType
from supervisor.docker.manager import DockerAPI


async def test_start(coresys: CoreSys, container: DockerContainer):
    """Test starting observer plugin."""
    with patch.object(
        DockerAPI, "run", return_value=container.show.return_value
    ) as run:
        await coresys.plugins.observer.start()

        run.assert_called_once()
        assert run.call_args.kwargs["ipv4"] == IPv4Address("172.30.32.6")
        assert run.call_args.kwargs["name"] == "hassio_observer"
        assert run.call_args.kwargs["hostname"] == "hassio-observer"
        assert run.call_args.kwargs["restart_policy"] == {"Name": "always"}
        assert run.call_args.kwargs["extra_hosts"] == {
            "supervisor": IPv4Address("172.30.32.2")
        }
        assert run.call_args.kwargs["oom_score_adj"] == -300
        assert run.call_args.kwargs["environment"]["NETWORK_MASK"] == ip_network(
            "172.30.32.0/23"
        )
        assert run.call_args.kwargs["ports"] == {"80/tcp": 4357}
        assert run.call_args.kwargs["mounts"] == [
            DockerMount(
                type=MountType.BIND,
                source="/run/docker.sock",
                target="/run/docker.sock",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs
