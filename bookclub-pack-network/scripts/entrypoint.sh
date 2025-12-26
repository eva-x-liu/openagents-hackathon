#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] PORT=${PORT:-<unset>}"
# network.yaml will be rendered by supervisord's network program (also OK to render here)

exec /usr/bin/supervisord -c /app/supervisord.conf