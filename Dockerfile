ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV \
    S6_SERVICES_GRACETIME=10000 \
    SUPERVISOR_API=http://localhost

ARG \
    BUILD_ARCH \
    CAS_VERSION

# Install base
WORKDIR /usr/src
RUN \
    set -x \
    && apk add --no-cache \
        eudev \
        eudev-libs \
        git \
        libffi \
        libpulse \
        musl \
        openssl
    && apk add --no-cache --virtual .build-dependencies \
        build-base \
        go \
    \
    && git clone -b v${CAS_VERSION} --depth 1 \
        https://github.com/codenotary/cas \
    && cd cas \
    && make cas \
    && mv cas /usr/bin/cas \
    \
    && apk del .build-dependencies \
    && rm -rf /root/go /root/.cache \
    && rm -rf /usr/src/cas

# Install requirements
COPY requirements.txt .
RUN \
    export MAKEFLAGS="-j$(nproc)" \
    && pip3 install --no-cache-dir --no-index --only-binary=:all: --find-links \
        "https://wheels.home-assistant.io/alpine-$(cut -d '.' -f 1-2 < /etc/alpine-release)/${BUILD_ARCH}/" \
        -r ./requirements.txt \
    && rm -f requirements.txt

# Install Home Assistant Supervisor
COPY . supervisor
RUN \
    pip3 install --no-cache-dir -e ./supervisor \
    && python3 -m compileall ./supervisor/supervisor


WORKDIR /
COPY rootfs /
