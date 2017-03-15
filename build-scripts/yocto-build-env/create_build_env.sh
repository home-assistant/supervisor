#!/bin/bash

set -ev

DOCKER_REPO=pvizeli
DOCKER_IMAGE=yocto-build-env

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

# Sanity checks
if [ "$#" -ne 1 ]; then
    echo "Usage: create_build_env.sh [<REVISION> | NONE]"
    exit 1
fi

REVISION=$1

# Build
docker build --pull --tag ${DOCKER_REPO}/${DOCKER_IMAGE}:${REVISION} -f ${SCRIPTPATH}/Dockerfile ${SCRIPTPATH}

# Tag
docker tag ${DOCKER_REPO}/${DOCKER_IMAGE}:${REVISION} ${DOCKER_REPO}/${DOCKER_IMAGE}:latest

if [ ${REVISION} != "NONE" ]; then
    # push
    docker push ${DOCKER_REPO}/${DOCKER_IMAGE}:${REVISION}
    docker push ${DOCKER_REPO}/${DOCKER_IMAGE}:latest
fi
