ARG BUILD_FROM
FROM $BUILD_FROM

ARG BUILD_ARCH

# Install base
RUN apk add --no-cache \
    openssl \
    libffi \
    musl \
    git \
    socat \
    glib \
    libstdc++ \
    eudev-libs

# Install requirements
COPY requirements.txt /usr/src/
RUN export MAKEFLAGS="-j$(nproc)" \
    && pip3 install --no-cache-dir --find-links https://wheels.hass.io/alpine-3.9/${BUILD_ARCH}/ \
    -r /usr/src/requirements.txt \
    && rm -f /usr/src/requirements.txt

# Install HassIO
COPY . /usr/src/hassio
RUN pip3 install --no-cache-dir /usr/src/hassio \
    && rm -rf /usr/src/hassio

CMD [ "python3", "-m", "hassio" ]
