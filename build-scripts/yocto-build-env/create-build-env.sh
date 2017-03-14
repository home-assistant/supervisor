#!/bin/bash

set -ev

DOCKER_REPO=pvizeli
DOCKER_IMAGE=yocto-build-env

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

if [ -z "${REVISION}" ]; then
    echo "[ERROR] No revision specified."
    exit 1
fi

# Build
docker build --pull --tag ${DOCKER_REPO}/${DOCKER_IMAGE}:${REVISION} -f ${SCRIPTPATH}/Dockerfile ${SCRIPTPATH}

# Tag
docker tag ${DOCKER_REPO}/${DOCKER_IMAGE}:${REVISION} ${DOCKER_REPO}/${DOCKER_IMAGE}:latest

# Push
docker push ${DOCKER_REPO}/${DOCKER_IMAGE}:${REVISION}
docker push ${DOCKER_REPO}/${DOCKER_IMAGE}:latest
