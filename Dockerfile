ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV \
    S6_SERVICES_GRACETIME=10000 \
    SUPERVISOR_API=http://localhost \
    CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 \
    UV_SYSTEM_PYTHON=true

ARG \
    COSIGN_VERSION \
    BUILD_ARCH \
    QEMU_CPU

# Install base
WORKDIR /usr/src
RUN \
    set -x \
    && apk add --no-cache \
        findutils \
        eudev \
        eudev-libs \
        git \
        libffi \
        libpulse \
        musl \
        openssl \
        yaml \
    \
    && curl -Lso /usr/bin/cosign "https://github.com/home-assistant/cosign/releases/download/${COSIGN_VERSION}/cosign_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/cosign \
    && pip3 install uv==0.6.17

# Install requirements
COPY requirements.txt .
RUN \
    if [ "${BUILD_ARCH}" = "i386" ]; then \
        setarch="linux32"; \
    else \
        setarch=""; \
    fi \
    && ${setarch} uv pip install --compile-bytecode --no-cache --no-build -r requirements.txt \
    && rm -f requirements.txt

# Install Home Assistant Supervisor
COPY . supervisor
RUN \
    uv pip install --no-cache -e ./supervisor \
    && python3 -m compileall ./supervisor/supervisor


WORKDIR /
COPY rootfs /
