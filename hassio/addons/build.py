"""HassIO addons build environment."""
from pathlib import Path

from .validate import SCHEMA_BUILD_CONFIG, BASE_IMAGES
from ..const import ATTR_SQUASH, ATTR_BUILD_FROM, ATTR_ARGS, META_ADDON
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
        return self._data[ATTR_BUILD_FROM].get(
            self.config.arch, BASE_IMAGES[self.config.arch])

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
        args = {
            'path': str(self.addon.path_location),
            'tag': "{}:{}".format(self.addon.image, version),
            'pull': True,
            'forcerm': True,
            'squash': self.squash,
            'labels': {
                'io.hass.version': version,
                'io.hass.arch': self.config.arch,
                'io.hass.type': META_ADDON,
                'io.hass.name': self.addon.name,
                'io.hass.description': self.addon.description,
            },
            'buildargs': {
                'BUILD_FROM': self.base_image,
                'BUILD_VERSION': version,
                'BUILD_ARCH': self.config.arch,
                **self.additional_args,
            }
        }

        if self.addon.url:
            args['labels']['io.hass.url'] = self.addon.url

        return args
