"""HassIO docker utilitys."""
import re

from ..const import ARCH_AARCH64, ARCH_ARMHF, ARCH_I386, ARCH_AMD64


RESIN_BASE_IMAGE = {
    ARCH_ARMHF: "resin/armhf-alpine:3.5",
    ARCH_AARCH64: "resin/aarch64-alpine:3.5",
    ARCH_I386: "resin/i386-alpine:3.5",
    ARCH_AMD64: "resin/amd64-alpine:3.5",
}

TMPL_IMAGE = re.compile(r"%%BASE_IMAGE%%")


def dockerfile_template(dockerfile, arch, version, meta_type):
    """Prepare a Hass.IO dockerfile."""
    buff = []
    resin_image = RESIN_BASE_IMAGE[arch]

    # read docker
    with dockerfile.open('r') as dock_input:
        for line in dock_input:
            line = TMPL_IMAGE.sub(resin_image, line)
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
