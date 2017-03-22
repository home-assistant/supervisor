FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += " \
    file://sync-authorized-keys.sh \
    file://sync-authorized-keys.service \
    "

SYSTEMD_SERVICE_${PN} += "sync-authorized-keys.service"

FILES_${PN} += " \
     ${systemd_unitdir} \
     ${bindir} \
     "/home/root/.ssh/" \
     "

do_install_append() {
    mkdir -p ${D}/home/root/.ssh

    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/sync-authorized-keys.sh ${D}${bindir}

    if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}${systemd_unitdir}/system
        install -c -m 0644 ${WORKDIR}/sync-authorized-keys.service ${D}${systemd_unitdir}/system

        sed -i -e 's,@BASE_BINDIR@,${base_bindir},g' \
            -e 's,@SBINDIR@,${sbindir},g' \
            -e 's,@BINDIR@,${bindir},g' \
            ${D}${systemd_unitdir}/system/*.service
    fi
}
