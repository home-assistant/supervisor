#!/bin/bash

set -ev

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

if [ -z "${REVISION}" ]; then
    echo "[ERROR] No revision specified."
    exit 1
fi

# Build
docker build --pull --tag pvizeli/yocto-build-env:${REVISION} -f ${SCRIPTPATH}/Dockerfile ${SCRIPTPATH}

# Tag
docker tag -f pvizeli/yocto-build-env:${REVISION} resin/yocto-build-env:latest

# Push
docker push pvizeli/yocto-build-env:${REVISION}
docker push pvizeli/yocto-build-env:latest
