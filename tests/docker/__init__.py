"""Docker tests."""

from supervisor.docker.const import DockerMount, MountBindOptions, MountType

# dev mount with equivalent of bind-recursive=writable specified via dict value
DEV_MOUNT = DockerMount(
    type=MountType.BIND,
    source="/dev",
    target="/dev",
    read_only=True,
    bind_options=MountBindOptions(read_only_non_recursive=True),
)
