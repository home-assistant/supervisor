DESCRIPTION = "hassio device controll"
SECTION = "console/utils"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${RESIN_COREBASE}/COPYING.Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = " \
    file://hassio-hc \
    file://hassio-hc.service \
    "

inherit allarch systemd

SYSTEMD_SERVICE_${PN} += "hassio-hc.service"
SYSTEMD_AUTO_ENABLE = "enable"

RDEPENDS_${PN} = " \
    bash \
    socat \
    "

FILES_${PN} += " \
     ${systemd_unitdir} \
     ${bindir} \
     "

do_install() {
    install -d ${D}${bindir}
    install -m 0775 ${WORKDIR}/hassio-hc ${D}${bindir}/hassio-hc

    if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}${systemd_unitdir}/system
        install -c -m 0644 ${WORKDIR}/hassio-hc.service ${D}${systemd_unitdir}/system

        sed -i -e 's,@BASE_BINDIR@,${base_bindir},g' \
            -e 's,@SBINDIR@,${sbindir},g' \
            -e 's,@BINDIR@,${bindir},g' \
            ${D}${systemd_unitdir}/system/*.service
    fi
}
