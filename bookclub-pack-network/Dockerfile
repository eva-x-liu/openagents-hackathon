FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# Install OpenAgents CLI (adjust if your project pins a version)
RUN pip install --no-cache-dir openagents

# Copy project
COPY . /app

# Make scripts executable
RUN chmod +x /app/scripts/*.sh || true

# Expose nothing explicitly (Zeabur routes via $PORT), but it's fine to document:
# HTTP: $PORT (Studio at /studio), gRPC: 8600 internal
ENV OA_GRPC_PORT=8600

CMD ["/app/scripts/entrypoint.sh"]