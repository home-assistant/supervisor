#!/bin/bash
set -e

# Update frontend
git submodule update --init --recursive --remote

[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cd home-assistant-polymer
nvm install
script/bootstrap

# build frontend
cd hassio
./script/build_hassio

# Copy frontend
rm -rf ../../supervisor/api/panel/*
cp -rf build/* ../../supervisor/api/panel/
