
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
    file://resinhub.conf \
    "

FILES_${PN} += " \
    ${sysconfdir} \
    "

do_install_append () {
    install -m 0755 ${WORKDIR}/resinhub.conf ${D}${sysconfdir}/
    sed -i -e 's:@RESINHUB_MACHINE@:${MACHINE}:g' ${D}${sysconfdir}/resinhub.conf
}
