"""Const for API."""

from enum import StrEnum

CONTENT_TYPE_BINARY = "application/octet-stream"
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_PNG = "image/png"
CONTENT_TYPE_TAR = "application/tar"
CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_URL = "application/x-www-form-urlencoded"

COOKIE_INGRESS = "ingress_session"

ATTR_AGENT_VERSION = "agent_version"
ATTR_APPARMOR_VERSION = "apparmor_version"
ATTR_ATTRIBUTES = "attributes"
ATTR_AVAILABLE_UPDATES = "available_updates"
ATTR_BACKGROUND = "background"
ATTR_BOOT_NAME = "boot_name"
ATTR_BOOT_SLOTS = "boot_slots"
ATTR_BOOT_TIMESTAMP = "boot_timestamp"
ATTR_BOOTS = "boots"
ATTR_BROADCAST_LLMNR = "broadcast_llmnr"
ATTR_BROADCAST_MDNS = "broadcast_mdns"
ATTR_BY_ID = "by_id"
ATTR_CHILDREN = "children"
ATTR_CONNECTION_BUS = "connection_bus"
ATTR_DATA_DISK = "data_disk"
ATTR_DEVICE = "device"
ATTR_DEV_PATH = "dev_path"
ATTR_DISKS = "disks"
ATTR_DRIVES = "drives"
ATTR_DT_SYNCHRONIZED = "dt_synchronized"
ATTR_DT_UTC = "dt_utc"
ATTR_EJECTABLE = "ejectable"
ATTR_FALLBACK = "fallback"
ATTR_FILESYSTEMS = "filesystems"
ATTR_GROUP_IDS = "group_ids"
ATTR_IDENTIFIERS = "identifiers"
ATTR_IS_ACTIVE = "is_active"
ATTR_IS_OWNER = "is_owner"
ATTR_JOB_ID = "job_id"
ATTR_JOBS = "jobs"
ATTR_LLMNR = "llmnr"
ATTR_LLMNR_HOSTNAME = "llmnr_hostname"
ATTR_LOCAL_ONLY = "local_only"
ATTR_MDNS = "mdns"
ATTR_MODEL = "model"
ATTR_MOUNTS = "mounts"
ATTR_MOUNT_POINTS = "mount_points"
ATTR_PANEL_PATH = "panel_path"
ATTR_REMOVABLE = "removable"
ATTR_REMOVE_CONFIG = "remove_config"
ATTR_REVISION = "revision"
ATTR_SEAT = "seat"
ATTR_SIGNED = "signed"
ATTR_STARTUP_TIME = "startup_time"
ATTR_STATUS = "status"
ATTR_SUBSYSTEM = "subsystem"
ATTR_SYSFS = "sysfs"
ATTR_SYSTEM_HEALTH_LED = "system_health_led"
ATTR_TIME_DETECTED = "time_detected"
ATTR_UPDATE_TYPE = "update_type"
ATTR_USAGE = "usage"
ATTR_USE_NTP = "use_ntp"
ATTR_USERS = "users"
ATTR_VENDOR = "vendor"


class BootSlot(StrEnum):
    """Boot names used by HAOS."""

    A = "A"
    B = "B"
