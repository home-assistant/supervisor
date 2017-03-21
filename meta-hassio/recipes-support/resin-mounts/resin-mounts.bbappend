
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
    file://home-root-.ssh.mount \
    "

SYSTEMD_SERVICE_${PN} += " \
    home-root-.ssh.mount \
    "

do_install_append () {
    if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}${systemd_unitdir}/system
        install -c -m 0644 ${WORKDIR}/home-root-.ssh.mount ${D}${systemd_unitdir}/system
    fi
}
