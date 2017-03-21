
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
    file://hassio.conf \
    file://resinhup.timer \
    file://resinhup.service \
    "

SYSTEMD_SERVICE_${PN} += " \
    resinhup.service \
    resinhup.timer \
    "

SYSTEMD_AUTO_ENABLE = "enable"

FILES_${PN} += " \
     ${systemd_unitdir} \
     ${bindir} \
     ${sysconfdir} \
     "

do_install_append() {
    install -m 0755 ${WORKDIR}/hassio.conf ${D}${sysconfdir}
    sed -i -e 's:@HASSIO_VERSION@:${HASSIO_VERSION}:g' ${D}${sysconfdir}/hassio.conf

    if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}${systemd_unitdir}/system
        install -c -m 0644 ${WORKDIR}/resinhup.service ${D}${systemd_unitdir}/system
        install -c -m 0644 ${WORKDIR}/resinhup.time ${D}${systemd_unitdir}/system

        sed -i -e 's,@BASE_BINDIR@,${base_bindir},g' \
            -e 's,@SBINDIR@,${sbindir},g' \
            -e 's,@BINDIR@,${bindir},g' \
            ${D}${systemd_unitdir}/system/*.service
    fi
}
