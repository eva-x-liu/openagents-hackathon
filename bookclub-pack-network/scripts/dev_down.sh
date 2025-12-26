#!/usr/bin/env bash
set -euo pipefail

pids=(
  .conversion.pid
  .ops.pid
  .content.pid
  .book_brief.pid
  .intake.pid
  .publisher.pid
  .studio.pid
  .network.pid
)

for f in "${pids[@]}"; do
  if [[ -f "$f" ]]; then
    pid="$(cat "$f" || true)"
    if [[ -n "${pid}" ]]; then
      echo "[dev_down] killing $f -> $pid"
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$f"
  fi
done

echo "[dev_down] done"
