
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://resinhup"

do_install_append() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/resinhup ${D}${bindir}
}
