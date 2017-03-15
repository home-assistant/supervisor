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
    echo "Usage: create_build_env.sh [<TAG> | NONE]"
    exit 1
fi

DOCKER_TAG=$1

# Build
docker build --pull --tag ${DOCKER_REPO}/${DOCKER_IMAGE}:${DOCKER_TAG} -f ${SCRIPTPATH}/Dockerfile ${SCRIPTPATH}

# Tag
docker tag ${DOCKER_REPO}/${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REPO}/${DOCKER_IMAGE}:latest

if [ ${DOCKER_TAG} != "NONE" ]; then
    # push
    docker push ${DOCKER_REPO}/${DOCKER_IMAGE}:${DOCKER_TAG}
    docker push ${DOCKER_REPO}/${DOCKER_IMAGE}:latest
fi
