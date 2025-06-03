#!/bin/bash
set -e

# Run database migrations
poetry run flask db upgrade

sleep 5m

# Start the application
exec gunicorn --bind 0.0.0.0:8000 "app:create_app('prod')"