#!/bin/bash

set -e

BUILD_CONTAINER_NAME=hassio-build-$$
DOCKER_REPO=pvizeli

cleanup() {
    echo "[INFO] Cleanup."

    # Stop docker container
    echo "[INFO] Cleaning up yocto-build container."
    docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
    docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true

    if [ "$1" == "fail" ]; then
        exit 1
    fi
}
trap 'cleanup fail' SIGINT SIGTERM

# Sanity checks
if [ "$#" -ne 2 ]; then
    echo "Usage: create_hassio_supervisor.sh <MACHINE> <TAG>|NONE"
    echo "Optional environment: BUILD_DIR"
    exit 1
fi
if [ $1 != 'armhf' ] && [ $1 != 'aarch64' ] && [ $1 != 'i386' ] && [ $1 != 'amd64' ]; then
    echo "Error: $1 is not a supported platform for hassio-supervisor!"
    exit 1
fi

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

ARCH=$1
BASE_IMAGE="resin\/${ARCH}-alpine:3.5"
DOCKER_TAG=$2
DOCKER_IMAGE=${ARCH}-hassio-supervisor
BUILD_DIR=${BUILD_DIR:=$SCRIPTPATH}
WORKSPACE=${BUILD_DIR:=$SCRIPTPATH}/hassio-supervisor

# setup docker
echo "[INFO] Setup docker for supervisor"
mkdir -p $BUILD_DIR
mkdir -p $WORKSPACE

sed "s/%%BASE_IMAGE%%/${BASE_IMAGE}/g" ../../supervisor/Dockerfile  > $WORKSPACE/Dockerfile

# Run build
echo "[INFO] start docker build"
docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true
docker run --rm \
    -v $WORKSPACE:/docker \
    -v ~/.docker:/root/.docker \
    -e DOCKER_REPO=$DOCKER_REPO \
    -e DOCKER_IMAGE=$DOCKER_IMAGE \
    -e DOCKER_TAG=$DOCKER_TAG \
    --name $BUILD_CONTAINER_NAME \
    --privileged \
    pvizeli/docker-build-env \
    /run-docker.sh

exit
# Write deploy artifacts
BUILD_DEPLOY_DIR=$WORKSPACE/deploy
DEVICE_TYPE_JSON=$WORKSPACE/$MACHINE.json
VERSION_HOSTOS=$(cat $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION_HOSTOS)

DEPLOY_ARTIFACT=$(jq --raw-output '.yocto.deployArtifact' $DEVICE_TYPE_JSON)
COMPRESSED=$(jq --raw-output '.yocto.compressed' $DEVICE_TYPE_JSON)
ARCHIVE=$(jq --raw-output '.yocto.archive' $DEVICE_TYPE_JSON)
mkdir -p $BUILD_DEPLOY_DIR
rm -rf $BUILD_DEPLOY_DIR/* # do we have anything there?
mv -v $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/$DEPLOY_ARTIFACT) $BUILD_DEPLOY_DIR/$DEPLOY_ARTIFACT
if [ "${COMPRESSED}" == 'true' ]; then
	if [ "${ARCHIVE}" == 'true' ]; then
		(cd $BUILD_DEPLOY_DIR && tar --remove-files  --use-compress-program pigz --directory=$DEPLOY_ARTIFACT -cvf ${DEPLOY_ARTIFACT}.tar.gz .)
	else
		 mv $BUILD_DEPLOY_DIR/$DEPLOY_ARTIFACT $BUILD_DEPLOY_DIR/resin.img
		(cd $BUILD_DEPLOY_DIR && tar --remove-files --use-compress-program pigz -cvf resin.img.tar.gz resin.img)
	fi
fi
if [ -f $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/resin-image-$MACHINE.resinhup-tar) ]; then
    mv -v $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/resin-image-$MACHINE.resinhup-tar) $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar
else
    echo "WARNING: No resinhup package found."
fi

mv -v $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION $BUILD_DEPLOY_DIR
mv -v $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION_HOSTOS $BUILD_DEPLOY_DIR
cp $DEVICE_TYPE_JSON $BUILD_DEPLOY_DIR/device-type.json
# move to deploy directory the kernel modules headers so we have it as a build artifact in jenkins
mv -v $WORKSPACE/build/tmp/deploy/images/$MACHINE/kernel_modules_headers.tar.gz $BUILD_DEPLOY_DIR

# If this is a clean production build, push a resinhup package to dockerhub
# and registry.resinstaging.io.
if [[ "$sourceBranch" == production* ]] && [ "$metaResinBranch" == "__ignore__" ] && [ "$supervisorTag" == "__ignore__" ]; then
    echo "INFO: Pushing resinhup package to dockerhub and registry.resinstaging.io."
    SLUG=$(jq --raw-output '.slug' $DEVICE_TYPE_JSON)
    DOCKER_REPO="resin/resinos"
    DOCKER_TAG="$VERSION_HOSTOS-$SLUG"
    RESINREG_REPO="registry.resinstaging.io/resin/resinos"
    RESINREG_TAG="$VERSION_HOSTOS-$SLUG"
    if [ -f $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar ]; then
        docker import $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar $DOCKER_REPO:$DOCKER_TAG
        docker push $DOCKER_REPO:$DOCKER_TAG
        docker rmi $DOCKER_REPO:$DOCKER_TAG # cleanup

        docker import $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar $RESINREG_REPO:$RESINREG_TAG
        docker push $RESINREG_REPO:$RESINREG_TAG
        docker rmi $RESINREG_REPO:$RESINREG_TAG # cleanup
    else
        echo "ERROR: The build didn't produce a resinhup package."
        exit 1
    fi
else
    echo "WARNING: There is no need to upload resinhup package for a non production clean build."
fi

# Cleanup the build directory
# Keep this after writing all artifacts
rm -rf $WORKSPACE/build
