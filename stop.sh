#!/usr/bin/env bash
# Stops and removes all containers started for this project.
set -e

docker compose down

echo "All services stopped."
