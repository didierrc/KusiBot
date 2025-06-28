#!/bin/bash
set -e

echo "Setting up instance folder..."
mkdir -p /app/instance
chmod -R 777 /app/instance

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:5000 "app:create_app('prod')"