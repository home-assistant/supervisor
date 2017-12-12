ARG BUILD_FROM
FROM $BUILD_FROM

# Add env
ENV LANG C.UTF-8

# Setup base
RUN apk add --no-cache \
        python3 \
        git \
        socat \
        libstdc++ \
    && apk add --no-cache --virtual .build-dependencies \
        make \
        python3-dev \
        g++ \
        file \
        pkgconfig \
    && pip3 install -vvv --no-cache-dir \
        uvloop \
        cchardet \
    && apk del .build-dependencies

# Install HassIO
COPY . /usr/src/hassio
RUN pip3 install --no-cache-dir /usr/src/hassio \
    && rm -rf /usr/src/hassio

CMD [ "python3", "-m", "hassio" ]
