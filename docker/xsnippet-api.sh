#!/bin/bash

set -eu

cd /opt/xsnippet

echo "Upgrading DB schema..."
python3 -m alembic.config upgrade head

echo "Starting xsnippet-api..."
exec /opt/xsnippet/xsnippet-api
