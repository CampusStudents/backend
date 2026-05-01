#!/bin/bash
set -e

./scripts/run_migrations.sh

exec gunicorn src.main:main_app -c gunicorn_config.py
