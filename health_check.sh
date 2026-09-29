#!/usr/bin/env bash
# Verifies backend, PostgreSQL, worker, and network connectivity.
set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "== Backend health =="
curl -sf "$BACKEND_URL/health" && echo " -> OK" || echo " -> FAILED"

echo "== Network connectivity test =="
curl -sf "$BACKEND_URL/network-test" && echo " -> OK" || echo " -> FAILED"

echo "== PostgreSQL health (via docker) =="
docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-scheduler}" || echo " -> FAILED"

echo "== Worker availability =="
curl -sf "$BACKEND_URL/workers" | python3 -m json.tool || echo " -> FAILED"

echo "== Done =="
