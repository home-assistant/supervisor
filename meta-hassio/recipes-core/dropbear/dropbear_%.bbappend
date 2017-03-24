FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += " \
    file://sync-authorized-keys \
    file://sync-authorized-keys.service \
    "

SYSTEMD_SERVICE_${PN} += "sync-authorized-keys.service"

FILES_${PN} += " \
     ${systemd_unitdir} \
     ${bindir} \
     "/home/root/.ssh/" \
     "

RDEPENDS_${PN} += "bash"

do_install_append() {
    install -d ${D}/home/root/.ssh

    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/sync-authorized-keys ${D}${bindir}

    if [ "${RESIN_CONNECTABLE_ENABLE_SERVICES}" = "1" ]; then
        rm -fr ${D}${localstatedir}/lib/dropbear/
        rm -f ${D}/home/root/.ssh/authorized_keys
    fi

    if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}${systemd_unitdir}/system
        install -c -m 0644 ${WORKDIR}/sync-authorized-keys.service ${D}${systemd_unitdir}/system

        sed -i -e 's,@BASE_BINDIR@,${base_bindir},g' \
            -e 's,@SBINDIR@,${sbindir},g' \
            -e 's,@BINDIR@,${bindir},g' \
            ${D}${systemd_unitdir}/system/*.service
    fi
}
