"""Test Docker manager."""

import asyncio
from unittest.mock import MagicMock, patch

from docker.errors import DockerException
import pytest
from requests import RequestException

from supervisor.coresys import CoreSys
from supervisor.docker.manager import CommandReturn, DockerAPI
from supervisor.exceptions import DockerError


async def test_run_command_success(docker: DockerAPI):
    """Test successful command execution."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"command output"

    # Mock docker containers.run to return our mock container
    docker.docker.containers.run.return_value = mock_container

    # Execute the command
    result = docker.run_command(
        image="alpine", version="3.18", command="echo hello", stdout=True, stderr=True
    )

    # Verify the result
    assert isinstance(result, CommandReturn)
    assert result.exit_code == 0
    assert result.output == b"command output"

    # Verify docker.containers.run was called correctly
    docker.docker.containers.run.assert_called_once_with(
        "alpine:3.18",
        command="echo hello",
        detach=True,
        network=docker.network.name,
        use_config_proxy=False,
        stdout=True,
        stderr=True,
    )

    # Verify container cleanup
    mock_container.remove.assert_called_once_with(force=True, v=True)


async def test_run_command_with_defaults(docker: DockerAPI):
    """Test command execution with default parameters."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 1}
    mock_container.logs.return_value = b"error output"

    # Mock docker containers.run to return our mock container
    docker.docker.containers.run.return_value = mock_container

    # Execute the command with minimal parameters
    result = docker.run_command(image="ubuntu")

    # Verify the result
    assert isinstance(result, CommandReturn)
    assert result.exit_code == 1
    assert result.output == b"error output"

    # Verify docker.containers.run was called with defaults
    docker.docker.containers.run.assert_called_once_with(
        "ubuntu:latest",  # default tag
        command=None,  # default command
        detach=True,
        network=docker.network.name,
        use_config_proxy=False,
    )

    # Verify container.logs was called with default stdout/stderr
    mock_container.logs.assert_called_once_with(stdout=True, stderr=True)


async def test_run_command_docker_exception(docker: DockerAPI):
    """Test command execution when Docker raises an exception."""
    # Mock docker containers.run to raise DockerException
    docker.docker.containers.run.side_effect = DockerException("Docker error")

    # Execute the command and expect DockerError
    with pytest.raises(DockerError, match="Can't execute command: Docker error"):
        docker.run_command(image="alpine", command="test")


async def test_run_command_request_exception(docker: DockerAPI):
    """Test command execution when requests raises an exception."""
    # Mock docker containers.run to raise RequestException
    docker.docker.containers.run.side_effect = RequestException("Connection error")

    # Execute the command and expect DockerError
    with pytest.raises(DockerError, match="Can't execute command: Connection error"):
        docker.run_command(image="alpine", command="test")


async def test_run_command_cleanup_on_exception(docker: DockerAPI):
    """Test that container cleanup happens even when an exception occurs."""
    # Mock container
    mock_container = MagicMock()

    # Mock docker.containers.run to return container, but container.wait to raise exception
    docker.docker.containers.run.return_value = mock_container
    mock_container.wait.side_effect = DockerException("Wait failed")

    # Execute the command and expect DockerError
    with pytest.raises(DockerError):
        docker.run_command(image="alpine", command="test")

    # Verify container cleanup still happened
    mock_container.remove.assert_called_once_with(force=True, v=True)


async def test_run_command_custom_stdout_stderr(docker: DockerAPI):
    """Test command execution with custom stdout/stderr settings."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"output"

    # Mock docker containers.run to return our mock container
    docker.docker.containers.run.return_value = mock_container

    # Execute the command with custom stdout/stderr
    result = docker.run_command(
        image="alpine", command="test", stdout=False, stderr=True
    )

    # Verify container.logs was called with the correct parameters
    mock_container.logs.assert_called_once_with(stdout=False, stderr=True)

    # Verify the result
    assert result.exit_code == 0
    assert result.output == b"output"


async def test_run_container_with_cidfile(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container creation with cidfile and bind mount."""
    # Mock container
    mock_container = MagicMock()
    mock_container.id = "test_container_id_12345"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"
    extern_cidfile_path = coresys.config.path_extern_cid_files / f"{container_name}.cid"

    docker.docker.containers.run.return_value = mock_container

    # Mock container creation
    with patch.object(
        docker.containers, "create", return_value=mock_container
    ) as create_mock:
        # Execute run with a container name
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda kwrgs: docker.run(**kwrgs),
            {"image": "test_image", "tag": "latest", "name": container_name},
        )

        # Check the container creation parameters
        create_mock.assert_called_once()
        kwargs = create_mock.call_args[1]

        assert "volumes" in kwargs
        assert str(extern_cidfile_path) in kwargs["volumes"]
        assert kwargs["volumes"][str(extern_cidfile_path)]["bind"] == "/run/cid"
        assert kwargs["volumes"][str(extern_cidfile_path)]["mode"] == "ro"

        # Verify container start was called
        mock_container.start.assert_called_once()

        # Verify cidfile was written with container ID
        assert cidfile_path.exists()
        assert cidfile_path.read_text() == mock_container.id

        assert result == mock_container


async def test_run_container_with_leftover_cidfile(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container creation removes leftover cidfile before creating new one."""
    # Mock container
    mock_container = MagicMock()
    mock_container.id = "test_container_id_new"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a leftover cidfile
    cidfile_path.touch()

    # Mock container creation
    with patch.object(
        docker.containers, "create", return_value=mock_container
    ) as create_mock:
        # Execute run with a container name
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda kwrgs: docker.run(**kwrgs),
            {"image": "test_image", "tag": "latest", "name": container_name},
        )

        # Verify container was created
        create_mock.assert_called_once()

        # Verify new cidfile was written with container ID
        assert cidfile_path.exists()
        assert cidfile_path.read_text() == mock_container.id

        assert result == mock_container


async def test_stop_container_with_cidfile_cleanup(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container stop with cidfile cleanup."""
    # Mock container
    mock_container = MagicMock()
    mock_container.status = "running"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a cidfile
    cidfile_path.touch()

    # Mock the containers.get method and cidfile cleanup
    with (
        patch.object(docker.containers, "get", return_value=mock_container),
    ):
        # Call stop_container with remove_container=True
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda kwrgs: docker.stop_container(**kwrgs),
            {"timeout": 10, "remove_container": True, "name": container_name},
        )

        # Verify container operations
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once_with(force=True, v=True)

        assert not cidfile_path.exists()


async def test_stop_container_without_removal_no_cidfile_cleanup(docker: DockerAPI):
    """Test container stop without removal doesn't clean up cidfile."""
    # Mock container
    mock_container = MagicMock()
    mock_container.status = "running"

    container_name = "test_container"

    # Mock the containers.get method and cidfile cleanup
    with (
        patch.object(docker.containers, "get", return_value=mock_container),
        patch("pathlib.Path.unlink") as mock_unlink,
    ):
        # Call stop_container with remove_container=False
        docker.stop_container(container_name, timeout=10, remove_container=False)

        # Verify container operations
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_not_called()

        # Verify cidfile cleanup was NOT called
        mock_unlink.assert_not_called()


async def test_cidfile_cleanup_handles_oserror(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test that cidfile cleanup handles OSError gracefully."""
    # Mock container
    mock_container = MagicMock()
    mock_container.status = "running"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a cidfile
    cidfile_path.touch()

    # Mock the containers.get method and cidfile cleanup to raise OSError
    with (
        patch.object(docker.containers, "get", return_value=mock_container),
        patch(
            "pathlib.Path.unlink", side_effect=OSError("File not found")
        ) as mock_unlink,
    ):
        # Call stop_container - should not raise exception
        docker.stop_container(container_name, timeout=10, remove_container=True)

        # Verify container operations completed
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once_with(force=True, v=True)

        # Verify cidfile cleanup was attempted
        mock_unlink.assert_called_once_with(missing_ok=True)
