#!/bin/bash
set -e

./scripts/run_migrations.sh

exec python -m src.main