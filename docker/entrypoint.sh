#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -U bookuser -d booksdb > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start application
echo "Starting application..."
exec "$@"
