#!/bin/bash

# Run database migrations
poetry run flask db upgrade

# Start the application
poetry run kusibot