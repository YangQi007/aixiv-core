#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
echo "Applying database migrations..."
alembic upgrade head
echo "Migrations applied successfully."

# Start the Uvicorn server
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 