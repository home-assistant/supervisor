
do_install_append() {
    install -d ${D}${sysconfdir}/default
    sed -i '/DROPBEAR_EXTRA_ARGS="-g"/d' ${D}/etc/default/dropbear
}
