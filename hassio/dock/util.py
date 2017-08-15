"""HassIO docker utilitys."""
import re

from ..const import ARCH_AARCH64, ARCH_ARMHF, ARCH_I386, ARCH_AMD64


HASSIO_BASE_IMAGE = {
    ARCH_ARMHF: "homeassistant/armhf-base:latest",
    ARCH_AARCH64: "homeassistant/aarch64-base:latest",
    ARCH_I386: "homeassistant/i386-base:latest",
    ARCH_AMD64: "homeassistant/amd64-base:latest",
}

TMPL_IMAGE = re.compile(r"%%BASE_IMAGE%%")


def dockerfile_template(dockerfile, arch, version, meta_type):
    """Prepare a Hass.IO dockerfile."""
    buff = []
    hassio_image = HASSIO_BASE_IMAGE[arch]
    custom_image = re.compile(r"^#{}:FROM".format(arch))

    # read docker
    with dockerfile.open('r') as dock_input:
        for line in dock_input:
            line = TMPL_IMAGE.sub(hassio_image, line)
            line = custom_image.sub("FROM", line)
            buff.append(line)

    # add metadata
    buff.append(create_metadata(version, arch, meta_type))

    # write docker
    with dockerfile.open('w') as dock_output:
        dock_output.writelines(buff)


def create_metadata(version, arch, meta_type):
    """Generate docker label layer for hassio."""
    return ('LABEL io.hass.version="{}" '
            'io.hass.arch="{}" '
            'io.hass.type="{}"').format(version, arch, meta_type)


def docker_process(method):
    """Wrap function with only run once."""
    async def wrap_api(api, *args, **kwargs):
        """Return api wrapper."""
        if api._lock.locked():
            _LOGGER.error(
                "Can't excute %s while a task is in progress", method.__name__)
            return False

        async with self._lock:
            return await method(api, *args, **kwargs)
