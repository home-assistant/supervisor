"""Host Audio support."""
import logging
import json
from pathlib import Path
from string import Template

import attr

from ..const import ATTR_INPUT, ATTR_OUTPUT, ATTR_DEVICES, ATTR_NAME, CHAN_ID, CHAN_TYPE
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

# pylint: disable=invalid-name
DefaultConfig = attr.make_class("DefaultConfig", ["input", "output"])


class AlsaAudio(CoreSysAttributes):
    """Handle Audio ALSA host data."""

    def __init__(self, coresys):
        """Initialize ALSA audio system."""
        self.coresys = coresys
        self._data = {ATTR_INPUT: {}, ATTR_OUTPUT: {}}
        self._cache = 0
        self._default = None

    @property
    def input_devices(self):
        """Return list of ALSA input devices."""
        self._update_device()
        return self._data[ATTR_INPUT]

    @property
    def output_devices(self):
        """Return list of ALSA output devices."""
        self._update_device()
        return self._data[ATTR_OUTPUT]

    def _update_device(self):
        """Update Internal device DB."""
        current_id = hash(frozenset(self.sys_hardware.audio_devices))

        # Need rebuild?
        if current_id == self._cache:
            return

        # Clean old stuff
        self._data[ATTR_INPUT].clear()
        self._data[ATTR_OUTPUT].clear()

        # Init database
        _LOGGER.info("Update ALSA device list")
        database = self._audio_database()

        # Process devices
        for dev_id, dev_data in self.sys_hardware.audio_devices.items():
            for chan_info in dev_data[ATTR_DEVICES]:
                chan_id = chan_info[CHAN_ID]
                chan_type = chan_info[CHAN_TYPE]
                alsa_id = f"{dev_id},{chan_id}"
                dev_name = dev_data[ATTR_NAME]

                # Lookup type
                if chan_type.endswith("playback"):
                    key = ATTR_OUTPUT
                elif chan_type.endswith("capture"):
                    key = ATTR_INPUT
                else:
                    _LOGGER.warning("Unknown channel type: %s", chan_type)
                    continue

                # Use name from DB or a generic name
                self._data[key][alsa_id] = (
                    database.get(self.sys_machine, {})
                    .get(dev_name, {})
                    .get(alsa_id, f"{dev_name}: {chan_id}")
                )

        self._cache = current_id

    @staticmethod
    def _audio_database():
        """Read local json audio data into dict."""
        json_file = Path(__file__).parents[1].joinpath("data/audiodb.json")

        try:
            # pylint: disable=no-member
            with json_file.open("r") as database:
                return json.loads(database.read())
        except (ValueError, OSError) as err:
            _LOGGER.warning("Can't read audio DB: %s", err)

        return {}

    @property
    def default(self):
        """Generate ALSA default setting."""
        # Init defaults
        if self._default is None:
            database = self._audio_database()
            alsa_input = database.get(self.sys_machine, {}).get(ATTR_INPUT)
            alsa_output = database.get(self.sys_machine, {}).get(ATTR_OUTPUT)

            self._default = DefaultConfig(alsa_input, alsa_output)

        # Search exists/new output
        if self._default.output is None and self.output_devices:
            self._default.output = next(iter(self.output_devices))
            _LOGGER.info("Detect output device %s", self._default.output)

        # Search exists/new input
        if self._default.input is None and self.input_devices:
            self._default.input = next(iter(self.input_devices))
            _LOGGER.info("Detect input device %s", self._default.input)

        return self._default

    def asound(self, alsa_input=None, alsa_output=None):
        """Generate an asound data."""
        alsa_input = alsa_input or self.default.input
        alsa_output = alsa_output or self.default.output

        # Read Template
        asound_file = Path(__file__).parents[1].joinpath("data/asound.tmpl")
        try:
            # pylint: disable=no-member
            with asound_file.open("r") as asound:
                asound_data = asound.read()
        except OSError as err:
            _LOGGER.error("Can't read asound.tmpl: %s", err)
            return ""

        # Process Template
        asound_template = Template(asound_data)
        return asound_template.safe_substitute(input=alsa_input, output=alsa_output)
