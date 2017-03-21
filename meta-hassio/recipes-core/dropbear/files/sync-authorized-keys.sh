#!/bin/bash

BOOT_SSH_KEY = /mnt/boot/authorized_keys
HOME_SSH_KEY = /home/root/.ssh/authorized_keys

if [ -f BOOT_SSH_KEY ]; then
    mv BOOT_SSH_KEY HOME_SSH_KEY
    chmod 0650 HOME_SSH_KEY
fi
