"""HassIO addons build environment."""
from pathlib import Path

from .validate SCHEMA_BUILD_CONFIG
from ..const import ATTR_SQUASH, ATTR_BASE_IMAGE, ATTR_ARGS, META_ADDON
from ..tools import JsonConfig


class AddonBuild(JsonConfig):
    """Handle build options for addons."""

    def __init__(self, config, addon):
        """Initialize addon builder."""
        self.config = config
        self.addon = addon

        super().__init__(
            Path(addon.path_location, 'build.json'), SCHEMA_BUILD_CONFIG)

    def save(self):
        """Ignore save function."""
        pass

    @property
    def base_image(self):
        """Base images for this addon."""
        return self._data[ATTR_BASE_IMAGE][self.config.arch]

    @property
    def squash(self):
        """Return True or False if squash is active."""
        return self._data[ATTR_SQUASH]

    @property
    def additional_args(self):
        """Return additional docker build arguments."""
        return self._data[ATTR_ARGS]

    def get_docker_args(self, version):
        """Create a dict with docker build arguments."""
        build_tag = "{}:{}".format(self.addon.image, version)

        return {
            'path': str(self.addon.path_location),
            'tag': build_tag,
            'pull': True,
            'forcerm': True,
            'squash': self.squash,
            'label': {
                'io.hass.version': version,
                'io.hass.arch': self.config.arch,
                'io.hass.type': META_ADDON,
            },
            'buildargs': {
                'BUILD_FROM': self.base_image,
                'BUILD_VERSION': version,
                'BUILD_ARCH': self.config.arch,
                **self.additional_args,
            }
        }
