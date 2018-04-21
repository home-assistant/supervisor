"""HassIO addons build environment."""
from pathlib import Path

from .validate import SCHEMA_BUILD_CONFIG, BASE_IMAGE
from ..const import ATTR_SQUASH, ATTR_BUILD_FROM, ATTR_ARGS, META_ADDON
from ..coresys import CoreSysAttributes
from ..utils.json import JsonConfig


class AddonBuild(JsonConfig, CoreSysAttributes):
    """Handle build options for addons."""

    def __init__(self, coresys, slug):
        """Initialize addon builder."""
        self.coresys = coresys
        self._id = slug

        super().__init__(
            Path(self.addon.path_location, 'build.json'), SCHEMA_BUILD_CONFIG)

    def save_data(self):
        """Ignore save function."""
        pass

    @property
    def addon(self):
        """Return addon of build data."""
        return self.sys_addons.get(self._id)

    @property
    def base_image(self):
        """Base images for this addon."""
        return self._data[ATTR_BUILD_FROM].get(
            self.sys_arch, BASE_IMAGE[self.sys_arch])

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
            'tag': f"{self.addon.image}:{version}",
            'pull': True,
            'forcerm': True,
            'squash': self.squash,
            'labels': {
                'io.hass.version': version,
                'io.hass.arch': self.sys_arch,
                'io.hass.type': META_ADDON,
                'io.hass.name': self._fix_label('name'),
                'io.hass.description': self._fix_label('description'),
            },
            'buildargs': {
                'BUILD_FROM': self.base_image,
                'BUILD_VERSION': version,
                'BUILD_ARCH': self.sys_arch,
                **self.additional_args,
            }
        }

        if self.addon.url:
            args['labels']['io.hass.url'] = self.addon.url

        return args

    def _fix_label(self, label_name):
        """Remove characters they are not supported."""
        label = getattr(self.addon, label_name, "")
        return label.replace("'", "")
