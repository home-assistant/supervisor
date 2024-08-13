"""Docker tests."""

from docker.types import Mount

# dev mount with equivalent of bind-recursive=writable specified via dict value
DEV_MOUNT = Mount(type="bind", source="/dev", target="/dev", read_only=True)
DEV_MOUNT["BindOptions"] = {"ReadOnlyNonRecursive": True}
