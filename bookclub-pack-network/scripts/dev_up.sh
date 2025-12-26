#!/usr/bin/env bash
set -euo pipefail

# ========= Ports =========
# Network HTTP port (serves base http endpoints; NOT the Studio port)
export PORT="${PORT:-8700}"

# Network gRPC port (agents connect here)
export OA_GRPC_PORT="${OA_GRPC_PORT:-8600}"

# Studio UI port (separate process in newer OpenAgents)
export STUDIO_PORT="${STUDIO_PORT:-8050}"

# ========= Render network.yaml =========
python3 scripts/render_network.py

echo "[dev_up] Starting OpenAgents network (HTTP:${PORT}, gRPC:${OA_GRPC_PORT})..."
nohup openagents network start network/network.yaml > .network.log 2>&1 &
echo $! > .network.pid
sleep 1

echo "[dev_up] Starting OpenAgents Studio (port:${STUDIO_PORT})..."
nohup openagents studio -s --studio-port "${STUDIO_PORT}" > .studio.log 2>&1 &
echo $! > .studio.pid
sleep 1

echo "[dev_up] Starting agents (connect gRPC:${OA_GRPC_PORT})..."

# Publisher first (receives worker task.complete)
nohup openagents agent start agents/publisher.yaml > .publisher.log 2>&1 &
echo $! > .publisher.pid
sleep 0.5

nohup openagents agent start agents/intake.yaml > .intake.log 2>&1 & echo $! > .intake.pid
nohup openagents agent start agents/book_brief.yaml > .book_brief.log 2>&1 & echo $! > .book_brief.pid
nohup openagents agent start agents/content_designer.yaml > .content.log 2>&1 & echo $! > .content.pid
nohup openagents agent start agents/ops_producer.yaml > .ops.log 2>&1 & echo $! > .ops.pid
nohup openagents agent start agents/conversion_strategist.yaml > .conversion.log 2>&1 & echo $! > .conversion.pid

echo
echo "[dev_up] Done."
echo "Network HTTP: http://localhost:${PORT}"
echo "Studio:       http://localhost:${STUDIO_PORT}"
echo "Logs: .network.log, .studio.log, .publisher.log, ..."
