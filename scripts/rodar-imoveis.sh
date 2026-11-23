#!/usr/bin/env bash
# Chamado pelo cron de hora em hora. Log em logs/imoveis.log.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
# Evita duas execuções ao mesmo tempo se uma demorar.
exec 9>logs/.imoveis.lock
flock -n 9 || exit 0
{
  echo "=== $(date '+%F %T')"
  "$HOME/.local/bin/uv" run radar imoveis
} >>logs/imoveis.log 2>&1
