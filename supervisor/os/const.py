"""Constants for OS."""

from awesomeversion import AwesomeVersion

FILESYSTEM_LABEL_DATA_DISK = "hassos-data"
FILESYSTEM_LABEL_DISABLED_DATA_DISK = "hassos-data-dis"
FILESYSTEM_LABEL_OLD_DATA_DISK = "hassos-data-old"
PARTITION_NAME_EXTERNAL_DATA_DISK = "hassos-data-external"
PARTITION_NAME_OLD_EXTERNAL_DATA_DISK = "hassos-data-external-old"

# Raspberry Pi firmware management requires the io.hass.os.Boards.RaspberryPi
# .Firmware D-Bus interface first shipped in this OS Agent release.
RPI_FIRMWARE_MIN_OS_AGENT_VERSION: AwesomeVersion = AwesomeVersion("1.9.0")
