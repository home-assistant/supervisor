# resin-connectable-service bbclass
#
# Author: Andrei Gherzan <andrei@resin.io>

python __anonymous() {
    # Enable/disable systemd services listed in RESIN_CONNECTABLE_SERVICES based on
    # RESIN_CONNECTABLE_ENABLE_SERVICES

    pn = d.getVar('PN', True)
    services = d.getVar('RESIN_CONNECTABLE_SERVICES', True).split()

    if pn in services:
        d.setVar('SYSTEMD_AUTO_ENABLE', 'enable')

}
systemd_populate_packages[vardeps] += "RESIN_CONNECTABLE_ENABLE_SERVICES"
