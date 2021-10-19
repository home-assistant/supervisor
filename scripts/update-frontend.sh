#!/bin/bash
source "/etc/supervisor_scripts/common"

set -e

# Update frontend
git submodule update --init --recursive --remote

[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cd home-assistant-polymer
nvm install
script/bootstrap

# Download translations
start_docker
./script/translations_download

# build frontend
cd hassio
./script/build_hassio

# Copy frontend
rm -rf ../../supervisor/api/panel/*
cp -rf build/* ../../supervisor/api/panel/

# Reset frontend git
cd ..
git reset --hard HEAD

stop_docker