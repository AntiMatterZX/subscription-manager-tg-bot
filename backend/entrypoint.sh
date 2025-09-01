#!/bin/bash
set -e

# Check if the migrations directory exists, if not, initialize and migrate
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
    flask db migrate -m "Initial migration"
elif [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
    echo "No migration versions found. Creating initial migration..."
    flask db migrate -m "Initial migration"
fi

# Apply database upgrades
echo "Applying database migrations..."
flask db upgrade

# Start the application
echo "Starting application server..."
exec gunicorn --worker-class eventlet -w 1 "run:app" --bind "0.0.0.0:5000"
