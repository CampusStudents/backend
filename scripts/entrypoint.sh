#!/bin/bash
set -e

./scripts/run_migrations.sh

exec uv run -m src.main
