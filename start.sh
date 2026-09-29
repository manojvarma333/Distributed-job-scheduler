#!/usr/bin/env bash
# Starts the complete distributed job scheduler stack via Docker Compose.
set -e

if [ ! -f .env ]; then
  echo "No .env found, copying .env.example -> .env"
  cp .env.example .env
fi

docker compose up --build -d

echo ""
echo "Stack starting. Once ready:"
echo "  Backend:   http://localhost:8000/docs"
echo "  Frontend:  http://localhost:4173"
echo ""
echo "Run ./health_check.sh to verify everything is up."
