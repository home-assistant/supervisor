"""Test Docker interface."""

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, PropertyMock, call, patch

import aiodocker
from awesomeversion import AwesomeVersion
from docker.errors import DockerException, NotFound
from docker.models.containers import Container
import pytest
from requests import RequestException

from supervisor.addons.manager import Addon
from supervisor.const import BusEvent, CoreState, CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DOCKER_HUB, DockerInterface
from supervisor.docker.manager import PullLogEntry, PullProgressDetail
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    DockerAPIError,
    DockerError,
    DockerNoSpaceOnDevice,
    DockerNotFound,
    DockerRequestError,
)
from supervisor.homeassistant.const import WSEvent, WSType
from supervisor.jobs import ChildJobSyncFilter, JobSchedulerOptions, SupervisorJob
from supervisor.jobs.decorator import Job
from supervisor.supervisor import Supervisor

from tests.common import AsyncIterator, load_json_fixture


@pytest.mark.parametrize(
    "cpu_arch, platform",
    [
        (CpuArch.ARMV7, "linux/arm/v7"),
        (CpuArch.ARMHF, "linux/arm/v6"),
        (CpuArch.AARCH64, "linux/arm64"),
        (CpuArch.I386, "linux/386"),
        (CpuArch.AMD64, "linux/amd64"),
    ],
)
async def test_docker_image_platform(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    cpu_arch: str,
    platform: str,
):
    """Test platform set correctly from arch."""
    coresys.docker.images.inspect.return_value = {"Id": "test:1.2.3"}
    await test_docker_interface.install(AwesomeVersion("1.2.3"), "test", arch=cpu_arch)
    coresys.docker.images.pull.assert_called_once_with(
        "test", tag="1.2.3", platform=platform, auth=None, stream=True
    )
    coresys.docker.images.inspect.assert_called_once_with("test:1.2.3")


async def test_docker_image_default_platform(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test platform set using supervisor arch when omitted."""
    coresys.docker.images.inspect.return_value = {"Id": "test:1.2.3"}
    with (
        patch.object(
            type(coresys.supervisor), "arch", PropertyMock(return_value="i386")
        ),
    ):
        await test_docker_interface.install(AwesomeVersion("1.2.3"), "test")
        coresys.docker.images.pull.assert_called_once_with(
            "test", tag="1.2.3", platform="linux/386", auth=None, stream=True
        )

    coresys.docker.images.inspect.assert_called_once_with("test:1.2.3")


@pytest.mark.parametrize(
    "image,registry_key",
    [
        ("homeassistant/amd64-supervisor", DOCKER_HUB),
        ("ghcr.io/home-assistant/amd64-supervisor", "ghcr.io"),
    ],
)
async def test_private_registry_credentials_passed_to_pull(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    image: str,
    registry_key: str,
):
    """Test credentials for private registries are passed to aiodocker pull."""
    coresys.docker.images.inspect.return_value = {"Id": f"{image}:1.2.3"}

    # Configure registry credentials
    coresys.docker.config._data["registries"] = {  # pylint: disable=protected-access
        registry_key: {"username": "testuser", "password": "testpass"}
    }

    with patch.object(
        type(coresys.supervisor), "arch", PropertyMock(return_value="amd64")
    ):
        await test_docker_interface.install(
            AwesomeVersion("1.2.3"), image, arch=CpuArch.AMD64
        )

    # Verify credentials were passed to aiodocker
    expected_auth = {"username": "testuser", "password": "testpass"}
    if registry_key != DOCKER_HUB:
        expected_auth["registry"] = registry_key

    coresys.docker.images.pull.assert_called_once_with(
        image, tag="1.2.3", platform="linux/amd64", auth=expected_auth, stream=True
    )


@pytest.mark.parametrize(
    "attrs,expected",
    [
        ({"State": {"Status": "running"}}, ContainerState.RUNNING),
        ({"State": {"Status": "exited", "ExitCode": 0}}, ContainerState.STOPPED),
        ({"State": {"Status": "exited", "ExitCode": 137}}, ContainerState.FAILED),
        (
            {"State": {"Status": "running", "Health": {"Status": "healthy"}}},
            ContainerState.HEALTHY,
        ),
        (
            {"State": {"Status": "running", "Health": {"Status": "unhealthy"}}},
            ContainerState.UNHEALTHY,
        ),
    ],
)
async def test_current_state(
    coresys: CoreSys, attrs: dict[str, Any], expected: ContainerState
):
    """Test current state for container."""
    container_collection = MagicMock()
    container_collection.get.return_value = Container(attrs)
    with patch(
        "supervisor.docker.manager.DockerAPI.containers",
        new=PropertyMock(return_value=container_collection),
    ):
        assert await coresys.homeassistant.core.instance.current_state() == expected


async def test_current_state_failures(coresys: CoreSys):
    """Test failure states for current state."""
    container_collection = MagicMock()
    with patch(
        "supervisor.docker.manager.DockerAPI.containers",
        new=PropertyMock(return_value=container_collection),
    ):
        container_collection.get.side_effect = NotFound("dne")
        assert (
            await coresys.homeassistant.core.instance.current_state()
            == ContainerState.UNKNOWN
        )

        container_collection.get.side_effect = DockerException()
        with pytest.raises(DockerAPIError):
            await coresys.homeassistant.core.instance.current_state()

        container_collection.get.side_effect = RequestException()
        with pytest.raises(DockerRequestError):
            await coresys.homeassistant.core.instance.current_state()


@pytest.mark.parametrize(
    "attrs,expected,fired_when_skip_down",
    [
        ({"State": {"Status": "running"}}, ContainerState.RUNNING, True),
        ({"State": {"Status": "exited", "ExitCode": 0}}, ContainerState.STOPPED, False),
        (
            {"State": {"Status": "exited", "ExitCode": 137}},
            ContainerState.FAILED,
            False,
        ),
        (
            {"State": {"Status": "running", "Health": {"Status": "healthy"}}},
            ContainerState.HEALTHY,
            True,
        ),
        (
            {"State": {"Status": "running", "Health": {"Status": "unhealthy"}}},
            ContainerState.UNHEALTHY,
            True,
        ),
    ],
)
async def test_attach_existing_container(
    coresys: CoreSys,
    attrs: dict[str, Any],
    expected: ContainerState,
    fired_when_skip_down: bool,
):
    """Test attaching to existing container."""
    attrs["Id"] = "abc123"
    attrs["Config"] = {}
    container_collection = MagicMock()
    container_collection.get.return_value = Container(attrs)
    with (
        patch(
            "supervisor.docker.manager.DockerAPI.containers",
            new=PropertyMock(return_value=container_collection),
        ),
        patch.object(type(coresys.bus), "fire_event") as fire_event,
        patch("supervisor.docker.interface.time", return_value=1),
    ):
        await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))
        await asyncio.sleep(0)
        assert [
            event
            for event in fire_event.call_args_list
            if event.args[0] == BusEvent.DOCKER_CONTAINER_STATE_CHANGE
        ] == [
            call(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                DockerContainerStateEvent("homeassistant", expected, "abc123", 1),
            )
        ]

        fire_event.reset_mock()
        await coresys.homeassistant.core.instance.attach(
            AwesomeVersion("2022.7.3"), skip_state_event_if_down=True
        )
        await asyncio.sleep(0)
        docker_events = [
            event
            for event in fire_event.call_args_list
            if event.args[0] == BusEvent.DOCKER_CONTAINER_STATE_CHANGE
        ]
        if fired_when_skip_down:
            assert docker_events == [
                call(
                    BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                    DockerContainerStateEvent("homeassistant", expected, "abc123", 1),
                )
            ]
        else:
            assert not docker_events


async def test_attach_container_failure(coresys: CoreSys):
    """Test attach fails to find container but finds image."""
    coresys.docker.containers.get.side_effect = DockerException()
    coresys.docker.images.inspect.return_value.setdefault("Config", {})["Image"] = (
        "sha256:abc123"
    )
    with patch.object(type(coresys.bus), "fire_event") as fire_event:
        await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))
        assert not [
            event
            for event in fire_event.call_args_list
            if event.args[0] == BusEvent.DOCKER_CONTAINER_STATE_CHANGE
        ]
        assert (
            coresys.homeassistant.core.instance.meta_config["Image"] == "sha256:abc123"
        )


async def test_attach_total_failure(coresys: CoreSys):
    """Test attach fails to find container or image."""
    coresys.docker.containers.get.side_effect = DockerException
    coresys.docker.images.inspect.side_effect = aiodocker.DockerError(
        400, {"message": ""}
    )
    with pytest.raises(DockerError):
        await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))


@pytest.mark.parametrize(
    "err", [aiodocker.DockerError(400, {"message": ""}), RequestException()]
)
async def test_image_pull_fail(
    coresys: CoreSys, capture_exception: Mock, err: Exception
):
    """Test failure to pull image."""
    coresys.docker.images.inspect.side_effect = err
    with pytest.raises(DockerError):
        await coresys.homeassistant.core.instance.install(
            AwesomeVersion("2022.7.3"), arch=CpuArch.AMD64
        )

    capture_exception.assert_called_once_with(err)


async def test_run_missing_image(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    capture_exception: Mock,
    path_extern,
    tmp_supervisor_data: Path,
):
    """Test run captures the exception when image is missing."""
    coresys.docker.containers.create.side_effect = [NotFound("missing"), MagicMock()]
    container.status = "stopped"
    install_addon_ssh.data["image"] = "test_image"

    with pytest.raises(DockerNotFound):
        await install_addon_ssh.instance.run()

    capture_exception.assert_called_once()


async def test_install_fires_progress_events(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test progress events are fired during an install for listeners."""

    # This is from a sample pull. Filtered log to just one per unique status for test
    logs = [
        {
            "status": "Pulling from home-assistant/odroid-n2-homeassistant",
            "id": "2025.7.2",
        },
        {"status": "Already exists", "progressDetail": {}, "id": "6e771e15690e"},
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "1578b14a573c"},
        {"status": "Waiting", "progressDetail": {}, "id": "1578b14a573c"},
        {
            "status": "Downloading",
            "progressDetail": {"current": 1378, "total": 1486},
            "progress": "[==============================================>    ]  1.378kB/1.486kB",
            "id": "1578b14a573c",
        },
        {"status": "Download complete", "progressDetail": {}, "id": "1578b14a573c"},
        {
            "status": "Extracting",
            "progressDetail": {"current": 1486, "total": 1486},
            "progress": "[==================================================>]  1.486kB/1.486kB",
            "id": "1578b14a573c",
        },
        {"status": "Pull complete", "progressDetail": {}, "id": "1578b14a573c"},
        {
            "status": "Verifying Checksum",
            "progressDetail": {},
            "id": "6a1e931d8f88",
        },
        {
            "status": "Digest: sha256:490080d7da0f385928022927990e04f604615f7b8c622ef3e58253d0f089881d"
        },
        {
            "status": "Status: Downloaded newer image for ghcr.io/home-assistant/odroid-n2-homeassistant:2025.7.2"
        },
    ]
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    events: list[PullLogEntry] = []

    async def capture_log_entry(event: PullLogEntry) -> None:
        events.append(event)

    coresys.bus.register_event(BusEvent.DOCKER_IMAGE_PULL_UPDATE, capture_log_entry)

    with (
        patch.object(
            type(coresys.supervisor), "arch", PropertyMock(return_value="i386")
        ),
    ):
        await test_docker_interface.install(AwesomeVersion("1.2.3"), "test")
        coresys.docker.images.pull.assert_called_once_with(
            "test", tag="1.2.3", platform="linux/386", auth=None, stream=True
        )
        coresys.docker.images.inspect.assert_called_once_with("test:1.2.3")

    await asyncio.sleep(1)
    assert events == [
        PullLogEntry(
            job_id=ANY,
            status="Pulling from home-assistant/odroid-n2-homeassistant",
            id="2025.7.2",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Already exists",
            progress_detail=PullProgressDetail(),
            id="6e771e15690e",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Pulling fs layer",
            progress_detail=PullProgressDetail(),
            id="1578b14a573c",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Waiting",
            progress_detail=PullProgressDetail(),
            id="1578b14a573c",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Downloading",
            progress_detail=PullProgressDetail(current=1378, total=1486),
            progress="[==============================================>    ]  1.378kB/1.486kB",
            id="1578b14a573c",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Download complete",
            progress_detail=PullProgressDetail(),
            id="1578b14a573c",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Extracting",
            progress_detail=PullProgressDetail(current=1486, total=1486),
            progress="[==================================================>]  1.486kB/1.486kB",
            id="1578b14a573c",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Pull complete",
            progress_detail=PullProgressDetail(),
            id="1578b14a573c",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Verifying Checksum",
            progress_detail=PullProgressDetail(),
            id="6a1e931d8f88",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Digest: sha256:490080d7da0f385928022927990e04f604615f7b8c622ef3e58253d0f089881d",
        ),
        PullLogEntry(
            job_id=ANY,
            status="Status: Downloaded newer image for ghcr.io/home-assistant/odroid-n2-homeassistant:2025.7.2",
        ),
    ]


async def test_install_progress_rounding_does_not_cause_misses(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    ha_ws_client: AsyncMock,
    capture_exception: Mock,
):
    """Test extremely close progress events do not create rounding issues."""
    coresys.core.set_state(CoreState.RUNNING)

    # Current numbers chosen to create a rounding issue with original code
    # Where a progress update came in with a value between the actual previous
    # value and what it was rounded to. It should not raise an out of order exception
    logs = [
        {
            "status": "Pulling from home-assistant/odroid-n2-homeassistant",
            "id": "2025.7.1",
        },
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {
            "status": "Downloading",
            "progressDetail": {"current": 432700000, "total": 436480882},
            "progress": "[=================================================> ]  432.7MB/436.5MB",
            "id": "1e214cd6d7d0",
        },
        {
            "status": "Downloading",
            "progressDetail": {"current": 432800000, "total": 436480882},
            "progress": "[=================================================> ]  432.8MB/436.5MB",
            "id": "1e214cd6d7d0",
        },
        {"status": "Verifying Checksum", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {"status": "Download complete", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {
            "status": "Extracting",
            "progressDetail": {"current": 432700000, "total": 436480882},
            "progress": "[=================================================> ]  432.7MB/436.5MB",
            "id": "1e214cd6d7d0",
        },
        {
            "status": "Extracting",
            "progressDetail": {"current": 432800000, "total": 436480882},
            "progress": "[=================================================> ]  432.8MB/436.5MB",
            "id": "1e214cd6d7d0",
        },
        {"status": "Pull complete", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {
            "status": "Digest: sha256:7d97da645f232f82a768d0a537e452536719d56d484d419836e53dbe3e4ec736"
        },
        {
            "status": "Status: Downloaded newer image for ghcr.io/home-assistant/odroid-n2-homeassistant:2025.7.1"
        },
    ]
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    # Schedule job so we can listen for the end. Then we can assert against the WS mock
    event = asyncio.Event()
    job, install_task = coresys.jobs.schedule_job(
        test_docker_interface.install,
        JobSchedulerOptions(),
        AwesomeVersion("1.2.3"),
        "test",
    )

    async def listen_for_job_end(reference: SupervisorJob):
        if reference.uuid != job.uuid:
            return
        event.set()

    coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_END, listen_for_job_end)
    await install_task
    await event.wait()

    capture_exception.assert_not_called()


@pytest.mark.parametrize(
    ("error_log", "exc_type", "exc_msg"),
    [
        (
            {
                "errorDetail": {
                    "message": "write /mnt/data/docker/tmp/GetImageBlob2228293192: no space left on device"
                },
                "error": "write /mnt/data/docker/tmp/GetImageBlob2228293192: no space left on device",
            },
            DockerNoSpaceOnDevice,
            "No space left on disk",
        ),
        (
            {"errorDetail": {"message": "failure"}, "error": "failure"},
            DockerError,
            "failure",
        ),
    ],
)
async def test_install_raises_on_pull_error(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    error_log: dict[str, Any],
    exc_type: type[DockerError],
    exc_msg: str,
):
    """Test exceptions raised from errors in pull log."""

    logs = [
        {
            "status": "Pulling from home-assistant/odroid-n2-homeassistant",
            "id": "2025.7.2",
        },
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "1578b14a573c"},
        {
            "status": "Downloading",
            "progressDetail": {"current": 1378, "total": 1486},
            "progress": "[==============================================>    ]  1.378kB/1.486kB",
            "id": "1578b14a573c",
        },
        error_log,
    ]
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    with pytest.raises(exc_type, match=exc_msg):
        await test_docker_interface.install(AwesomeVersion("1.2.3"), "test")


async def test_install_progress_handles_download_restart(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    ha_ws_client: AsyncMock,
    capture_exception: Mock,
):
    """Test install handles docker progress events that include a download restart."""
    coresys.core.set_state(CoreState.RUNNING)

    # Fixture emulates a download restart as it docker logs it
    # A log out of order exception should not be raised
    logs = load_json_fixture("docker_pull_image_log_restart.json")
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    with (
        patch.object(
            type(coresys.supervisor), "arch", PropertyMock(return_value="i386")
        ),
    ):
        # Schedule job so we can listen for the end. Then we can assert against the WS mock
        event = asyncio.Event()
        job, install_task = coresys.jobs.schedule_job(
            test_docker_interface.install,
            JobSchedulerOptions(),
            AwesomeVersion("1.2.3"),
            "test",
        )

        async def listen_for_job_end(reference: SupervisorJob):
            if reference.uuid != job.uuid:
                return
            event.set()

        coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_END, listen_for_job_end)
        await install_task
        await event.wait()

    capture_exception.assert_not_called()


@pytest.mark.parametrize(
    "extract_log",
    [
        {
            "status": "Extracting",
            "progressDetail": {"current": 96, "total": 96},
            "progress": "[==================================================>]      96B/96B",
            "id": "02a6e69d8d00",
        },
        {
            "status": "Extracting",
            "progressDetail": {"current": 1, "units": "s"},
            "progress": "1 s",
            "id": "02a6e69d8d00",
        },
    ],
    ids=["normal_extract_log", "containerd_snapshot_extract_log"],
)
async def test_install_progress_handles_layers_skipping_download(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    capture_exception: Mock,
    extract_log: dict[str, Any],
):
    """Test install handles small layers that skip downloading phase and go directly to download complete.

    Reproduces the real-world scenario from Supervisor issue #6286:
    - Small layer (02a6e69d8d00) completes Download complete at 10:14:08 without ever Downloading
    - Normal layer (3f4a84073184) starts Downloading at 10:14:09 with progress updates

    Under containerd snapshotter this presumably can still occur and Supervisor will have even less info
    since extract logs don't have a total. Supervisor should generally just ignore these and set progress
    from the larger images that take all the time.
    """
    coresys.core.set_state(CoreState.RUNNING)

    # Reproduce EXACT sequence from SupervisorNoUpdateProgressLogs.txt:
    # Small layer (02a6e69d8d00) completes BEFORE normal layer (3f4a84073184) starts downloading
    logs = [
        {"status": "Pulling from test/image", "id": "latest"},
        # Small layer that skips downloading (02a6e69d8d00 in logs, 96 bytes)
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "02a6e69d8d00"},
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "3f4a84073184"},
        {"status": "Waiting", "progressDetail": {}, "id": "02a6e69d8d00"},
        {"status": "Waiting", "progressDetail": {}, "id": "3f4a84073184"},
        # Goes straight to Download complete (10:14:08 in logs) - THIS IS THE KEY MOMENT
        {"status": "Download complete", "progressDetail": {}, "id": "02a6e69d8d00"},
        # Normal layer that downloads (3f4a84073184 in logs, 25MB)
        # Downloading starts (10:14:09 in logs) - progress updates should happen NOW!
        {
            "status": "Downloading",
            "progressDetail": {"current": 260937, "total": 25371463},
            "progress": "[>                                                  ]  260.9kB/25.37MB",
            "id": "3f4a84073184",
        },
        {
            "status": "Downloading",
            "progressDetail": {"current": 5505024, "total": 25371463},
            "progress": "[==========>                                        ]  5.505MB/25.37MB",
            "id": "3f4a84073184",
        },
        {
            "status": "Downloading",
            "progressDetail": {"current": 11272192, "total": 25371463},
            "progress": "[======================>                            ]  11.27MB/25.37MB",
            "id": "3f4a84073184",
        },
        {"status": "Download complete", "progressDetail": {}, "id": "3f4a84073184"},
        {
            "status": "Extracting",
            "progressDetail": {"current": 25371463, "total": 25371463},
            "progress": "[==================================================>]  25.37MB/25.37MB",
            "id": "3f4a84073184",
        },
        {"status": "Pull complete", "progressDetail": {}, "id": "3f4a84073184"},
        # Small layer finally extracts (10:14:58 in logs)
        extract_log,
        {"status": "Pull complete", "progressDetail": {}, "id": "02a6e69d8d00"},
        {"status": "Digest: sha256:test"},
        {"status": "Status: Downloaded newer image for test/image:latest"},
    ]
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    # Capture immutable snapshots of install job progress using job.as_dict()
    # This solves the mutable object problem - we snapshot state at call time
    install_job_snapshots = []
    original_on_job_change = coresys.jobs._on_job_change  # pylint: disable=W0212

    def capture_and_forward(job_obj, attribute, value):
        # Capture immutable snapshot if this is the install job with progress
        if job_obj.name == "docker_interface_install" and job_obj.progress > 0:
            install_job_snapshots.append(job_obj.as_dict())
        # Forward to original to maintain functionality
        return original_on_job_change(job_obj, attribute, value)

    with patch.object(coresys.jobs, "_on_job_change", side_effect=capture_and_forward):
        event = asyncio.Event()
        job, install_task = coresys.jobs.schedule_job(
            test_docker_interface.install,
            JobSchedulerOptions(),
            AwesomeVersion("1.2.3"),
            "test",
        )

        async def listen_for_job_end(reference: SupervisorJob):
            if reference.uuid != job.uuid:
                return
            event.set()

        coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_END, listen_for_job_end)
        await install_task
        await event.wait()

        # First update from layer download should have rather low progress ((260937/25445459) / 2 ~ 0.5%)
        assert install_job_snapshots[0]["progress"] < 1

        # Total 8 events should lead to a progress update on the install job
        assert len(install_job_snapshots) == 8

        # Job should complete successfully
        assert job.done is True
        assert job.progress == 100
        capture_exception.assert_not_called()


async def test_missing_total_handled_gracefully(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    ha_ws_client: AsyncMock,
    capture_exception: Mock,
):
    """Test missing 'total' fields in progress details handled gracefully."""
    coresys.core.set_state(CoreState.RUNNING)

    # Progress details with missing 'total' fields observed in real-world pulls
    logs = [
        {
            "status": "Pulling from home-assistant/odroid-n2-homeassistant",
            "id": "2025.7.1",
        },
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {
            "status": "Downloading",
            "progressDetail": {"current": 436480882},
            "progress": "[===================================================]  436.5MB/436.5MB",
            "id": "1e214cd6d7d0",
        },
        {"status": "Verifying Checksum", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {"status": "Download complete", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {
            "status": "Extracting",
            "progressDetail": {"current": 436480882},
            "progress": "[===================================================]  436.5MB/436.5MB",
            "id": "1e214cd6d7d0",
        },
        {"status": "Pull complete", "progressDetail": {}, "id": "1e214cd6d7d0"},
        {
            "status": "Digest: sha256:7d97da645f232f82a768d0a537e452536719d56d484d419836e53dbe3e4ec736"
        },
        {
            "status": "Status: Downloaded newer image for ghcr.io/home-assistant/odroid-n2-homeassistant:2025.7.1"
        },
    ]
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    # Schedule job so we can listen for the end. Then we can assert against the WS mock
    event = asyncio.Event()
    job, install_task = coresys.jobs.schedule_job(
        test_docker_interface.install,
        JobSchedulerOptions(),
        AwesomeVersion("1.2.3"),
        "test",
    )

    async def listen_for_job_end(reference: SupervisorJob):
        if reference.uuid != job.uuid:
            return
        event.set()

    coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_END, listen_for_job_end)
    await install_task
    await event.wait()

    capture_exception.assert_not_called()


async def test_install_progress_containerd_snapshot(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test install handles docker progress events using containerd snapshotter."""
    coresys.core.set_state(CoreState.RUNNING)

    class TestDockerInterface(DockerInterface):
        """Test interface for events."""

        @property
        def name(self) -> str:
            """Name of test interface."""
            return "test_interface"

        @Job(
            name="mock_docker_interface_install",
            child_job_syncs=[
                ChildJobSyncFilter("docker_interface_install", progress_allocation=1.0)
            ],
        )
        async def mock_install(self) -> None:
            """Mock install."""
            await super().install(
                AwesomeVersion("1.2.3"), image="test", arch=CpuArch.I386
            )

    # Fixture emulates log as received when using containerd snapshotter
    # Should not error but progress gets choppier once extraction starts
    logs = load_json_fixture("docker_pull_image_log_containerd_snapshot.json")
    coresys.docker.images.pull.return_value = AsyncIterator(logs)
    test_docker_interface = TestDockerInterface(coresys)

    with patch.object(Supervisor, "arch", PropertyMock(return_value="i386")):
        await test_docker_interface.mock_install()
        coresys.docker.images.pull.assert_called_once_with(
            "test", tag="1.2.3", platform="linux/386", auth=None, stream=True
        )
        coresys.docker.images.inspect.assert_called_once_with("test:1.2.3")

    await asyncio.sleep(1)

    def job_event(progress: float, done: bool = False):
        return {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.JOB,
                "data": {
                    "name": "mock_docker_interface_install",
                    "reference": "test_interface",
                    "uuid": ANY,
                    "progress": progress,
                    "stage": None,
                    "done": done,
                    "parent_id": None,
                    "errors": [],
                    "created": ANY,
                    "extra": None,
                },
            },
        }

    assert [c.args[0] for c in ha_ws_client.async_send_command.call_args_list] == [
        # During downloading we get continuous progress updates from download status
        job_event(0),
        job_event(3.4),
        job_event(8.5),
        job_event(10.2),
        job_event(15.3),
        job_event(18.8),
        job_event(29.0),
        job_event(35.8),
        job_event(42.6),
        job_event(49.5),
        job_event(56.0),
        job_event(62.8),
        # Downloading phase is considered 70% of total. After we only get one update
        # per image downloaded when extraction is finished. It uses the total size
        # received during downloading to determine percent complete then.
        job_event(70.0),
        job_event(84.8),
        job_event(100),
        job_event(100, True),
    ]
