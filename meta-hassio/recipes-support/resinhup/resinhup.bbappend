
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
    file://resinhup.sh \
    file://resinhup.service \
    "

SYSTEMD_SERVICE_${PN} += "
    resinhup.service \
    resinhup.timer \
    "

SYSTEMD_AUTO_ENABLE = "enable"

FILES_${PN} += " \
     ${systemd_unitdir} \
     ${bindir} \
     "

do_install_append() {
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
