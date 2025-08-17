#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed successfully." 