
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SUPERVISOR_REPOSITORY_armv5 = "pvizeli/armhf-hassio-supervisor"
SUPERVISOR_REPOSITORY_armv6 = "pvizeli/armhf-hassio-supervisor"
SUPERVISOR_REPOSITORY_armv7a = "pvizeli/armhf-hassio-supervisor"
SUPERVISOR_REPOSITORY_armv7ve = "pvizeli/armhf-hassio-supervisor"
SUPERVISOR_REPOSITORY_aarch64 = "pvizeli/aarch64-hassio-supervisor"
SUPERVISOR_REPOSITORY_x86 = "pvizeli/i386-hassio-supervisor"
SUPERVISOR_REPOSITORY_x86-64 = "pvizeli/amd64-hassio-supervisor"

SUPERVISOR_TAG = "${HASSIO_SUPERVISOR_TAG}"
TARGET_REPOSITORY = "${SUPERVISOR_REPOSITORY}"
TARGET_TAG = "${SUPERVISOR_TAG}"

SYSTEMD_AUTO_ENABLE = "enable"

do_install_append () {
    install -d ${D}${sysconfdir}/resin-supervisor
    sed -i -e 's:@HOMEASSISTANT_REPOSITORY@:${HOMEASSISTANT_REPOSITORY}:g' ${D}${sysconfdir}/resin-supervisor/supervisor.conf
    sed -i -e 's:@MACHINE@:${MACHINE}:g' ${D}${sysconfdir}/resin-supervisor/supervisor.conf
    sed -i -e 's:@RESINOS_VERSION@:${HOSTOS_VERSION}:g' ${D}${sysconfdir}/resin-supervisor/supervisor.conf
}
