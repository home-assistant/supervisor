"""Test Docker manager."""

from unittest.mock import MagicMock

from docker.errors import DockerException
import pytest
from requests import RequestException

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
