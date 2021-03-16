ARG BUILD_FROM

FROM $BUILD_FROM AS builder

ARG VCN_VERSION
ARG BUILD_ARCH
WORKDIR /usr/src

RUN \
    set -x \
    && apk add --no-cache \
        build-base \
        go \
        git \
    \
    && git clone -b v${VCN_VERSION} --depth 1 \
        https://github.com/codenotary/vcn \
    && cd vcn \
    \
    # Fix: https://github.com/codenotary/vcn/issues/131
    && go get github.com/codenotary/immudb@4cf9e2ae06ac2e6ec98a60364c3de3eab5524757 \
    \
    && if [ "${BUILD_ARCH}" = "armhf" ]; then \
        GOARM=6 GOARCH=arm go build -o vcn -ldflags="-s -w" ./cmd/vcn; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then \
        GOARM=7 GOARCH=arm go build -o vcn -ldflags="-s -w" ./cmd/vcn; \
    elif [ "${BUILD_ARCH}" = "aarch64" ]; then \
        GOARCH=arm64 go build -o vcn -ldflags="-s -w" ./cmd/vcn; \
    elif [ "${BUILD_ARCH}" = "i386" ]; then \
        GOARCH=386 go build -o vcn -ldflags="-s -w" ./cmd/vcn; \
    elif [ "${BUILD_ARCH}" = "amd64" ]; then \
        GOARCH=amd64 go build -o vcn -ldflags="-s -w" ./cmd/vcn; \
    else \
        exit 1; \
    fi


FROM $BUILD_FROM

ENV \
    S6_SERVICES_GRACETIME=10000 \
    SUPERVISOR_API=http://localhost

# Install base
COPY --from=builder /usr/src/vcn /usr/bin/vcn
RUN \
    apk add --no-cache \
        eudev \
        eudev-libs \
        git \
        glib \
        libffi \
        libpulse \
        musl \
        openssl

ARG BUILD_ARCH
WORKDIR /usr/src

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
