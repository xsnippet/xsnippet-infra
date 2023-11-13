FROM debian:buster-slim

ARG RELEASE_ARCH=x86_64
ARG RELEASE_OS=linux
ARG RELEASE_TAG=latest

RUN apt-get update && \
    apt-get install -y curl libpq5 python3-alembic python3-psycopg2 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/xsnippet && \
    cd /opt/xsnippet && \
    curl -L https://github.com/xsnippet/xsnippet-api/archive/refs/tags/${RELEASE_TAG?}.tar.gz | tar xzf - --strip-components=1 && \
    curl -L https://github.com/xsnippet/xsnippet-api/releases/download/${RELEASE_TAG?}/xsnippet-api-${RELEASE_ARCH?}-${RELEASE_OS?}.gz | tar xzf -

COPY xsnippet-api.sh /opt/xsnippet/xsnippet-api.sh

ENV ROCKET_ADDRESS=127.0.0.1 \
    ROCKET_PORT=8000 \
    RUST_BACKTRACE=1
EXPOSE $ROCKET_PORT
ENTRYPOINT ["/opt/xsnippet/xsnippet-api.sh"]
